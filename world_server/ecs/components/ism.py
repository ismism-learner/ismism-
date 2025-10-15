# world_server/ecs/components/ism.py
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any
from ..component import Component

# Helper function to create a default ideology entry
def create_default_ideology():
    """Creates a default 'pure identity' ideology where the IXP matrix normalizes to an identity matrix."""
    return {
        "code": "1-1-1-1",
        "intensity": 1.0,
        # This IXP structure ensures a normalized identity matrix, representing pure Identity.
        "ixp": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
        "data": {}
    }

# Helper function to create a default 4x4 Identity matrix
def create_default_matrix():
    return np.identity(4).tolist()

@dataclass
class IsmComponent(Component):
    """
    Represents the ideological makeup of an entity (the NPC_Mind object). It holds
    all active ideologies and the resulting final decision matrix.
    """
    # Private backing field for active_ideologies
    _active_ideologies: List[Dict[str, Any]] = field(default_factory=list, init=False)

    # The final, dynamically calculated decision matrix for behavior.
    final_decision_matrix: List[List[float]] = field(default_factory=create_default_matrix)

    def __post_init__(self):
        """Initialize with a default ideology and calculate the matrix."""
        # This check prevents re-initialization on load
        if not self._active_ideologies:
            self._active_ideologies = [create_default_ideology()]
        self._update_final_decision_matrix()

    @property
    def active_ideologies(self) -> List[Dict[str, Any]]:
        """Getter for the list of active ideologies."""
        return self._active_ideologies

    @active_ideologies.setter
    def active_ideologies(self, value: List[Dict[str, Any]]):
        """
        Setter for active ideologies. Triggers a recalculation of the
        final decision matrix whenever the list is modified.
        """
        self._active_ideologies = value
        self._update_final_decision_matrix()

    def _update_final_decision_matrix(self):
        """
        Calculates the final_decision_matrix as a weighted average of all active
        ideologies' matrices, weighted by their intensity. This is the core of
        the NPC_Mind's decision-making basis.
        """
        final_matrix = np.zeros((4, 4))
        # Ensure that intensities sum to 1.0 for correct weighting.
        self._normalize_intensities()
        total_intensity = sum(ideology['intensity'] for ideology in self._active_ideologies)

        if not self._active_ideologies or total_intensity == 0:
            self.final_decision_matrix = create_default_matrix()
            return

        for ideology in self._active_ideologies:
            # The 'quantification' or 'gene_matrix' should be pre-calculated and stored.
            # Here, we derive it from the IXP matrix for dynamic evolution.
            ideology_matrix = np.zeros((4, 4))
            # The 'ixp' field in the ideology object acts as the basis for its matrix
            ixp_matrix = ideology.get('ixp', [[0]*4]*4)

            for i in range(4):
                row_sum = sum(ixp_matrix[i])
                if row_sum > 0:
                    ideology_matrix[i] = [val / row_sum for val in ixp_matrix[i]]
                # If a pillar has no IXP, it contributes nothing to the final matrix for that ideology

            # Weight this ideology's matrix by its normalized intensity
            weight = ideology['intensity']
            final_matrix += np.array(ideology_matrix) * weight

        self.final_decision_matrix = final_matrix.tolist()
        # print(f"DEBUG: Updated final_decision_matrix: {self.final_decision_matrix}") # For verification

    def _normalize_intensities(self):
        """
        Ensures that the sum of all intensities in active_ideologies is 1.0.
        This is crucial for accurate weighted averaging.
        """
        total_intensity = sum(ideo.get('intensity', 0) for ideo in self._active_ideologies)
        if total_intensity > 0:
            for ideology in self._active_ideologies:
                ideology['intensity'] /= total_intensity
        elif self._active_ideologies:
            # If total is 0 but list is not empty, distribute equally
            for ideology in self._active_ideologies:
                ideology['intensity'] = 1.0 / len(self._active_ideologies)


    @property
    def dominant_ideology(self) -> Dict[str, Any]:
        """Returns the ideology with the highest intensity."""
        if not self._active_ideologies:
            return create_default_ideology()
        return max(self._active_ideologies, key=lambda x: x.get('intensity', 0))

    def trigger_matrix_update(self):
        """
        Public method to manually trigger a recalculation of the final decision matrix.
        This is useful after direct manipulation of an ideology's IXP matrix.
        """
        self._update_final_decision_matrix()