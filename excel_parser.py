import pandas as pd
import json
import sys
import re
from quantization_engine import QuantizationEngine

# Ensure stdout can handle UTF-8 for printing
sys.stdout.reconfigure(encoding='utf-8')

def parse_philosophy_field(entry, field_name):
    """
    Intelligently parses a philosophy field, handling simple strings,
    'vs' structures, and complex mediator structures.
    """
    base_value = str(entry.get(field_name, "")).strip()
    relation = str(entry.get(f"{field_name}.1", "")).strip()
    counter = str(entry.get(f"{field_name}.2", "")).strip()

    # If there's no relation or counter, it's a simple field.
    if not relation and not counter:
        return base_value

    # Handle "A vs B" structure (e.g., '对立于')
    if relation.lower() in ['vs', '对立于']:
        return {
            "base": base_value,
            "relation": "vs",
            "counter": counter
        }

    # Handle "A [mediator] B" structure
    else:
        return {
            "base": base_value,
            "relation": relation, # The relation itself is the mediator text
            "counter": counter
        }

def clean_ism_data(raw_data):
    """
    Cleans the raw data from the Excel file and structures it based on the new, complex rules.
    """
    cleaned_data = []
    for entry in raw_data:
        name_field = str(entry.get('主义名称', '')).strip()
        if not name_field or ' ' not in name_field:
            continue

        parts = name_field.split(' ', 1)
        ism_id = parts[0]
        ism_name = parts[1]

        philosophy = {
            'field_theory': parse_philosophy_field(entry, '场域论'),
            'ontology': parse_philosophy_field(entry, '本体论'),
            'epistemology': parse_philosophy_field(entry, '认识论'),
            'teleology': parse_philosophy_field(entry, '目的论')
        }

        cleaned_data.append({
            'id': ism_id,
            'name': ism_name,
            'philosophy': philosophy,
            'representative': str(entry.get('代表人物', ''))
        })
    return cleaned_data

def main():
    """
    Reads all sheets from the new Excel file, cleans the data according to complex rules,
    quantizes it, and saves the final structured data to 'isms_final.json'.
    """
    excel_path = '主义主义/59号-哲学意识形态填空.xlsx' # Reverting to the available file
    output_path = 'isms_final.json'

    try:
        all_sheets = pd.read_excel(excel_path, sheet_name=None, na_filter=False, dtype=str)
        df = pd.concat(all_sheets.values(), ignore_index=True)
        raw_data = df.to_dict(orient="records")

        all_isms_data = clean_ism_data(raw_data)

        engine = QuantizationEngine()

        print("Quantizing ism data...")
        for ism_data in all_isms_data:
            ism_id = ism_data['id']
            # Only quantize for full 4-digit IDs as per logic
            if len(ism_id.split('-')) == 4:
                scores = engine.calculate_scores(ism_id)
                ism_data['quantification'] = {'axes': scores}

        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(all_isms_data, jsonfile, ensure_ascii=False, indent=2)

        print(f"\nProcess complete.")
        print(f"Processed and quantized {len(all_isms_data)} total entries.")
        print(f"Final structured data saved to {output_path}")

    except FileNotFoundError:
        print(f'{{"error": "File not found at {excel_path}. Please ensure it is in the root directory."}}')
    except Exception as e:
        print(f'{{"error": "An unexpected error occurred: {e}"}}')

if __name__ == '__main__':
    main()