public partial class JobComponent : Component
{
    public string WorkplaceBuildingName { get; set; }

    public JobComponent(string workplaceBuildingName)
    {
        WorkplaceBuildingName = workplaceBuildingName;
    }
}