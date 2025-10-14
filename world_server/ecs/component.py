# world_server/ecs/component.py
"""
Defines the base class for all Components.
"""
from dataclasses import dataclass

# Using dataclass as a base for components to reduce boilerplate.
# This is a marker class. All components will inherit from this.
@dataclass
class Component:
    pass