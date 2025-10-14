# world_server/ecs/systems/hobby_system.py
import random
from ..system import System
from ..components.hobby_component import HobbyComponent
from ..components.needs import NeedsComponent
from ..components.ism import IsmComponent

class HobbySystem(System):
    """
    Manages the logic for NPCs performing hobbies, producing goods, and discovering new recipes.
    """
    def __init__(self, consumer_goods_def):
        super().__init__()
        self.consumer_goods_def = consumer_goods_def
        # Keep track of globally discovered recipes
        self.discovered_recipes = set()

    def process(self, *args, **kwargs):
        pass

    def _check_for_discovery(self, entity_id, hobby_id, skill_level):
        """
        Checks if an NPC discovers a new recipe based on hobby, skill, ontology, and world state.
        """
        needs_comp = self.world.get_component(entity_id, NeedsComponent)
        ism_comp = self.world.get_component(entity_id, IsmComponent)
        tech_system = self.world.tech_system # Get the technology system from the world
        if not needs_comp or not ism_comp or not tech_system:
            return

        # Get the NPC's ontology keywords from the IsmComponent
        npc_ontology_keywords = set(ism_comp.data.get("dialogue_cues", {}).get("keywords", []))

        # Base discovery chance is very low
        base_discovery_chance = 0.01

        # High stress acts as a catalyst for discovery
        stress_multiplier = 5.0 if needs_comp.stress > 70 else 1.0

        # Find potential undiscovered recipes that match the NPC's hobby, ontology, and tech level
        potential_discoveries = []
        for good in self.consumer_goods_def:
            if (good.get('discoverable') and
                    good['good_id'] not in self.discovered_recipes and
                    good['hobby'] == hobby_id):

                # 1. Check Technology Requirement
                tech_field = good.get('tech_field')
                required_level = good.get('required_tech_level', 0)
                current_tech_level = tech_system.tech_levels.get(tech_field, {}).get('level', 0)

                if current_tech_level < required_level:
                    continue # Not advanced enough to discover this yet

                # 2. Check Ontology Requirement
                required_ontology = set(good.get('required_ontology', []))
                if not required_ontology.issubset(npc_ontology_keywords):
                    continue # NPC's philosophy doesn't align

                # If all checks pass, it's a potential discovery
                potential_discoveries.append(good)

        if not potential_discoveries:
            return

        # The higher the tech level is *above* the requirement, the easier the discovery
        # We calculate this for the first potential discovery for simplicity
        first_potential = potential_discoveries[0]
        tech_field = first_potential.get('tech_field')
        required_level = first_potential.get('required_tech_level', 0)
        current_tech_level = tech_system.tech_levels.get(tech_field, {}).get('level', 0)
        tech_bonus_multiplier = 1.0 + ( (current_tech_level - required_level) * 0.5) # 50% bonus per level above req

        discovery_chance = base_discovery_chance * stress_multiplier * tech_bonus_multiplier

        if random.random() < discovery_chance:
            # A discovery is made!
            discovered_good = random.choice(potential_discoveries)
            discovered_id = discovered_good['good_id']
            self.discovered_recipes.add(discovered_id)
            print(f"🌟 [Discovery] Through reconciling their philosophy of {list(discovered_good.get('required_ontology', []))} with their craft, Entity {entity_id} has discovered the recipe for {discovered_good['name']}!")

    def perform_hobby(self, entity_id, hobby_id):
        """
        Processes an NPC's hobby action, producing a good and potentially increasing skill.
        Also gives a chance for discovering new recipes.
        """
        hobby_comp = self.world.get_component(entity_id, HobbyComponent)
        if not hobby_comp:
            return

        skill_level = hobby_comp.skills.get(hobby_id, 1)

        # First, check for a discovery event before producing a regular item
        self._check_for_discovery(entity_id, hobby_id, skill_level)

        # Determine the quality of the produced good based on skill and discovered recipes
        possible_goods = [
            g for g in self.consumer_goods_def
            if g['hobby'] == hobby_id and g['tier'] <= skill_level and (not g.get('discoverable') or g['good_id'] in self.discovered_recipes)
        ]

        if not possible_goods:
            return

        produced_good_template = random.choice(possible_goods)
        new_good = produced_good_template.copy()
        new_good['hobby_origin'] = hobby_id

        hobby_comp.inventory.append(new_good)
        print(f"Entity {entity_id} produced {new_good['name']} through {hobby_id}.")

        # Chance to increase skill
        if random.random() < 0.1:  # 10% chance to improve
            hobby_comp.skills[hobby_id] = min(10, skill_level + 1)
            print(f"Entity {entity_id}'s skill in {hobby_id} increased to {hobby_comp.skills[hobby_id]}!")