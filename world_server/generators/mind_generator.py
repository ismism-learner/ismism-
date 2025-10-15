import random

def generate_npc_mind(region_data, biography, all_isms_by_id):
    """
    Generates an NPC's mind, creating a primary and secondary ideology
    based on their environment and life experiences.
    """
    meme_pool = region_data.get("meme_pool", [])
    if not meme_pool:
        return []

    # 1. Filtering (Simple placeholder logic)
    # Filter out "complex" ideologies for NPCs with no education
    filtered_pool = list(meme_pool) # Make a copy
    if biography.get("education") == "none":
        filtered_pool = [ism_id for ism_id in filtered_pool if not ism_id.startswith('3-')]

    if not filtered_pool: # Fallback to original pool if filtering removes everything
        filtered_pool = list(meme_pool)

    # 2. Primary Ideology Generation
    primary_ism_id = random.choice(filtered_pool)
    primary_ism_data = all_isms_by_id.get(primary_ism_id, {})

    active_ideologies = [{
        "code": primary_ism_id,
        "intensity": round(random.uniform(0.7, 1.0), 2),
        "ixp": _generate_initial_ixp(primary_ism_id),
        "data": primary_ism_data.get('philosophy', {})
    }]

    # 3. Secondary Ideology / Internal Conflict Generation
    secondary_ism_id = None
    defining_event = biography.get("defining_event")

    # Use defining event to force a specific secondary ideology
    if defining_event == "witnessed_corruption":
        # This event strongly suggests a cynical or conflict-oriented worldview.
        # As per the example, we'll implant "Modern Cynicism" (1-3-2-2)
        secondary_ism_id = "1-3-2-2"
    elif defining_event == "survived_a_shipwreck":
        # This could lead to a focus on chance, chaos, or struggle.
        # We'll pick a '2-' (conflict) or '4-' (collapse) ism if available.
        conflict_isms = [ism for ism in all_isms_by_id if ism.startswith('2-') or ism.startswith('4-')]
        if conflict_isms:
            secondary_ism_id = random.choice(conflict_isms)

    # If no defining event, pick another compatible ism from the pool
    else:
        compatible_pool = [ism_id for ism_id in filtered_pool if ism_id != primary_ism_id]
        if compatible_pool:
            secondary_ism_id = random.choice(compatible_pool)

    # Add the secondary ideology if one was chosen
    if secondary_ism_id and secondary_ism_id in all_isms_by_id:
        secondary_ism_data = all_isms_by_id.get(secondary_ism_id, {})
        active_ideologies.append({
            "code": secondary_ism_id,
            "intensity": 0.3,
            "ixp": _generate_initial_ixp(secondary_ism_id),
            "data": secondary_ism_data.get('philosophy', {})
        })

    return active_ideologies

def _generate_initial_ixp(gene_code):
    """Generates a baseline IXP matrix for a given ideology code."""
    initial_ixp = [[0.0] * 4 for _ in range(4)]
    try:
        gene_parts = [int(g) for g in gene_code.split('-')]
        for i_part, stage in enumerate(gene_parts):
            if 1 <= stage <= 4:
                initial_ixp[i_part][stage - 1] = 100.0  # Baseline value
    except (ValueError, IndexError):
        # Fallback for invalid codes
        for i in range(4):
            initial_ixp[i][0] = 100.0
    return initial_ixp