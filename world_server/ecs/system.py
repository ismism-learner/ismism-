# world_server/ecs/system.py
"""
Defines the base class for all Systems.
"""

class System:
    """
    The base class for all systems.
    A system contains logic that operates on entities with specific components.
    """
    def __init__(self):
        # The world instance will be set by the World object when the system is added.
        self.world = None

    def process(self, *args, **kwargs):
        """

        This method will be called by the World on each game loop tick.
        Subclasses should implement their logic here.
        """
        raise NotImplementedError