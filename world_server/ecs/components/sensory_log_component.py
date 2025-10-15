# world_server/ecs/components/sensory_log_component.py
from dataclasses import dataclass, field
from typing import List, Dict, Any
from ..component import Component

@dataclass
class SensoryLogComponent(Component):
    """
    Represents the Urge level of memory (X=1, Realism).
    A short-term log of raw sensory experiences, mapping events to valence.
    """
    # A list of simple dictionaries, e.g.,
    # [{'event': 'ATE_GOOD_FOOD', 'location': 'loc_1', 'valence': 0.8, 'timestamp': 1234}]
    # Valence is -1 (bad) to 1 (good).
    log: List[Dict[str, Any]] = field(default_factory=list)
    log_capacity: int = 20 # How many recent events to remember.

    def add_event(self, event: Dict[str, Any]):
        """Adds a new event to the log, maintaining capacity."""
        self.log.append(event)
        # Prune the log if it exceeds capacity
        if len(self.log) > self.log_capacity:
            self.log.pop(0)