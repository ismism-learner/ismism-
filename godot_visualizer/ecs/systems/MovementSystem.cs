using Ecs.Components;
using Godot;

namespace Ecs.Systems
{
    /// <summary>
    /// Handles the movement of entities.
    /// </summary>
    public class MovementSystem : System
    {
        public override void Process()
        {
            var entities = world.GetEntitiesWithComponents(typeof(PositionComponent), typeof(StateComponent));

            foreach (var entityId in entities)
            {
                var state = world.GetComponent<StateComponent>(entityId);

                if (state.CurrentState == "Moving")
                {
                    var pos = world.GetComponent<PositionComponent>(entityId);
                    var targetPosition = (Vector2)state.ActionData["target_position"];

                    var direction = (targetPosition - pos.Position).Normalized();
                    var newPosition = pos.Position + direction * 1.0f; // Move 1 unit per tick

                    // Check if we've reached the destination
                    if (pos.Position.DistanceTo(targetPosition) < 1.5f)
                    {
                        pos.Position = targetPosition;
                        state.CurrentState = "Idle";
                        state.ActionData.Clear();
                        GD.Print($"Entity {entityId} reached destination.");
                    }
                    else
                    {
                        pos.Position = newPosition;
                    }
                }
            }
        }
    }
}