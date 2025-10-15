using Ecs.Components;
using Godot;
using System.Linq;

namespace Managers
{
    public partial class TownLedgerManager : Node
    {
        public float CurrentAverageGrievance { get; private set; }
        public float CurrentTotalGdp { get; private set; }

        public override void _Process(double delta)
        {
            var world = GetNode<Ecs.World>("/root/World");
            if (world == null) return;

            var laborers = world.GetEntitiesWithComponents(typeof(CharacterSheetComponent), typeof(FinancialComponent))
                .Where(id => world.GetComponent<IdentityComponent>(id).Name.StartsWith("Laborer"))
                .ToList();

            if (laborers.Count > 0)
            {
                CurrentAverageGrievance = laborers.Average(id => world.GetComponent<CharacterSheetComponent>(id).Grievance);
                CurrentTotalGdp = laborers.Sum(id => world.GetComponent<FinancialComponent>(id).GdpContribution);
            }
        }
    }
}