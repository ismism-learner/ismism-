# world_server/ecs/components/ism.py
from dataclasses import dataclass, field
from typing import Dict, Any
from ..component import Component

@dataclass
class IsmComponent(Component):
    data: Dict[str, Any] = field(default_factory=dict)