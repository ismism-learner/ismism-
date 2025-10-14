import json
import copy

def get_default_npc_parameters():
    """
    Returns a deep copy of the default NPC parameter structure.
    """
    return {
        "identity": {
            "primary_ism_code": "",
            "primary_ism_name": "",
            "equipped_isms": [], # List of {"code": "x", "name": "y", "weight": z}
            "npc_name": "",
            "description_prompt": ""
        },
        "core_motivations": { "order_vs_chaos": 0, "altruism_vs_egoism": 0, "tradition_vs_progress": 0, "fatalism_vs_agency": 0 },
        "worldview": { "mysticism_vs_rationalism": 0, "divinity_perception": "INDIFFERENT" },
        "social_profile": { "sociability": 0, "trust_level": 50, "faction_loyalty": 0, "conflict_stance": "OBSERVER", "hierarchy_acceptance": 0 },
        "behavior_patterns": { "risk_taking": 0, "proactivity": 0, "pragmatism_vs_idealism": 0, "materialism": 0 },
        "behavioral_scripts": {
            "hunger_satisfaction": "DEFAULT_EAT",
            "leisure_activity": "DEFAULT_WANDER",
            "social_interaction": "DEFAULT_GREET",
            "conflict_resolution": "DEFAULT_FLEE"
        },
        "quest_preferences": { "RESEARCH": 0, "DIPLOMACY": 0, "EXPLORATION": 0, "COMBAT": 0, "COLLECTION": 0, "PILGRIMAGE": 0, "ESPIONAGE": 0, "CONQUEST": 0, "ALCHEMY": 0, "RITUAL": 0, "DEBATE": 0 },
        "dialogue_cues": { "keywords": [] }
    }

def load_rules(filepath="rules.json"):
    """
    Loads the quantization rules from a JSON file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_rules_fusion(weighted_isms, rules):
    """
    Applies a set of rules to a weighted list of isms to generate a single,
    fused set of NPC parameters.

    Args:
        weighted_isms (list): A list of dictionaries, where each dict is
                              {"ism": ism_data, "weight": float}.
        rules (list): A list of rule objects loaded from rules.json.

    Returns:
        dict: The fully calculated and fused NPC parameter space.
    """
    final_npc_params = get_default_npc_parameters()

    # --- Populate Identity ---
    if weighted_isms:
        primary_ism = weighted_isms[0]["ism"]
        final_npc_params["identity"]["primary_ism_code"] = primary_ism.get("code", "N/A")
        final_npc_params["identity"]["primary_ism_name"] = primary_ism.get("name", "N/A")
        final_npc_params["identity"]["equipped_isms"] = [
            {"code": item["ism"].get("code"), "name": item["ism"].get("name"), "weight": item.get("weight")}
            for item in weighted_isms
        ]

    all_keywords = set()

    # --- Fusion Logic ---
    for item in weighted_isms:
        ism_data = item["ism"]
        weight = item["weight"]

        # Collect all keywords for dialogue cues
        for scope in ["field_theory", "ontology", "epistemology", "teleology"]:
            all_keywords.update(ism_data.get(scope, []))

        # Apply rules for this specific ism
        for rule in rules:
            conditions_met = True
            for clause in rule["conditions"]["clauses"]:
                scope = clause["scope"]
                keyword = clause["keyword"]

                if scope in ["field_theory", "ontology", "epistemology", "teleology"]:
                    if keyword not in ism_data.get(scope, []): conditions_met = False; break
                elif scope == "code" and not ism_data.get("code", "").startswith(keyword): conditions_met = False; break
                elif scope == "name" and keyword not in ism_data.get("name", ""): conditions_met = False; break

            if conditions_met:
                for action in rule["actions"]:
                    param_path = action["param"].split('.')
                    op = action["operation"]
                    target = final_npc_params
                    for key in param_path[:-1]: target = target[key]
                    final_key = param_path[-1]

                    if op == "add" or op == "add_weight":
                        # Apply weight only to numerical additions
                        weighted_value = action["value"] * weight
                        target[final_key] += weighted_value
                    elif op == "set":
                        # For "set", the last one applied wins, weight is ignored.
                        # This is a design choice for definitive actions.
                        target[final_key] = action["value"]

    final_npc_params["dialogue_cues"]["keywords"] = sorted(list(all_keywords))
    return final_npc_params

if __name__ == '__main__':
    # ================== Example Usage for Fusion Engine ==================
    print("--- Testing the new Fusion Engine ---")

    # 1. Mock "ism" data that would be loaded by the parser
    # A noble scholar who is also a cynic and a bit of a slob
    ethical_intellectualism = {"code": "2-1-2-1", "name": "伦理智性主义", "field_theory": ["本质"], "ontology": ["善"], "epistemology": ["理论"], "teleology": ["安歇"]}
    cynicism = {"code": "2-1-3-4", "name": "犬儒主义", "field_theory": ["数"], "ontology": ["犬儒"], "epistemology": ["实践"], "teleology": ["安歇"]}
    vulgarism = {"code": "1-4-4-2", "name": "粗俗主义", "field_theory": ["庸俗"], "ontology": ["粗俗"], "epistemology": ["实践"], "teleology": ["冲突"]}

    # 2. Define the NPC's "equipped" isms with weights
    npc_composition = [
        {"ism": ethical_intellectualism, "weight": 1.0}, # Primary
        {"ism": cynicism, "weight": 0.6},
        {"ism": vulgarism, "weight": 0.4}
    ]

    # 3. Load the rules
    try:
        loaded_rules = load_rules()
        print(f"Successfully loaded {len(loaded_rules)} rules.")
    except FileNotFoundError:
        print("Error: rules.json not found.")
        exit()

    # 4. Apply the rules to generate the fused NPC
    fused_npc = apply_rules_fusion(npc_composition, loaded_rules)

    # 5. Print the result
    print("\n--- Generated Fused NPC Parameters ---")
    print(json.dumps(fused_npc, indent=2, ensure_ascii=False))