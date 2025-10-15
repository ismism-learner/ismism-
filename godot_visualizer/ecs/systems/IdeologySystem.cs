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
        private const float DecayRate = 0.05f; // Strength lost per tick
        private const float DeathThreshold = 1.0f; // Strength below which an ideology is forgotten
        private const float ReinforcementStrength = 2.0f;
        private const float IxpGain = 1.0f;
        private const float BirthThreshold = 100.0f;

        public override void Process()
        {
            if (_dataManager == null)
            {
                _dataManager = world.GetNode<DataManager>("/root/DataManager");
            }

            var entities = world.GetEntitiesWithComponents(typeof(IsmComponent));
            foreach (var entityId in entities)
            {
                var ismComp = world.GetComponent<IsmComponent>(entityId);
                var ideologiesToRemove = new List<string>();

                var keys = new List<string>(ismComp.ActiveIdeologies.Keys);
                foreach (var ismId in keys)
                {
                    // Decay
                    ismComp.ActiveIdeologies[ismId] -= DecayRate;

                    // Death
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

                if (ideologiesToRemove.Count > 0)
                {
                    RecalculateDecisionMatrix(entityId);
                }
            }
        }

        public void AddIdeology(long entityId, string ismId, float initialStrength = 50.0f)
        {
            var ismComp = world.GetComponent<IsmComponent>(entityId);
            if (ismComp != null)
            {
                ismComp.AddIdeology(ismId, initialStrength);
                RecalculateDecisionMatrix(entityId);
            }
        }

        public void ProcessExperience(long entityId, Array<string> keywords)
        {
            var ismComp = world.GetComponent<IsmComponent>(entityId);
            if (ismComp == null || keywords == null) return;

            // Reinforcement
            foreach (var ismId in ismComp.ActiveIdeologies.Keys.ToList())
            {
                var ismData = (Dictionary)_dataManager.Isms[ismId];
                var ismKeywords = (Array<string>)ismData["keywords"];
                if (keywords.Any(k => ismKeywords.Contains(k)))
                {
                    ismComp.ActiveIdeologies[ismId] = Mathf.Min(100, ismComp.ActiveIdeologies[ismId] + ReinforcementStrength);
                }
            }

            // IXP Gain & Birth Check
            foreach (var keyword in keywords)
            {
                if (!ismComp.IdeologyExperiencePoints.ContainsKey(keyword))
                {
                    ismComp.IdeologyExperiencePoints[keyword] = 0;
                }
                ismComp.IdeologyExperiencePoints[keyword] += IxpGain;

                if (ismComp.IdeologyExperiencePoints[keyword] >= BirthThreshold)
                {
                    CheckForBirth(entityId, keyword);
                    ismComp.IdeologyExperiencePoints[keyword] = 0; // Reset after check
                }
            }

            RecalculateDecisionMatrix(entityId);
        }

        private void CheckForBirth(long entityId, string triggerKeyword)
        {
            var ismComp = world.GetComponent<IsmComponent>(entityId);
            var potentialChildren = _dataManager.GetChildIsms(triggerKeyword);
            if (potentialChildren.Count == 0) return;

            // Find the strongest parent ideology that matches the keyword
            string parentIsm = null;
            float maxStrength = 0;
            foreach (var ismId in ismComp.ActiveIdeologies.Keys)
            {
                var ismData = (Dictionary)_dataManager.Isms[ismId];
                var ismKeywords = (Array<string>)ismData["keywords"];
                if (ismKeywords.Contains(triggerKeyword) && ismComp.ActiveIdeologies[ismId] > maxStrength)
                {
                    maxStrength = ismComp.ActiveIdeologies[ismId];
                    parentIsm = ismId;
                }
            }

            if (parentIsm != null)
            {
                var childIsm = potentialChildren[0]; // Simplified: pick the first potential child
                if (!ismComp.ActiveIdeologies.ContainsKey(childIsm))
                {
                    float parentNewStrength = maxStrength / 2;
                    ismComp.ActiveIdeologies[parentIsm] = parentNewStrength;
                    AddIdeology(entityId, childIsm, parentNewStrength);
                    GD.Print($"Ideology '{childIsm}' has birthed from '{parentIsm}' for entity {entityId}!");
                }
            }
        }

        public void RecalculateDecisionMatrix(long entityId)
        {
            var ismComp = world.GetComponent<IsmComponent>(entityId);
            if (ismComp == null) return;

            var matrix = new float[4, 4];
            float totalStrength = 0;

            foreach (var (ismId, strength) in ismComp.ActiveIdeologies)
            {
                var ismData = (Dictionary)_dataManager.Isms[ismId];
                var weights = (Dictionary)ismData["quantized_data"];
                var field = (Array<float>)weights["field_theory"];

                for (int i = 0; i < 4; i++) matrix[0, i] += field[i] * strength;
                // ... and so on for other pillars
                totalStrength += strength;
            }

            if (totalStrength > 0)
            {
                for (int i = 0; i < 4; i++)
                {
                    for (int j = 0; j < 4; j++)
                    {
                        matrix[i, j] /= totalStrength;
                    }
                }
            }

            ismComp.FinalDecisionMatrix = matrix;
        }
    }
}