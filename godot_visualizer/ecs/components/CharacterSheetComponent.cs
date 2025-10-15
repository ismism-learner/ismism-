namespace Ecs.Components
{
    public partial class CharacterSheetComponent : Component
    {
        // The number of hours this NPC is required to work each day.
        public float WorkHoursPerDay { get; set; } = 8.0f;

        // Physical health, from 0 to 100.
        public float Health { get; set; } = 100.0f;

        // The drive to act on impulse and emotion. (0-100)
        public float Passion { get; set; } = 50.0f;

        // The ability to plan and delay gratification. (0-100)
        public float Rationality { get; set; } = 50.0f;

        // A measure of dissatisfaction from being exploited. (0-100)
        public float Grievance { get; set; } = 0.0f;

        // The individual's physical fighting ability. (0-100)
        public float MartialProwess { get; set; } = 10.0f;
    }
}