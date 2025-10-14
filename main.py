import os
import json
import random
import shutil
from data_parser import load_all_data
from quantization_engine import load_rules, apply_rules_fusion

# --- Config ---
TOC_FILE = 'ismism-/主义主义/目录.md'
CSV_DATA_FILE = 'ismism-/主义主义/isms_data.csv'
RULES_FILE = 'rules.json'
OUTPUT_DIR = 'generated_npcs_final'
NUM_NPCS_TO_GENERATE = 50

# --- Helper Functions ---
def get_isms_by_prefix(isms_db, prefix):
    return [ism for ism in isms_db if ism.get("code", "").startswith(prefix)]

def get_isms_with_keyword(isms_db, scope, keyword):
    return [ism for ism in isms_db if keyword in ism.get(scope, [])]

def get_unique_ism(pool, used_codes):
    """Gets a unique ism from the pool that hasn't been used yet."""
    available = [ism for ism in pool if ism["code"] not in used_codes]
    if not available:
        return None
    return random.choice(available)

# --- Main Application ---
def generate_final_npcs():
    """
    The main function to generate NPCs based on refined archetypes.
    """
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    print(f"Cleaned and created output directory: {OUTPUT_DIR}")

    all_isms = load_all_data(TOC_FILE, CSV_DATA_FILE)
    rules = load_rules(RULES_FILE)

    if not all_isms or not rules:
        print("Could not load isms or rules. Halting.")
        return

    # --- Refined Archetype Definitions ---
    # We create more specific pools to ensure diversity
    archetypes = {
        "Philosopher_King": {
            "primary_pool": get_isms_by_prefix(all_isms, "3-"), # Must be an idealist
            "secondary_pool": get_isms_with_keyword(all_isms, "ontology", "善") + get_isms_with_keyword(all_isms, "ontology", "理念"),
            "num_secondary": random.randint(1, 2),
            "naming_prefix": "PhilosopherKing"
        },
        "Cynical_Guard": {
            "primary_pool": get_isms_with_keyword(all_isms, "name", "犬儒"),
            "secondary_pool": get_isms_with_keyword(all_isms, "field_theory", "庸俗") + get_isms_with_keyword(all_isms, "teleology", "冲突"),
            "num_secondary": random.randint(2, 3),
            "naming_prefix": "CynicalGuard"
        },
        "Materialist_Merchant": {
            "primary_pool": get_isms_with_keyword(all_isms, "ontology", "欲望"),
            "secondary_pool": get_isms_with_keyword(all_isms, "field_theory", "意志") + get_isms_with_keyword(all_isms, "epistemology", "实践"),
            "num_secondary": random.randint(2, 3),
            "naming_prefix": "MaterialistMerchant"
        }
    }

    generated_count = 0
    for i in range(NUM_NPCS_TO_GENERATE):
        archetype_name = random.choice(list(archetypes.keys()))
        archetype = archetypes[archetype_name]

        used_codes = set()
        weighted_isms = []

        # 1. Select Primary Ism
        primary_ism = get_unique_ism(archetype["primary_pool"], used_codes)
        if primary_ism:
            used_codes.add(primary_ism["code"])
            weighted_isms.append({"ism": primary_ism, "weight": 1.0})
        else:
            continue

        # 2. Select Secondary Isms
        num_secondary = archetype["num_secondary"]
        for _ in range(num_secondary):
            secondary_ism = get_unique_ism(archetype["secondary_pool"], used_codes)
            if secondary_ism:
                used_codes.add(secondary_ism["code"])
                weight = round(random.uniform(0.4, 0.8), 2)
                weighted_isms.append({"ism": secondary_ism, "weight": weight})

        if not weighted_isms:
            continue

        # 3. Generate Fused NPC
        fused_npc = apply_rules_fusion(weighted_isms, rules)

        # 4. Assign a unique name and save
        npc_name = f"{archetype['naming_prefix']}_{i+1}"
        fused_npc["identity"]["npc_name"] = npc_name

        output_filename = f"{npc_name}.json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fused_npc, f, indent=2, ensure_ascii=False)

        generated_count += 1

    print(f"\nBatch generation of final composite NPCs complete.")
    print(f"Successfully generated {generated_count} NPC data files in '{OUTPUT_DIR}/'.")

if __name__ == '__main__':
    generate_final_npcs()