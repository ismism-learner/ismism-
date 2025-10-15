using Ecs.Components;
using Godot.Collections;
using System.Linq;

namespace Ecs.Systems
{
    public partial class GoalGenerationSystem : Ecs.System
    {
        private const float HighRationalityThreshold = 60.0f;

        public override void Process()
        {
            var entities = world.GetEntitiesWithComponents(
                typeof(CharacterSheetComponent),
                typeof(NeedsComponent),
                typeof(RelationshipComponent)
            );

            foreach (var entityId in entities)
            {
                var sheet = world.GetComponent<CharacterSheetComponent>(entityId);
                if (sheet.Rationality < HighRationalityThreshold) continue;

                var needs = world.GetComponent<NeedsComponent>(entityId);

                GenerateGoals(entityId, sheet, needs);
            }
        }

        private void GenerateGoals(int entityId, CharacterSheetComponent sheet, NeedsComponent needs)
        {
            // Goal: Recruit followers if you are a leader type and have no followers
            if (world.GetComponent<IsmComponent>(entityId)?.GetDominantIsm()?.StartsWith("2") == true)
            {
                var relationships = world.GetComponent<RelationshipComponent>(entityId);
                bool hasFollowers = relationships.Relationships.Values.Any(r => r.Type == RelationshipType.Follower);
                if (!hasFollowers && !HasDemand(needs, "type", "RECRUIT_FOLLOWERS"))
                {
                    needs.Demands.Add(new Dictionary { { "type", "RECRUIT_FOLLOWERS" } });
                    Godot.GD.Print($"GOAL: Entity {entityId} has generated a goal to RECRUIT_FOLLOWERS.");
                }
            }

            // Goal: Increase free time if work hours are high
            if (sheet.WorkHoursPerDay > 10 && !HasDemand(needs, "type", "INCREASE_FREE_TIME"))
            {
                needs.Demands.Add(new Dictionary { { "type", "INCREASE_FREE_TIME" } });
                Godot.GD.Print($"GOAL: Entity {entityId} has generated a goal to INCREASE_FREE_TIME.");
            }

            // Goal: Improve health if it's low
            if (sheet.Health < 40 && !HasDemand(needs, "type", "IMPROVE_HEALTH"))
            {
                needs.Demands.Add(new Dictionary { { "type", "IMPROVE_HEALTH" } });
                 Godot.GD.Print($"GOAL: Entity {entityId} has generated a goal to IMPROVE_HEALTH.");
            }
        }

        private bool HasDemand(NeedsComponent needs, string key, string value)
        {
            return needs.Demands.Any(d => d.Contains(key) && d[key].ToString() == value);
        }
    }
}