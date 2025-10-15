# world_server/ecs/systems/motivation_system.py
import random
from ..system import System
from ..components.ism import IsmComponent
from ..components.needs import NeedsComponent

class MotivationSystem(System):
    """
    The core of the Worldview-Driven Motivation and Memory Engine (WD-MME).
    This system reads an NPC's dominant ideology to determine their fundamental
    level of motivation and generates high-level goals (Demands) accordingly.
    """

    def process(self, *args, **kwargs):
        """
        Processes all entities with Ism and Needs components to generate
        ideology-driven demands.
        """
        # Process entities on a staggered schedule to improve performance
        if self.world.time % 10 != 0: # Process roughly once per day
            return

        entities_to_process = self.world.get_entities_with_components(IsmComponent, NeedsComponent)

        for entity_id in entities_to_process:
            ism_comp = self.world.get_component(entity_id, IsmComponent)
            needs_comp = self.world.get_component(entity_id, NeedsComponent)

            dominant_ideology = ism_comp.dominant_ideology
            if not dominant_ideology:
                continue

            try:
                # The Field Theory code is the first digit of the 'code' string
                field_theory_code = int(dominant_ideology.get('code', '1-1-1-1').split('-')[0])
            except (ValueError, IndexError):
                field_theory_code = 1 # Default to Realism

            # Check if a high-level demand from this system already exists
            if any(d.get('source') == 'MotivationSystem' for d in needs_comp.demands):
                continue

            # Generate a new high-level demand based on the motivation level
            new_demand = None
            if field_theory_code == 1: # Urge (Realism)
                # Goal: Satisfy immediate needs. This is the baseline, handled by NeedsSystem.
                # No special demand needed; the absence of higher-order goals IS the goal.
                pass
            elif field_theory_code == 2: # Demand (Metaphysics)
                # Goal: Seek social victory and recognition.
                new_demand = {'type': 'PURSUE_SOCIAL_STANDING', 'source': 'MotivationSystem'}
            elif field_theory_code == 3: # Desire for Knowledge (Idealism)
                # Goal: Solve a mystery or explore a concept.
                new_demand = {'type': 'PURSUE_KNOWLEDGE', 'source': 'MotivationSystem'}
            elif field_theory_code == 4: # Subversion (Praxis)
                # Goal: Undermine a power structure.
                new_demand = {'type': 'PURSUE_SUBVERSION', 'source': 'MotivationSystem'}

            if new_demand:
                needs_comp.demands.append(new_demand)
                print(f"INFO: MotivationSystem: NPC {entity_id} generated high-level demand: {new_demand['type']}")