using Ecs.Components;
using Godot;
using Managers;
using System.Linq;

namespace Ecs.Systems
{
    public partial class GovernanceSystem : Ecs.System
    {
        private TownLedgerManager _ledger;
        private int _governorId = -1;

        public override void Process()
        {
            if (_ledger == null) _ledger = world.GetNode<TownLedgerManager>("/root/TownLedgerManager");
            if (_governorId == -1) FindGovernor();
            if (_governorId == -1) return;

            var goals = world.GetComponent<TownGoalsComponent>(_governorId);
            if (goals == null) return;

            // Check if the town's GDP meets the governor's target
            if (_ledger.CurrentTotalGdp < goals.TargetGdpAbsolute)
            {
                var gdpShortfall = goals.TargetGdpAbsolute - _ledger.CurrentTotalGdp;
                IssueDirectivesToCouncil(gdpShortfall);
            }
        }

        private void FindGovernor()
        {
            var governorEntity = world.GetEntitiesWithComponents(typeof(TownGoalsComponent)).FirstOrDefault();
            if (governorEntity != default)
            {
                _governorId = governorEntity;
            }
        }

        private void IssueDirectivesToCouncil(float gdpShortfall)
        {
            var councilMembers = world.GetEntitiesWithComponents(typeof(IdentityComponent))
                .Where(id => world.GetComponent<IdentityComponent>(id).Name.StartsWith("Councilor"));

            foreach (var councilorId in councilMembers)
            {
                var needs = world.GetComponent<NeedsComponent>(councilorId);
                // The directive to the council is to solve the GDP shortfall
                if (needs != null && !needs.Demands.Any(d => d["type"].ToString() == "ALLOCATE_PRODUCTION_TARGETS"))
                {
                    needs.Demands.Add(new Godot.Collections.Dictionary {
                        { "type", "ALLOCATE_PRODUCTION_TARGETS" },
                        { "gdp_shortfall", gdpShortfall }
                    });
                    GD.Print($"GOVERNANCE: Issued 'ALLOCATE_PRODUCTION_TARGETS' directive to Councilor {councilorId} for a shortfall of {gdpShortfall}.");
                }
            }
        }
    }
}