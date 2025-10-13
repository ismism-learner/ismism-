import json
import copy

def get_default_npc_parameters():
    """
    Returns a deep copy of the default NPC parameter structure (v2 draft).
    Ensures that each NPC starts from a fresh, neutral baseline.
    """
    return {
        "identity": {
            "ism_code": "",
            "ism_name": "",
            "npc_name": "",
            "description_prompt": ""
        },
        "core_motivations": {
            "order_vs_chaos": 0,
            "altruism_vs_egoism": 0,
            "tradition_vs_progress": 0,
            "fatalism_vs_agency": 0
        },
        "worldview": {
            "mysticism_vs_rationalism": 0,
            "divinity_perception": "INDIFFERENT"
        },
        "social_profile": {
            "sociability": 0,
            "trust_level": 50,
            "faction_loyalty": 0,
            "conflict_stance": "OBSERVER",
            "hierarchy_acceptance": 0
        },
        "behavior_patterns": {
            "risk_taking": 0,
            "proactivity": 0,
            "pragmatism_vs_idealism": 0,
            "materialism": 0
        },
        "quest_preferences": {
            "RESEARCH": 0,
            "DIPLOMACY": 0,
            "EXPLORATION": 0,
            "COMBAT": 0,
            "COLLECTION": 0,
            "PILGRIMAGE": 0,
            "ESPIONAGE": 0,
            "CONQUEST": 0,
            "ALCHEMY": 0,
            "RITUAL": 0,
            "DEBATE": 0
        },
        "dialogue_cues": {
            "field_theory": [],
            "ontology": [],
            "epistemology": [],
            "teleology": [],
            "keywords": []
        }
    }

def load_rules(filepath="rules.json"):
    """
    Loads the quantization rules from a JSON file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_rules(ism_data, rules):
    """
    Applies a set of rules to an ism's data to generate NPC parameters.

    Args:
        ism_data (dict): A dictionary containing the ism's keyword vectors.
                         e.g., {"field_theory": ["世界", "对抗", "时间"], ...}
        rules (list): A list of rule objects loaded from rules.json.

    Returns:
        dict: The fully calculated NPC parameter space.
    """
    npc_params = get_default_npc_parameters()

    # Populate identity and dialogue cues first
    # (This assumes ism_data also contains 'code' and 'name' for simplicity)
    npc_params["identity"]["ism_code"] = ism_data.get("code", "N/A")
    npc_params["identity"]["ism_name"] = ism_data.get("name", "N/A")
    npc_params["dialogue_cues"]["field_theory"] = ism_data.get("field_theory", [])
    npc_params["dialogue_cues"]["ontology"] = ism_data.get("ontology", [])
    npc_params["dialogue_cues"]["epistemology"] = ism_data.get("epistemology", [])
    npc_params["dialogue_cues"]["teleology"] = ism_data.get("teleology", [])
    
    all_keywords = set()
    for keywords in ism_data.values():
        if isinstance(keywords, list):
            all_keywords.update(keywords)
    npc_params["dialogue_cues"]["keywords"] = list(all_keywords)


    for rule in rules:
        conditions_met = True
        # Currently only supports AND logic, can be extended for OR/NOT
        for clause in rule["conditions"]["clauses"]:
            scope = clause["scope"]
            keyword = clause["keyword"]
            if keyword not in ism_data.get(scope, []):
                conditions_met = False
                break
        
        if conditions_met:
            for action in rule["actions"]:
                param_path = action["param"].split('.')
                op = action["operation"]
                value = action["value"]

                # Navigate the parameter path
                target = npc_params
                for i, key in enumerate(param_path[:-1]):
                    target = target[key]
                
                final_key = param_path[-1]

                if op == "add":
                    target[final_key] += value
                elif op == "set":
                    target[final_key] = value
                elif op == "add_weight": # Specific for quest_preferences
                    target[final_key] += value

    return npc_params

if __name__ == '__main__':
    # ================== Example Usage ==================
    # This is a test case demonstrating how the engine will be used.
    # We will replace this with the actual data parser later.

    # 1. Define a sample "ism" based on our discussion of Apeironism
    apeironism = {
        "code": "2-1-1-1",
        "name": "阿派朗主义",
        "field_theory": ["世界", "对抗", "时间"],
        "ontology": ["Apeiron"],
        "epistemology": ["有序的理性世界"],
        "teleology": ["和谐/有序", "循环"]
    }

    # 2. Load the rules
    try:
        loaded_rules = load_rules()
        print(f"Successfully loaded {len(loaded_rules)} rules.")
    except FileNotFoundError:
        print("Error: rules.json not found. Please create it.")
        exit()

    # 3. Apply the rules to generate the NPC
    generated_npc = apply_rules(apeironism, loaded_rules)

    # 4. Print the result
    print("\n--- Generated NPC Parameters for '阿派朗主义' ---")
    print(json.dumps(generated_npc, indent=2, ensure_ascii=False))