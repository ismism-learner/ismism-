namespace Ecs.Components
{
    /// <summary>
    /// Holds static character information that rarely changes.
    /// </summary>
    public class CharacterSheetComponent : Component
    {
        public string HomeLocationId { get; set; }
        public string WorkplaceLocationId { get; set; }
        public int WorkHoursStart { get; set; }
        public int WorkHoursEnd { get; set; }

        public CharacterSheetComponent(string homeLocationId, string workplaceLocationId, int workHoursStart, int workHoursEnd)
        {
            HomeLocationId = homeLocationId;
            WorkplaceLocationId = workplaceLocationId;
            WorkHoursStart = workHoursStart;
            WorkHoursEnd = workHoursEnd;
        }
    }
}