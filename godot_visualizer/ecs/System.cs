namespace Ecs
{
    /// <summary>
    /// The base class for all systems in the ECS.
    /// Systems contain the logic that operates on entities with specific components.
    /// </summary>
    public abstract class System
    {
        // The world instance will be set by the World object when the system is added.
        protected World world;

        public void SetWorld(World world)
        {
            this.world = world;
        }

        /// <summary>
        /// This method will be called by the World on each simulation tick.
        /// Subclasses must implement their logic here.
        /// </summary>
        public abstract void Process();
    }
}