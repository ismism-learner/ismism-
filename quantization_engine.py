import json

class QuantizationEngine:
    """
    Calculates the philosophical axes scores for a given ism ID based on a set of rules.
    """
    def __init__(self, rules_path='rules.json'):
        """
        Initializes the engine by loading the rules from the specified path.
        """
        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = json.load(f)
        self.axes = self.rules.get('axes', {})

    def _normalize(self, value, axis_values):
        """
        Normalizes a calculated score to be within the [-1.0, 1.0] range.
        The normalization is based on the theoretical min/max possible score for that axis.
        """
        min_val = sum(v for v in axis_values if v < 0) * 4
        max_val = sum(v for v in axis_values if v > 0) * 4

        if value == 0:
            return 0.0
        if value > 0:
            return round(value / max_val, 4) if max_val != 0 else 0.0
        else: # value < 0
            return round(value / abs(min_val), 4) if min_val != 0 else 0.0


    def calculate_scores(self, ism_id):
        """
        Calculates the scores for a given ism_id across all defined philosophical axes.

        Args:
            ism_id (str): The ID of the ism, e.g., "4-1-2-2".

        Returns:
            dict: A dictionary containing the calculated score for each axis.
        """
        scores = {}
        # Split the ID string "4-1-2-2" into a list of its numeric parts ['4', '1', '2', '2']
        parts = ism_id.split('-')

        for axis_name, axis_data in self.axes.items():
            axis_values = {k: v for k, v in axis_data['values'].items()}

            # Sum the contribution of each part of the ID
            total_score = sum(axis_values.get(part, 0) for part in parts)

            # Normalize the score to fit within the standard [-1.0, 1.0] range
            normalized_score = self._normalize(total_score, axis_values.values())
            scores[axis_name] = normalized_score

        return scores

    def calculate_dialectical_matrix(self, ism_id):
        """
        Generates a quantization matrix based on the dialectical logic progression.
        1: Pure Identity [1.0, 0.0, 0.0, 0.0]
        2: Difference & Contradiction [0.5, 0.5, 0.0, 0.0]
        3: Synthesis & Mediation [0.25, 0.25, 0.5, 0.0]
        4: Failure of Synthesis & Collapse [0.0, 0.0, 0.0, 1.0]

        Args:
            ism_id (str): The gene code of the ism, e.g., "3-2-4-1".

        Returns:
            dict: A dictionary containing the weight vectors for each philosophical pillar.
        """
        dialectical_map = {
            '1': [1.0, 0.0, 0.0, 0.0],  # Pure Identity
            '2': [0.5, 0.5, 0.0, 0.0],   # Difference & Contradiction
            '3': [0.25, 0.25, 0.5, 0.0],# Synthesis & Mediation
            '4': [0.0, 0.0, 0.0, 1.0]   # Failure of Synthesis
        }

        pillars = ["field_theory", "ontology", "epistemology", "teleology"]
        parts = ism_id.split('-')

        if len(parts) != 4:
            # For simpler isms (e.g. "1-2-3"), we can pad with a default value or handle as an error.
            # For now, let's assume valid 4-part codes.
            # You could also expand this to handle 1, 2, 3-part IDs if necessary.
            return None

        matrix = {}
        for i, pillar_name in enumerate(pillars):
            code = parts[i]
            matrix[pillar_name] = dialectical_map.get(code, [0.0, 0.0, 0.0, 0.0]) # Default to neutral if code is invalid

        return matrix

# --- Example Usage ---
if __name__ == '__main__':
    engine = QuantizationEngine()

    # --- Original Score Calculation Test ---
    print("--- LEGACY SCORE CALCULATION ---")
    test_isms_legacy = ["1-1-1-1", "4-1-2-2"]
    for ism in test_isms_legacy:
        calculated_scores = engine.calculate_scores(ism)
        print(f"--- Scores for Ism ID: {ism} ---")
        for axis, score in calculated_scores.items():
            print(f"  - {axis}: {score}")
        print("\\n")

    # --- New Dialectical Matrix Calculation Test ---
    print("--- NEW DIALECTICAL MATRIX CALCULATION ---")
    test_ism_dialectical = "3-2-4-1"
    matrix = engine.calculate_dialectical_matrix(test_ism_dialectical)
    print(f"--- Dialectical Matrix for Ism ID: {test_ism_dialectical} ---")
    if matrix:
        for pillar, weights in matrix.items():
            print(f"  - {pillar}: {weights}")
    print("\\n")