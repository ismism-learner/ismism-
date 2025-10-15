using Godot.Collections;

namespace Ecs.Components
{
    /// <summary>
    /// Manages an entity's hobbies, skills, and crafted goods inventory.
    /// </summary>
    public class HobbyComponent : Component
    {
        // A dictionary mapping hobby_id to skill level (e.g., { "painting": 75.0 })
        public Dictionary<string, float> Skills { get; set; }

        // A list of items the NPC has crafted.
        // Each item is a dictionary, e.g., { "item_id": "portrait", "quality": "masterpiece" }
        public Array<Dictionary> Inventory { get; set; }

        public HobbyComponent()
        {
            Skills = new Dictionary<string, float>();
            Inventory = new Array<Dictionary>();
        }
    }
}