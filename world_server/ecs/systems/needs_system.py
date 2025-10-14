# world_server/ecs/systems/needs_system.py
from world_server.ecs.system import System
from world_server.ecs.components.needs import NeedsComponent
from world_server.ecs.components.state import StateComponent
from world_server.ecs.components.economy import EconomyComponent
from world_server.ecs.components.financial_component import FinancialComponent
from world_server.ecs.components.hobby_component import HobbyComponent
from world_server.resource_manager import ResourceManager
import random

class NeedsSystem(System):
    """
    Handles the progression of NPC needs over time and sets goals when thresholds are met.
    """
    def __init__(self):
        super().__init__()
        self.last_hour = 0

    def process(self, *args, **kwargs):
        locations = kwargs.get('locations', [])
        # Part 1: Update needs based on time
        current_hour = self.world.time // self.world.ticks_per_hour
        if current_hour > self.last_hour:
            self._update_hourly_needs()
            self.last_hour = current_hour

        # Part 2: Evaluate needs and set goals for each entity
        entities_with_needs = self.world.get_entities_with_components(NeedsComponent, StateComponent, EconomyComponent)
        for entity_id in entities_with_needs:
            self._evaluate_entity_needs(entity_id, locations)

    def _update_hourly_needs(self):
        """Updates the needs for all entities that change on an hourly basis."""
        # Query for all components at once for efficiency
        # We now need IsmComponent to access the quantification data
        from world_server.ecs.components.ism import IsmComponent
        entities_to_update = self.world.get_entities_with_components(NeedsComponent, FinancialComponent, IsmComponent, StateComponent)

        for entity_id in entities_to_update:
            needs_comp = self.world.get_component(entity_id, NeedsComponent)
            financial_comp = self.world.get_component(entity_id, FinancialComponent)
            ism_comp = self.world.get_component(entity_id, IsmComponent)
            state_comp = self.world.get_component(entity_id, StateComponent)

            # Update hunger
            hunger_change = needs_comp.needs['hunger']['change_per_hour']
            needs_comp.needs['hunger']['current'] = min(needs_comp.needs['hunger']['max'], needs_comp.needs['hunger']['current'] + hunger_change)

            # Update energy
            energy_change = needs_comp.needs['energy']['change_per_hour']
            needs_comp.needs['energy']['current'] = max(0, needs_comp.needs['energy']['current'] + energy_change)

            # Update stress
            stress_resistance = needs_comp.alchemy_bonus.get('stress_resistance', 0.0)
            base_stress_change = needs_comp.needs['stress']['change_per_hour']

            # --- New: Debt-induced Stress ---
            debt_stress_increase = 0
            if financial_comp and financial_comp.loans > 0:
                # Stress increases by 0.1 per hour for every 100 in debt.
                debt_stress_increase = (financial_comp.loans / 100) * 0.1

            # --- New: Ism-based Stress Modification ---
            ism_stress_modifier = 1.0 # Default modifier
            # Check if the NPC is currently idle/unemployed
            if not needs_comp.demands and state_comp.goal in ["Wander", "Idle"]:
                conformity_score = ism_comp.quantification.get('axes', {}).get('conformity_rebellion', 0.0)
                if conformity_score <= -0.5: # High conformity
                    ism_stress_modifier = 0.5 # More content with doing nothing, half stress gain
                elif conformity_score >= 0.5: # High rebellion
                    ism_stress_modifier = 2.0 # More anxious when idle, double stress gain

            total_stress_change = (base_stress_change + debt_stress_increase) * ism_stress_modifier * (1 - stress_resistance)
            needs_comp.needs['stress']['current'] = min(needs_comp.needs['stress']['max'], needs_comp.needs['stress']['current'] + total_stress_change)

            # Update idealism
            idealism_change = needs_comp.needs['idealism']['change_per_hour']
            needs_comp.needs['idealism']['current'] = max(0, needs_comp.needs['idealism']['current'] + idealism_change)

            # Update fulfillment
            if 'fulfillment' in needs_comp.needs:
                fulfillment_change = needs_comp.needs['fulfillment']['change_per_hour']
                needs_comp.needs['fulfillment']['current'] = min(needs_comp.needs['fulfillment']['max'], needs_comp.needs['fulfillment']['current'] + fulfillment_change)


    def _evaluate_entity_needs(self, entity_id, locations):
        """Evaluates an individual entity's needs and sets a goal if necessary."""
        needs_comp = self.world.get_component(entity_id, NeedsComponent)
        state_comp = self.world.get_component(entity_id, StateComponent)
        economy_comp = self.world.get_component(entity_id, EconomyComponent)
        financial_comp = self.world.get_component(entity_id, FinancialComponent)

        # Do not re-evaluate if already on a critical mission
        if isinstance(state_comp.goal, dict) or state_comp.goal in ["FLEE_FROM_THREAT", "REPLACE_SOURCE_OF_TRAUMA"]:
             return

        # Tier 3 (Real)
        if needs_comp.desire['real']['rupture'] > 50 and needs_comp.desire['real']['source_of_trauma']:
            state_comp.goal = "REPLACE_SOURCE_OF_TRAUMA"
            return

        # Tier 1 (Physiological)
        # Hunger
        if needs_comp.needs['hunger']['current'] > needs_comp.needs['hunger']['priority_threshold']:
            best_food_location = ResourceManager.get_richest_location("GRAIN", locations)
            if best_food_location:
                state_comp.goal = {"type": "GO_TO_LOCATION", "target_location_id": best_food_location['id'], "purpose": "SATISFY_HUNGER"}
                return

        # Energy
        if needs_comp.needs['energy']['current'] < needs_comp.needs['energy']['priority_threshold']:
            shelter_locations = [loc for loc in locations if loc.get('type') == 'SHELTER']
            if shelter_locations:
                # Simplified: just pick one, not closest
                target_loc = shelter_locations[0]
                state_comp.goal = {"type": "GO_TO_LOCATION", "target_location_id": target_loc['id'], "purpose": "REST"}
                return

        # Stress
        if needs_comp.needs['stress']['current'] > needs_comp.needs['stress']['priority_threshold']:
            affordable_locations = [loc for loc in locations if loc.get('type') == 'ENTERTAINMENT' and economy_comp.money >= loc.get('cost', 0)]
            if affordable_locations:
                target_loc = affordable_locations[0] # Simplified
                state_comp.goal = {"type": "GO_TO_LOCATION", "target_location_id": target_loc['id'], "purpose": "SEEK_ENTERTAINMENT"}
                return

        # Fulfillment/Hobbies
        if 'fulfillment' in needs_comp.needs and needs_comp.needs['fulfillment']['current'] > needs_comp.needs['fulfillment']['priority_threshold']:
            hobby_comp = self.world.get_component(entity_id, HobbyComponent)
            if hobby_comp and hobby_comp.interests:
                # Find a hobby the NPC is interested in
                # For now, just pick the one with the highest interest
                top_hobby = max(hobby_comp.interests, key=hobby_comp.interests.get)

                # Find a location for this hobby
                # This is a simplified search logic
                hobby_locations = [
                    loc for loc in locations if (
                        (loc.get('type') == 'HOBBY_LOCATION' and loc.get('hobby_type') == top_hobby) or
                        (loc.get('type') == 'WORKPLACE' and loc.get('work_type') == top_hobby)
                    )
                ]

                if hobby_locations:
                    target_loc = random.choice(hobby_locations)
                    state_comp.goal = {"type": "GO_TO_LOCATION", "target_location_id": target_loc['id'], "purpose": "PURSUE_HOBBY", "hobby_id": top_hobby}
                    return

        # --- New Financial Needs ---

        # 0. Desire to sell goods when low on cash and holding inventory
        hobby_comp = self.world.get_component(entity_id, HobbyComponent)
        if economy_comp.money < 50 and hobby_comp and hobby_comp.inventory:
            market_locations = [loc for loc in locations if loc.get('type') == 'MARKETPLACE']
            if market_locations:
                target_loc = random.choice(market_locations)
                state_comp.goal = {"type": "GO_TO_LOCATION", "target_location_id": target_loc['id'], "purpose": "SELL_GOODS"}
                return

        # 1. Desire to deposit excess cash
        if economy_comp.money > 200:
            bank_locations = [loc for loc in locations if loc.get('type') == 'COMMERCIAL_BANK']
            if bank_locations:
                target_loc = random.choice(bank_locations)
                state_comp.goal = {"type": "GO_TO_LOCATION", "target_location_id": target_loc['id'], "purpose": "DEPOSIT_MONEY"}
                return

        # 2. Desire to get a loan for opportunities
        # (Simplified: "WORK" demand implies a desire to invest/expand)
        if economy_comp.money < 50 and financial_comp.credit_score > 500 and "WORK" in needs_comp.demands:
            bank_locations = [loc for loc in locations if loc.get('type') == 'COMMERCIAL_BANK']
            if bank_locations:
                target_loc = random.choice(bank_locations)
                state_comp.goal = {"type": "GO_TO_LOCATION", "target_location_id": target_loc['id'], "purpose": "GET_LOAN"}
                return

        # 3. Desire for luxury goods when wealthy
        if financial_comp.bank_balance > 1000:
             # Find luxury shops
            luxury_shops = [loc for loc in locations if loc.get('produces') in ['LUXURY_GOOD', 'ARTWORK']]
            if luxury_shops:
                target_loc = random.choice(luxury_shops)
                state_comp.goal = {"type": "GO_TO_LOCATION", "target_location_id": target_loc['id'], "purpose": "BUY_LUXURY_GOOD"}
                # We would also need to add logic in ActionSystem to handle the actual purchase
                return

        # Tier 2 (Societal/Ideological) - Now handles complex demands
        if needs_comp.demands:
            # For now, just process the first demand in the list
            demand = needs_comp.demands[0]

            if demand['type'] == 'WORK':
                work_locations = [loc for loc in locations if loc.get('type') == 'WORKPLACE']
                if work_locations:
                    # This could be improved to find a specific kind of work
                    target_loc = work_locations[0] # Simplified
                    state_comp.goal = {"type": "GO_TO_LOCATION", "target_location_id": target_loc['id'], "purpose": "WORK"}
                    # Note: We don't remove the demand here, allowing it to be a continuous driver.
                    # A more advanced system could have conditions for demand completion.
                    return

            elif demand['type'] == 'PURSUE_HOBBY':
                hobby_id = demand.get('hobby_id')
                # Find a location for this hobby
                hobby_locations = [
                    loc for loc in locations if (
                        (loc.get('type') == 'HOBBY_LOCATION' and loc.get('hobby_type') == hobby_id) or
                        (loc.get('type') == 'WORKPLACE' and loc.get('work_type') == hobby_id)
                    )
                ]
                if hobby_locations:
                    target_loc = random.choice(hobby_locations)
                    state_comp.goal = {"type": "GO_TO_LOCATION", "target_location_id": target_loc['id'], "purpose": "PURSUE_HOBBY", "hobby_id": hobby_id}
                    # This is a one-time action derived from an aspiration, so we remove the demand upon acting on it.
                    needs_comp.demands.pop(0)
                    return

        # Default to wander
        if state_comp.goal in ["Wander", "Idle"]:
            state_comp.goal = "Wander"