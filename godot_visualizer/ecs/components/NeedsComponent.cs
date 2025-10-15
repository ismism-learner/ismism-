using Godot.Collections;

namespace Ecs.Components
{
    /// <summary>
    /// Stores the needs and demands of an entity, which drive its behavior.
    /// </summary>
    public class NeedsComponent : Component
    {
        public float Stress { get; set; } // 0-100
        public float Hunger { get; set; } // 0-100
        public float Fulfillment { get; set; } // 0-100, for hobbies/purpose
        public float PreviousStress { get; set; } = 0;

        // A list of complex goals, e.g., { "type": "PURSUE_HOBBY", "hobby_id": "painting" }
        public Array<Dictionary> Demands { get; set; }

        public NeedsComponent(float stress, float hunger, float fulfillment = 50f)
        {
            Stress = stress;
            Hunger = hunger;
            Fulfillment = fulfillment;
            Demands = new Array<Dictionary>();
        }
    }
}