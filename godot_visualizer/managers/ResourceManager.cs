using Godot;
using Godot.Collections;
using System.Linq;

namespace Managers
{
    /// <summary>
    /// Autoload singleton for managing global resources and location inventories.
    /// </summary>
    public partial class ResourceManager : Node
    {
        private Dictionary<string, Dictionary> _locationsById;

        public override void _Ready()
        {
            // We can't access other singletons in _Ready, so we defer this.
            Callable.From(() =>
            {
                var dataManager = GetNode<DataManager>("/root/DataManager");
                _locationsById = new Dictionary<string, Dictionary>();
                foreach (var loc in dataManager.Locations)
                {
                    // Make a mutable copy
                    var locCopy = loc.Duplicate(true);
                    if (!locCopy.Contains("inventory"))
                    {
                        locCopy["inventory"] = new Dictionary();
                    }
                    _locationsById[locCopy["id"].ToString()] = locCopy;
                }
                GD.Print("ResourceManager is ready.");
            }).CallDeferred();
        }

        public Dictionary GetLocation(string locationId)
        {
            return _locationsById.GetValueOrDefault(locationId);
        }

        public void Produce(string locationId, string resource, int amount)
        {
            var location = GetLocation(locationId);
            if (location == null) return;

            var inventory = (Dictionary)location["inventory"];
            var currentAmount = inventory.GetValueOrDefault(resource, 0).AsInt32();
            inventory[resource] = currentAmount + amount;
        }

        public bool Consume(string locationId, string resource, int amount)
        {
            var location = GetLocation(locationId);
            if (location == null) return false;

            var inventory = (Dictionary)location["inventory"];
            var currentAmount = inventory.GetValueOrDefault(resource, 0).AsInt32();

            if (currentAmount >= amount)
            {
                inventory[resource] = currentAmount - amount;
                return true;
            }
            return false;
        }

        public string FindMostResourceRichLocation(string resource)
        {
            string bestLocationId = null;
            int maxAmount = -1;

            foreach (var pair in _locationsById)
            {
                var inventory = (Dictionary)pair.Value["inventory"];
                var currentAmount = inventory.GetValueOrDefault(resource, 0).AsInt32();
                if (currentAmount > maxAmount)
                {
                    maxAmount = currentAmount;
                    bestLocationId = pair.Key;
                }
            }

            return bestLocationId;
        }
    }
}