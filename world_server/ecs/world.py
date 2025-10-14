# world_server/ecs/world.py
"""
The core of the ECS framework. Manages entities, components, and systems.
"""
from typing import Type, TypeVar, Dict, List, Optional
from .entity import Entity, create_entity
from .component import Component
from .system import System

C = TypeVar('C', bound=Component)

class World:
    def __init__(self):
        self.entities: Dict[Entity, Dict[Type[Component], Component]] = {}
        self.systems: List[System] = []

        # --- World State ---
        self.time: int = 0
        self.ticks_per_hour: int = 60 # e.g., 60 ticks represent one in-game hour

    def create_entity(self) -> Entity:
        """Creates a new entity and returns its ID."""
        entity_id = create_entity()
        self.entities[entity_id] = {}
        return entity_id

    def add_component(self, entity_id: Entity, component_instance: C) -> None:
        """Adds a component instance to an entity."""
        component_type = type(component_instance)
        self.entities[entity_id][component_type] = component_instance

    def get_component(self, entity_id: Entity, component_type: Type[C]) -> Optional[C]:
        """Retrieves a component instance for an entity."""
        return self.entities.get(entity_id, {}).get(component_type)

    def has_component(self, entity_id: Entity, component_type: Type[C]) -> bool:
        """Checks if an entity has a specific component."""
        return component_type in self.entities.get(entity_id, {})

    def get_entities_with_components(self, *component_types: Type[C]) -> List[Entity]:
        """Returns a list of all entities that have all the specified component types."""
        if not component_types:
            return []

        return [
            entity_id for entity_id, components in self.entities.items()
            if all(ctype in components for ctype in component_types)
        ]

    def add_system(self, system_instance: System) -> None:
        """Adds a system to the world."""
        system_instance.world = self
        self.systems.append(system_instance)

    def process(self, *args, **kwargs) -> None:
        """
        Calls the process method for all registered systems in the order they were added.
        Passes any additional arguments to each system.
        """
        for system in self.systems:
            system.process(*args, **kwargs)