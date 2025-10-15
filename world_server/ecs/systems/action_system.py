# world_server/ecs/systems/action_system.py
import random
from world_server.ecs.system import System
from world_server.ecs.components.position import PositionComponent
from world_server.ecs.components.state import StateComponent
from world_server.ecs.components.needs import NeedsComponent
from world_server.ecs.components.economy import EconomyComponent
from world_server.ecs.components.ism import IsmComponent
from world_server.resource_manager import ResourceManager

class ActionSystem(System):
    """
    Executes actions for entities when they reach their goal destination.
    """
    def process(self, locations, *args, **kwargs):
        entities_with_goals = self.world.get_entities_with_components(PositionComponent, StateComponent, NeedsComponent)
        ideology_system = self.world.ideology_system if hasattr(self.world, 'ideology_system') else None

        for entity_id in entities_with_goals:
            # Check if the entity has an ideology component to reinforce
            if not self.world.has_component(entity_id, IsmComponent):
                continue

            pos_comp = self.world.get_component(entity_id, PositionComponent)
            state_comp = self.world.get_component(entity_id, StateComponent)

            if not (isinstance(state_comp.goal, dict) and state_comp.goal.get("type") == "GO_TO_LOCATION"):
                continue

            target_loc_id = state_comp.goal["target_location_id"]
            target_loc = next((loc for loc in locations if loc['id'] == target_loc_id), None)

            if not target_loc:
                state_comp.goal = "Wander"
                continue

            dist_to_target = ((pos_comp.x - target_loc['position']['x'])**2 + (pos_comp.y - target_loc['position']['y'])**2)**0.5

            if dist_to_target <= target_loc.get("radius", 10):
                purpose = state_comp.goal.get("purpose")
                needs_comp = self.world.get_component(entity_id, NeedsComponent)
                action_keywords = []

                if purpose == "SATISFY_HUNGER":
                    state_comp.action = "Eating"
                    if ResourceManager.consume(target_loc, "GRAIN", 5, locations):
                        needs_comp.needs['hunger']['current'] = max(0, needs_comp.needs['hunger']['current'] - 25)
                        action_keywords = ["SURVIVAL", "CONSUMPTION", "SUSTENANCE"]
                        if needs_comp.needs['hunger']['current'] <= 0:
                            state_comp.goal = "Wander"
                    else:
                        state_comp.action = "Confused (No Food)"
                        state_comp.goal = "Wander"

                elif purpose == "REST":
                    state_comp.action = "Sleeping"
                    needs_comp.needs['energy']['current'] = min(needs_comp.needs['energy']['max'], needs_comp.needs['energy']['current'] + 2.5)
                    action_keywords = ["RECOVERY", "REST", "PEACE"]
                    if needs_comp.needs['energy']['current'] >= needs_comp.needs['energy']['max']:
                        state_comp.goal = "Wander"

                elif purpose == "WORK":
                    economy_comp = self.world.get_component(entity_id, EconomyComponent)
                    work_type = target_loc.get('work_type', 'Working')
                    state_comp.action = f"{work_type}"
                    ResourceManager.produce(target_loc, self.world)
                    economy_comp.money += 1
                    needs_comp.needs['energy']['current'] = max(0, needs_comp.needs['energy']['current'] - 0.2)
                    needs_comp.needs['stress']['current'] = min(needs_comp.needs['stress']['max'], needs_comp.needs['stress']['current'] + 0.3)

                    action_keywords = ["PRODUCTION", "DUTY", "LABOR", "ECONOMY", work_type.upper()]

                    if work_type == "ALCHEMY":
                        self.world.tech_system.add_tech_points(self.world, "alchemy", 1)
                        action_keywords.extend(["KNOWLEDGE", "TRANSFORMATION"])
                    elif work_type == "AUTOMATA":
                        self.world.tech_system.add_tech_points(self.world, "automata", 1)
                        action_keywords.extend(["INVENTION", "MECHANISM"])

                    if random.random() < 0.03:
                        state_comp.goal = "Wander"

                elif purpose == "SEEK_ENTERTAINMENT":
                    economy_comp = self.world.get_component(entity_id, EconomyComponent)
                    cost = target_loc.get('cost', 0)
                    state_comp.action = f"Enjoying at {target_loc['name']}"
                    economy_comp.money -= cost
                    needs_comp.needs['stress']['current'] = max(0, needs_comp.needs['stress']['current'] - 50)
                    action_keywords = ["LEISURE", "CULTURE", "CONSUMPTION", "ART"]
                    state_comp.goal = "Wander"

                elif purpose == "PURSUE_HOBBY":
                    hobby_id = state_comp.goal.get("hobby_id")
                    if hobby_id and self.world.hobby_system:
                        state_comp.action = f"Pursuing hobby: {hobby_id}"
                        self.world.hobby_system.perform_hobby(entity_id, hobby_id)
                        if 'fulfillment' in needs_comp.needs:
                            needs_comp.needs['fulfillment']['current'] = max(0, needs_comp.needs['fulfillment']['current'] - 50)
                        needs_comp.needs['stress']['current'] = max(0, needs_comp.needs['stress']['current'] - 10)
                        action_keywords = ["CREATIVITY", "FULFILLMENT", "LEISURE", hobby_id.upper()]
                    state_comp.goal = "Wander"

                elif purpose == "BUY_LUXURY_GOOD" or purpose == "BUY_GOOD":
                    economy_comp = self.world.get_component(entity_id, EconomyComponent)
                    cost = 150
                    state_comp.action = f"Buying {target_loc.get('produces', 'goods')}"
                    if economy_comp.money >= cost:
                        economy_comp.money -= cost
                        needs_comp.needs['stress']['current'] = max(0, needs_comp.needs['stress']['current'] - 20)
                        if 'fulfillment' in needs_comp.needs:
                             needs_comp.needs['fulfillment']['current'] = max(0, needs_comp.needs['fulfillment']['current'] - 30)
                        action_keywords = ["COMMERCE", "LUXURY", "CONSUMPTION", "WEALTH"]
                    else:
                        state_comp.action = "Window Shopping"
                        action_keywords = ["DESIRE", "FRUSTRATION", "POVERTY"]
                    state_comp.goal = "Wander"

                elif purpose == "SELL_GOODS":
                    state_comp.action = "Selling Goods"
                    hobby_comp = self.world.get_component(entity_id, HobbyComponent)
                    economy_comp = self.world.get_component(entity_id, EconomyComponent)

                    if hobby_comp and hobby_comp.inventory:
                        item_to_sell = hobby_comp.inventory.pop(0)
                        sale_price = item_to_sell.get('base_value', 10)
                        economy_comp.money += sale_price
                        if 'inventory' not in target_loc:
                            target_loc['inventory'] = {}
                        item_name = item_to_sell['name']
                        target_loc['inventory'][item_name] = target_loc['inventory'].get(item_name, 0) + 1
                        print(f"INFO: {entity_id} sold {item_name} for {sale_price} gold.")

                        action_keywords = ["COMMERCE", "PROFIT", "PRODUCTION", "AMBITION"]

                        if hasattr(self.world, 'desire_system'):
                            trigger_event = {'type': 'SOLD_GOODS', 'hobby_id': item_to_sell.get('hobby_origin'), 'value': sale_price}
                            self.world.desire_system.generate_imaginary_aspiration(entity_id, trigger_event)

                    state_comp.goal = "Wander"

                # --- IDEOLOGY REINFORCEMENT HOOK ---
                if action_keywords and ideology_system:
                    ideology_system.reinforce(entity_id, action_keywords)