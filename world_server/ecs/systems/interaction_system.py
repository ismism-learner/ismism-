# world_server/ecs/systems/interaction_system.py
import random
from world_server.ecs.system import System
from world_server.ecs.components.position import PositionComponent
from world_server.ecs.components.ism import IsmComponent
from world_server.ecs.components.relationship import RelationshipComponent
from world_server.ecs.components.needs import NeedsComponent
from world_server.ecs.components.state import StateComponent
from world_server.ecs.components.identity import IdentityComponent

class InteractionSystem(System):
    """
    Manages social interactions between entities.
    """
    def process(self, interactions, *args, **kwargs):
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
                    self._evaluate_and_initiate_interaction(entity_id, other_id, interactions)
                    break # Interact with only one entity per tick to simplify logic

    def _get_all_ism_keywords(self, entity_id):
        ism_comp = self.world.get_component(entity_id, IsmComponent)
        keywords = set()
        ism_data = ism_comp.data
        for key in ['field_theory', 'ontology', 'epistemology', 'teleology']:
            keywords.update(ism_data.get(key, {}).get('keywords', []))
        for secondary_ism in ism_data.get('secondary_isms', []):
            for key in ['field_theory', 'ontology', 'epistemology', 'teleology']:
                keywords.update(secondary_ism.get(key, {}).get('keywords', []))
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

    def _evaluate_and_initiate_interaction(self, initiator_id, target_id, interactions):
        possible_interactions = [
            inter for inter in interactions if self._check_interaction_conditions(inter, initiator_id, target_id)
        ]
        if not possible_interactions:
            return

        # Decision logic
        relationship_comp = self.world.get_component(initiator_id, RelationshipComponent)
        affinity = relationship_comp.relations.get(target_id, {}).get("affinity", 0)

        chosen_interaction = None
        if affinity < -20:
            hostile_options = [i for i in possible_interactions if i.get('type') == 'aggressive']
            if hostile_options: chosen_interaction = random.choice(hostile_options)
        elif affinity > 20:
            friendly_options = [i for i in possible_interactions if i.get('type') == 'friendly']
            if friendly_options: chosen_interaction = random.choice(friendly_options)
        else:
            chosen_interaction = random.choice(possible_interactions)

        if chosen_interaction:
            self._apply_interaction(chosen_interaction, initiator_id, target_id)

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

        print(f"'{target_identity.name}' reacts. Affinity towards '{initiator_identity.name}' is now {new_target_affinity}.")