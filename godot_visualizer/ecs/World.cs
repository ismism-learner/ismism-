using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using Ecs.Components;
using Godot.Collections;

namespace Ecs
{
    /// <summary>
    /// The core of the ECS framework. Manages all entities, components, and systems.
    /// Configured as an Autoload singleton in Godot, so it's globally accessible.
    /// </summary>
    public partial class World : Node
    {
        private long _nextEntityId = 0;
        private Dictionary<long, Dictionary<Type, Component>> _entities = new Dictionary<long, Dictionary<Type, Component>>();
        private List<System> _systems = new List<System>();

        // --- World State ---
        public int Time { get; private set; } = 0;
        public const int TicksPerHour = 60;

        public override void _Ready()
        {
            GD.Print("ECS World is ready.");
            LoadNpcs();
        }

        public override void _PhysicsProcess(double delta)
        {
            // This is the main simulation loop.
            Process();
        }

        /// <summary>
        /// Creates a new entity and returns its ID.
        /// </summary>
        public long CreateEntity()
        {
            long entityId = _nextEntityId++;
            _entities[entityId] = new Dictionary<Type, Component>();
            return entityId;
        }

        /// <summary>
        /// Adds a component instance to an entity.
        /// </summary>
        public void AddComponent<T>(long entityId, T component) where T : Component
        {
            _entities[entityId][typeof(T)] = component;
        }

        /// <summary>
        /// Retrieves a component instance for an entity.
        /// </summary>
        public T GetComponent<T>(long entityId) where T : Component
        {
            var components = _entities.GetValueOrDefault(entityId);
            if (components != null && components.TryGetValue(typeof(T), out var component))
            {
                return (T)component;
            }
            return null;
        }

        /// <summary>
        /// Checks if an entity has a specific component.
        /// </summary>
        public bool HasComponent<T>(long entityId) where T : Component
        {
            return _entities.ContainsKey(entityId) && _entities[entityId].ContainsKey(typeof(T));
        }

        /// <summary>
        /// Removes a component from an entity.
        /// </summary>
        public void RemoveComponent<T>(long entityId) where T : Component
        {
            if (HasComponent<T>(entityId))
            {
                _entities[entityId].Remove(typeof(T));
            }
        }

        /// <summary>
        /// Returns a list of all entities that have all the specified component types.
        /// </summary>
        public IEnumerable<long> GetEntitiesWithComponents(params Type[] componentTypes)
        {
            if (componentTypes == null || componentTypes.Length == 0)
            {
                return Enumerable.Empty<long>();
            }

            return _entities.Where(pair => componentTypes.All(type => pair.Value.ContainsKey(type)))
                            .Select(pair => pair.Key);
        }

        /// <summary>
        /// Adds a system to the world.
        /// </summary>
        public void AddSystem(System system)
        {
            system.SetWorld(this);
            _systems.Add(system);
        }

        /// <summary>
        /// Calls the Process method for all registered systems.
        /// </summary>
        private void Process()
        {
            foreach (var system in _systems)
            {
                system.Process();
            }
            Time++;
        }

        private void LoadNpcs()
        {
            GD.Print("Loading NPC database...");
            var path = "res://world_server/npc_database.json";
            using var file = FileAccess.Open(path, FileAccess.ModeFlags.Read);
            if (file == null)
            {
                GD.PushError($"Failed to open NPC database file: {path}");
                return;
            }

            var content = file.GetAsText();
            var json = new Json();
            if (json.Parse(content) != Error.Ok)
            {
                GD.PushError($"Failed to parse NPC database JSON: {json.GetErrorMessage()}");
                return;
            }

            var npcDataArray = (Array<Dictionary>)json.Data;
            GD.Print($"Found {npcDataArray.Count} NPCs in database.");

            var villageManager = GetNode<VillageManager>("/root/VillageManager");
            var houses = villageManager.GetBuildingsByType("House");
            var workplaces = villageManager.GetBuildingsByType("Workshop");
            int houseIndex = 0;
            int workplaceIndex = 0;

            foreach (var npcData in npcDataArray)
            {
                var entityId = CreateEntity();

                // Identity
                var identityData = (Dictionary)npcData["IdentityComponent"];
                AddComponent(entityId, new IdentityComponent(
                    identityData["name"].ToString(),
                    identityData["birthplace"].ToString(),
                    (Dictionary)identityData["biography"]
                ));

                // Position
                var positionData = (Array<float>)npcData["PositionComponent"];
                AddComponent(entityId, new PositionComponent(new Vector2(positionData[0], positionData[1])));

                // State
                AddComponent(entityId, new StateComponent());

                // Financial
                var financialData = (Dictionary)npcData["FinancialComponent"];
                AddComponent(entityId, new FinancialComponent(financialData["money"].AsFloat()));

                // Needs
                var needsData = (Dictionary)npcData["NeedsComponent"];
                AddComponent(entityId, new NeedsComponent(needsData["stress"].AsFloat(), needsData["hunger"].AsFloat()));

                // Ism
                var ismComp = new IsmComponent();
                var ismData = (Dictionary)npcData["IsmComponent"];
                var activeIsms = (Array<string>)ismData["active_ideologies"];
                foreach(var ism in activeIsms)
                {
                    ismComp.AddIdeology(ism);
                }
                AddComponent(entityId, ismComp);

                // Relationship
                AddComponent(entityId, new RelationshipComponent());

                // Hobby
                AddComponent(entityId, new HobbyComponent());

                // Housing and Job
                if (houses.Count > 0)
                {
                    var house = houses[houseIndex++ % houses.Count];
                    AddComponent(entityId, new HousingComponent(house.Name));
                    house.Occupants.Add((int)entityId);
                }

                if (workplaces.Count > 0)
                {
                    var workplace = workplaces[workplaceIndex++ % workplaces.Count];
                    AddComponent(entityId, new JobComponent(workplace.Name));
                    workplace.Occupants.Add((int)entityId);
                }
            }
            GD.Print("Finished loading NPCs.");
        }
    }
}