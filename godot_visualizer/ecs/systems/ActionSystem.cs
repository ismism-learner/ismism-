using Ecs.Components;
using Godot;
using Godot.Collections;
using Managers;

namespace Ecs.Systems
{
    /// <summary>
    /// Translates entity demands into concrete actions.
    /// </summary>
    public class ActionSystem : System
    {
        private ResourceManager _resourceManager;

        public override void Process()
        {
            if (_resourceManager == null)
            {
                _resourceManager = world.GetNode<ResourceManager>("/root/ResourceManager");
            }

            var entities = world.GetEntitiesWithComponents(typeof(NeedsComponent), typeof(StateComponent), typeof(PositionComponent));

            foreach (var entityId in entities)
            {
                var state = world.GetComponent<StateComponent>(entityId);
                var needs = world.GetComponent<NeedsComponent>(entityId);

                // Part 1: Act on demands if idle
                if (state.CurrentState == "Idle" && needs.Demands.Count > 0)
                {
                    ProcessDemands(entityId, state, needs);
                }
                // Part 2: Process ongoing actions
                else if (state.CurrentState == "Sleeping")
                {
                    needs.Energy = Mathf.Min(needs.Energy + 0.5f, 100); // Restore energy
                    if (needs.Energy >= 100) state.CurrentState = "Idle"; // Wake up when fully rested
                }
                else if (state.CurrentState == "Working")
                {
                    needs.Energy = Mathf.Max(needs.Energy - 0.2f, 0); // Consume energy
                    var financial = world.GetComponent<FinancialComponent>(entityId);
                    financial.Money += 0.1f; // Earn money
                }
                else if (state.CurrentState == "ConsumeFood")
                {
                    needs.Hunger = Mathf.Max(needs.Hunger - 1.0f, 0); // Satiate hunger
                    if (needs.Hunger <= 0) state.CurrentState = "Idle"; // Stop eating when full
                }
            }
        }

        private void ProcessDemands(long entityId, StateComponent state, NeedsComponent needs)
        {
            var demand = needs.Demands[0]; // Process the highest priority demand
            var demandType = demand["type"].ToString();

            GD.Print($"Entity {entityId} is acting on demand: {demandType}");

            if (demandType == "EAT_FOOD")
            {
                var foodLocationId = "tavern_1";
                var locationData = _resourceManager.GetLocation(foodLocationId);
                if (locationData != null)
                {
                    var targetPosition = (Vector2)locationData["position"];
                    state.CurrentState = "Moving";
                    state.ActionData["target_position"] = targetPosition;
                    state.ActionData["on_arrival_action"] = "ConsumeFood";
                    GD.Print($"Entity {entityId} is moving to {locationData["name"]} to eat.");
                }
            }
            else if (demandType == "WORK")
            {
                var sheet = world.GetComponent<CharacterSheetComponent>(entityId);
                var workLocationId = sheet.WorkplaceLocationId;
                var locationData = _resourceManager.GetLocation(workLocationId);
                if (locationData != null)
                {
                    var targetPosition = (Vector2)locationData["position"];
                    state.CurrentState = "Moving";
                    state.ActionData["target_position"] = targetPosition;
                    state.ActionData["on_arrival_action"] = "Working";
                    GD.Print($"Entity {entityId} is moving to their workplace: {locationData["name"]}.");
                }
            }
            else if (demandType == "SLEEP")
            {
                var sheet = world.GetComponent<CharacterSheetComponent>(entityId);
                var homeLocationId = sheet.HomeLocationId;
                var locationData = _resourceManager.GetLocation(homeLocationId);
                if (locationData != null)
                {
                    var targetPosition = (Vector2)locationData["position"];
                    state.CurrentState = "Moving";
                    state.ActionData["target_position"] = targetPosition;
                    state.ActionData["on_arrival_action"] = "Sleeping";
                    GD.Print($"Entity {entityId} is moving home to {locationData["name"]} to sleep.");
                }
            }

            needs.Demands.RemoveAt(0);
        }
    }
}