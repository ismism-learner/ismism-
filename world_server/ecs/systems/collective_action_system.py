# world_server/ecs/systems/collective_action_system.py
from ..system import System

class CollectiveActionSystem(System):
    """
    A placeholder system for managing and triggering collective actions
    defined in collective_actions.json.

    Future implementation will involve checking trigger conditions and
    initiating actions for groups of NPCs.
    """
    def __init__(self):
        super().__init__()
        self.tick_counter = 0

    def process(self, *args, **kwargs):
        """
        The main processing loop for the collective action system.
        """
        self.tick_counter += 1
        # For now, this system only prints a debug message every 100 ticks
        # to show that it's running and integrated into the main loop.
        if self.tick_counter % 100 == 0:
            collective_actions = kwargs.get('collective_actions', [])
            if collective_actions:
                # print(f"[DEBUG] CollectiveActionSystem is running. {len(collective_actions)} action types loaded.")
                pass