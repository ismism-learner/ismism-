using Godot;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

public partial class VillageManager : Node
{
    public List<Building> Buildings { get; private set; } = new List<Building>();

    private class BuildingData
    {
        public string Name { get; set; }
        public string BuildingType { get; set; }
        public PositionData Position { get; set; }
    }

    private class PositionData
    {
        public float x { get; set; }
        public float y { get; set; }
    }

    public override void _Ready()
    {
        base._Ready();
        LoadBuildings("res://world_server/buildings.json");
    }

    private void LoadBuildings(string path)
    {
        using var file = FileAccess.Open(path, FileAccess.ModeFlags.Read);
        if (file == null)
        {
            GD.PushError($"Failed to open JSON file: {path}");
            return;
        }

        var content = file.GetAsText();

        try
        {
            var buildingsData = JsonSerializer.Deserialize<List<BuildingData>>(content);
            foreach (var bData in buildingsData)
            {
                var position = new Vector2(bData.Position.x, bData.Position.y);
                Buildings.Add(new Building(bData.Name, bData.BuildingType, position));
            }
            GD.Print($"Successfully loaded {Buildings.Count} buildings from {path}");
        }
        catch (JsonException e)
        {
            GD.PushError($"Failed to parse buildings JSON: {e.Message}");
        }
    }

    public Building GetBuilding(string name)
    {
        return Buildings.Find(b => b.Name == name);
    }

    public List<Building> GetBuildingsByType(string type)
    {
        return Buildings.FindAll(b => b.BuildingType == type);
    }

    public Building FindAvailableBuilding(string buildingType)
    {
        return Buildings.FirstOrDefault(b => b.BuildingType == buildingType && !b.IsFull());
    }
}