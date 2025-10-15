# world_server/ecs/components/identity.py
from dataclasses import dataclass, field
from ..component import Component

from typing import Optional, Dict, Any

@dataclass
class IdentityComponent(Component):
    name: str
    description: str
    birthplace: Optional[str] = None

    # Biography
    social_class: str = "proletariat"
    education_level: str = "basic"
    age_bracket: str = "middle-aged"
    defining_event: Optional[str] = None