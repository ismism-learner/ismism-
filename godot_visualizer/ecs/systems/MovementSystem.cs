using Ecs.Components;
using Godot;

namespace Ecs.Systems
{
    public partial class MovementSystem : Ecs.System
    {
        private const float MoveSpeed = 1.0f;
        private const float ProximityThreshold = 1.5f;

        public override void Process()
        {
            var entities = World.GetEntitiesWithComponents(typeof(PositionComponent), typeof(MoveToComponent));

            foreach (var entityId in entities)
            {
                var pos = World.GetComponent<PositionComponent>(entityId);
                var moveTo = World.GetComponent<MoveToComponent>(entityId);

                var direction = (moveTo.TargetPosition - pos.Position).Normalized();
                var newPosition = pos.Position + direction * MoveSpeed;

                if (pos.Position.DistanceTo(moveTo.TargetPosition) < ProximityThreshold)
                {
                    pos.Position = moveTo.TargetPosition;
                    World.RemoveComponent<MoveToComponent>(entityId);
                    // GD.Print($"Entity {entityId} reached destination.");
                }
                else
                {
                    pos.Position = newPosition;
                }
            }
        }
    }
}