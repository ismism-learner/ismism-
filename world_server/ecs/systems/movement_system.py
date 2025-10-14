# world_server/ecs/systems/movement_system.py
import random
from world_server.ecs.system import System
from world_server.ecs.components.position import PositionComponent
from world_server.ecs.components.state import StateComponent

class MovementSystem(System):
    """
    Handles the movement of entities based on their current goal.
    """
    def process(self, *args, **kwargs):
        locations = kwargs.get('locations', [])
        speed = 2
        entities_to_move = self.world.get_entities_with_components(PositionComponent, StateComponent)

        for entity_id in entities_to_move:
            pos_comp = self.world.get_component(entity_id, PositionComponent)
            state_comp = self.world.get_component(entity_id, StateComponent)

            move_x, move_y = 0, 0

            # --- Movement logic based on goal ---
            if isinstance(state_comp.goal, dict) and state_comp.goal.get("type") == "GO_TO_LOCATION":
                target_loc_id = state_comp.goal["target_location_id"]
                target_loc = next((loc for loc in locations if loc['id'] == target_loc_id), None)

                if target_loc:
                    target_pos = target_loc["position"]
                    dist_to_target = ((pos_comp.x - target_pos['x'])**2 + (pos_comp.y - target_pos['y'])**2)**0.5

                    # If not yet at the destination, move towards it
                    if dist_to_target > target_loc.get("radius", 10):
                        state_comp.action = f"Going to {target_loc['name']}"
                        dx = target_pos['x'] - pos_comp.x
                        dy = target_pos['y'] - pos_comp.y
                        if dist_to_target > 0:
                            move_x = (dx / dist_to_target) * speed
                            move_y = (dy / dist_to_target) * speed
                    # Else, the entity has arrived. The ActionSystem will handle the logic at the location.

            elif state_comp.goal == "Wander":
                state_comp.action = "Wandering"
                move_x, move_y = random.choice([-speed, speed, 0]), random.choice([-speed, speed, 0])

            # Add other non-location-based movement goals here if needed
            # e.g., elif state_comp.goal == "FLEE_FROM_THREAT":

            # --- Update position ---
            if move_x != 0 or move_y != 0:
                pos_comp.x = max(0, min(800, pos_comp.x + move_x))
                pos_comp.y = max(0, min(600, pos_comp.y + move_y))