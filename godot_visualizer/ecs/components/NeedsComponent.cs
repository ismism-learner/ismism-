using Godot.Collections;

namespace Ecs.Components
{
    /// <summary>
    /// Stores the needs and demands of an entity, which drive its behavior.
    /// </summary>
    public class NeedsComponent : Component
    {
        public float Energy { get; set; } // 0-100
        public float Hunger { get; set; } // 0-100

        // A list of complex goals, e.g., { "type": "PURSUE_HOBBY", "hobby_id": "painting" }
        public Array<Dictionary> Demands { get; set; }

        public NeedsComponent(float energy, float hunger)
        {
            Energy = energy;
            Hunger = hunger;
            Demands = new Array<Dictionary>();
        }
    }
}