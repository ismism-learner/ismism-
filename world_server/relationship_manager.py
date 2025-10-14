import json
from typing import Dict, Any

# Assuming the ECS components are accessible. This might need adjustment
# based on the actual project structure.
from world_server.ecs.components.relationship import RelationshipComponent
from world_server.ecs.components.identity import IdentityComponent

class RelationshipManager:
    def __init__(self, relationship_types_path: str = "world_server/relationship_types.json"):
        self.relationship_types = self._load_relationship_types(relationship_types_path)

    def _load_relationship_types(self, path: str) -> Dict[str, Any]:
        """Loads relationship type definitions from a JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                print(f"Loading relationship types from {path}...")
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Relationship types file not found at {path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {path}")
            return {}

    def update_relationship_status(self, npc1_id, npc2_id, interaction: Dict, world):
        """
        Checks and updates the relationship status between two NPCs based on their
        current affinity and the last interaction.
        """
        # 1. Get current relationship data from npc1's perspective
        rel_comp = world.get_component(npc1_id, RelationshipComponent)

        # Initialize relationship entry if it doesn't exist
        if npc2_id not in rel_comp.relations:
            rel_comp.relations[npc2_id] = {"affinity": 0, "status": None}

        relationship_data = rel_comp.relations[npc2_id]
        current_affinity = relationship_data.get("affinity", 0)
        current_status = relationship_data.get("status")

        # 2. Check for relationship dissolution if a status already exists
        if current_status:
            dissolution_triggers = self.relationship_types[current_status]['dissolution_triggers']

            should_dissolve = False
            # Special case for 'Rival': dissolves when affinity goes ABOVE the threshold
            if current_status == 'Rival':
                if current_affinity >= dissolution_triggers['affinity_threshold']:
                    should_dissolve = True
            # Default case for positive relationships: dissolves when affinity goes BELOW the threshold
            else:
                if current_affinity < dissolution_triggers['affinity_threshold']:
                    should_dissolve = True

            if should_dissolve:
                original_status = current_status
                npc1_identity = world.get_component(npc1_id, IdentityComponent)
                npc2_identity = world.get_component(npc2_id, IdentityComponent)
                print(f"**RELATIONSHIP DISSOLVED**: {npc1_identity.name}'s status of '{original_status}' towards {npc2_identity.name} has ended.")
                relationship_data['status'] = None
                current_status = None # Update for the formation check below

                # --- HOOK FOR SYMBOLIC DESIRE ---
                if hasattr(world, 'desire_system'):
                    trigger_event = {
                        'type': f'LOST_{original_status.upper()}', # e.g., LOST_RIVAL
                        'target_id': npc2_id
                    }
                    world.desire_system.generate_symbolic_aspiration(npc1_id, trigger_event)

        # 3. Check for relationship formation if no status currently exists
        if not current_status:
            for rel_type, data in self.relationship_types.items():
                formation_triggers = data['formation_triggers']

                # Check affinity threshold
                if current_affinity >= formation_triggers['affinity_threshold']:
                    # Check for required interaction keyword
                    required_keyword = formation_triggers.get('required_interaction_keyword')
                    interaction_keyword = interaction.get('keyword')

                    if not required_keyword or (required_keyword and interaction_keyword == required_keyword):
                        relationship_data['status'] = rel_type
                        npc1_identity = world.get_component(npc1_id, IdentityComponent)
                        npc2_identity = world.get_component(npc2_id, IdentityComponent)
                        print(f"**RELATIONSHIP FORMED**: {npc1_identity.name} now considers {npc2_identity.name} a '{rel_type}'.")

                        # --- HOOK FOR SYMBOLIC DESIRE ---
                        if hasattr(world, 'desire_system'):
                            trigger_event = {
                                'type': f'GAINED_{rel_type.upper()}', # e.g., GAINED_RIVAL
                                'target_id': npc2_id
                            }
                            world.desire_system.generate_symbolic_aspiration(npc1_id, trigger_event)

                        # Stop after forming one relationship
                        break

        # 4. Update the component in the world
        world.add_component(npc1_id, rel_comp)