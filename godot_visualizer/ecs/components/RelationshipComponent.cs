using Godot.Collections;

namespace Ecs.Components
{
    /// <summary>
    /// Stores all relationships this entity has with other entities.
    /// </summary>
    public class RelationshipComponent : Component
    {
        // Maps other entity IDs to a dictionary containing affinity and status.
        // e.g., { 1234: { "affinity": 50.0, "status": "Comrade" } }
        public Dictionary<long, Dictionary> Relations { get; set; }

        public RelationshipComponent()
        {
            Relations = new Dictionary<long, Dictionary>();
        }
    }
}