# world_server/ecs/components/praxis_ledger_component.py
from dataclasses import dataclass, field
from typing import Dict, Any, List
from ..component import Component

@dataclass
class PraxisLedgerComponent(Component):
    """
    Represents the Subversion level of memory (X=4, Praxis).
    Models the world's underlying rules, power structures, and their weaknesses.
    """
    # A model of perceived power structures.
    # e.g., {'faction_merchants': {'power_source': 'money', 'weakness': 'supply_chain'}}
    power_structures: Dict[str, Dict[str, str]] = field(default_factory=dict)

    # A list of planned subversive activities or strategies.
    # e.g., [{'type': 'DISRUPT_ECONOMY', 'target': 'faction_merchants', 'method': 'corner_market_on_ore'}]
    subversive_plans: List[Dict[str, Any]] = field(default_factory=list)

    # Knowledge of specific system exploits or hidden mechanics.
    # e.g., "Spreading rumors at the tavern (loc_3) lowers target's social standing."
    known_exploits: List[str] = field(default_factory=list)

    def model_power_structure(self, structure_id: str, source: str, weakness: str):
        """Updates the NPC's model of a power structure."""
        self.power_structures[structure_id] = {
            'power_source': source,
            'weakness': weakness
        }