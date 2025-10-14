# world_server/ecs/systems/needs_system.py
from world_server.ecs.system import System
from world_server.ecs.components.needs import NeedsComponent
from world_server.ecs.components.state import StateComponent
from world_server.ecs.components.economy import EconomyComponent
from world_server.resource_manager import ResourceManager

class NeedsSystem(System):
    """
    Handles the progression of NPC needs over time and sets goals when thresholds are met.
    """
    def __init__(self):
        super().__init__()
        self.last_hour = 0

    def process(self, locations, interactions):
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
        entities_with_needs = self.world.get_entities_with_components(NeedsComponent)
        for entity_id in entities_with_needs:
            needs_comp = self.world.get_component(entity_id, NeedsComponent)

            # Update hunger
            hunger_change = needs_comp.needs['hunger']['change_per_hour']
            needs_comp.needs['hunger']['current'] = min(needs_comp.needs['hunger']['max'], needs_comp.needs['hunger']['current'] + hunger_change)

            # Update energy
            energy_change = needs_comp.needs['energy']['change_per_hour']
            needs_comp.needs['energy']['current'] = max(0, needs_comp.needs['energy']['current'] + energy_change)

            # Update stress
            stress_change = needs_comp.needs['stress']['change_per_hour']
            needs_comp.needs['stress']['current'] = min(needs_comp.needs['stress']['max'], needs_comp.needs['stress']['current'] + stress_change)

            # Update idealism
            idealism_change = needs_comp.needs['idealism']['change_per_hour']
            needs_comp.needs['idealism']['current'] = max(0, needs_comp.needs['idealism']['current'] + idealism_change)

    def _evaluate_entity_needs(self, entity_id, locations):
        """Evaluates an individual entity's needs and sets a goal if necessary."""
        needs_comp = self.world.get_component(entity_id, NeedsComponent)
        state_comp = self.world.get_component(entity_id, StateComponent)
        economy_comp = self.world.get_component(entity_id, EconomyComponent)

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

        # Tier 2 (Societal/Ideological)
        if "WORK" in needs_comp.demands:
            work_locations = [loc for loc in locations if loc.get('type') == 'WORKPLACE']
            if work_locations:
                target_loc = work_locations[0] # Simplified
                state_comp.goal = {"type": "GO_TO_LOCATION", "target_location_id": target_loc['id'], "purpose": "WORK"}
                return

        # Default to wander
        if state_comp.goal in ["Wander", "Idle"]:
            state_comp.goal = "Wander"