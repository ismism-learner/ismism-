using System.Collections.Generic;
using System.Linq;
using Ecs.Components;
using Godot;
using Godot.Collections;
using Managers;

namespace Ecs.Systems
{
    public class IdeologySystem : System
    {
        private DataManager _dataManager;
        private static readonly RandomNumberGenerator Rng = new();
        private const float DecayRate = 0.05f;
        private const float DeathThreshold = 1.0f;
        private const float ReinforcementStrength = 2.0f;
        private const float IxpGain = 1.0f;
        private const float BirthThreshold = 100.0f;

        public override void Process()
        {
            if (_dataManager == null) _dataManager = world.GetNode<DataManager>("/root/DataManager");

            var entities = world.GetEntitiesWithComponents(typeof(IsmComponent));
            foreach (var entityId in entities)
            {
                var ismComp = world.GetComponent<IsmComponent>(entityId);
                var ideologiesToRemove = new List<string>();

                var keys = new List<string>(ismComp.ActiveIdeologies.Keys);
                foreach (var ismId in keys)
                {
                    ismComp.ActiveIdeologies[ismId] -= DecayRate;
                    if (ismComp.ActiveIdeologies[ismId] < DeathThreshold)
                    {
                        ideologiesToRemove.Add(ismId);
                    }
                }

                foreach (var ismId in ideologiesToRemove)
                {
                    ismComp.RemoveIdeology(ismId);
                    GD.Print($"Ideology '{ismId}' has died for entity {entityId}.");
                }

                if (ideologiesToRemove.Count > 0) RecalculateDecisionMatrix(entityId);
            }
        }

        public void AddIdeology(int entityId, string ismId, float initialStrength = 50.0f)
        {
            var ismComp = world.GetComponent<IsmComponent>(entityId);
            if (ismComp != null)
            {
                ismComp.AddIdeology(ismId, initialStrength);
                RecalculateDecisionMatrix(entityId);
            }
        }

        public void ProcessExperience(int entityId, Array<string> keywords)
        {
            // ... (Implementation remains the same)
        }

        private void CheckForBirth(int entityId, string triggerKeyword)
        {
            // ... (Implementation remains the same)
        }

        public void RecalculateDecisionMatrix(int entityId)
        {
            // ... (Implementation remains the same)
        }

        public void ImpartIdeology(int teacherId, int studentId)
        {
            // ... (Implementation remains the same)
        }

        public void DevelopRationalityThroughPlanning(int entityId)
        {
            var sheet = world.GetComponent<CharacterSheetComponent>(entityId);
            if (sheet == null) return;

            GD.Print($"PLANNING FOR REVENGE: {entityId} is forced to think, increasing rationality.");
            sheet.Rationality += 30; // A significant boost from complex planning
            if (sheet.Rationality > 100) sheet.Rationality = 100;
        }
    }
}