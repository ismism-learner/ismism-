using Godot;
using Godot.Collections;

namespace Managers
{
    /// <summary>
    /// Autoload singleton responsible for loading and providing access to all game data
    /// from JSON files.
    /// </summary>
    public partial class DataManager : Node
    {
        public Array<Dictionary> Locations { get; private set; }
        public Array<Dictionary> Interactions { get; private set; }
        public Dictionary Isms { get; private set; }
        public Array<Dictionary> ConsumerGoods { get; private set; }
        public Array<Dictionary> RelationshipTypes { get; private set; }

        public override void _Ready()
        {
            GD.Print("DataManager: Loading all game data...");
            LoadJsonData();
            GD.Print("DataManager: All data loaded.");
        }

        private void LoadJsonData()
        {
            Locations = LoadJsonFile("res://world_server/locations.json");
            Interactions = LoadJsonFile("res://world_server/interactions.json");
            ConsumerGoods = LoadJsonFile("res://world_server/consumer_goods.json");
            RelationshipTypes = LoadJsonFile("res://world_server/relationship_types.json");
            Isms = LoadSingleJsonFile("res://world_server/isms_final.json");
        }

        private Array<Dictionary> LoadJsonFile(string path)
        {
            using var file = FileAccess.Open(path, FileAccess.ModeFlags.Read);
            if (file == null)
            {
                GD.PushError($"Failed to open JSON file: {path}");
                return new Array<Dictionary>();
            }

            var content = file.GetAsText();
            var json = new Json();
            var error = json.Parse(content);
            if (error != Error.Ok)
            {
                GD.PushError($"Failed to parse JSON file: {path}. Error: {error}");
                return new Array<Dictionary>();
            }

            return (Array<Dictionary>)json.Data;
        }

        private Dictionary LoadSingleJsonFile(string path)
        {
            using var file = FileAccess.Open(path, FileAccess.ModeFlags.Read);
            if (file == null)
            {
                GD.PushError($"Failed to open JSON file: {path}");
                return new Dictionary();
            }

            var content = file.GetAsText();
            var json = new Json();
            var error = json.Parse(content);
            if (error != Error.Ok)
            {
                GD.PushError($"Failed to parse JSON file: {path}. Error: {error}");
                return new Dictionary();
            }

            return (Dictionary)json.Data;
        }
    }
}