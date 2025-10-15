using System.Linq;
using Ecs.Components;
using Godot;
using Godot.Collections;
using System.Collections.Generic;

namespace Ecs.Systems
{
    public class ActionSystem : Ecs.System
    {
        public override void Process()
        {
            var entities = world.GetEntitiesWithComponents(
                typeof(NeedsComponent), typeof(StateComponent), typeof(CharacterSheetComponent), typeof(JobComponent)
            );

            foreach (var entityId in entities)
            {
                var state = world.GetComponent<StateComponent>(entityId);

                if (state.CurrentState == "EnforcingQuota")
                {
                    ProcessQuotaEnforcement(entityId, state);
                }
                else if (state.CurrentState == "Idle")
                {
                    ProcessIdle(entityId, state);
                }
                else if (state.CurrentState == "Working")
                {
                    ProcessWork(entityId, state);
                }
            }
        }

        private void ProcessIdle(int entityId, StateComponent state)
        {
            var needs = world.GetComponent<NeedsComponent>(entityId);
            if (needs.Demands.Count == 0) return;

            var bestAction = DecideNextAction(entityId, needs);
            if (bestAction == null) return;

            needs.Demands.Remove(bestAction);
            ExecuteAction(entityId, bestAction);
        }

        private void ProcessQuotaEnforcement(int managerId, StateComponent state)
        {
            var directive = (Dictionary)state.ActionData["directive"];
            float targetGdp = directive["gdp_target"].AsSingle();

            var relationships = world.GetComponent<RelationshipComponent>(managerId);
            var subordinates = relationships.Relationships.Values.Where(r => r.Type == RelationshipType.Follower).Select(r => r.TargetNpcId).ToList();

            float currentGdp = subordinates.Sum(id => world.GetComponent<FinancialComponent>(id).GdpContribution);

            if (currentGdp < targetGdp)
            {
                var managementSystem = world.GetSystem<ManagementSystem>();
                managementSystem.TryToExploit(managerId, subordinates);
            }
            else
            {
                state.CurrentState = "Idle";
            }
        }

        private void ProcessWork(int laborerId, StateComponent state)
        {
            var financial = world.GetComponent<FinancialComponent>(laborerId);
            financial.GdpContribution += 0.1f;
            financial.Money += 0.01f;
        }

        private Dictionary DecideNextAction(int entityId, NeedsComponent needs)
        {
            var sheet = world.GetComponent<CharacterSheetComponent>(entityId);
            return needs.Demands
                .Select(demand => new { Demand = demand, Score = CalculateUtilityScore(demand, sheet) })
                .OrderByDescending(x => x.Score)
                .FirstOrDefault()?.Demand;
        }

        private float CalculateUtilityScore(Dictionary demand, CharacterSheetComponent sheet)
        {
            var type = demand["type"].ToString();
            switch (type)
            {
                case "MEET_QUOTA": return 1000;
                case "WORK": return 100;
                default: return 0;
            }
        }

        private void ExecuteAction(int entityId, Dictionary demand)
        {
            var state = world.GetComponent<StateComponent>(entityId);
            var type = demand["type"].ToString();

            if (type == "MEET_QUOTA")
            {
                state.CurrentState = "EnforcingQuota";
                state.ActionData["directive"] = demand;
            }
            else if (type == "WORK")
            {
                // Simplified: Immediately start working. No movement.
                state.CurrentState = "Working";
            }
        }
    }
}