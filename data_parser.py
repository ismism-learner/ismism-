import csv
import re
import os

def parse_toc(filepath):
    """
    Parses the table of contents (目录.md) to build a map
    from an ism's name to its code.
    e.g., {"阿派朗（无界限）主义": "2-1-1-1"}
    """
    name_to_code = {}
    # Regex to capture code (e.g., 2-1-1-1) and name
    # It handles various formats and potential whitespaces
    pattern = re.compile(r"([\d\-\.]*)\s+([^—\d\s]+.*)")

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                code = match.group(1).strip()
                name = match.group(2).strip()

                # Further clean up the name to remove page numbers etc.
                name = re.sub(r'\s+\d+$', '', name).strip()

                # Handle cases where the name might be split from the code
                if name and code:
                    # A simple heuristic to link multi-line names to their code
                    if not code and last_code:
                        code = last_code

                    name_to_code[name] = code
                    last_code = code
                elif name:
                    last_code = None


    # Manual corrections for known complex cases from the file
    name_to_code["拜物教"] = "1-2-2-3"
    name_to_code["时间崇拜"] = "1-2-2-4"
    name_to_code["魔法师主义"] = "1-2-3-3"
    name_to_code["厌女症-虚无主义"] = "1-3-3-4"


    return name_to_code

def parse_isms_data_csv(filepath, name_to_code_map):
    """
    Parses the main ism data from the provided CSV file.
    It uses the name_to_code_map to associate the data with the correct code.
    """
    all_isms = []

    if not os.path.exists(filepath):
        print(f"Warning: Data file not found at {filepath}. Please create it.")
        print("The system will run with no data.")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            # Skip header or empty rows
            if not row or not row[0]:
                continue

            ism_name = row[0].strip()

            # --- New, more robust matching logic ---
            # 1. Clean the name from the CSV (e.g., "1-1-1-1 科学独断论" -> "科学独断论")
            cleaned_ism_name = re.sub(r'^[\d\.\-]+\s*', '', ism_name).strip()

            # 2. Find the corresponding code from the map
            matched_code = name_to_code_map.get(cleaned_ism_name)

            # 3. Handle special cases where names might differ slightly (e.g., with/without quotes)
            if not matched_code:
                 for map_name, map_code in name_to_code_map.items():
                     # A 'fuzzy' match: check if one name is a substring of the other
                     if cleaned_ism_name in map_name or map_name in cleaned_ism_name:
                         matched_code = map_code
                         break

            if not matched_code:
                print(f"Warning: Could not find code for ism: '{ism_name}'. Skipping.")
                continue

            # Structure the data according to our model
            # Each "论" has 3 keywords.
            ism_obj = {
                "code": matched_code,
                "name": ism_name,
                "field_theory": [k.strip() for k in row[1:4] if k.strip()],
                "ontology":     [k.strip() for k in row[4:7] if k.strip()],
                "epistemology": [k.strip() for k in row[7:10] if k.strip()],
                "teleology":    [k.strip() for k in row[10:13] if k.strip()],
            }
            all_isms.append(ism_obj)

    return all_isms

def load_all_data(toc_path, csv_path):
    """
    Orchestrates the loading of all philosophical data.
    """
    print(f"Parsing Table of Contents from: {toc_path}")
    name_map = parse_toc(toc_path)
    print(f"Found {len(name_map)} name-to-code mappings.")

    print(f"Parsing Ism data from: {csv_path}")
    isms_data = parse_isms_data_csv(csv_path, name_map)
    print(f"Successfully parsed {len(isms_data)} isms from CSV.")

    return isms_data

if __name__ == '__main__':
    # ================== Example Usage ==================
    # This demonstrates how the parser will be used by the main script.

    TOC_FILE = 'ismism-/主义主义/目录.md'
    CSV_DATA_FILE = 'ismism-/主义主义/isms_data.csv'

    all_philosophy_data = load_all_data(TOC_FILE, CSV_DATA_FILE)

    if all_philosophy_data:
        print("\n--- Sample of Parsed Data ---")
        # Print the first 2 parsed isms as a sample
        import json
        print(json.dumps(all_philosophy_data[:2], indent=2, ensure_ascii=False))
    else:
        print("\nNo data was loaded. Please ensure 'isms_data.csv' exists.")