using Ecs.Components;
using Godot;

namespace Ecs.Systems
{
    public partial class ScheduleSystem : Ecs.System
    {
        public override void Process()
        {
            var entities = World.GetEntitiesWithComponents(typeof(JobComponent), typeof(HousingComponent), typeof(PositionComponent));

            foreach (var entityId in entities)
            {
                // Simple schedule: work during the day, home at night.
                // 8 AM to 5 PM is work time.
                var hour = (World.Time / World.TicksPerHour) % 24;

                if (hour >= 8 && hour < 17)
                {
                    // Go to work
                    var job = World.GetComponent<JobComponent>(entityId);
                    var villageManager = World.GetNode<VillageManager>("/root/VillageManager");
                    var workplace = villageManager.GetBuilding(job.WorkplaceBuildingName);
                    if (workplace != null)
                    {
                         // If not already moving, and not at the destination
                        if (!World.HasComponent<MoveToComponent>(entityId))
                        {
                            var position = World.GetComponent<PositionComponent>(entityId);
                            if (position.Position.DistanceTo(workplace.Position) > 10.0f)
                            {
                                World.AddComponent(entityId, new MoveToComponent(workplace.Position));
                            }
                        }
                    }
                }
                else
                {
                    // Go home
                    var housing = World.GetComponent<HousingComponent>(entityId);
                    var villageManager = World.GetNode<VillageManager>("/root/VillageManager");
                    var home = villageManager.GetBuilding(housing.HomeBuildingName);
                    if (home != null)
                    {
                        // If not already moving, and not at the destination
                        if (!World.HasComponent<MoveToComponent>(entityId))
                        {
                            var position = World.GetComponent<PositionComponent>(entityId);
                            if (position.Position.DistanceTo(home.Position) > 10.0f)
                            {
                                World.AddComponent(entityId, new MoveToComponent(home.Position));
                            }
                        }
                    }
                }
            }
        }
    }
}