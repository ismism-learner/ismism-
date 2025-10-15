# world_server/ecs/systems/interaction_system.py
import random
from world_server.ecs.system import System
from world_server.ecs.components.position import PositionComponent
from world_server.ecs.components.ism import IsmComponent
from world_server.ecs.components.relationship import RelationshipComponent
from world_server.ecs.components.needs import NeedsComponent
from world_server.ecs.components.state import StateComponent
from world_server.ecs.components.identity import IdentityComponent

# Map pillar names to their index in the IXP matrix, matching EvolutionSystem
PILLAR_MAP = {"field": 0, "ontology": 1, "epistemology": 2, "teleology": 3}
# Map stage names to their index in the IXP matrix
STAGE_MAP = {"identity": 0, "contradiction": 1, "synthesis": 2, "collapse": 3}

class InteractionSystem(System):
    """
    Manages social interactions between entities.
    """
    def process(self, *args, **kwargs):
        interactions = kwargs.get('interactions', [])
        relationship_types = kwargs.get('relationship_types', {})
        # This check is expensive, so we don't run it every single tick.
        if random.random() > 0.05:
            return

        all_entities = self.world.get_entities_with_components(
            PositionComponent, IsmComponent, RelationshipComponent, NeedsComponent, StateComponent
        )

        for entity_id in all_entities:
            # Re-fetch in case components were modified by a previous interaction in the same tick
            pos_comp = self.world.get_component(entity_id, PositionComponent)

            for other_id in all_entities:
                if entity_id == other_id:
                    continue

                other_pos_comp = self.world.get_component(other_id, PositionComponent)

                dist = ((pos_comp.x - other_pos_comp.x)**2 + (pos_comp.y - other_pos_comp.y)**2)**0.5
                if dist < 80: # Interaction distance
                    self._evaluate_and_initiate_interaction(entity_id, other_id, interactions, relationship_types)
                    break # Interact with only one entity per tick to simplify logic

    def _get_all_ism_keywords(self, entity_id):
        """
        Extracts all unique, non-empty string keywords from an entity's active ideologies.
        This involves recursively searching through the philosophy data structures.
        """
        ism_comp = self.world.get_component(entity_id, IsmComponent)
        keywords = set()

        if not ism_comp or not ism_comp.active_ideologies:
            return []

        # This recursive function will dig through dictionaries to find all string values.
        def extract_keywords_recursive(data):
            if isinstance(data, str):
                if data: # Ensure the string is not empty
                    keywords.add(data)
            elif isinstance(data, dict):
                for value in data.values():
                    extract_keywords_recursive(value)
            elif isinstance(data, list):
                 for item in data:
                    extract_keywords_recursive(item)

        for ideology in ism_comp.active_ideologies:
            # The actual philosophical data is stored under the 'data' key of each ideology object.
            philosophy_data = ideology.get('data', {})
            extract_keywords_recursive(philosophy_data)

        return list(keywords)

    def _check_interaction_conditions(self, interaction, initiator_id, target_id):
        initiator_keywords = self._get_all_ism_keywords(initiator_id)
        target_keywords = self._get_all_ism_keywords(target_id)
        conditions = interaction.get('conditions', {})

        if 'initiator_has_any_keyword' in conditions and not any(k in initiator_keywords for k in conditions['initiator_has_any_keyword']):
            return False
        if 'target_has_any_keyword' in conditions and not any(k in target_keywords for k in conditions['target_has_any_keyword']):
            return False
        if 'target_must_not_have_keyword' in conditions and any(k in target_keywords for k in conditions['target_must_not_have_keyword']):
            return False
        return True

    def _evaluate_and_initiate_interaction(self, initiator_id, target_id, interactions, relationship_types):
        possible_interactions = [
            inter for inter in interactions if self._check_interaction_conditions(inter, initiator_id, target_id)
        ]
        if not possible_interactions:
            return

        # Decision logic
        relationship_comp = self.world.get_component(initiator_id, RelationshipComponent)
        relation_data = relationship_comp.relations.get(target_id, {})
        affinity = relation_data.get("affinity", 0)
        status = relation_data.get("status")

        # --- New logic for behavior mods ---
        behavior_mods = relationship_types.get(status, {}).get("behavior_mods", {})
        forbidden = behavior_mods.get("forbidden_interactions", [])
        prioritized = behavior_mods.get("prioritized_interactions", [])

        # Filter out forbidden interactions
        possible_interactions = [inter for inter in possible_interactions if inter['name'] not in forbidden]

        if not possible_interactions:
            return

        # --- New: Weight interactions using the Final Decision Matrix ---
        initiator_ism_comp = self.world.get_component(initiator_id, IsmComponent)
        matrix = initiator_ism_comp.final_decision_matrix
        field_theory_vec = matrix[0] # Social disposition
        epistemology_vec = matrix[2] # Information/knowledge disposition

        weights = []
        for inter in possible_interactions:
            # Start with a base weight of 1
            weight = 1.0
            # Aggressive interactions are favored by "Contradiction"
            if inter.get('type') == 'aggressive':
                weight += 4.0 * field_theory_vec[1] # Contradiction
            # Friendly interactions are favored by "Synthesis"
            if inter.get('type') == 'friendly':
                weight += 4.0 * field_theory_vec[2] # Synthesis
            # Knowledge-based interactions (like Discuss Philosophy) are favored by Epistemology
            if inter.get('keyword') == 'KNOWLEDGE':
                 # Identity (dogmatic), Contradiction (debate), Synthesis (learning)
                weight += 2.0 * (epistemology_vec[0] + epistemology_vec[1] + epistemology_vec[2])

            # Apply multiplier for prioritized interactions from relationship status
            if inter['name'] in prioritized:
                weight *= 5

            weights.append(weight)

        chosen_interaction = random.choices(possible_interactions, weights=weights, k=1)[0]

        if chosen_interaction:
            self._apply_interaction(chosen_interaction, initiator_id, target_id)

    def _apply_ixp_gain(self, entity_id, ixp_gain_data):
        """Applies IXP gain to a specific entity."""
        if not ixp_gain_data:
            return

        ism_comp = self.world.get_component(entity_id, IsmComponent)
        if not ism_comp:
            return

        for pillar_name, stages in ixp_gain_data.items():
            pillar_index = PILLAR_MAP.get(pillar_name.lower())
            if pillar_index is None:
                continue

            for stage_name, value in stages.items():
                stage_index = STAGE_MAP.get(stage_name.lower())
                if stage_index is None:
                    continue

                ism_comp.ixp[pillar_index][stage_index] += value
                # print(f"Entity {entity_id} gained {value} IXP in {pillar_name}/{stage_name}") # DEBUG

    def _apply_interaction(self, interaction, initiator_id, target_id):
        initiator_identity = self.world.get_component(initiator_id, IdentityComponent)
        target_identity = self.world.get_component(target_id, IdentityComponent)
        print(f"'{initiator_identity.name}' initiates '{interaction['name']}' with '{target_identity.name}'.")

        effects = interaction.get('effects', {})

        # Apply effects to initiator
        initiator_needs = self.world.get_component(initiator_id, NeedsComponent)
        initiator_needs.needs['idealism']['current'] += effects.get('initiator_idealism_change', 0)

        # --- Apply effects to target and initiator (bidirectional relationship update) ---
        initiator_rels = self.world.get_component(initiator_id, RelationshipComponent)
        target_needs = self.world.get_component(target_id, NeedsComponent)
        target_rels = self.world.get_component(target_id, RelationshipComponent)

        affinity_change = effects.get('base_affinity_change', 0)

        # Update target's affinity towards initiator
        current_target_affinity = target_rels.relations.get(initiator_id, {}).get("affinity", 0)
        new_target_affinity = current_target_affinity + affinity_change
        target_rels.relations[initiator_id] = {"affinity": new_target_affinity}

        # Update initiator's affinity towards target
        current_initiator_affinity = initiator_rels.relations.get(target_id, {}).get("affinity", 0)
        new_initiator_affinity = current_initiator_affinity + affinity_change
        initiator_rels.relations[target_id] = {"affinity": new_initiator_affinity}

        target_needs.needs['idealism']['current'] += effects.get('target_idealism_change', 0)
        target_needs.desire['real']['rupture'] += effects.get('target_rupture_change', 0)
        if effects.get('target_rupture_change', 0) > 0:
            target_needs.desire['real']['source_of_trauma'] = initiator_id

        # Reaction logic
        target_state = self.world.get_component(target_id, StateComponent)
        if interaction.get('type') == 'aggressive':
            target_state.goal = "FLEE_FROM_THREAT"
            target_state.action = "Fleeing"

        # --- New IXP Gain Logic ---
        ixp_gain = effects.get('ixp_gain', {})
        if ixp_gain:
            self._apply_ixp_gain(initiator_id, ixp_gain.get('initiator'))
            self._apply_ixp_gain(target_id, ixp_gain.get('target'))

        # --- New 'Ism' Propagation Logic ---
        propagate_chance = effects.get('propagate_ism_chance', 0)
        if random.random() < propagate_chance:
            initiator_ism_comp = self.world.get_component(initiator_id, IsmComponent)
            target_ism_comp = self.world.get_component(target_id, IsmComponent)

            # Can only propagate secondary isms to avoid overwriting primary identity
            if initiator_ism_comp.data.get('secondary_isms'):
                ism_to_propagate = random.choice(initiator_ism_comp.data['secondary_isms'])

                # Ensure the target doesn't already have this ism
                target_primary_ism = target_ism_comp.data.get('primary_ism_code')
                target_secondary_codes = [ism.get('ism_code') for ism in target_ism_comp.data.get('secondary_isms', [])]

                if ism_to_propagate['ism_code'] != target_primary_ism and ism_to_propagate['ism_code'] not in target_secondary_codes:
                    if 'secondary_isms' not in target_ism_comp.data:
                        target_ism_comp.data['secondary_isms'] = []
                    target_ism_comp.data['secondary_isms'].append(ism_to_propagate)
                    print(f"**IDEOLOGY SPREAD**: '{initiator_identity.name}' propagated '{ism_to_propagate['name']}' to '{target_identity.name}'!")


        print(f"'{target_identity.name}' reacts. Affinity towards '{initiator_identity.name}' is now {new_target_affinity}.")