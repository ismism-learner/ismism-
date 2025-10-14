# world_server/ecs/systems/desire_system.py
from ..system import System
from ..components.needs import NeedsComponent
from ..components.hobby_component import HobbyComponent
from ..components.relationship import RelationshipComponent

class DesireSystem(System):
    """
    Manages the lifecycle of NPC desires, generating long-term Aspirations
    and breaking them down into actionable Demands.
    """
    def __init__(self):
        super().__init__()

    def process(self, *args, **kwargs):
        """
        Main loop for the desire system.
        Currently focuses on breaking down existing aspirations into demands.
        """
        entities_with_needs = self.world.get_entities_with_components(NeedsComponent)
        for entity_id in entities_with_needs:
            self._breakdown_aspirations(entity_id)

    def generate_imaginary_aspiration(self, entity_id, trigger_event: dict):
        """
        Generates a new Aspiration based on ambition and completed goals.
        This will be called by other systems (e.g., ActionSystem) upon goal completion.
        """
        needs_comp = self.world.get_component(entity_id, NeedsComponent)
        print(f"DEBUG: Generating imaginary aspiration for {entity_id} due to trigger: {trigger_event}")
        # Placeholder logic: If an NPC sells a good, they aspire to earn more money.
        if trigger_event.get('type') == 'SOLD_GOODS':
            new_aspiration = {'type': 'EARN_MONEY_FROM_HOBBY', 'amount': 200, 'hobby_id': trigger_event.get('hobby_id')}
            # Avoid duplicate aspirations
            if new_aspiration not in needs_comp.desire['imaginary']['aspirations']:
                needs_comp.desire['imaginary']['aspirations'].append(new_aspiration)
                print(f"INFO: {entity_id} now aspires to {new_aspiration['type']}!")

    def generate_symbolic_aspiration(self, entity_id, trigger_event: dict):
        """
        Generates a new Aspiration based on social recognition and relationships.
        This will be called by the RelationshipManager.
        """
        needs_comp = self.world.get_component(entity_id, NeedsComponent)
        print(f"DEBUG: Generating symbolic aspiration for {entity_id} due to trigger: {trigger_event}")
        # Placeholder logic: If an NPC gains a rival, they aspire to outperform them.
        if trigger_event.get('type') == 'GAINED_RIVAL':
            rival_id = trigger_event.get('target_id')
            # Determine shared hobby/field
            own_hobby_comp = self.world.get_component(entity_id, HobbyComponent)
            rival_hobby_comp = self.world.get_component(rival_id, HobbyComponent)
            if own_hobby_comp and rival_hobby_comp:
                shared_hobbies = set(own_hobby_comp.interests.keys()) & set(rival_hobby_comp.interests.keys())
                if shared_hobbies:
                    hobby_to_compete_in = list(shared_hobbies)[0] # Compete in the first shared hobby
                    new_aspiration = {'type': 'OUTPERFORM_RIVAL', 'rival_id': rival_id, 'hobby_id': hobby_to_compete_in}
                    if new_aspiration not in needs_comp.desire['symbolic']['aspirations']:
                        needs_comp.desire['symbolic']['aspirations'].append(new_aspiration)
                        print(f"INFO: {entity_id} now aspires to {new_aspiration['type']} in {hobby_to_compete_in}!")


    def _breakdown_aspirations(self, entity_id):
        """
        Checks an entity's aspirations and creates concrete Demands to fulfill them.
        """
        needs_comp = self.world.get_component(entity_id, NeedsComponent)
        hobby_comp = self.world.get_component(entity_id, HobbyComponent)

        # Combine all aspirations for processing
        all_aspirations = needs_comp.desire['imaginary']['aspirations'] + needs_comp.desire['symbolic']['aspirations']

        for aspiration in all_aspirations:
            # Simple breakdown logic for now
            if aspiration['type'] == 'EARN_MONEY_FROM_HOBBY':
                # To earn money, the NPC needs to craft and sell items.
                # This creates a demand to pursue the relevant hobby.
                demand = {'type': 'PURSUE_HOBBY', 'hobby_id': aspiration['hobby_id'], 'reason': 'aspiration_earn_money'}
                if demand not in needs_comp.demands:
                    needs_comp.demands.append(demand)
                    print(f"INFO: {entity_id} now has a demand to pursue {demand['hobby_id']} to earn money.")

            elif aspiration['type'] == 'OUTPERFORM_RIVAL':
                # To outperform a rival, the NPC must improve their skill.
                demand = {'type': 'PURSUE_HOBBY', 'hobby_id': aspiration['hobby_id'], 'reason': 'aspiration_outperform_rival'}
                if demand not in needs_comp.demands:
                    needs_comp.demands.append(demand)
                    print(f"INFO: {entity_id} now has a demand to pursue {demand['hobby_id']} to beat their rival.")