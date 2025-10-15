namespace Ecs.Components
{
    public partial class FinancialComponent : Component
    {
        public float Money { get; set; }
        public float BankBalance { get; set; }
        public float Loans { get; set; }

        // Represents the economic output of this individual in the last cycle.
        public float GdpContribution { get; set; } = 0;

        public FinancialComponent()
        {
            Money = 100;
            BankBalance = 0;
            Loans = 0;
        }
    }
}