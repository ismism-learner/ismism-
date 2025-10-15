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
            var entities = world.GetEntitiesWithComponents(
                typeof(NeedsComponent),
                typeof(CharacterSheetComponent)
            );

            foreach (var entityId in entities)
            {
                var needs = world.GetComponent<NeedsComponent>(entityId);
                var sheet = world.GetComponent<CharacterSheetComponent>(entityId);

                // Basic needs decay over time
                needs.Hunger = Mathf.Min(needs.Hunger + 0.1f, 100);
                needs.Energy = Mathf.Max(needs.Energy - 0.05f, 0);

                // Check for work hours
                var currentHour = (world.Time / World.TicksPerHour) % 24;
                if (currentHour >= sheet.WorkHoursStart && currentHour < sheet.WorkHoursEnd)
                {
                    if (!HasDemand(needs, "type", "WORK"))
                    {
                        needs.Demands.Add(new Godot.Collections.Dictionary { { "type", "WORK" } });
                        GD.Print($"Entity {entityId} needs to work (it's work time).");
                    }
                }

                // Generate demands based on needs thresholds
                if (needs.Energy < 20 && !HasDemand(needs, "type", "SLEEP"))
                {
                    needs.Demands.Add(new Godot.Collections.Dictionary { { "type", "SLEEP" } });
                    GD.Print($"Entity {entityId} is tired and wants to sleep.");
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