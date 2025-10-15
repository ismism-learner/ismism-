using Godot;
using Godot.Collections;
using System.Linq;

namespace Managers
{
    /// <summary>
    /// Autoload singleton responsible for procedurally generating NPC properties
    /// like biography and mind.
    /// </summary>
    public partial class GeneratorManager : Node
    {
        private DataManager _dataManager;

        public override void _Ready()
        {
            Callable.From(() =>
            {
                _dataManager = GetNode<DataManager>("/root/DataManager");
                GD.Print("GeneratorManager is ready.");
            }).CallDeferred();
        }

        /// <summary>
        /// Generates a biography for an NPC based on their birthplace.
        /// </summary>
        public Dictionary GenerateBiography(string birthplaceId)
        {
            var biography = new Dictionary
            {
                { "social_class", "Peasant" },
                { "education", "None" },
                { "defining_event", "The Great Famine" }
            };

            // In a real implementation, this would be more complex,
            // using data from the birthplace location to influence the outcome.
            // For now, it's a direct translation of the simple Python placeholder.
            return biography;
        }

        /// <summary>
        /// Generates an ideological profile (IsmComponent) for an NPC.
        /// </summary>
        public Dictionary GenerateMind(Dictionary biography, string birthplaceId)
        {
            // This is a simplified placeholder logic.
            // A full implementation would query region data and filter based on biography.
            var mind = new Dictionary
            {
                { "primary_ism", "4-1-1-1" }, // Default starting 'ism'
                { "secondary_ism", "3-2-1" },
                { "conflicting_ism", "2-1" }
            };
            return mind;
        }
    }
}