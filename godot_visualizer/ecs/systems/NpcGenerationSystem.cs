using Ecs.Components;
using Godot;
using System.Collections.Generic;

namespace Ecs.Systems
{
    public partial class NpcGenerationSystem : System
    {
        private static readonly RandomNumberGenerator Rng = new();
        private const int CouncilSize = 20;
        private const int ManagersPerCouncilMember = 20;
        private const int LaborersPerManager = 60;

        public override void Process()
        {
            if (world.Time > 0)
            {
                Enabled = false;
                return;
            }

            GenerateTownPopulation();
        }

        private void GenerateTownPopulation()
        {
            var governorId = CreateNpc("Governor", "4000", 95);
            world.AddComponent(governorId, new TownGoalsComponent());

            var councilMembers = new List<int>();
            for (int i = 0; i < CouncilSize; i++)
            {
                var councilMemberId = CreateNpc($"Councilor {i+1}", "4100", Rng.RandfRange(70, 90));
                councilMembers.Add(councilMemberId);
                EstablishSubordinateLink(governorId, councilMemberId);
            }

            foreach (var councilMemberId in councilMembers)
            {
                for (int i = 0; i < ManagersPerCouncilMember; i++)
                {
                    var managerId = CreateNpc($"Manager {councilMemberId}-{i+1}", "2100", Rng.RandfRange(50, 70));
                    EstablishSubordinateLink(councilMemberId, managerId);

                    for (int j = 0; j < LaborersPerManager; j++)
                    {
                        var laborerId = CreateNpc($"Laborer {managerId}-{j+1}", "1100", Rng.RandfRange(20, 40));
                        EstablishSubordinateLink(managerId, laborerId);
                    }
                }
            }
        }

        private int CreateNpc(string name, string dominantIsm, float rationality)
        {
            var entityId = world.CreateEntity();

            world.AddComponent(entityId, new IdentityComponent { Name = name });
            world.AddComponent(entityId, new RelationshipComponent());
            world.AddComponent(entityId, new FinancialComponent());
            world.AddComponent(entityId, new NeedsComponent(0,0));

            var sheet = new CharacterSheetComponent { Rationality = rationality };
            world.AddComponent(entityId, sheet);

            var ismComponent = new IsmComponent();
            ismComponent.AddIdeology(dominantIsm, 100);
            world.AddComponent(entityId, ismComponent);

            return entityId;
        }

        private void EstablishSubordinateLink(int superiorId, int subordinateId)
        {
            var superiorRels = world.GetComponent<RelationshipComponent>(superiorId);
            superiorRels.AddOrUpdateRelationship(subordinateId, RelationshipType.Follower, 100);
        }
    }
}