using Ecs.Components;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace Ecs.Systems
{
    public partial class ManagementSystem : Ecs.System
    {
        public override void Process()
        {
            // This system will be more event-driven in the future.
            // For now, its logic is exposed via public methods for other systems to call.
        }

        // This is the core public method that other systems (like ActionSystem) will call.
        public void TryToExploit(int leaderId, List<int> subordinateIds)
        {
            float projectedMight = CalculateProjectedMight(leaderId);
            float resistancePotential = CalculateResistancePotential(subordinateIds);

            GD.Print($"LEADER {leaderId}: Projected Might = {projectedMight}");
            GD.Print($"SUBORDINATES: Resistance Potential = {resistancePotential}");

            // The leader needs a significant power advantage to succeed.
            if (projectedMight > resistancePotential * 1.5f)
            {
                GD.Print("EXPLOIT SUCCEEDED.");
                foreach (var subId in subordinateIds)
                {
                    var sheet = world.GetComponent<CharacterSheetComponent>(subId);
                    if (sheet != null)
                    {
                        // Increase work hours and grievance
                        sheet.WorkHoursPerDay += 1;
                        sheet.Grievance += 5;

                        // Clamp values
                        if (sheet.WorkHoursPerDay > 16) sheet.WorkHoursPerDay = 16;
                        if (sheet.Grievance > 100) sheet.Grievance = 100;

                        GD.Print($"Subordinate {subId} now works {sheet.WorkHoursPerDay} hours/day. Grievance is {sheet.Grievance}.");
                    }
                }
            }
            else
            {
                GD.Print("EXPLOIT FAILED. Resistance was too high.");
                // Future enhancement: Failed attempts could increase leader's stress or cause a conflict.
            }
        }

        private float CalculateProjectedMight(int leaderId)
        {
            var leaderSheet = world.GetComponent<CharacterSheetComponent>(leaderId);
            var leaderRelationships = world.GetComponent<RelationshipComponent>(leaderId);
            if (leaderSheet == null || leaderRelationships == null) return 0;

            // Leader's own might is a small factor.
            float totalMight = leaderSheet.MartialProwess * 0.2f;

            var followers = leaderRelationships.Relationships.Values
                .Where(r => r.Type == RelationshipType.Follower && r.Strength > 50);

            foreach (var followerRel in followers)
            {
                var followerSheet = world.GetComponent<CharacterSheetComponent>(followerRel.TargetNpcId);
                if (followerSheet != null)
                {
                    // The might from followers is the main component.
                    totalMight += followerSheet.MartialProwess;
                }
            }
            return totalMight;
        }

        private float CalculateResistancePotential(List<int> subordinateIds)
        {
            float totalResistance = 0;
            foreach (var subId in subordinateIds)
            {
                var subSheet = world.GetComponent<CharacterSheetComponent>(subId);
                if (subSheet != null)
                {
                    totalResistance += subSheet.MartialProwess;
                }
            }
            return totalResistance;
        }
    }
}