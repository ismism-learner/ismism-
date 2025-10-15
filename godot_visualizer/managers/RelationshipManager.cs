using Godot;
using Ecs;
using Ecs.Components;
using Godot.Collections;

namespace Managers
{
    /// <summary>
    /// Autoload singleton for managing NPC relationships.
    /// </summary>
    public partial class RelationshipManager : Node
    {
        private DataManager _dataManager;
        private World _world;

        public override void _Ready()
        {
            Callable.From(() =>
            {
                _dataManager = GetNode<DataManager>("/root/DataManager");
                _world = GetNode<World>("/root/World");
                GD.Print("RelationshipManager is ready.");
            }).CallDeferred();
        }

        public void UpdateRelationship(long entity1, long entity2, string interactionKeyword)
        {
            var relComp1 = _world.GetComponent<RelationshipComponent>(entity1);
            var relComp2 = _world.GetComponent<RelationshipComponent>(entity2);
            if (relComp1 == null || relComp2 == null) return;

            // Ensure relationship entries exist for both entities
            if (!relComp1.Relations.ContainsKey(entity2))
            {
                relComp1.Relations[entity2] = new Dictionary { { "affinity", 0.0f }, { "status", "" } };
            }
            if (!relComp2.Relations.ContainsKey(entity1))
            {
                relComp2.Relations[entity1] = new Dictionary { { "affinity", 0.0f }, { "status", "" } };
            }

            var relationshipData = relComp1.Relations[entity2];

            foreach (var typeDef in _dataManager.RelationshipTypes)
            {
                var conditions = (Dictionary)typeDef["conditions"];
                var requiredKeyword = conditions.GetValueOrDefault("interaction_keyword", "").ToString();

                if (requiredKeyword == interactionKeyword)
                {
                    var currentAffinity = relationshipData["affinity"].AsFloat();
                    var minAffinity = conditions.GetValueOrDefault("min_affinity", -101.0f).AsFloat();
                    var maxAffinity = conditions.GetValueOrDefault("max_affinity", 101.0f).AsFloat();

                    if (currentAffinity >= minAffinity && currentAffinity <= maxAffinity)
                    {
                        var newStatus = typeDef["name"].ToString();
                        GD.Print($"Updating relationship between {entity1} and {entity2} to: {newStatus}");
                        relationshipData["status"] = newStatus;
                        // Also update the other entity's perspective
                        relComp2.Relations[entity1]["status"] = newStatus;
                        break;
                    }
                }
            }
        }
    }
}