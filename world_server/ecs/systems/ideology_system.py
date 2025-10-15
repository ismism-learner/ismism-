# world_server/ecs/systems/ideology_system.py
from ..system import System
from ..components.ism import IsmComponent

# Constants
DECAY_RATE = 0.005  # How much intensity a non-dominant ideology loses per cycle
DEATH_THRESHOLD = 0.05 # Intensity below which an ideology is considered "dead"
REINFORCEMENT_FACTOR = 0.02 # How much intensity is gained upon reinforcement

class IdeologySystem(System):
    """
    Manages the continuous lifecycle of ideologies within NPCs, including
    reinforcement from actions and the natural decay of non-dominant ideas.
    """

    def __init__(self):
        super().__init__()
        # This system should run frequently to model the "use it or lose it" principle
        self.process_interval = 20 # Represents roughly once per "day"
        self.tick_counter = 0

    def process(self, *args, **kwargs):
        """
        Periodically runs the decay and death process for all NPCs.
        """
        self.tick_counter += 1
        if self.tick_counter < self.process_interval:
            return
        self.tick_counter = 0

        entities = self.world.get_entities_with_components(IsmComponent)
        for entity_id in entities:
            ism_comp = self.world.get_component(entity_id, IsmComponent)
            if len(ism_comp.active_ideologies) > 1:
                self._apply_decay_and_death(ism_comp)

    def _apply_decay_and_death(self, ism_comp: IsmComponent):
        """
        Applies decay to non-dominant ideologies and removes dead ones, transferring
        the intensity to the dominant ideology.
        """
        if len(ism_comp.active_ideologies) <= 1:
            return

        dominant_ideology = ism_comp.dominant_ideology
        decayed_total = 0.0
        surviving_ideologies = []

        # First, separate survivors from the dead and calculate total decay
        for ideology in ism_comp.active_ideologies:
            if ideology['code'] == dominant_ideology['code']:
                surviving_ideologies.append(ideology)
                continue

            # Apply decay
            decay_amount = ideology['intensity'] * DECAY_RATE
            ideology['intensity'] -= decay_amount
            decayed_total += decay_amount

            # Check for death
            if ideology['intensity'] < DEATH_THRESHOLD:
                print(f"**IDEOLOGICAL DEATH**: Ideology {ideology['code']} has faded away.")
                # Add its remaining intensity to the pot to be transferred
                decayed_total += ideology['intensity']
            else:
                surviving_ideologies.append(ideology)

        # Add the total decayed amount to the dominant ideology
        if dominant_ideology in surviving_ideologies:
            dominant_ideology['intensity'] += decayed_total

        # Update the component's list of active ideologies
        ism_comp.active_ideologies = surviving_ideologies

        # Finally, re-normalize all intensities to ensure they sum to 1.0
        self._normalize_intensities(ism_comp)

    def process_experience(self, entity_id: int, ixp_events: list):
        """
        Processes an incoming list of IXP events for a specific entity.
        The IXP is added to the dominant ideology's IXP matrix.
        """
        ism_comp = self.world.get_component(entity_id, IsmComponent)
        if not ism_comp:
            return

        dominant_ideology = ism_comp.dominant_ideology
        if not dominant_ideology:
            return

        # A mapping from domain name to pillar index
        domain_map = {"场域论": 0, "本体论": 1, "认识论": 2, "目的论": 3}

        for event in ixp_events:
            domain = event.get("domain")
            state = event.get("state")
            value = event.get("value")

            if domain in domain_map and isinstance(state, int) and 1 <= state <= 4:
                pillar_index = domain_map[domain]
                # State is 1-based, index is 0-based
                state_index = state - 1

                # Add the IXP to the corresponding cell
                dominant_ideology['ixp'][pillar_index][state_index] += value
                print(f"**IXP GAIN**: Entity {entity_id} gained {value} IXP in {domain} (State {state}). New value: {dominant_ideology['ixp'][pillar_index][state_index]}")

        # Trigger a matrix recalculation after processing all events
        ism_comp.trigger_matrix_update()

    def reinforce(self, entity_id: int, action_keywords: list):
        """
        Reinforces the ideology most aligned with a performed action, increasing its
        intensity and decreasing others proportionally.
        """
        ism_comp = self.world.get_component(entity_id, IsmComponent)
        if not ism_comp or len(ism_comp.active_ideologies) <= 1:
            return

        best_match_ideology = self._find_best_match(ism_comp.active_ideologies, action_keywords)
        if not best_match_ideology:
            return

        # Increase the intensity of the best match
        increase = REINFORCEMENT_FACTOR
        best_match_ideology['intensity'] += increase

        # Decrease the intensity of all other ideologies proportionally
        total_other_intensity = 1.0 - (best_match_ideology['intensity'] - increase)
        if total_other_intensity > 0:
            for ideology in ism_comp.active_ideologies:
                if ideology['code'] != best_match_ideology['code']:
                    # The decrease is proportional to their share of the remaining intensity
                    ideology['intensity'] -= (increase * (ideology['intensity'] / total_other_intensity))

        print(f"**IDEOLOGICAL REINFORCEMENT**: Action reinforced {best_match_ideology['code']}.")

        # Normalize to correct any floating point inaccuracies
        self._normalize_intensities(ism_comp)

    def _find_best_match(self, ideologies: list, keywords: list) -> dict | None:
        """
        Finds the ideology that has the most keywords in common with the action.
        This is a simplification; a more complex version could use the matrix.
        """
        best_match = None
        max_score = 0

        for ideology in ideologies:
            # Recursively get all keywords from the ideology's data structure
            ideology_keywords = self._extract_keywords(ideology.get('data', {}))
            common_keywords = set(ideology_keywords) & set(keywords)
            score = len(common_keywords)

            if score > max_score:
                max_score = score
                best_match = ideology

        return best_match

    def _extract_keywords(self, data: dict) -> list:
        """
        Recursively extracts all string values from a nested dictionary.
        """
        keywords = []
        for key, value in data.items():
            if isinstance(value, str):
                keywords.append(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        keywords.append(item)
            elif isinstance(value, dict):
                keywords.extend(self._extract_keywords(value))
        return keywords

    def add_ideology(self, entity_id: int, code: str, intensity: float, data: dict = None):
        """
        External API to add a new ideology to an NPC's mind.
        """
        ism_comp = self.world.get_component(entity_id, IsmComponent)
        if not ism_comp:
            return

        # Avoid adding a duplicate ideology
        if any(ideo['code'] == code for ideo in ism_comp.active_ideologies):
            return

        new_ideology = {
            "code": code,
            "intensity": intensity,
            # Initialize with a base IXP that creates an identity matrix for this gene code
            "ixp": [[1.0 if i == int(g)-1 else 0.0 for i in range(4)] for g in code.split('-')],
            "data": data or {}
        }

        ism_comp.active_ideologies.append(new_ideology)
        self._normalize_intensities(ism_comp)
        ism_comp.trigger_matrix_update()
        print(f"**API CALL**: Added ideology {code} with intensity {intensity} to entity {entity_id}.")

    def purify_ideology(self, entity_id: int, code: str):
        """
        External API to force one ideology to become dominant, suppressing all others.
        Represents a "moment of truth" or radicalization.
        """
        ism_comp = self.world.get_component(entity_id, IsmComponent)
        if not ism_comp:
            return

        target_ideology = None
        other_total_intensity = 0.0

        for ideology in ism_comp.active_ideologies:
            if ideology['code'] == code:
                target_ideology = ideology
            else:
                other_total_intensity += ideology['intensity']

        if not target_ideology:
            # If the ideology doesn't exist, add it with dominant intensity
            self.add_ideology(entity_id, code, 0.95)
            # Clean up others
            self.purify_ideology(entity_id, code)
            return

        # Set the target to be highly dominant
        target_ideology['intensity'] = 0.95

        # Distribute the remaining intensity proportionally among the others
        remaining_intensity = 0.05
        for ideology in ism_comp.active_ideologies:
            if ideology['code'] != code:
                if other_total_intensity > 0:
                    proportional_intensity = (ideology['intensity'] / other_total_intensity) * remaining_intensity
                    ideology['intensity'] = proportional_intensity
                else:
                    # This case handles if somehow other intensities were 0
                    ideology['intensity'] = 0

        self._normalize_intensities(ism_comp)
        ism_comp.trigger_matrix_update()
        print(f"**API CALL**: Purified entity {entity_id}'s mind. Ideology {code} is now dominant.")

    def _normalize_intensities(self, ism_comp: IsmComponent):
        """
        Ensures the sum of all intensities in active_ideologies is 1.0.
        """
        total_intensity = sum(ideo['intensity'] for ideo in ism_comp.active_ideologies)
        if total_intensity > 0:
            for ideology in ism_comp.active_ideologies:
                ideology['intensity'] /= total_intensity