import random
from typing import Dict, Any, Optional

SOCIAL_CLASSES = {
    "proletariat": 0.6,
    "petite_bourgeoisie": 0.25,
    "bourgeoisie": 0.1,
    "lumpenproletariat": 0.05,
}

EDUCATION_LEVELS = {
    "illiterate": 0.4,
    "basic": 0.4,
    "higher": 0.2,
}

AGE_BRACKETS = {
    "youth": 0.4,
    "middle-aged": 0.4,
    "elderly": 0.2,
}

DEFINING_EVENTS = {
    "war_veteran": 0.1,
    "family_bankruptcy": 0.1,
    "witnessed_miracle": 0.05,
    "betrayed_by_loved_one": 0.1,
    "none": 0.65
}

def generate_biography() -> Dict[str, Any]:
    """
    Generates a set of biographical tags for an NPC.
    """

    social_class = random.choices(list(SOCIAL_CLASSES.keys()), list(SOCIAL_CLASSES.values()), k=1)[0]
    education_level = random.choices(list(EDUCATION_LEVELS.keys()), list(EDUCATION_LEVELS.values()), k=1)[0]
    age_bracket = random.choices(list(AGE_BRACKETS.keys()), list(AGE_BRACKETS.values()), k=1)[0]
    defining_event_choice = random.choices(list(DEFINING_EVENTS.keys()), list(DEFINING_EVENTS.values()), k=1)[0]

    defining_event: Optional[str] = defining_event_choice if defining_event_choice != "none" else None

    return {
        "social_class": social_class,
        "education_level": education_level,
        "age_bracket": age_bracket,
        "defining_event": defining_event,
    }