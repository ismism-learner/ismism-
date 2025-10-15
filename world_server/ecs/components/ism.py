# world_server/ecs/components/ism.py
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any
from ..component import Component

# Helper function to create a default ideology entry
def create_default_ideology():
    return {
        "code": "1-1-1-1",
        "intensity": 1.0,
        "ixp": [[100.0, 0, 0, 0]] + [[0.0] * 4 for _ in range(3)], # Start with some base IXP
        "data": {}
    }

@dataclass
class IsmComponent(Component):
    """
    Represents the ideological makeup of an entity, which can be a composite
    of several competing ideologies.
    """
    active_ideologies: List[Dict[str, Any]] = field(default_factory=lambda: [create_default_ideology()])

    @property
    def dominant_ideology(self) -> Dict[str, Any]:
        """Returns the ideology with the highest intensity."""
        if not self.active_ideologies:
            return create_default_ideology() # Should not happen, but as a fallback
        return max(self.active_ideologies, key=lambda x: x['intensity'])

    @property
    def quantification(self) -> Dict[str, Any]:
        """
        Calculates a final, weighted-average decision matrix based on the intensity
        of all active ideologies.
        """
        final_matrix = np.zeros((4, 4))
        total_intensity = sum(ideology['intensity'] for ideology in self.active_ideologies)

        if total_intensity == 0:
            # Fallback to a default "Identity" matrix if total intensity is zero
            final_matrix = np.diag([1.0, 1.0, 1.0, 1.0])
            return {"matrix": final_matrix.tolist()}

        for ideology in self.active_ideologies:
            ideology_matrix = np.zeros((4, 4))
            for i in range(4):
                row_sum = sum(ideology['ixp'][i])
                if row_sum > 0:
                    ideology_matrix[i] = [val / row_sum for val in ideology['ixp'][i]]
                # If row_sum is 0, it remains a row of zeros

            # Weight this ideology's matrix by its intensity
            weight = ideology['intensity'] / total_intensity
            final_matrix += np.array(ideology_matrix) * weight

        return {"matrix": final_matrix.tolist()}