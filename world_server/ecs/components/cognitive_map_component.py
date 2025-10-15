# world_server/ecs/components/cognitive_map_component.py
from dataclasses import dataclass, field
from typing import Dict, Any, List, Set
from ..component import Component

@dataclass
class CognitiveMapComponent(Component):
    """
    Represents the Desire for Knowledge level of memory (X=3, Idealism).
    Stores abstract concepts, unsolved mysteries, and research plans.
    """
    # A set of concepts the NPC is aware of.
    known_concepts: Set[str] = field(default_factory=set)

    # A list of questions or mysteries the NPC is currently pondering.
    # e.g., [{'topic': 'AUTOMATA_SOULS', 'status': 'investigating', 'plan': ['talk_to_alchemist', 'read_ancient_book']}]
    unsolved_mysteries: List[Dict[str, Any]] = field(default_factory=list)

    # Hypotheses the NPC has formed.
    # e.g., {'hypothesis': 'Automata are powered by captured spirits.', 'confidence': 0.3}
    hypotheses: List[Dict[str, Any]] = field(default_factory=list)

    def add_mystery(self, topic: str, initial_plan: List[str]):
        """Adds a new mystery to the cognitive map if not already present."""
        if not any(m['topic'] == topic for m in self.unsolved_mysteries):
            self.unsolved_mysteries.append({
                'topic': topic,
                'status': 'pending',
                'plan': initial_plan
            })