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

                // Only process actions if the entity is idle and has demands
                if (state.CurrentState == "Idle" && needs.Demands.Count > 0)
                {
                    var demand = needs.Demands[0]; // Process the highest priority demand
                    var demandType = demand["type"].ToString();

                    GD.Print($"Entity {entityId} is acting on demand: {demandType}");

                    if (demandType == "EAT_FOOD")
                    {
                        // For simplicity, we assume the tavern is the only food source.
                        // A more complex system would search for the best/closest food source.
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
                            state.ActionData["on_arrival_action"] = "Work";
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
                            state.ActionData["on_arrival_action"] = "Sleep";
                            GD.Print($"Entity {entityId} is moving home to {locationData["name"]} to sleep.");
                        }
                    }

                    // Remove the processed demand
                    needs.Demands.RemoveAt(0);
                }
            }
        }
    }
}