import unittest
import numpy as np
from world_server.ecs.components.ism import IsmComponent

class TestIsmComponent(unittest.TestCase):

    def test_initialization(self):
        """Test that the component initializes correctly with a default ideology."""
        ism_comp = IsmComponent()
        self.assertEqual(len(ism_comp.active_ideologies), 1)
        self.assertAlmostEqual(ism_comp.active_ideologies[0]['intensity'], 1.0)

        # Default IXP for a '1-1-1-1' is Identity, so the matrix should be an identity matrix
        expected_matrix = np.identity(4).tolist()
        self.assertEqual(ism_comp.final_decision_matrix, expected_matrix)

    def test_add_second_ideology_and_recalculate_matrix(self):
        """Test that the final_decision_matrix is correctly recalculated."""
        ism_comp = IsmComponent()

        # The first ideology is a pure 'Identity' (1-1-1-1), which normalizes to an identity matrix.
        # Let's give it an intensity of 0.75.
        # The default ixp is already an identity matrix, so we just set the intensity.
        ism_comp.active_ideologies[0]['intensity'] = 0.75

        # The second ideology will be a pure 'Contradiction' (2-2-2-2).
        # Its IXP matrix should represent contradiction in every pillar.
        new_ideology = {
            "code": "2-2-2-2",
            "intensity": 0.25,
            # This IXP structure normalizes to a matrix with 0.5 in the first two columns for each row.
            "ixp": [[1.0, 1.0, 0.0, 0.0], [1.0, 1.0, 0.0, 0.0], [1.0, 1.0, 0.0, 0.0], [1.0, 1.0, 0.0, 0.0]],
            "data": {}
        }

        # Use the setter to trigger recalculation
        current_ideologies = ism_comp.active_ideologies
        ism_comp.active_ideologies = current_ideologies + [new_ideology]

        # --- Verification ---
        self.assertEqual(len(ism_comp.active_ideologies), 2)
        # Intensities should be normalized
        self.assertAlmostEqual(ism_comp.active_ideologies[0]['intensity'], 0.75)
        self.assertAlmostEqual(ism_comp.active_ideologies[1]['intensity'], 0.25)

        # The final matrix should be a weighted average
        # Ideology 1 matrix (Identity)
        matrix1 = np.identity(4)
        # Ideology 2 matrix (Contradiction)
        matrix2 = np.zeros((4,4))
        matrix2[:, 0] = 0.5
        matrix2[:, 1] = 0.5

        expected_final_matrix = (matrix1 * 0.75) + (matrix2 * 0.25)

        # Compare the results
        final_matrix_np = np.array(ism_comp.final_decision_matrix)
        np.testing.assert_allclose(final_matrix_np, expected_final_matrix, rtol=1e-5)

if __name__ == '__main__':
    unittest.main()