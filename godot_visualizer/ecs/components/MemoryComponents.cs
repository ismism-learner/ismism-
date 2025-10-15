using Godot.Collections;

namespace Ecs.Components
{
    /// <summary>
    /// Logs raw sensory events (e.g., "saw another NPC").
    /// </summary>
    public class SensoryLogComponent : Component
    {
        public Array<Dictionary> Log { get; set; } = new Array<Dictionary>();
    }

    /// <summary>
    /// Records social interactions and their outcomes.
    /// </summary>
    public class SocialLedgerComponent : Component
    {
        public Array<Dictionary> Ledger { get; set; } = new Array<Dictionary>();
    }

    /// <summary>
    /// Stores information about locations and the resources/entities within them.
    /// </summary>
    public class CognitiveMapComponent : Component
    {
        public Dictionary<string, Array<long>> LocationEntityMap { get; set; } = new Dictionary<string, Array<long>>();
    }

    /// <summary>
    /// Records the NPC's own actions and their results, forming a basis for future planning.
    /// </summary>
    public class PraxisLedgerComponent : Component
    {
        public Array<Dictionary> Ledger { get; set; } = new Array<Dictionary>();
    }
}