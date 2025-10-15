import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from world_server.ecs.components.ism import IsmComponent
from world_server.ecs.systems.ideology_system import IdeologySystem
from world_server.ecs.systems.evolution_system import EvolutionSystem
from world_server.ecs.world import World

class TestIdeology(unittest.TestCase):

    def setUp(self):
        """Set up a fresh world and systems for each test."""
        self.ecs_world = World()
        self.ideology_system = IdeologySystem()
        self.evolution_system = EvolutionSystem()
        self.ecs_world.add_system(self.ideology_system)
        self.ecs_world.add_system(self.evolution_system)

    def test_process_experience(self):
        """Verify that IXP is correctly added to the dominant ideology."""
        npc_id = self.ecs_world.create_entity()
        ism_comp = IsmComponent()
        self.ecs_world.add_component(npc_id, ism_comp)

        # Initial IXP should be 1.0 in the first column of each row
        self.assertEqual(ism_comp.dominant_ideology['ixp'][0][0], 1.0)

        # Define an IXP event
        ixp_event = [{"domain": "目的论", "state": 2, "value": 20}]

        # Process the experience
        self.ideology_system.process_experience(npc_id, ixp_event)

        # The IXP should be added to the '目的论' (pillar 3), 'state' 2 (index 1)
        self.assertEqual(ism_comp.dominant_ideology['ixp'][3][1], 20.0)

    def test_dialectical_evolution(self):
        """Test the 'birth' of a new ideology based on dialectical rules."""
        npc_id = self.ecs_world.create_entity()
        ism_comp = IsmComponent()
        # Start with a basic ideology
        ism_comp.active_ideologies = [{
            "code": "1-1-1-1",
            "intensity": 1.0,
            "ixp": [[10, 5, 0, 0], [10, 5, 0, 0], [10, 5, 0, 0], [10, 5, 0, 0]],
            "data": {}
        }]
        self.ecs_world.add_component(npc_id, ism_comp)

        # Trigger evolution by making IXP for state 2 greater than state 1 in the first pillar
        ism_comp.dominant_ideology['ixp'][0][1] = 15

        # Process the evolution system enough times to trigger the check
        for _ in range(10):
            self.evolution_system.process()

        # A new ideology should have been born
        self.assertEqual(len(ism_comp.active_ideologies), 2)

        # Find the new ideology
        new_ideology = next(ideo for ideo in ism_comp.active_ideologies if ideo['code'] == '2-1-1-1')
        self.assertIsNotNone(new_ideology)

        # Check intensity shift
        self.assertAlmostEqual(new_ideology['intensity'], 0.51)

    def test_add_ideology_api(self):
        """Test the external API for adding a new ideology."""
        npc_id = self.ecs_world.create_entity()
        ism_comp = IsmComponent()
        self.ecs_world.add_component(npc_id, ism_comp)

        # Add a new ideology
        self.ideology_system.add_ideology(npc_id, "2-2-2-2", 0.5)

        # There should be two ideologies now
        self.assertEqual(len(ism_comp.active_ideologies), 2)

        # Check if the new ideology is present
        self.assertTrue(any(ideo['code'] == '2-2-2-2' for ideo in ism_comp.active_ideologies))

    def test_purify_ideology_api(self):
        """Test the external API for forcing an ideology to be dominant."""
        npc_id = self.ecs_world.create_entity()
        ism_comp = IsmComponent()
        # Add a few ideologies
        ism_comp.active_ideologies = [
            {"code": "1-1-1-1", "intensity": 0.4, "ixp": [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]], "data": {}},
            {"code": "2-2-2-2", "intensity": 0.6, "ixp": [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]], "data": {}}
        ]
        self.ecs_world.add_component(npc_id, ism_comp)

        # Purify the '1-1-1-1' ideology
        self.ideology_system.purify_ideology(npc_id, "1-1-1-1")

        # The purified ideology should have 0.95 intensity
        purified_ideology = next(ideo for ideo in ism_comp.active_ideologies if ideo['code'] == '1-1-1-1')
        self.assertAlmostEqual(purified_ideology['intensity'], 0.95)

    def test_reinforcement(self):
        """Test that reinforcement increases the correct ideology's intensity."""
        npc_id = self.ecs_world.create_entity()
        ism_comp = IsmComponent()
        ism_comp.active_ideologies = [
            {"code": "1-1-1-1", "intensity": 0.5, "ixp": [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]], "data": {"keywords": ["peace", "order"]}},
            {"code": "2-2-2-2", "intensity": 0.5, "ixp": [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]], "data": {"keywords": ["chaos", "freedom"]}}
        ]
        self.ecs_world.add_component(npc_id, ism_comp)

        self.ideology_system.reinforce(npc_id, ["freedom"])

        chaos_ideology = next(ideo for ideo in ism_comp.active_ideologies if ideo['code'] == '2-2-2-2')
        self.assertTrue(chaos_ideology['intensity'] > 0.5)

    def test_decay_and_death(self):
        """Test that non-dominant ideologies decay and are removed when below threshold."""
        npc_id = self.ecs_world.create_entity()
        ism_comp = IsmComponent()
        ism_comp.active_ideologies = [
            {"code": "1-1-1-1", "intensity": 0.9, "ixp": [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]], "data": {}},
            {"code": "2-2-2-2", "intensity": 0.06, "ixp": [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]], "data": {}},
            {"code": "3-3-3-3", "intensity": 0.04, "ixp": [[0,0,1,0],[0,0,1,0],[0,0,1,0],[0,0,1,0]], "data": {}} # This one should die
        ]
        self.ecs_world.add_component(npc_id, ism_comp)

        # Process the system enough times to trigger decay
        for _ in range(20):
            self.ideology_system.process()

        # The weak ideology should be dead
        self.assertEqual(len(ism_comp.active_ideologies), 2)
        self.assertFalse(any(ideo['code'] == '3-3-3-3' for ideo in ism_comp.active_ideologies))

        # The dominant ideology should have absorbed the intensity
        dominant_ideology = ism_comp.dominant_ideology
        self.assertTrue(dominant_ideology['intensity'] > 0.9)


if __name__ == '__main__':
    unittest.main()