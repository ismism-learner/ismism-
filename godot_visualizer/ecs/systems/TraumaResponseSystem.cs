using Ecs.Components;
using Godot;
using Godot.Collections;

namespace Ecs.Systems
{
    public partial class TraumaResponseSystem : Ecs.System
    {
        public override void Process()
        {
            var entities = world.GetEntitiesWithComponents(typeof(ProfoundTraumaComponent), typeof(IsmComponent), typeof(NeedsComponent));

            foreach (var entityId in entities)
            {
                var isms = world.GetComponent<IsmComponent>(entityId);

                // If already on the path of revenge, do nothing.
                if (isms.GetDominantIsm() == "1444") continue;

                GD.Print($"TRAUMA RESPONSE: Entity {entityId} is processing their trauma.");

                // 1. Force the revenge ideology
                var ideologySystem = world.GetSystem<IdeologySystem>();
                ideologySystem.AddIdeology(entityId, "1444", 95.0f); // Make it dominant

                // 2. Generate the overarching revenge demand
                var needs = world.GetComponent<NeedsComponent>(entityId);
                var trauma = world.GetComponent<ProfoundTraumaComponent>(entityId);
                // Clear other urges to focus on revenge
                needs.Demands.Clear();
                needs.Demands.Add(new Dictionary {
                    { "type", "SEEK_REVENGE" },
                    { "perpetrator", trauma.PerpetratorId }
                });

                GD.Print($"Entity {entityId} is now consumed by the need for revenge (1444) against {trauma.PerpetratorId}.");

                // The trauma is now being processed, we can remove the component
                // so this doesn't trigger every frame.
                world.RemoveComponent<ProfoundTraumaComponent>(entityId);
            }
        }
    }
}