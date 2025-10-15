using Godot.Collections;

namespace Ecs.Components
{
    /// <summary>
    /// Represents the NPC's mind, containing their ideologies and decision matrix.
    /// </summary>
    public class IsmComponent : Component
    {
        // List of ideology IDs (e.g., "4-1-1-1")
        public Array<string> ActiveIdeologies { get; private set; }

        // A 4x4 matrix representing the NPC's worldview, derived from their ideologies.
        public float[,] FinalDecisionMatrix { get; set; }

        public IsmComponent()
        {
            ActiveIdeologies = new Array<string>();
            FinalDecisionMatrix = new float[4, 4];
            // Initialize with an identity matrix (neutral)
            for (int i = 0; i < 4; i++)
            {
                for (int j = 0; j < 4; j++)
                {
                    FinalDecisionMatrix[i, j] = (i == j) ? 1.0f : 0.0f;
                }
            }
        }

        public void AddIdeology(string ismId)
        {
            if (!ActiveIdeologies.Contains(ismId))
            {
                ActiveIdeologies.Add(ismId);
                // In a real implementation, we would now call a system
                // to recalculate the FinalDecisionMatrix.
            }
        }
    }
}