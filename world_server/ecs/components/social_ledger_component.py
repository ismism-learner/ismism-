# world_server/ecs/components/social_ledger_component.py
from dataclasses import dataclass, field
from typing import Dict, Any, List
from ..component import Component

@dataclass
class SocialLedgerComponent(Component):
    """
    Represents the Demand level of memory (X=2, Metaphysics).
    A graph-like structure tracking social victories, defeats, and obligations.
    """
    # Key is the other entity's ID.
    # Value is a dictionary of social interactions.
    # e.g., {'npc_2': {'wins': 2, 'losses': 1, 'favors_owed': 1, 'favors_granted': 0}}
    ledger: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def record_interaction(self, other_entity_id: str, outcome: str):
        """
        Records the outcome of a social interaction, e.g., 'win', 'loss', 'grant_favor'.
        """
        if other_entity_id not in self.ledger:
            self.ledger[other_entity_id] = {'wins': 0, 'losses': 0, 'favors_owed': 0, 'favors_granted': 0}

        if outcome == 'win':
            self.ledger[other_entity_id]['wins'] += 1
        elif outcome == 'loss':
            self.ledger[other_entity_id]['losses'] += 1
        elif outcome == 'grant_favor': # You granted them a favor, they owe you.
            self.ledger[other_entity_id]['favors_owed'] += 1
        elif outcome == 'receive_favor': # You received a favor, you owe them.
            self.ledger[other_entity_id]['favors_granted'] += 1