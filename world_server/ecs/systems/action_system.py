# world_server/ecs/systems/action_system.py
import random
from world_server.ecs.system import System
from world_server.ecs.components.position import PositionComponent
from world_server.ecs.components.state import StateComponent
from world_server.ecs.components.needs import NeedsComponent
from world_server.ecs.components.economy import EconomyComponent
from world_server.resource_manager import ResourceManager

class ActionSystem(System):
    """
    Executes actions for entities when they reach their goal destination.
    """
    def process(self, locations, *args, **kwargs):
        entities_with_goals = self.world.get_entities_with_components(PositionComponent, StateComponent, NeedsComponent)

        for entity_id in entities_with_goals:
            pos_comp = self.world.get_component(entity_id, PositionComponent)
            state_comp = self.world.get_component(entity_id, StateComponent)

            # Check if the entity has a location-based goal
            if not (isinstance(state_comp.goal, dict) and state_comp.goal.get("type") == "GO_TO_LOCATION"):
                continue

            target_loc_id = state_comp.goal["target_location_id"]
            target_loc = next((loc for loc in locations if loc['id'] == target_loc_id), None)

            if not target_loc:
                state_comp.goal = "Wander" # Target location doesn't exist, reset goal
                continue

            dist_to_target = ((pos_comp.x - target_loc['position']['x'])**2 + (pos_comp.y - target_loc['position']['y'])**2)**0.5

            # If the entity has arrived at the location
            if dist_to_target <= target_loc.get("radius", 10):
                purpose = state_comp.goal.get("purpose")
                needs_comp = self.world.get_component(entity_id, NeedsComponent)

                if purpose == "SATISFY_HUNGER":
                    state_comp.action = "Eating"
                    if ResourceManager.consume(target_loc, "GRAIN", 5, locations):
                        needs_comp.needs['hunger']['current'] = max(0, needs_comp.needs['hunger']['current'] - 25)
                        if needs_comp.needs['hunger']['current'] <= 0:
                            state_comp.goal = "Wander"
                    else:
                        state_comp.action = "Confused (No Food)"
                        state_comp.goal = "Wander"

                elif purpose == "REST":
                    state_comp.action = "Sleeping"
                    needs_comp.needs['energy']['current'] = min(needs_comp.needs['energy']['max'], needs_comp.needs['energy']['current'] + 2.5)
                    if needs_comp.needs['energy']['current'] >= needs_comp.needs['energy']['max']:
                        state_comp.goal = "Wander"

                elif purpose == "WORK":
                    economy_comp = self.world.get_component(entity_id, EconomyComponent)
                    work_type = target_loc.get('work_type', 'Working')
                    state_comp.action = f"{work_type}"

                    # Produce resources
                    ResourceManager.produce(target_loc, locations)

                    # Gain money and affect needs
                    economy_comp.money += 1
                    needs_comp.needs['energy']['current'] = max(0, needs_comp.needs['energy']['current'] - 0.2)
                    needs_comp.needs['stress']['current'] = min(needs_comp.needs['stress']['max'], needs_comp.needs['stress']['current'] + 0.3)

                    # --- Contribute to Technology ---
                    if work_type == "ALCHEMY":
                        self.world.tech_system.add_tech_points(self.world, "alchemy", 1)
                    elif work_type == "AUTOMATA":
                        self.world.tech_system.add_tech_points(self.world, "automata", 1)

                    if random.random() < 0.03:
                        state_comp.goal = "Wander"

                elif purpose == "SEEK_ENTERTAINMENT":
                    economy_comp = self.world.get_component(entity_id, EconomyComponent)
                    cost = target_loc.get('cost', 0)
                    state_comp.action = f"Enjoying at {target_loc['name']}"
                    economy_comp.money -= cost
                    needs_comp.needs['stress']['current'] = max(0, needs_comp.needs['stress']['current'] - 50)
                    # Ideological influence can be handled here as well
                    state_comp.goal = "Wander"

                elif purpose == "PURSUE_HOBBY":
                    hobby_id = state_comp.goal.get("hobby_id")
                    if hobby_id and self.world.hobby_system:
                        state_comp.action = f"Pursuing hobby: {hobby_id}"
                        self.world.hobby_system.perform_hobby(entity_id, hobby_id)

                        # Reduce fulfillment need
                        if 'fulfillment' in needs_comp.needs:
                            needs_comp.needs['fulfillment']['current'] = max(0, needs_comp.needs['fulfillment']['current'] - 50)

                        # Hobby also reduces some stress
                        needs_comp.needs['stress']['current'] = max(0, needs_comp.needs['stress']['current'] - 10)

                    # For now, pursuing a hobby is a one-time action, then they wander off
                    state_comp.goal = "Wander"

                elif purpose == "BUY_LUXURY_GOOD" or purpose == "BUY_GOOD":
                    economy_comp = self.world.get_component(entity_id, EconomyComponent)
                    # For simplicity, let's assume a fixed cost for luxury goods
                    cost = 150
                    state_comp.action = f"Buying {target_loc.get('produces', 'goods')}"
                    if economy_comp.money >= cost:
                        economy_comp.money -= cost
                        needs_comp.needs['stress']['current'] = max(0, needs_comp.needs['stress']['current'] - 20) # Satisfaction
                        if 'fulfillment' in needs_comp.needs:
                             needs_comp.needs['fulfillment']['current'] = max(0, needs_comp.needs['fulfillment']['current'] - 30)
                    else:
                        # If they can't afford it, maybe try to withdraw from bank first?
                        # For now, just reset. This could be a future improvement.
                        state_comp.action = "Window Shopping"
                    state_comp.goal = "Wander"

                # After completing an action, the goal is often reset
                # If goal is not reset inside the purpose block, it means it's a continuous action
                # like working or sleeping.