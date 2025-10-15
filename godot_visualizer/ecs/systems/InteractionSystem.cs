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

        private const float InteractionDistance = 20.0f; // Max distance for interaction
        private const int InteractionCooldown = 300; // Ticks between interactions

        public override void Process()
        {
            if (_relationshipManager == null)
            {
                _relationshipManager = World.GetNode<RelationshipManager>("/root/RelationshipManager");
            }

            var entities = World.GetEntitiesWithComponents(typeof(JobComponent), typeof(PositionComponent), typeof(StateComponent));

            foreach (var entityId in entities)
            {
                var state = World.GetComponent<StateComponent>(entityId);

                // Simple cooldown to prevent constant interactions
                if (World.Time - state.LastInteractionTime < InteractionCooldown)
                {
                    continue;
                }

                var job = World.GetComponent<JobComponent>(entityId);
                var pos = World.GetComponent<PositionComponent>(entityId);

                // Find colleagues at the same workplace
                var colleagues = World.GetEntitiesWithComponents(typeof(JobComponent), typeof(PositionComponent));
                foreach (var colleagueId in colleagues)
                {
                    if (entityId == colleagueId) continue;

                    var colleagueJob = World.GetComponent<JobComponent>(colleagueId);
                    if (colleagueJob.WorkplaceBuildingName == job.WorkplaceBuildingName)
                    {
                        var colleaguePos = World.GetComponent<PositionComponent>(colleagueId);
                        if (pos.Position.DistanceTo(colleaguePos.Position) < InteractionDistance)
                        {
                            // Trigger an interaction
                            PerformInteraction(entityId, colleagueId, "WorkplaceChat");
                            state.LastInteractionTime = World.Time; // Update cooldown timer
                            break; // Interact with one person per tick
                        }
                    }
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