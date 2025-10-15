import godot
import threading
import time
import json
import sys
import os

# Add the project root to the Python path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world_server.server import Server

@godot.expose_script_class
class WorldSimBridge(godot.Node):

    def __init__(self):
        super().__init__()
        self.world_server = None
        self.simulation_thread = None
        self.is_running = False
        self.world_state_json = ""
        self.lock = threading.Lock()

    def _run_simulation(self):
        """The main loop for the simulation thread."""
        self.world_server = Server()

        # We need to adapt the server's game loop to run without async/websockets
        # For now, we'll simulate the tick-based update
        while self.is_running:
            self.world_server.ecs_world.process(
                locations=self.world_server.locations,
                interactions=self.world_server.interactions,
                relationship_types=self.world_server.relationship_types,
                consumer_goods=self.world_server.consumer_goods,
                collective_actions=self.world_server.collective_actions
            )

            # Update the shared world state
            current_state = self.world_server.get_world_state()
            with self.lock:
                self.world_state_json = current_state

            time.sleep(0.5) # ~2 ticks per second

    @godot.expose_method
    def start_simulation(self):
        """Starts the Python simulation in a new thread."""
        if not self.is_running:
            self.is_running = True
            self.simulation_thread = threading.Thread(target=self._run_simulation)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()

    @godot.expose_method
    def get_world_state_json(self) -> str:
        """Returns the latest world state as a JSON string."""
        with self.lock:
            return self.world_state_json

    def _exit_tree(self):
        """Clean up when the node is removed from the scene."""
        self.is_running = False
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join()
        godot.print("Python simulation thread stopped.")