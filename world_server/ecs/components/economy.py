# world_server/ecs/components/economy.py
from dataclasses import dataclass
from ..component import Component

@dataclass
class EconomyComponent(Component):
    money: int = 0