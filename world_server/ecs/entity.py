# world_server/ecs/entity.py
"""
Defines the Entity, which is just a unique identifier.
"""
import uuid

# An Entity is simply a unique ID. We use an alias for clarity.
Entity = uuid.UUID

def create_entity() -> Entity:
    """Creates a new, unique entity."""
    return uuid.uuid4()