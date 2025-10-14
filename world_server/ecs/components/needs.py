# world_server/ecs/components/needs.py
from dataclasses import dataclass, field
from typing import Dict, Any, List
from ..component import Component

@dataclass
class NeedsComponent(Component):
    # Tier 1: Physiological Needs
    needs: Dict[str, Any] = field(default_factory=lambda: {
        'hunger': {
            'current': 0,
            'max': 100,
            'change_per_hour': 4,
            'priority_threshold': 50
        },
        'energy': {
            'current': 100,
            'max': 100,
            'change_per_hour': -5,
            'priority_threshold': 30
        },
        'stress': {
            'current': 0,
            'max': 100,
            'change_per_hour': 1,
            'priority_threshold': 50
        },
        'idealism': {
            'current': 50,
            'max': 100,
            'change_per_hour': -0.1,
            'priority_threshold': 40
            },
            'fulfillment': {
                'current': 0,
                'max': 100,
                'change_per_hour': 2,
                'priority_threshold': 60
        }
    })

    # Tier 2: Societal/Ideological Demands
    demands: List[str] = field(default_factory=list)

    # Tier 3: Lacanian Desire
    desire: Dict[str, Any] = field(default_factory=lambda: {
        'imaginary': {},
        'symbolic': {},
        'real': {
            'rupture': 0,
            'source_of_trauma': None
        }
    })

    # Bonuses from technology or other global effects
    alchemy_bonus: Dict[str, float] = field(default_factory=lambda: {
        'stress_resistance': 0.0 # e.g., 0.1 means 10% less stress gain
    })