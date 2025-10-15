using Godot.Collections;

namespace Ecs.Components
{
    /// <summary>
    /// Represents the NPC's mind, containing their ideologies and decision matrix.
    /// </summary>
    public class IsmComponent : Component
    {
        // Dictionary of ideology IDs to their current strength (0-100)
        public Dictionary<string, float> ActiveIdeologies { get; private set; }

        // Tracks experience points (IXP) towards birthing new ideologies.
        // The key could be an ideology pillar or a keyword.
        public Dictionary<string, float> IdeologyExperiencePoints { get; private set; }

        // A 4x4 matrix representing the NPC's worldview, derived from their ideologies.
        public float[,] FinalDecisionMatrix { get; set; }

        public IsmComponent()
        {
            ActiveIdeologies = new Dictionary<string, float>();
            IdeologyExperiencePoints = new Dictionary<string, float>();
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

        public void AddIdeology(string ismId, float initialStrength = 50.0f)
        {
            if (!ActiveIdeologies.ContainsKey(ismId))
            {
                ActiveIdeologies[ismId] = initialStrength;
            }
        }

        public void RemoveIdeology(string ismId)
        {
            if (ActiveIdeologies.ContainsKey(ismId))
            {
                ActiveIdeologies.Remove(ismId);
            }
        }
    }
}