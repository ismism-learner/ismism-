import json
import os
import random
import sys
import uuid

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world_server.generators.biography_generator import generate_biography
from world_server.generators.mind_generator import generate_npc_mind

class NpcDatabaseGenerator:
    def __init__(self):
        self.locations = []
        self.regions = {}
        self.all_isms_data = []
        self.isms_by_id = {}
        self.consumer_goods = []
        self._load_game_definitions()

    def _load_game_definitions(self):
        """Loads all static data files needed for NPC generation."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..'))

        def load_json_file(file_path, error_message, default_value=None):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                print(f"Error: {error_message} '{file_path}' not found.")
                return default_value
            except json.JSONDecodeError:
                print(f"Error: {error_message} '{file_path}' is not valid JSON.")
                return default_value

        isms_path = os.path.join(project_root, "isms_final.json")
        self.all_isms_data = load_json_file(isms_path, "Ism data file", [])
        if self.all_isms_data:
            self.isms_by_id = {ism['id']: ism for ism in self.all_isms_data if 'id' in ism}

        locations_path = os.path.join(script_dir, "locations.json")
        locations_data = load_json_file(locations_path, "Locations file", [])
        if locations_data:
            for i, loc in enumerate(locations_data):
                loc['id'] = f"loc_{i}"
            self.locations = locations_data

        regions_path = os.path.join(script_dir, "regions.json")
        self.regions = load_json_file(regions_path, "Regions file", {})

        goods_path = os.path.join(script_dir, "consumer_goods.json")
        self.consumer_goods = load_json_file(goods_path, "Consumer goods file", [])


    def generate_npcs(self, num_npcs):
        """Generates a specified number of NPCs and returns them as a list of dictionaries."""
        if not self.isms_by_id or not self.locations or not self.regions:
            print("Error: Game data is not loaded correctly. Cannot generate NPCs.")
            return []

        npc_database = []
        for _ in range(num_npcs):
            entity_id = str(uuid.uuid4())

            # 1. Select birthplace and region
            birthplace_loc = random.choice(self.locations)
            birthplace_id = birthplace_loc['id']
            region_id = birthplace_loc.get('region_id')

            if not region_id or region_id not in self.regions:
                continue

            region_data = self.regions[region_id]

            # 2. Generate Biography
            biography = generate_biography(region_id, region_data)

            # 3. Generate Mind (Ideologies)
            initial_ideologies = generate_npc_mind(region_data, biography, self.isms_by_id)
            if not initial_ideologies:
                continue

            # 4. Create Components
            primary_ism_id = initial_ideologies[0]['code']
            ism_data = self.isms_by_id.get(primary_ism_id, {})
            npc_name = ism_data.get("name", "Nameless")

            identity_comp = {
                "name": npc_name,
                "description": f"A {biography['social_class']} with {biography['education']} education.",
                "birthplace": birthplace_id,
                "biography": biography
            }

            position_comp = {"x": random.randint(50, 750), "y": random.randint(50, 550)}

            ism_comp = {"active_ideologies": initial_ideologies}

            initial_stress = random.randint(0, 30)
            initial_money = random.randint(20, 100)
            birthplace_type = birthplace_loc.get('type')

            if birthplace_type in ['WORKPLACE', 'FOOD_SOURCE']:
                initial_stress += 10; initial_money -= 15
            elif birthplace_type in ['CENTRAL_BANK', 'COMMERCIAL_BANK', 'MARKETPLACE']:
                initial_stress -= 5; initial_money += 30

            needs_comp = {
                "needs": {
                    "hunger": {"current": random.randint(0, 40), "max": 100, "rate_of_change": 0.1},
                    "energy": {"current": random.randint(50, 90), "max": 100, "rate_of_change": 0.05},
                    "stress": {"current": max(0, min(initial_stress, 100)), "max": 100, "rate_of_change": 0}
                },
                "demands": [],
                "desire": {
                    "imaginary": {"aspirations": []},
                    "symbolic": {"aspirations": []},
                    "real": {"rupture": 0, "trauma_source": None}
                }
            }

            economy_comp = {"money": max(1, initial_money)}
            state_comp = {"action": "IDLE", "goal": None}
            relationship_comp = {"relations": {}}
            financial_comp = {"loans": 0.0}

            all_philosophy_keywords = []
            for ideology in initial_ideologies:
                philosophy_values = []
                def extract_values(d):
                    for v in d.values():
                        if isinstance(v, str): philosophy_values.append(v)
                        elif isinstance(v, dict): extract_values(v)
                extract_values(ideology.get("data", {}))
                all_philosophy_keywords.extend(philosophy_values)
            ism_keywords = " ".join(all_philosophy_keywords)

            hobby_comp = {"interests": {}, "skills": {}, "inventory": []}
            if "科学" in ism_keywords or "技术" in ism_keywords:
                hobby_comp["interests"]["AUTOMATA"] = random.uniform(60, 90)
                hobby_comp["interests"]["ALCHEMY"] = random.uniform(50, 80)
                hobby_comp["skills"][random.choice(["AUTOMATA", "ALCHEMY"])] = random.randint(1, 3)
            if "艺术" in ism_keywords or "美学" in ism_keywords:
                hobby_comp["interests"]["PAINTING"] = random.uniform(60, 90)
                hobby_comp["interests"]["CRAFTING"] = random.uniform(40, 70)
                hobby_comp["skills"]["PAINTING"] = random.randint(1, 3)
            hobby_comp["interests"]["EXERCISE"] = random.uniform(10, 40)

            npc_data = {
                "id": entity_id,
                "components": {
                    "identity": identity_comp,
                    "position": position_comp,
                    "ism": ism_comp,
                    "needs": needs_comp,
                    "economy": economy_comp,
                    "state": state_comp,
                    "relationship": relationship_comp,
                    "financial": financial_comp,
                    "hobby": hobby_comp,
                    "sensory_log": {"log": []},
                    "social_ledger": {"entries": []},
                    "cognitive_map": {"known_locations": {}},
                    "praxis_ledger": {"actions": []}
                }
            }
            npc_database.append(npc_data)

        return npc_database

    def save_to_file(self, npc_database, filename="npc_database.json"):
        """Saves the NPC database to a JSON file."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(npc_database, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved {len(npc_database)} NPCs to '{file_path}'.")

if __name__ == "__main__":
    generator = NpcDatabaseGenerator()
    num_npcs = 50 # Number of NPCs to generate
    npc_data = generator.generate_npcs(num_npcs)
    if npc_data:
        generator.save_to_file(npc_data)