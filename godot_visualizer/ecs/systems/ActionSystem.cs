using System.Linq;
using Ecs.Components;
using Godot;
using Godot.Collections;
using Managers;

namespace Ecs.Systems
{
    /// <summary>
    /// Translates entity demands into concrete actions using a utility-based decision model.
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

            var entities = world.GetEntitiesWithComponents(typeof(NeedsComponent), typeof(StateComponent), typeof(PositionComponent), typeof(IsmComponent));

            foreach (var entityId in entities)
            {
                var state = world.GetComponent<StateComponent>(entityId);
                if (state.CurrentState != "Idle") continue;

                var needs = world.GetComponent<NeedsComponent>(entityId);
                if (needs.Demands.Count == 0) continue;

                var bestAction = DecideNextAction(entityId);
                if (bestAction == null) continue;

                var demandType = bestAction["type"].ToString();
                GD.Print($"Entity {entityId} decided to act on demand: {demandType}");

                ExecuteAction(entityId, demandType);

                // Remove the fulfilled demand
                needs.Demands.Remove(bestAction);
            }
        }

        private Dictionary DecideNextAction(long entityId)
        {
            var needs = world.GetComponent<NeedsComponent>(entityId);
            var isms = world.GetComponent<IsmComponent>(entityId);

            Dictionary bestDemand = null;
            float maxScore = -1f;

            foreach (var demand in needs.Demands)
            {
                float score = CalculateUtilityScore(demand, needs, isms);
                if (score > maxScore)
                {
                    maxScore = score;
                    bestDemand = demand;
                }
            }
            return bestDemand;
        }

        private float CalculateUtilityScore(Dictionary demand, NeedsComponent needs, IsmComponent isms)
        {
            var type = demand["type"].ToString();
            switch (type)
            {
                case "EAT_FOOD":
                    return needs.Hunger; // Score is directly proportional to hunger level
                case "SEEK_ENTERTAINMENT":
                    return needs.Stress; // Score is proportional to stress level
                case "WORK":
                case "CREATE_ART":
                    // Ideological urges are weighted by the strength of the corresponding ideology
                    return isms.ActiveIdeologies.Values.Max(); // Simplified: use the strongest ideology's strength
                default:
                    return 0f;
            }
        }

        private void ExecuteAction(long entityId, string demandType)
        {
            var state = world.GetComponent<StateComponent>(entityId);
            var ideologySystem = world.GetSystem<IdeologySystem>();

            if (demandType == "EAT_FOOD")
            {
                var foodLocationId = _resourceManager.FindMostResourceRichLocation("FOOD");
                if (string.IsNullOrEmpty(foodLocationId)) return;

                var locationData = _resourceManager.GetLocation(foodLocationId);
                state.ActionData["target_position"] = (Vector2)locationData["position"];
                state.ActionData["on_arrival_action"] = "ConsumeFood";
                state.CurrentState = "Moving";

                ideologySystem.ProcessExperience(entityId, new Array<string> { "CONSUMPTION", "SURVIVAL" });
            }
            else if (demandType == "WORK")
            {
                var job = world.GetComponent<JobComponent>(entityId);
                if (job == null || string.IsNullOrEmpty(job.WorkplaceBuildingName)) return;

                var workplace = _resourceManager.GetLocation(job.WorkplaceBuildingName);
                state.ActionData["target_position"] = (Vector2)workplace["position"];
                state.ActionData["on_arrival_action"] = "DoWork";
                state.CurrentState = "Moving";

                ideologySystem.ProcessExperience(entityId, new Array<string> { "WORK", "LABOR", "DUTY" });
            }
            else if (demandType == "CREATE_ART")
            {
                var housing = world.GetComponent<HousingComponent>(entityId);
                if (housing == null || string.IsNullOrEmpty(housing.HomeBuildingName)) return;

                var home = _resourceManager.GetLocation(housing.HomeBuildingName);
                state.ActionData["target_position"] = (Vector2)home["position"];
                state.ActionData["on_arrival_action"] = "DoArt";
                state.CurrentState = "Moving";

                ideologySystem.ProcessExperience(entityId, new Array<string> { "ART", "AESTHETICS", "CREATION" });
            }
        }
    }
}