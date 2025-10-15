# world_server/ecs/components/identity.py
from dataclasses import dataclass
from ..component import Component

from typing import Optional

from typing import Dict, Any

@dataclass
class IdentityComponent(Component):
    name: str
    description: str
    birthplace: Optional[str] = None
    biography: Optional[Dict[str, Any]] = None