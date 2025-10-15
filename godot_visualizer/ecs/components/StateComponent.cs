using Godot.Collections;

namespace Ecs.Components
{
    /// <summary>
    /// Stores the current state and action data of an entity.
    /// </summary>
    public partial class StateComponent : Component
    {
        public string CurrentState { get; set; } // e.g., "Idle", "Working", "Moving"
        public Dictionary ActionData { get; set; } // e.g., target_entity, target_location
        public int LastInteractionTime { get; set; } = -1000; // Initialize to allow immediate interaction

        public StateComponent(string initialState = "Idle")
        {
            CurrentState = initialState;
            ActionData = new Dictionary();
        }
    }
}