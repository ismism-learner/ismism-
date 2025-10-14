from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class FinancialComponent:
    """
    Stores an entity's financial information.
    """
    bank_balance: float = 0.0
    loans: float = 0.0 # Total loan amount
    credit_score: float = 500.0  # Starting credit score
    is_in_default: bool = False