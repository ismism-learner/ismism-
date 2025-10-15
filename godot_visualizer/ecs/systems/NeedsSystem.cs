using Ecs.Components;
using Godot;
using Godot.Collections;
using Managers;

namespace Ecs.Systems
{
    /// <summary>
    /// Updates entity needs over time and generates demands and ideology-driven urges.
    /// </summary>
    public class NeedsSystem : System
    {
        private DataManager _dataManager;
        private const float IdeologyUrgeThreshold = 50.0f;

        public override void Process()
        {
            if (_dataManager == null)
            {
                _dataManager = world.GetNode<DataManager>("/root/DataManager");
            }

            var entities = world.GetEntitiesWithComponents(typeof(NeedsComponent), typeof(IsmComponent), typeof(FinancialComponent));

            foreach (var entityId in entities)
            {
                var needs = world.GetComponent<NeedsComponent>(entityId);
                var financial = world.GetComponent<FinancialComponent>(entityId);

                // 1. Process Biological Needs
                needs.Hunger = Mathf.Min(needs.Hunger + 0.1f, 100);
                needs.Stress = Mathf.Min(needs.Stress + 0.05f, 100);
                if (financial.Loans > 0)
                {
                    needs.Stress = Mathf.Min(needs.Stress + (financial.Loans / 1000.0f), 100);
                }

                if (needs.Stress > 80 && !HasDemand(needs, "type", "SEEK_ENTERTAINMENT"))
                {
                    needs.Demands.Add(new Dictionary { { "type", "SEEK_ENTERTAINMENT" } });
                }
                if (needs.Hunger > 70 && !HasDemand(needs, "type", "EAT_FOOD"))
                {
                    needs.Demands.Add(new Dictionary { { "type", "EAT_FOOD" } });
                }

                // 2. Process Ideological Urges
                var ismComp = world.GetComponent<IsmComponent>(entityId);
                foreach (var (ismId, strength) in ismComp.ActiveIdeologies)
                {
                    if (strength > IdeologyUrgeThreshold)
                    {
                        var ismData = (Dictionary)_dataManager.Isms[ismId];
                        var keywords = (Array<string>)ismData["keywords"];

                        if (keywords.Contains("ART") && !HasDemand(needs, "type", "CREATE_ART"))
                        {
                            needs.Demands.Add(new Dictionary { { "type", "CREATE_ART" } });
                            GD.Print($"Entity {entityId} feels an urge to create art from ideology {ismId}.");
                        }
                        if (keywords.Contains("WORK") && !HasDemand(needs, "type", "WORK"))
                        {
                            needs.Demands.Add(new Dictionary { { "type", "WORK" } });
                            GD.Print($"Entity {entityId} feels an urge to work from ideology {ismId}.");
                        }
                    }
                }
            }
        }

        private bool HasDemand(NeedsComponent needs, string key, string value)
        {
            foreach (var demand in needs.Demands)
            {
                if (demand.Contains(key) && demand[key].ToString() == value)
                {
                    return true;
                }
            }
            return false;
        }
    }
}