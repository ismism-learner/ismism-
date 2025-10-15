using Ecs.Components;
using Godot;
using Godot.Collections;
using Managers;

namespace Ecs.Systems
{
    /// <summary>
    /// Manages interactions between entities.
    /// </summary>
    public class InteractionSystem : System
    {
        private RelationshipManager _relationshipManager;

        public override void Process()
        {
            // In a full implementation, this system would be triggered by specific
            // "Interact" actions set in the StateComponent.
            // For this migration, we'll create a placeholder that demonstrates the core logic.

            if (_relationshipManager == null)
            {
                // Get the singleton instance
                _relationshipManager = world.GetNode<RelationshipManager>("/root/RelationshipManager");
            }

            // Example Trigger: Find entities wanting to interact
            var entities = world.GetEntitiesWithComponents(typeof(StateComponent));
            foreach (var entityId in entities)
            {
                var state = world.GetComponent<StateComponent>(entityId);
                if (state.CurrentState == "RequestInteraction")
                {
                    var targetId = (long)state.ActionData["target_id"];
                    var interactionType = state.ActionData["interaction_type"].ToString(); // e.g., "DiscussPhilosophy"

                    PerformInteraction(entityId, targetId, interactionType);

                    // Reset state after interaction
                    state.CurrentState = "Idle";
                }
            }
        }

        private void PerformInteraction(long initiatorId, long receiverId, string interactionType)
        {
            GD.Print($"Entity {initiatorId} is interacting with {receiverId} ({interactionType}).");

            // 1. Update Affinity (simplified)
            var relComp = world.GetComponent<RelationshipComponent>(initiatorId);
            if (relComp.Relations.TryGetValue(receiverId, out var relationData))
            {
                relationData["affinity"] = relationData["affinity"].AsFloat() + 5.0f;
            }

            // 2. Update Relationship Status based on interaction keyword
            // This would look up the interaction definition from DataManager
            var interactionKeyword = "COOPERATION"; // Placeholder
            _relationshipManager.UpdateRelationship(initiatorId, receiverId, interactionKeyword);

            // 3. Propagate Ideology (simplified)
            var initiatorIsm = world.GetComponent<IsmComponent>(initiatorId);
            var receiverIsm = world.GetComponent<IsmComponent>(receiverId);
            if (initiatorIsm.ActiveIdeologies.Count > 1)
            {
                var ideologyToSpread = initiatorIsm.ActiveIdeologies[1]; // Spread secondary 'ism'
                receiverIsm.AddIdeology(ideologyToSpread);
                GD.Print($"Ideology '{ideologyToSpread}' spread from {initiatorId} to {receiverId}.");
            }
        }
    }
}