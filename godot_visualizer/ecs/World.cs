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
        /// Retrieves a system of a specific type.
        /// </summary>
        public T GetSystem<T>() where T : System
        {
            return _systems.OfType<T>().FirstOrDefault();
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
    }
}