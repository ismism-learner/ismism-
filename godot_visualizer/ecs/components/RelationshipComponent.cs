using System.Collections.Generic;

namespace Ecs.Components
{
    public enum RelationshipType
    {
        Friend,
        Lover,
        Mentor,
        Student,
        Parent,
        Child,
        Follower
    }

    public class Relationship
    {
        public int TargetNpcId { get; set; }
        public RelationshipType Type { get; set; }
        public float Strength { get; set; } // e.g., 0-100

        public Relationship(int targetNpcId, RelationshipType type, float initialStrength)
        {
            TargetNpcId = targetNpcId;
            Type = type;
            Strength = initialStrength;
        }
    }

    public partial class RelationshipComponent : Component
    {
        public Dictionary<int, Relationship> Relationships { get; private set; } = new Dictionary<int, Relationship>();

        public void AddOrUpdateRelationship(int targetNpcId, RelationshipType type, float strengthChange)
        {
            if (Relationships.TryGetValue(targetNpcId, out var existingRelationship))
            {
                existingRelationship.Strength += strengthChange;
                // Clamp strength between 0 and 100
                if (existingRelationship.Strength > 100) existingRelationship.Strength = 100;
                if (existingRelationship.Strength < 0) existingRelationship.Strength = 0;
            }
            else
            {
                Relationships.Add(targetNpcId, new Relationship(targetNpcId, type, strengthChange));
            }
        }

        public Relationship GetRelationshipWith(int targetNpcId)
        {
            Relationships.TryGetValue(targetNpcId, out var relationship);
            return relationship;
        }
    }
}