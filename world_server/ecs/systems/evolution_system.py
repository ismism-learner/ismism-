# world_server/ecs/systems/evolution_system.py
import random
from ..system import System
from ..components.ism import IsmComponent

# Constants for IXP Evolution
IXP_THRESHOLDS = {
    1: 500,   # Threshold to evolve from Identity to Contradiction
    2: 1000,  # Threshold to evolve from Contradiction to Synthesis
    3: 2000,  # Threshold to evolve from Synthesis to Collapse
}
# Map pillar names to their index in the IXP matrix
PILLAR_MAP = {"field": 0, "ontology": 1, "epistemology": 2, "teleology": 3}
INITIAL_IXP_VALUE = 100.0

class EvolutionSystem(System):
    """
    Handles the evolution of NPC ideologies based on accumulated experience (IXP).
    """

    def __init__(self, world=None):
        super().__init__(world)
        # Run this system less frequently than others
        self.process_interval = 10 # Process every 10 server ticks
        self.tick_counter = 0

    def process(self, *args, **kwargs):
        self.tick_counter += 1
        if self.tick_counter < self.process_interval:
            return

        self.tick_counter = 0

        entities = self.world.get_entities_with_components(IsmComponent)
        for entity_id in entities:
            ism_comp = self.world.get_component(entity_id, IsmComponent)
            self._check_for_evolution(entity_id, ism_comp)

    def _check_for_evolution(self, entity_id, ism_comp: IsmComponent):
        """
        Checks each ideological pillar to see if an evolution threshold has been met.
        """
        current_gene_parts = [int(g) for g in ism_comp.gene_code.split('-')]

        for i in range(4): # Iterate through the four pillars
            current_stage = current_gene_parts[i]
            if current_stage >= 4: # Already at the final stage (Collapse)
                continue

            threshold = IXP_THRESHOLDS.get(current_stage)
            if not threshold:
                continue

            # The "next" stage's IXP is what drives the evolution.
            # e.g., to evolve from stage 1 (Identity) to 2 (Contradiction),
            # we check the IXP of the Contradiction column (index 1).
            ixp_to_check = ism_comp.ixp[i][current_stage]

            if ixp_to_check >= threshold:
                self._evolve_pillar(ism_comp, i, current_stage + 1)

    def _evolve_pillar(self, ism_comp: IsmComponent, pillar_index: int, new_stage: int):
        """
        Evolves a specific pillar to the next stage, updating the gene code
        and resetting the IXP for that pillar.
        """
        print(f"**IDEOLOGICAL EVOLUTION**: Entity's pillar {pillar_index} is evolving to stage {new_stage}!")

        # Update gene code
        current_gene_parts = ism_comp.gene_code.split('-')
        current_gene_parts[pillar_index] = str(new_stage)
        ism_comp.gene_code = "-".join(current_gene_parts)

        # Reset IXP for the evolved pillar
        # The new stage starts with the base IXP, others are zero.
        new_ixp_row = [0.0] * 4
        new_ixp_row[new_stage - 1] = INITIAL_IXP_VALUE
        ism_comp.ixp[pillar_index] = new_ixp_row

        # Optional: Trigger a desire to reflect on this change?
        # This could be a hook to the DesireSystem in the future.
        # For example: self.world.desire_system.generate_symbolic_aspiration(...)