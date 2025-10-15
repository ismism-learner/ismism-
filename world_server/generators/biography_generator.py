import random

def generate_biography(region_id, region_data):
    """
    Generates a basic biography for an NPC based on their home region.
    """
    biography = {
        "social_class": "commoner",
        "education": "none",
        "defining_event": None
    }

    # Region-specific biography logic
    if region_id == "theocratic_capital":
        biography["social_class"] = random.choice(["proletariat", "clergyman", "guard"])
        biography["education"] = "basic_religious" if biography["social_class"] != "proletariat" else "none"
        if biography["social_class"] == "guard":
            if random.random() < 0.3:
                biography["defining_event"] = "witnessed_corruption"

    elif region_id == "chaotic_port":
        biography["social_class"] = random.choice(["merchant", "sailor", "thief"])
        biography["education"] = "street_smarts"
        if random.random() < 0.2:
            biography["defining_event"] = "survived_a_shipwreck"

    elif region_id == "ivory_tower":
        biography["social_class"] = random.choice(["scholar", "student", "artisan"])
        biography["education"] = "higher_education"
        if random.random() < 0.15:
            biography["defining_event"] = "made_a_discovery"

    return biography