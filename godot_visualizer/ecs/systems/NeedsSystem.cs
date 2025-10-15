using Ecs.Components;
using Godot;
using Godot.Collections;
using Managers;

namespace Ecs.Systems
{
    public class NeedsSystem : System
    {
        private DataManager _dataManager;
        private const float IdeologyUrgeThreshold = 50.0f;
        private const float HighStressThreshold = 80.0f;

        public override void Process()
        {
            if (_dataManager == null)
            {
                _dataManager = world.GetNode<DataManager>("/root/DataManager");
            }

            var entities = world.GetEntitiesWithComponents(typeof(NeedsComponent), typeof(IsmComponent));

            foreach (var entityId in entities)
            {
                var needs = world.GetComponent<NeedsComponent>(entityId);

                // Store current stress before modification
                needs.PreviousStress = needs.Stress;

                // 1. Process Biological Needs
                needs.Hunger = Mathf.Min(needs.Hunger + 0.1f, 100);
                needs.Stress = Mathf.Min(needs.Stress + 0.05f, 100);

                // 2. Generate Demands
                if (needs.Stress > HighStressThreshold && !HasDemand(needs, "type", "SEEK_ENTERTAINMENT"))
                {
                    needs.Demands.Add(new Dictionary { { "type", "SEEK_ENTERTAINMENT" } });
                }
                if (needs.Hunger > 70 && !HasDemand(needs, "type", "EAT_FOOD"))
                {
                    needs.Demands.Add(new Dictionary { { "type", "EAT_FOOD" } });
                }

                // 3. Process Work Demands based on Schedule
                var identity = world.GetComponent<IdentityComponent>(entityId);
                if (identity.Name.StartsWith("Laborer"))
                {
                    var sheet = world.GetComponent<CharacterSheetComponent>(entityId);
                    var hour = (world.Time / 360) % 24; // Assuming TicksPerHour is 360
                    var workEndHour = 8 + (int)sheet.WorkHoursPerDay;

                    if (hour >= 8 && hour < workEndHour)
                    {
                        if (!HasDemand(needs, "type", "WORK"))
                        {
                            needs.Demands.Add(new Dictionary { { "type", "WORK" } });
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