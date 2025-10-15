# world_server/ecs/components/ism.py
from dataclasses import dataclass, field
from typing import Dict, Any
from ..component import Component

@dataclass
class IsmComponent(Component):
    data: Dict[str, Any] = field(default_factory=dict)
    gene_code: str = "1-1-1-1"
    # Ideological Experience Points (IXP)
    # Rows: 0:Field, 1:Ontology, 2:Epistemology, 3:Teleology
    # Cols: 0:Identity, 1:Contradiction, 2:Synthesis, 3:Collapse
    ixp: list[list[float]] = field(default_factory=lambda: [[0.0] * 4 for _ in range(4)])

    @property
    def quantification(self) -> Dict[str, Any]:
        """
        Calculates the weight matrix from the IXP on the fly for backward compatibility.
        The final output is a dictionary containing the matrix, matching the old structure.
        """
        matrix = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            row_sum = sum(self.ixp[i])
            if row_sum > 0:
                matrix[i] = [val / row_sum for val in self.ixp[i]]
            else:
                # Avoid division by zero. If a row is all zeros, maybe default to identity?
                # For now, just keep it as zeros.
                matrix[i] = [0.0, 0.0, 0.0, 0.0]

        # The old quantification was a dict {'matrix': [...]}, so we match that
        return {"matrix": matrix}