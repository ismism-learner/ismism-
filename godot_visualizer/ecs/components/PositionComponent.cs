using Godot;

namespace Ecs.Components
{
    /// <summary>
    /// Stores the entity's position in the world.
    /// </summary>
    public class PositionComponent : Component
    {
        public Vector2 Position { get; set; }

        public PositionComponent(Vector2 position)
        {
            Position = position;
        }
    }
}