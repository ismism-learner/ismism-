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
                        var foodLocationId = _resourceManager.FindMostResourceRichLocation("FOOD");
                        if (!string.IsNullOrEmpty(foodLocationId))
                        {
                            var locationData = _resourceManager.GetLocation(foodLocationId);
                            var targetPosition = (Vector2)locationData["position"];

                            state.CurrentState = "Moving";
                            state.ActionData["target_position"] = targetPosition;
                            state.ActionData["on_arrival_action"] = "ConsumeFood";

                            GD.Print($"Entity {entityId} is moving to {foodLocationId} to eat.");
                        }
                    }
                    else if (demandType == "SEEK_ENTERTAINMENT")
                    {
                        // Logic to find an entertainment location would go here
                    }

                    // Remove the processed demand
                    needs.Demands.RemoveAt(0);
                }
            }
        }
    }
}