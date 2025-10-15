using Godot;
using System.Collections.Generic;

public partial class Building : Node
{
    public string Name { get; set; }
    public string BuildingType { get; set; }
    public Vector2 Position { get; set; }
    public List<int> Occupants { get; set; }

    public Building(string name, string buildingType, Vector2 position)
    {
        Name = name;
        BuildingType = buildingType;
        Position = position;
        Occupants = new List<int>();
    }
}