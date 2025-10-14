# world_server/ecs/components/identity.py
from dataclasses import dataclass
from ..component import Component

@dataclass
class IdentityComponent(Component):
    name: str
    description: str