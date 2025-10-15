using Ecs.Components;
using Godot;
using Godot.Collections;
using Managers;

namespace Ecs.Systems
{
    public class NpcGenerationSystem : System
    {
        private DataManager _dataManager;
        private VillageManager _villageManager;
        private static readonly RandomNumberGenerator Rng = new();

        public override void Process()
        {
            // This system should only run once at the beginning.
            if (world.Time > 0)
            {
                Enabled = false;
                return;
            }

            if (_dataManager == null) _dataManager = world.GetNode<DataManager>("/root/DataManager");
            if (_villageManager == null) _villageManager = world.GetNode<VillageManager>("/root/VillageManager");

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
            // Find available housing and workplace BEFORE creating the entity
            var home = _villageManager.FindAvailableBuilding("House");
            if (home == null)
            {
                GD.PrintErr("Generation failed: No available houses for new NPC. Stopping population generation.");
                return; // Stop creating NPCs if there's no housing
            }

            var workplace = _villageManager.FindAvailableBuilding("Workshop");
            if (workplace == null)
            {
                GD.PrintErr("Generation failed: No available workplaces for new NPC. Stopping population generation.");
                return; // Stop creating NPCs if there are no jobs
            }

            var entityId = world.CreateEntity();
            var locationName = location["name"].ToString();
            var locationPosition = (Vector2)location["position"];

            world.AddComponent(entityId, new IdentityComponent { Name = $"Person from {locationName}" });
            world.AddComponent(entityId, new PositionComponent { Position = locationPosition });
            world.AddComponent(entityId, new StateComponent { CurrentState = "Idle" });
            world.AddComponent(entityId, new NeedsComponent { Hunger = Rng.RandfRange(0, 50), Stress = Rng.RandfRange(0, 50) });
            world.AddComponent(entityId, new FinancialComponent { Money = Rng.RandfRange(50, 200) });

            // Assign to the found home and workplace
            world.AddComponent(entityId, new HousingComponent { HomeBuildingName = home.Name });
            home.Occupants.Add((int)entityId);

            world.AddComponent(entityId, new JobComponent { WorkplaceBuildingName = workplace.Name });
            workplace.Occupants.Add((int)entityId);

            var ismComponent = new IsmComponent();
            foreach (var ismId in foundingIdeologies)
            {
                ismComponent.AddIdeology(ismId, Rng.RandfRange(40, 80));
            }
            world.AddComponent(entityId, ismComponent);

            world.GetSystem<IdeologySystem>().RecalculateDecisionMatrix(entityId);

            GD.Print($"Generated NPC for {locationName} and assigned to House: {home.Name}, Workplace: {workplace.Name}");
        }
    }
}