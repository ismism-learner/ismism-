# world_server/ecs/systems/hobby_system.py
import random
from ..system import System
from ..components.hobby_component import HobbyComponent

class HobbySystem(System):
    """
    Manages the logic for NPCs performing hobbies and producing goods.
    """
    def __init__(self, world, consumer_goods_def):
        super().__init__(world)
        self.consumer_goods_def = consumer_goods_def

    def perform_hobby(self, entity_id, hobby_id):
        """
        Processes an NPC's hobby action, producing a good and potentially increasing skill.
        """
        hobby_comp = self.world.get_component(entity_id, HobbyComponent)
        if not hobby_comp:
            # This NPC doesn't have hobbies, so do nothing.
            return

        skill_level = hobby_comp.skills.get(hobby_id, 1)

        # Determine the quality of the produced good based on skill
        possible_goods = [g for g in self.consumer_goods_def if g['hobby'] == hobby_id and g['tier'] <= skill_level]
        if not possible_goods:
            # No goods can be produced at this skill level
            return

        produced_good = random.choice(possible_goods)

        # Add the new good to the NPC's inventory
        hobby_comp.inventory.append(produced_good)
        print(f"Entity {entity_id} produced {produced_good['name']} through {hobby_id}.")

        # Chance to increase skill
        if random.random() < 0.1: # 10% chance to improve
            hobby_comp.skills[hobby_id] = min(10, skill_level + 1)
            print(f"Entity {entity_id}'s skill in {hobby_id} increased to {hobby_comp.skills[hobby_id]}!")