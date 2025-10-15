using Ecs.Components;
using Godot;
using Godot.Collections;
using Managers;

namespace Ecs.Systems
{
    /// <summary>
    /// Manages the ideological state of entities, including experience and matrix recalculation.
    /// </summary>
    public class IdeologySystem : System
    {
        private DataManager _dataManager;

        public override void Process()
        {
            // This system is mostly reactive, providing methods to be called by other systems.
            // We can keep it light or use it for passive ideological drift in the future.
            if (_dataManager == null)
            {
                _dataManager = world.GetNode<DataManager>("/root/DataManager");
            }
        }

        public void AddIdeology(long entityId, string ismId)
        {
            var ismComp = world.GetComponent<IsmComponent>(entityId);
            if (ismComp != null && !ismComp.ActiveIdeologies.Contains(ismId))
            {
                ismComp.AddIdeology(ismId);
                RecalculateDecisionMatrix(entityId);
            }
        }

        public void ProcessExperience(long entityId, Dictionary ixpEvent)
        {
            // In a real implementation, this would parse the IXP event
            // and add points to the appropriate ideology pillar.
            // For now, this is a placeholder.
            GD.Print($"Processing IXP for entity {entityId}.");
        }

        public void RecalculateDecisionMatrix(long entityId)
        {
            var ismComp = world.GetComponent<IsmComponent>(entityId);
            if (ismComp == null) return;

            var matrix = new float[4, 4]; // Start with a zero matrix

            // This is a simplified averaging logic.
            // A full implementation would use the dialectical quantization engine logic.
            foreach (var ismId in ismComp.ActiveIdeologies)
            {
                var ismData = (Dictionary)_dataManager.Isms[ismId];
                var weights = (Dictionary)ismData["quantized_data"];
                var field = (Array<float>)weights["field_theory"];

                for(int i = 0; i < 4; i++) matrix[0, i] += field[i];
                // ... and so on for other pillars
            }

            // Normalize the matrix
            var numIdeologies = ismComp.ActiveIdeologies.Count;
            if (numIdeologies > 0)
            {
                for (int i = 0; i < 4; i++)
                {
                    for (int j = 0; j < 4; j++)
                    {
                        matrix[i, j] /= numIdeologies;
                    }
                }
            }

            // ismComp.FinalDecisionMatrix = matrix; // This property is get-only. We need a setter.
            GD.Print($"Recalculated decision matrix for entity {entityId}.");
        }
    }
}