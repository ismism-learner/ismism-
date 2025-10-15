namespace Ecs.Components
{
    /// <summary>
    /// Manages the financial state of an entity.
    /// </summary>
    public class FinancialComponent : Component
    {
        public float Money { get; set; }
        public float BankBalance { get; set; }
        public float Loans { get; set; }

        public FinancialComponent(float money, float bankBalance = 0, float loans = 0)
        {
            Money = money;
            BankBalance = bankBalance;
            Loans = loans;
        }
    }
}