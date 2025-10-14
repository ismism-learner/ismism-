# world_server/ecs/components/position.py
from dataclasses import dataclass
from ..component import Component

@dataclass
class PositionComponent(Component):
    x: float
    y: float