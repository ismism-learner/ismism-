using Ecs.Components;
using Godot;
using System.Linq;

namespace Ecs.Systems
{
    public partial class PlanningSystem : Ecs.System
    {
        public override void Process()
        {
            var councilMembers = world.GetEntitiesWithComponents(typeof(IdentityComponent), typeof(NeedsComponent))
                .Where(id => world.GetComponent<IdentityComponent>(id).Name.StartsWith("Councilor"));

            foreach (var councilorId in councilMembers)
            {
                var needs = world.GetComponent<NeedsComponent>(councilorId);
                var directive = needs.Demands.FirstOrDefault(d => d["type"].ToString() == "ALLOCATE_PRODUCTION_TARGETS");

                if (directive != null)
                {
                    float totalShortfall = directive["gdp_shortfall"].AsSingle();
                    DistributeTargetsToManagers(councilorId, totalShortfall);
                    needs.Demands.Remove(directive);
                }
            }
        }

        private void DistributeTargetsToManagers(int councilorId, float totalShortfall)
        {
            var councilorRels = world.GetComponent<RelationshipComponent>(councilorId);
            var managers = councilorRels.Relationships.Values
                .Where(r => r.Type == RelationshipType.Follower)
                .Select(r => r.TargetNpcId)
                .ToList();

            if (managers.Count == 0) return;

            float individualTarget = totalShortfall / managers.Count;

            foreach (var managerId in managers)
            {
                var managerNeeds = world.GetComponent<NeedsComponent>(managerId);
                if (managerNeeds != null && !managerNeeds.Demands.Any(d => d["type"].ToString() == "MEET_QUOTA"))
                {
                    managerNeeds.Demands.Add(new Godot.Collections.Dictionary {
                        { "type", "MEET_QUOTA" },
                        { "gdp_target", individualTarget }
                    });
                    GD.Print($"PLANNING: Councilor {councilorId} assigned Manager {managerId} a GDP target of {individualTarget}.");
                }
            }
        }
    }
}