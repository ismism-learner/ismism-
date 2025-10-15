using Ecs.Components;
using Godot;
using Godot.Collections;
using Managers;

namespace Ecs.Systems
{
    public class NpcGenerationSystem : System
    {
        private DataManager _dataManager;
        private static readonly RandomNumberGenerator Rng = new();

        public override void Process()
        {
            // This system should only run once at the beginning.
            if (world.Time > 0)
            {
                Enabled = false;
                return;
            }

            if (_dataManager == null)
            {
                _dataManager = world.GetNode<DataManager>("/root/DataManager");
            }

            GenerateNpcsFromLocations();
        }

        private void GenerateNpcsFromLocations()
        {
            var locations = _dataManager.Locations;
            foreach (var locationData in locations)
            {
                var location = (Dictionary)locationData;
                if (!location.Contains("initial_population") || !location.Contains("founding_ideologies")) continue;

                var population = location["initial_population"].AsInt32();
                var ideologies = (Array<string>)location["founding_ideologies"];

                for (int i = 0; i < population; i++)
                {
                    CreateNpc(location, ideologies);
                }
            }
        }

        private void CreateNpc(Dictionary location, Array<string> foundingIdeologies)
        {
            var entityId = world.CreateEntity();
            var locationName = location["name"].ToString();
            var locationPosition = (Vector2)location["position"];

            world.AddComponent(entityId, new IdentityComponent { Name = $"Person from {locationName}" });
            world.AddComponent(entityId, new PositionComponent { Position = locationPosition });
            world.AddComponent(entityId, new StateComponent { CurrentState = "Idle" });
            world.AddComponent(entityId, new NeedsComponent { Hunger = Rng.RandfRange(0, 50), Stress = Rng.RandfRange(0, 50) });
            world.AddComponent(entityId, new FinancialComponent { Money = Rng.RandfRange(50, 200) });
            var villageManager = world.GetNode<VillageManager>("/root/VillageManager");

            // Assign to a house
            var homeBuildingId = location["id"].ToString();
            world.AddComponent(entityId, new HousingComponent { HomeBuildingName = homeBuildingId });
            var homeBuilding = villageManager.GetBuilding(homeBuildingId);
            if (homeBuilding != null)
            {
                homeBuilding.Occupants.Add((int)entityId);
            }

            // Assign to a workplace if the location is also a workplace
            if (location["type"].ToString() == "WORKPLACE")
            {
                world.AddComponent(entityId, new JobComponent { WorkplaceBuildingName = homeBuildingId });
            }

            var ismComponent = new IsmComponent();
            foreach (var ismId in foundingIdeologies)
            {
                ismComponent.AddIdeology(ismId, Rng.RandfRange(40, 80));
            }
            world.AddComponent(entityId, ismComponent);

            world.GetSystem<IdeologySystem>().RecalculateDecisionMatrix(entityId);

            GD.Print($"Generated NPC for {locationName} with ideologies: {string.Join(", ", foundingIdeologies)}");
        }
    }
}