namespace Ecs.Components
{
    public partial class TownGoalsComponent : Component
    {
        // Target: Increase the town's total GDP by this amount in the next cycle.
        public float TargetGdpAbsolute { get; set; } = 50000.0f;

        // Target: Keep the town's average grievance below this level.
        public float MaxAverageGrievance { get; set; } = 20.0f;
    }
}