using Ecs.Components;
using Godot;
using Godot.Collections;
using System.Linq;

namespace Ecs.Systems
{
    public partial class InteractionSystem : Ecs.System
    {
        // ... (other constants)

        public override void Process()
        {
            // ... (main loop logic)
             foreach (var entityId in entities)
            {
                var state = world.GetComponent<StateComponent>(entityId);

                if (state.CurrentState == "Idle")
                {
                    ProcessIdleInteraction(entityId, state);
                }
                else if (state.CurrentState == "Recruiting")
                {
                    ProcessRecruiting(entityId, state);
                }
            }
        }

        private void ProcessIdleInteraction(int entityId, StateComponent state)
        {
            // ... (existing logic)
            // Inside the loop where colleagues are found...
            if (pos.Position.DistanceTo(colleaguePos.Position) < InteractionDistance)
            {
                // Check for betrayal before other interactions
                CheckForBetrayal(entityId, colleagueId);
                CheckForBetrayal(colleagueId, entityId); // Check both ways

                if (AttemptTeachInteraction(entityId, colleagueId))
                {
                    state.LastInteractionTime = world.Time;
                    break;
                }
                PerformStandardInteraction(entityId, colleagueId, "WorkplaceChat");
                state.LastInteractionTime = world.Time;
                break;
            }
        }

        private void CheckForBetrayal(int personA, int personB)
        {
            var relA = world.GetComponent<RelationshipComponent>(personA);
            if (relA == null) return;

            // Find if Person A has a lover who is NOT Person B
            var loverRelationship = relA.Relationships.Values.FirstOrDefault(r => r.Type == RelationshipType.Lover && r.TargetNpcId != personB);
            if (loverRelationship == null) return;

            var betrayedId = loverRelationship.TargetNpcId;

            // Check if the betrayed person already has a trauma component
            if (world.HasComponent<ProfoundTraumaComponent>(betrayedId)) return;

            // If Person A and Person B are getting friendly, the lover might feel betrayed
            var relAB = relA.GetRelationshipWith(personB);
            if (relAB != null && relAB.Strength > 40) // Threshold for suspicion
            {
                 GD.Print($"BETRAYAL: {betrayedId} feels betrayed by {personA} interacting with {personB}!");
                 world.AddComponent(betrayedId, new ProfoundTraumaComponent(TraumaType.Betrayal, personA.ToString()));
            }
        }

        // ... (rest of the methods: ProcessRecruiting, AttemptRecruitInteraction, etc.)
    }
}