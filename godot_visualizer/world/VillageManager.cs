using Godot;
using System.Collections.Generic;

public partial class VillageManager : Node
{
    public List<Building> Buildings { get; private set; } = new List<Building>();

    public override void _Ready()
    {
        base._Ready();
        GenerateVillage();
    }

    private void GenerateVillage()
    {
        // For now, let's create a few simple buildings.
        // We can expand this later to be more procedural.
        Buildings.Add(new Building("Blacksmith", "Workshop", new Vector2(100, 150)));
        Buildings.Add(new Building("Bakery", "Workshop", new Vector2(250, 100)));
        Buildings.Add(new Building("House 1", "House", new Vector2(100, 300)));
        Buildings.Add(new Building("House 2", "House", new Vector2(250, 300)));
        Buildings.Add(new Building("House 3", "House", new Vector2(400, 300)));
    }

    public Building GetBuilding(string name)
    {
        return Buildings.Find(b => b.Name == name);
    }

    public List<Building> GetBuildingsByType(string type)
    {
        return Buildings.FindAll(b => b.BuildingType == type);
    }
}