# world_server/ecs/components/hobby_component.py
from dataclasses import dataclass, field
from typing import Dict, List, Any
from ..component import Component

@dataclass
class HobbyComponent(Component):
    """
    Stores data related to an NPC's hobbies, skills, and produced goods.
    """
    # Maps hobby_id to an interest score (e.g., 0-100)
    interests: Dict[str, float] = field(default_factory=dict)

    # Maps hobby_id to a skill level (e.g., 1-10)
    skills: Dict[str, int] = field(default_factory=dict)

    # A list of consumer goods the NPC owns
    inventory: List[Dict[str, Any]] = field(default_factory=list)