public partial class HousingComponent : Component
{
    public string HomeBuildingName { get; set; }

    public HousingComponent(string homeBuildingName)
    {
        HomeBuildingName = homeBuildingName;
    }
}