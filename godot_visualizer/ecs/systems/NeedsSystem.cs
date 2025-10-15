using Ecs.Components;
using Godot;

namespace Ecs.Systems
{
    /// <summary>
    /// Updates entity needs over time and generates demands based on them.
    /// </summary>
    public class NeedsSystem : System
    {
        public override void Process()
        {
            var entities = world.GetEntitiesWithComponents(typeof(NeedsComponent), typeof(FinancialComponent));

            foreach (var entityId in entities)
            {
                var needs = world.GetComponent<NeedsComponent>(entityId);
                var financial = world.GetComponent<FinancialComponent>(entityId);

                // Basic needs decay over time
                needs.Hunger = Mathf.Min(needs.Hunger + 0.1f, 100);
                needs.Stress = Mathf.Min(needs.Stress + 0.05f, 100);

                // Stress increases with debt
                if (financial.Loans > 0)
                {
                    needs.Stress = Mathf.Min(needs.Stress + (financial.Loans / 1000.0f), 100);
                }

                // Generate demands based on needs thresholds
                if (needs.Stress > 80 && !HasDemand(needs, "type", "SEEK_ENTERTAINMENT"))
                {
                    needs.Demands.Add(new Godot.Collections.Dictionary { { "type", "SEEK_ENTERTAINMENT" } });
                    GD.Print($"Entity {entityId} is stressed and wants to find entertainment.");
                }

                if (needs.Hunger > 70 && !HasDemand(needs, "type", "EAT_FOOD"))
                {
                    needs.Demands.Add(new Godot.Collections.Dictionary { { "type", "EAT_FOOD" } });
                    GD.Print($"Entity {entityId} is hungry and wants to eat.");
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