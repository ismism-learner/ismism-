import unittest
import os
import sys
import json
from unittest.mock import Mock, MagicMock

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from world_server.relationship_manager import RelationshipManager
from world_server.ecs.components.relationship import RelationshipComponent
from world_server.ecs.components.identity import IdentityComponent

class TestRelationshipManager(unittest.TestCase):

    def setUp(self):
        """Set up a mock world and a relationship manager for each test."""
        # Create a mock for the ECS world
        self.mock_world = Mock()

        # Mock NPCs (entity IDs)
        self.npc1_id = "npc1"
        self.npc2_id = "npc2"

        # Mock components
        self.npc1_rel_comp = RelationshipComponent(relations={})
        self.npc2_rel_comp = RelationshipComponent(relations={})
        self.npc1_identity = IdentityComponent(name="Alice", description="A test NPC")
        self.npc2_identity = IdentityComponent(name="Bob", description="Another test NPC")

        # Configure the mock world's get_component method
        def get_component_side_effect(entity_id, component_type):
            if entity_id == self.npc1_id:
                if component_type == RelationshipComponent: return self.npc1_rel_comp
                if component_type == IdentityComponent: return self.npc1_identity
            if entity_id == self.npc2_id:
                if component_type == RelationshipComponent: return self.npc2_rel_comp
                if component_type == IdentityComponent: return self.npc2_identity
            return None

        self.mock_world.get_component = MagicMock(side_effect=get_component_side_effect)
        self.mock_world.add_component = Mock()

        # Instantiate the manager
        self.relationship_manager = RelationshipManager()

    def test_comrade_formation(self):
        """Test that a 'Comrade' relationship forms with high affinity and correct interaction."""
        # Arrange: Set high affinity and a cooperative interaction
        self.npc1_rel_comp.relations[self.npc2_id] = {"affinity": 80, "status": None}
        cooperative_interaction = {"name": "Discuss Philosophy", "keyword": "COOPERATION"}

        # Act
        self.relationship_manager.update_relationship_status(self.npc1_id, self.npc2_id, cooperative_interaction, self.mock_world)

        # Assert
        updated_status = self.npc1_rel_comp.relations[self.npc2_id].get("status")
        self.assertEqual(updated_status, "Comrade")
        self.mock_world.add_component.assert_called_with(self.npc1_id, self.npc1_rel_comp)

    def test_friend_formation_without_keyword(self):
        """Test that a 'Friend' relationship forms on high affinity, even without a specific keyword."""
        # Arrange: High affinity, and a neutral interaction
        self.npc1_rel_comp.relations[self.npc2_id] = {"affinity": 80, "status": None}
        neutral_interaction = {"name": "Small Talk", "keyword": "NEUTRAL"} # 'Friend' does not require a keyword

        # Act
        self.relationship_manager.update_relationship_status(self.npc1_id, self.npc2_id, neutral_interaction, self.mock_world)

        # Assert
        updated_status = self.npc1_rel_comp.relations[self.npc2_id].get("status")
        self.assertEqual(updated_status, "Friend", "Status should be 'Friend' based on high affinity alone")

    def test_rival_dissolution(self):
        """Test that a 'Rival' relationship is dissolved when affinity rises above the threshold."""
        # Arrange: Existing 'Rival' status, but affinity has improved
        self.npc1_rel_comp.relations[self.npc2_id] = {"affinity": 10, "status": "Rival"} # Rival dissolution is at 0
        improving_interaction = {"name": "Offer Gift"} # No keyword needed for dissolution

        # Act
        self.relationship_manager.update_relationship_status(self.npc1_id, self.npc2_id, improving_interaction, self.mock_world)

        # Assert
        updated_status = self.npc1_rel_comp.relations[self.npc2_id].get("status")
        self.assertIsNone(updated_status, "Rival status should be dissolved when affinity improves")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)