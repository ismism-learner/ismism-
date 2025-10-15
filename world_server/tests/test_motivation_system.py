import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from world_server.ecs.world import World
from world_server.ecs.components.ism import IsmComponent
from world_server.ecs.components.needs import NeedsComponent
from world_server.ecs.systems.motivation_system import MotivationSystem

class TestMotivationSystem(unittest.TestCase):

    def setUp(self):
        """Set up a fresh world and systems for each test."""
        self.ecs_world = World()
        self.motivation_system = MotivationSystem()
        self.ecs_world.add_system(self.motivation_system)

    def _create_test_npc(self, ideology_code: str):
        """Helper function to create an NPC with a specific ideology."""
        npc_id = self.ecs_world.create_entity()
        # Create a basic ideology structure
        ideology = {
            "code": ideology_code,
            "intensity": 1.0,
            "ixp": [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]],
            "data": {}
        }
        ism_comp = IsmComponent()
        ism_comp.active_ideologies = [ideology] # Set the property after initialization
        needs_comp = NeedsComponent()
        self.ecs_world.add_component(npc_id, ism_comp)
        self.ecs_world.add_component(npc_id, needs_comp)
        return npc_id, needs_comp

    def test_demand_generation_level_2(self):
        """Test if ideology '2-x-x-x' generates a 'PURSUE_SOCIAL_STANDING' demand."""
        npc_id, needs_comp = self._create_test_npc("2-1-1-1")

        # Process the motivation system
        self.motivation_system.process()

        self.assertEqual(len(needs_comp.demands), 1)
        self.assertEqual(needs_comp.demands[0]['type'], 'PURSUE_SOCIAL_STANDING')
        self.assertEqual(needs_comp.demands[0]['source'], 'MotivationSystem')

    def test_demand_generation_level_3(self):
        """Test if ideology '3-x-x-x' generates a 'PURSUE_KNOWLEDGE' demand."""
        npc_id, needs_comp = self._create_test_npc("3-1-1-1")

        # Process the motivation system
        self.motivation_system.process()

        self.assertEqual(len(needs_comp.demands), 1)
        self.assertEqual(needs_comp.demands[0]['type'], 'PURSUE_KNOWLEDGE')
        self.assertEqual(needs_comp.demands[0]['source'], 'MotivationSystem')

    def test_demand_generation_level_4(self):
        """Test if ideology '4-x-x-x' generates a 'PURSUE_SUBVERSION' demand."""
        npc_id, needs_comp = self._create_test_npc("4-1-1-1")

        # Process the motivation system
        self.motivation_system.process()

        self.assertEqual(len(needs_comp.demands), 1)
        self.assertEqual(needs_comp.demands[0]['type'], 'PURSUE_SUBVERSION')
        self.assertEqual(needs_comp.demands[0]['source'], 'MotivationSystem')

    def test_no_demand_for_level_1(self):
        """Test if ideology '1-x-x-x' does not generate a high-level demand."""
        npc_id, needs_comp = self._create_test_npc("1-1-1-1")

        # Process the motivation system
        self.motivation_system.process()

        self.assertEqual(len(needs_comp.demands), 0)

    def test_demand_not_duplicated(self):
        """Test that the system doesn't add a demand if one already exists."""
        npc_id, needs_comp = self._create_test_npc("2-1-1-1")

        # Manually add a demand from the same source
        needs_comp.demands.append({'type': 'PURSUE_SOCIAL_STANDING', 'source': 'MotivationSystem'})

        # Process the motivation system
        self.motivation_system.process()

        # The list should still only contain the one demand
        self.assertEqual(len(needs_comp.demands), 1)

if __name__ == '__main__':
    unittest.main()