namespace Ecs.Components
{
    public enum TraumaType
    {
        Betrayal, // e.g., lover left for someone else
        Loss,     // e.g., mentor or loved one died
        Injustice // e.g., wrongfully punished by a faction
    }

    public partial class ProfoundTraumaComponent : Component
    {
        public TraumaType Type { get; set; }

        // Can be an individual NPC ID or a faction/group ID in the future
        public string PerpetratorId { get; set; }

        public ProfoundTraumaComponent(TraumaType type, string perpetratorId)
        {
            Type = type;
            PerpetratorId = perpetratorId;
        }
    }
}