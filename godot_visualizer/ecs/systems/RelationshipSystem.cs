using Ecs.Components;
using Godot;
using Managers;
using System.Linq;

namespace Ecs.Systems
{
    public partial class RelationshipSystem : Ecs.System
    {
        private DataManager _dataManager;
        private const float ProximityThreshold = 50.0f; // How close NPCs need to be
        private const float CompatibilityBonus = 0.1f; // How much strength is gained per frame

        public override void Process()
        {
            if (_dataManager == null)
            {
                _dataManager = world.GetNode<DataManager>("/root/DataManager");
            }

            var entities = world.GetEntitiesWithComponents(
                typeof(PositionComponent),
                typeof(IsmComponent),
                typeof(RelationshipComponent)
            ).ToList();

            // Inefficient to check all pairs, but fine for a prototype.
            // A spatial partitioning system would optimize this.
            for (int i = 0; i < entities.Count; i++)
            {
                for (int j = i + 1; j < entities.Count; j++)
                {
                    var entityA = entities[i];
                    var entityB = entities[j];

                    var posA = world.GetComponent<PositionComponent>(entityA);
                    var posB = world.GetComponent<PositionComponent>(entityB);

                    if (posA.Position.DistanceTo(posB.Position) < ProximityThreshold)
                    {
                        CheckAndApplyCompatibility(entityA, entityB);
                    }
                }
            }
        }

        private void CheckAndApplyCompatibility(int entityA, int entityB)
        {
            var ismsA = world.GetComponent<IsmComponent>(entityA);
            var ismsB = world.GetComponent<IsmComponent>(entityB);

            string dominantIsmA = ismsA.GetDominantIsm();
            string dominantIsmB = ismsB.GetDominantIsm();

            if (dominantIsmA == null || dominantIsmB == null) return;

            bool isCompatible = IsPairCompatible(dominantIsmA, dominantIsmB);

            if (isCompatible)
            {
                var relA = world.GetComponent<RelationshipComponent>(entityA);
                var relB = world.GetComponent<RelationshipComponent>(entityB);

                // For now, let's just make them friends.
                // A more complex system could evolve this relationship type.
                relA.AddOrUpdateRelationship(entityB, RelationshipType.Friend, CompatibilityBonus);
                relB.AddOrUpdateRelationship(entityA, RelationshipType.Friend, CompatibilityBonus);

                GD.Print($"Compatibility found between {entityA} ({dominantIsmA}) and {entityB} ({dominantIsmB}). Friendship strength increasing.");
            }
        }

        private bool IsPairCompatible(string ismA, string ismB)
        {
            var compatibilityRules = _dataManager.Compatibility;

            // Check A -> B
            if (compatibilityRules.Contains(ismA))
            {
                if (compatibilityRules[ismA].ToString() == ismB)
                {
                    return true;
                }
            }

            // Check B -> A (for symmetric compatibility)
            if (compatibilityRules.Contains(ismB))
            {
                if (compatibilityRules[ismB].ToString() == ismA)
                {
                    return true;
                }
            }

            return false;
        }
    }
}