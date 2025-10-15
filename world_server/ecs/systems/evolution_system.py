# world_server/ecs/systems/evolution_system.py
import random
import copy
from ..system import System
from ..components.ism import IsmComponent

# Constants
INITIAL_IXP_VALUE = 100.0 # The starting IXP for a newly birthed ideological pillar
INTENSITY_SHIFT_FACTOR = 0.51 # New ideology gets 51% of the combined intensity

class EvolutionSystem(System):
    """
    Handles the "birth" of new ideologies when an NPC's IXP crosses a threshold.
    This represents a moment of ideological crisis and schism.
    """

    def __init__(self):
        super().__init__()
        self.process_interval = 10
        self.tick_counter = 0

    def process(self, *args, **kwargs):
        self.tick_counter += 1
        if self.tick_counter < self.process_interval:
            return
        self.tick_counter = 0

        entities = self.world.get_entities_with_components(IsmComponent)
        for entity_id in entities:
            ism_comp = self.world.get_component(entity_id, IsmComponent)
            # We only check the dominant ideology for evolution potential
            dominant_ideology = ism_comp.dominant_ideology
            self._check_for_evolution(entity_id, ism_comp, dominant_ideology)

    def _check_for_evolution(self, entity_id: int, ism_comp: IsmComponent, ideology: dict):
        """
        Checks a specific ideology within an NPC to see if any of its pillars can evolve
        based on the new dialectical threshold rules.
        """
        current_gene_parts = [int(g) for g in ideology['code'].split('-')]
        ixp_matrix = ideology.get('ixp', [])

        if not ixp_matrix:
            return

        for i in range(4): # Iterate through the four pillars (Field, Ontology, etc.)
            current_stage = current_gene_parts[i]
            ixp_row = ixp_matrix[i]

            should_evolve = False
            if current_stage == 1 and ixp_row[1] > ixp_row[0]:
                should_evolve = True
            elif current_stage == 2 and ixp_row[2] > (ixp_row[0] + ixp_row[1]):
                should_evolve = True
            elif current_stage == 3 and ixp_row[3] > max(ixp_row[0], ixp_row[1], ixp_row[2]):
                should_evolve = True

            if should_evolve:
                new_stage = current_stage + 1
                if new_stage <= 4:
                    self._birth_new_ideology(ism_comp, ideology, i, new_stage)
                    # Stop after one evolution per tick to prevent cascades
                    return

    def _birth_new_ideology(self, ism_comp: IsmComponent, source_ideology: dict, pillar_index: int, new_stage: int):
        """
        Creates a new ideology, adds it to the NPC's mind, and performs an intensity shift.
        """
        print(f"**IDEOLOGICAL BIRTH**: Entity's ideology {source_ideology['code']} is birthing a new one at pillar {pillar_index}, stage {new_stage}!")

        # 1. Create the new ideology
        new_ideology = copy.deepcopy(source_ideology)

        # Update gene code for the new ideology
        new_gene_parts = new_ideology['code'].split('-')
        new_gene_parts[pillar_index] = str(new_stage)
        new_ideology['code'] = "-".join(new_gene_parts)

        # Reset IXP for the evolved pillar in the new ideology
        new_ixp_row = [0.0] * 4
        new_ixp_row[new_stage - 1] = INITIAL_IXP_VALUE
        new_ideology['ixp'][pillar_index] = new_ixp_row

        # Also reset the source ideology's IXP for that pillar
        source_ideology['ixp'][pillar_index] = [0.0] * 4
        source_ideology['ixp'][pillar_index][int(source_ideology['code'].split('-')[pillar_index])-1] = INITIAL_IXP_VALUE


        # 2. Perform the Intensity Shift
        # The shift only happens between the source and the new ideology
        total_intensity_of_pair = source_ideology['intensity']
        new_ideology['intensity'] = total_intensity_of_pair * INTENSITY_SHIFT_FACTOR
        source_ideology['intensity'] = total_intensity_of_pair * (1 - INTENSITY_SHIFT_FACTOR)

        # 3. Add the new ideology to the active list
        ism_comp.active_ideologies.append(new_ideology)

        # 4. Normalize all intensities across the component so they sum to 1.0
        self._normalize_intensities(ism_comp)

    def _normalize_intensities(self, ism_comp: IsmComponent):
        """
        Ensures the sum of all intensities in active_ideologies is 1.0.
        """
        total_intensity = sum(ideo['intensity'] for ideo in ism_comp.active_ideologies)
        if total_intensity > 0:
            for ideology in ism_comp.active_ideologies:
                ideology['intensity'] /= total_intensity