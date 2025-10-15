using Godot.Collections;

namespace Ecs.Components
{
    /// <summary>
    /// Stores the core identity information of an entity.
    /// </summary>
    public class IdentityComponent : Component
    {
        public string Name { get; set; }
        public string BirthplaceId { get; set; }
        public Dictionary Biography { get; set; } // e.g., social_class, education

        public IdentityComponent(string name, string birthplaceId, Dictionary biography)
        {
            Name = name;
            BirthplaceId = birthplaceId;
            Biography = biography;
        }
    }
}