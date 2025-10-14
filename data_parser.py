import csv
import os
import json
import sys
from quantization_engine import QuantizationEngine

# Ensure stdout can handle UTF-8 for printing
sys.stdout.reconfigure(encoding='utf-8')

def find_md_file(start_path, ism_id, ism_name):
    """
    Find the markdown file corresponding to an ism_id and ism_name.
    It handles the complexity of nested directories and filename variations.
    """
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.endswith('.md') and file.startswith(f"{ism_id} "):
                return os.path.join(root, file)
    return None

def main():
    """
    Main function to parse, quantize, and save all ism data.
    """
    # Use the original directory name
    csv_path = '主义主义/isms_data.csv'
    md_path = '主义主义'
    output_path = 'isms_final.json'

    all_isms_data = []
    engine = QuantizationEngine()

    print("--- Starting Parsing and Quantization Process ---")

    # Step 1: Parse the base data from the CSV
    try:
        with open(csv_path, mode='r', encoding='GB18030', errors='ignore') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            print(f"Successfully opened {csv_path}")

            for row in reader:
                if not row: continue
                try:
                    ism_id = row[0]
                    ism_name = row[1]

                    ism_data = {
                        'id': ism_id,
                        'name': ism_name,
                        'philosophy': {
                            'field_theory': row[2],
                            'ontology': row[3],
                            'epistemology': row[4],
                            'teleology': row[5]
                        },
                        'source_text': '',
                        'quantification': {} # Placeholder for quantization results
                    }

                    # Step 2: Find and read the corresponding markdown file
                    md_file_path = find_md_file(md_path, ism_id, ism_name)
                    if md_file_path:
                        with open(md_file_path, 'r', encoding='utf-8', errors='ignore') as md_file:
                            ism_data['source_text'] = md_file.read()

                    # Step 3: Use the Quantization Engine to calculate scores
                    scores = engine.calculate_scores(ism_id)
                    ism_data['quantification']['axes'] = scores
                    # Placeholder for future keyword extraction logic
                    ism_data['quantification']['keywords'] = []

                    all_isms_data.append(ism_data)
                except IndexError:
                    print(f"Warning: Skipping malformed row: {row}")
                    continue
    except FileNotFoundError:
        print(f"FATAL ERROR: Could not find the main data file at {csv_path}. Please ensure the '主义主义' directory was renamed to 'isms_data_dir'.")
        return

    # Step 4: Write the final, consolidated data to a JSON file
    with open(output_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(all_isms_data, jsonfile, ensure_ascii=False, indent=2)

    print(f"\n--- Process Complete ---")
    print(f"Processed and quantized {len(all_isms_data)} isms.")
    print(f"Final structured data saved to {output_path}")

if __name__ == '__main__':
    main()