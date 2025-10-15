using Godot;
using System.Collections.Generic;

public partial class Building : Node
{
    public string Name { get; set; }
    public string BuildingType { get; set; }
    public Vector2 Position { get; set; }
    public List<int> Occupants { get; set; }
    public int Capacity { get; set; }

    public Building(string name, string buildingType, Vector2 position)
    {
        Name = name;
        BuildingType = buildingType;
        Position = position;
        Occupants = new List<int>();

        // Set default capacity based on type
        if (BuildingType == "House")
        {
            Capacity = 2;
        }
        else if (BuildingType == "Workshop")
        {
            Capacity = 1;
        }
        else
        {
            Capacity = 1; // Default for any other type
        }
    }

    public bool IsFull()
    {
        return Occupants.Count >= Capacity;
    }
}