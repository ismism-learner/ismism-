import pandas as pd
import json
import sys
import re
from quantization_engine import QuantizationEngine

# Ensure stdout can handle UTF-8 for printing
sys.stdout.reconfigure(encoding='utf-8')

def parse_philosophy_chunk(base_val, mediator_val, counter_val):
    """
    Parses a chunk of 3 values corresponding to a philosophy pillar.
    """
    base = str(base_val).strip()
    mediator = str(mediator_val).strip()
    counter = str(counter_val).strip()

    # If mediator and counter are both empty, it's a simple value.
    if not mediator and not counter:
        return base

    # Otherwise, it's a complex structure.
    # Clean the mediator text by removing "调和者：" as requested.
    cleaned_relation = mediator.replace("调和者：", "").strip()

    return {
        "base": base,
        "relation": cleaned_relation,
        "counter": counter
    }

def clean_sheet_data(df, is_special_sheet=False):
    """
    Cleans the raw data from a single Excel sheet (as a DataFrame), structuring it based on positional columns.
    Handles the special '4-x-x-x' case if is_special_sheet is True.
    """
    cleaned_data = []
    NAME_COL = 0
    pillar_names = ['field_theory', 'ontology', 'epistemology', 'teleology']

    for index, row in df.iterrows():
        name_field = str(row.iloc[NAME_COL]).strip()
        if not name_field or ' ' not in name_field:
            continue

        try:
            ism_id, ism_name = name_field.split(' ', 1)
        except ValueError:
            continue

        philosophy = {}
        current_col = 1  # Start from the first philosophy column

        # The logic depends on whether this is the special sheet AND the ID starts with '4-'
        is_special_ism = is_special_sheet and ism_id.startswith('4-')

        # Define required columns for safety check
        required_cols = 14 if is_special_ism else 13

        if len(row) < required_cols:
            continue # Skip rows that don't have enough data

        if is_special_ism:
            # Field Theory has 4 components
            ft_base = str(row.iloc[current_col]).strip()
            ft_relation = str(row.iloc[current_col + 1]).strip().replace("调和者：", "")
            ft_counter = str(row.iloc[current_col + 2]).strip()
            ft_action_unit = str(row.iloc[current_col + 3]).strip()
            philosophy['field_theory'] = {
                "base": ft_base, "relation": ft_relation, "counter": ft_counter, "action_unit": ft_action_unit
            }
            current_col += 4
            # Process remaining 3 pillars
            for pillar_name in pillar_names[1:]:
                base_val, med_val, count_val = row.iloc[current_col], row.iloc[current_col + 1], row.iloc[current_col + 2]
                philosophy[pillar_name] = parse_philosophy_chunk(base_val, med_val, count_val)
                current_col += 3
        else:
            # All pillars have 3 components
            for pillar_name in pillar_names:
                base_val, med_val, count_val = row.iloc[current_col], row.iloc[current_col + 1], row.iloc[current_col + 2]
                philosophy[pillar_name] = parse_philosophy_chunk(base_val, med_val, count_val)
                current_col += 3

        representative = str(row.iloc[current_col]).strip() if len(row) > current_col else ''

        cleaned_data.append({
            'id': ism_id, 'name': ism_name, 'philosophy': philosophy, 'representative': representative
        })
    return cleaned_data


def main():
    """
    Reads all sheets from the Excel file, cleans data sheet by sheet according to its structure,
    quantizes it, and saves the final structured data to 'isms_final.json'.
    """
    excel_path = '主义主义/59号-哲学意识形态填空.xlsx'
    output_path = 'isms_final.json'

    try:
        all_sheets_dfs = pd.read_excel(excel_path, sheet_name=None, na_filter=False, dtype=str)

        all_isms_data = []
        sheet_names = list(all_sheets_dfs.keys())

        # Process first sheet (standard structure)
        if len(sheet_names) > 0:
            first_sheet_df = all_sheets_dfs[sheet_names[0]]
            all_isms_data.extend(clean_sheet_data(first_sheet_df, is_special_sheet=False))

        # Process second sheet (special structure for '4-x-x-x')
        if len(sheet_names) > 1:
            second_sheet_df = all_sheets_dfs[sheet_names[1]]
            all_isms_data.extend(clean_sheet_data(second_sheet_df, is_special_sheet=True))

        # Process any remaining sheets as standard
        if len(sheet_names) > 2:
            for sheet_name in sheet_names[2:]:
                other_sheet_df = all_sheets_dfs[sheet_name]
                all_isms_data.extend(clean_sheet_data(other_sheet_df, is_special_sheet=False))

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