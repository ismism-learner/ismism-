# world_server/ecs/systems/desire_system.py
from ..system import System
from ..components.needs import NeedsComponent
from ..components.hobby_component import HobbyComponent
from ..components.relationship import RelationshipComponent
from ..components.financial_component import FinancialComponent

# Define a constant for the debt threshold to trigger aspirations
DEBT_ASPIRATION_THRESHOLD = 500

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
        1. Checks for new desire-triggering conditions.
        2. Breaks down existing aspirations into actionable demands.
        """
        # We need IsmComponent to access the decision matrix
        from ..components.ism import IsmComponent
        entities_to_process = self.world.get_entities_with_components(NeedsComponent, FinancialComponent, IsmComponent)

        for entity_id in entities_to_process:
            self._check_for_event_driven_triggers(entity_id)
            # New: Periodically check for ideology-driven aspirations
            if self.world.time % 100 == 0: # Check roughly every few days
                self._generate_ideological_aspirations(entity_id)
            self._breakdown_aspirations(entity_id)

    def _check_for_event_driven_triggers(self, entity_id):
        """Checks for specific world-state events that can trigger new aspirations."""
        financial_comp = self.world.get_component(entity_id, FinancialComponent)
        if financial_comp.loans > DEBT_ASPIRATION_THRESHOLD:
            # Check if this aspiration already exists to avoid spamming
            needs_comp = self.world.get_component(entity_id, NeedsComponent)
            if not any(a['type'] == 'ACHIEVE_FINANCIAL_STABILITY' for a in needs_comp.desire['symbolic']['aspirations']):
                self.generate_financial_aspiration(entity_id, {'type': 'HIGH_DEBT', 'amount': financial_comp.loans})

    def _generate_ideological_aspirations(self, entity_id):
        """
        Generates long-term aspirations based on the NPC's core Teleology.
        This is driven by the final_decision_matrix.
        """
        ism_comp = self.world.get_component(entity_id, IsmComponent)
        needs_comp = self.world.get_component(entity_id, NeedsComponent)
        teleology_vec = ism_comp.final_decision_matrix[3] # Purpose/Goal pillar

        # [3][0] = Identity (Self-preservation, self-improvement)
        if teleology_vec[0] > 0.6 and random.random() < 0.1:
             new_aspiration = {'type': 'MASTER_PRIMARY_HOBBY'}
             if not any(a['type'] == new_aspiration['type'] for a in needs_comp.desire['imaginary']['aspirations']):
                 needs_comp.desire['imaginary']['aspirations'].append(new_aspiration)
                 print(f"INFO: {entity_id} is driven by their ideology to master their primary hobby!")

        # [3][1] = Contradiction (Overcoming a challenge, defeating a rival)
        if teleology_vec[1] > 0.6 and random.random() < 0.1:
            # This is a good place to hook into the rivalry system more abstractly
            # For now, let's create a generic "seek power" aspiration
            new_aspiration = {'type': 'SEEK_POWER_OVER_OTHERS'}
            if not any(a['type'] == new_aspiration['type'] for a in needs_comp.desire['symbolic']['aspirations']):
                 needs_comp.desire['symbolic']['aspirations'].append(new_aspiration)
                 print(f"INFO: {entity_id} is driven by their ideology to seek power!")

        # [3][2] = Synthesis (Community building, achieving harmony)
        if teleology_vec[2] > 0.6 and random.random() < 0.1:
            new_aspiration = {'type': 'BUILD_COMMUNITY_PROJECT'}
            if not any(a['type'] == new_aspiration['type'] for a in needs_comp.desire['symbolic']['aspirations']):
                 needs_comp.desire['symbolic']['aspirations'].append(new_aspiration)
                 print(f"INFO: {entity_id} is driven by their ideology to build a community project!")

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

    def generate_financial_aspiration(self, entity_id, trigger_event: dict):
        """
        Generates a new Aspiration based on financial distress.
        """
        needs_comp = self.world.get_component(entity_id, NeedsComponent)
        print(f"DEBUG: Generating financial aspiration for {entity_id} due to trigger: {trigger_event}")
        new_aspiration = {'type': 'ACHIEVE_FINANCIAL_STABILITY'}
        if new_aspiration not in needs_comp.desire['symbolic']['aspirations']:
            needs_comp.desire['symbolic']['aspirations'].append(new_aspiration)
            print(f"INFO: {entity_id}, burdened by debt, now aspires to achieve financial stability!")


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
                    # print(f"INFO: {entity_id} now has a demand to pursue {demand['hobby_id']} to earn money.")

            elif aspiration['type'] == 'OUTPERFORM_RIVAL':
                # To outperform a rival, the NPC must improve their skill.
                demand = {'type': 'PURSUE_HOBBY', 'hobby_id': aspiration['hobby_id'], 'reason': 'aspiration_outperform_rival'}
                if demand not in needs_comp.demands:
                    needs_comp.demands.append(demand)
                    # print(f"INFO: {entity_id} now has a demand to pursue {demand['hobby_id']} to beat their rival.")

            elif aspiration['type'] == 'ACHIEVE_FINANCIAL_STABILITY':
                # To achieve stability, the NPC needs to work diligently.
                # This creates a persistent 'WORK' demand.
                # This is a simplification; a more complex system could generate more varied demands.
                demand = {'type': 'WORK'}
                if demand not in needs_comp.demands:
                    needs_comp.demands.append(demand)
                    print(f"INFO: {entity_id} is now driven by a demand to WORK to achieve financial stability.")