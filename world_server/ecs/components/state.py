# world_server/ecs/components/state.py
from dataclasses import dataclass, field
from typing import Any, Optional
from ..component import Component

@dataclass
class StateComponent(Component):
    action: str = "Idle"
    goal: Any = "Wander"
    target_entity_id: Optional[Any] = None # For interactions or targeted actions
    target_location_id: Optional[str] = None # For movement to a specific location