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

# --- Example Usage ---
if __name__ == '__main__':
    engine = QuantizationEngine()

    # --- Test Cases ---
    test_isms = ["1-1-1-1", "2-2-2-2", "3-3-3-3", "4-4-4-4", "4-1-2-2"]

    for ism in test_isms:
        calculated_scores = engine.calculate_scores(ism)
        print(f"--- Scores for Ism ID: {ism} ---")
        for axis, score in calculated_scores.items():
            print(f"  - {axis}: {score}")
        print("\\n")