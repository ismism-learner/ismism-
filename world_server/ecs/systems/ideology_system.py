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
        Applies decay to non-dominant ideologies and removes dead ones.
        """
        dominant_ideology = ism_comp.dominant_ideology
        decayed_total = 0.0
        surviving_ideologies = []

        for ideology in ism_comp.active_ideologies:
            if ideology['code'] != dominant_ideology['code']:
                decay_amount = ideology['intensity'] * DECAY_RATE
                ideology['intensity'] -= decay_amount
                decayed_total += decay_amount

            if ideology['intensity'] < DEATH_THRESHOLD:
                print(f"**IDEOLOGICAL DEATH**: Ideology {ideology['code']} has faded away.")
                # Don't add it to the list of survivors, but add its remaining intensity to the pot
                decayed_total += ideology['intensity']
            else:
                surviving_ideologies.append(ideology)

        # Add the total decayed amount to the dominant ideology
        if dominant_ideology in surviving_ideologies:
             dominant_ideology['intensity'] += decayed_total

        ism_comp.active_ideologies = surviving_ideologies
        self._normalize_intensities(ism_comp)

    def reinforce(self, entity_id: int, action_keywords: list):
        """
        Reinforces an ideology that aligns with a performed action.
        """
        ism_comp = self.world.get_component(entity_id, IsmComponent)
        if not ism_comp or len(ism_comp.active_ideologies) <= 1:
            return

        best_match = self._find_best_match(ism_comp.active_ideologies, action_keywords)
        if not best_match:
            return

        # Increase intensity of the best match
        best_match['intensity'] += REINFORCEMENT_FACTOR
        print(f"**IDEOLOGICAL REINFORCEMENT**: Action reinforced {best_match['code']}.")

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

    def _normalize_intensities(self, ism_comp: IsmComponent):
        """
        Ensures the sum of all intensities in active_ideologies is 1.0.
        """
        total_intensity = sum(ideo['intensity'] for ideo in ism_comp.active_ideologies)
        if total_intensity > 0:
            for ideology in ism_comp.active_ideologies:
                ideology['intensity'] /= total_intensity