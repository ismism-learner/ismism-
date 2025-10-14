# world_server/ecs/components/relationship.py
from dataclasses import dataclass, field
from typing import Dict
from ..entity import Entity

@dataclass
class RelationshipComponent:
    relations: Dict[Entity, Dict] = field(default_factory=dict) # Key: other_entity_id, Value: {"affinity": 0}