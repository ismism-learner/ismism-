import random
from ..world import World
from ..components.needs import NeedsComponent
from ..components.state import StateComponent
from ..components.position import PositionComponent
from ..components.economy import EconomyComponent
from ..components.financial_component import FinancialComponent
from ..system import System


class BankingSystem(System):
    """
    Handles all banking and financial activities for NPCs.
    - Manages loans, deposits, and withdrawals.
    - Handles loan approval, repayment, and default.
    - Simulates central bank actions.
    """
    def process(self, world: World, locations: list):
        # --- 1. Macro-economic actions (Central Bank) ---
        # Periodically, the central bank injects capital into commercial banks.
        if world.time % 100 == 0:  # Every 100 ticks
            self._central_bank_action(locations)

        # --- 2. Process individual NPC financial actions ---
        entities_to_process = world.get_entities_with_components(StateComponent, EconomyComponent, FinancialComponent, PositionComponent)

        for entity_id in entities_to_process:
            state = world.get_component(entity_id, StateComponent)

            # Find the bank the NPC is currently at
            bank_location = self._get_location_by_entity_position(world, entity_id, locations, ["COMMERCIAL_BANK"])
            if not bank_location:
                continue

            # Handle actions
            if state.action == "DEPOSIT_MONEY":
                self._handle_deposit(world, entity_id, bank_location)
            elif state.action == "WITHDRAW_MONEY":
                self._handle_withdraw(world, entity_id, bank_location)
            elif state.action == "GET_LOAN":
                self._handle_loan_application(world, entity_id, bank_location)

        # --- 3. Process loan repayments and defaults (less frequent) ---
        if world.time % 50 == 0: # Every 50 ticks
            self._process_loan_repayments(world)


    def _central_bank_action(self, locations: list):
        """Injects money from the central bank into all commercial banks."""
        central_bank = next((loc for loc in locations if loc['type'] == 'CENTRAL_BANK'), None)
        if not central_bank:
            return

        commercial_banks = [loc for loc in locations if loc['type'] == 'COMMERCIAL_BANK']
        if not commercial_banks:
            return

        # Distribute a portion of central bank reserves to commercial banks
        injection_amount = central_bank['cash_reserves'] * 0.01
        if injection_amount <= 0:
            return

        amount_per_bank = injection_amount / len(commercial_banks)

        for bank in commercial_banks:
            bank['cash_reserves'] += amount_per_bank
        central_bank['cash_reserves'] -= injection_amount
        print(f"[BankingSystem] Central Bank injected {amount_per_bank:.2f} into {len(commercial_banks)} commercial banks.")

    def _get_location_by_entity_position(self, world: World, entity_id: int, locations: list, location_types: list) -> dict | None:
        """Finds the location an entity is currently at, based on their position."""
        position = world.get_component(entity_id, PositionComponent)
        for loc in locations:
            if loc['type'] in location_types:
                dist_sq = (position.x - loc['position']['x'])**2 + (position.y - loc['position']['y'])**2
                if dist_sq <= loc['radius']**2:
                    return loc
        return None

    def _handle_deposit(self, world: World, entity_id: int, bank_location: dict):
        """Handles an NPC depositing money into a bank."""
        economy = world.get_component(entity_id, EconomyComponent)
        financial = world.get_component(entity_id, FinancialComponent)
        state = world.get_component(entity_id, StateComponent)

        if economy.money > 0:
            deposit_amount = economy.money
            financial.bank_balance += deposit_amount
            bank_location['cash_reserves'] += deposit_amount
            economy.money = 0
            print(f"[BankingSystem] Entity {entity_id} deposited {deposit_amount:.2f}. New balance: {financial.bank_balance:.2f}")

        # Action is complete, reset state
        state.action = "IDLE"
        state.goal = None

    def _handle_loan_application(self, world: World, entity_id: int, bank_location: dict):
        """Handles an NPC applying for a loan."""
        financial = world.get_component(entity_id, FinancialComponent)
        economy = world.get_component(entity_id, EconomyComponent)
        needs = world.get_component(entity_id, NeedsComponent)
        state = world.get_component(entity_id, StateComponent)

        # Loan amount is based on a "desire", for now, let's use a fixed amount for simplicity
        # A more complex version would have this in the NeedsComponent demand.
        loan_amount_requested = 200.0

        # Loan is approved based on credit score and bank reserves
        if financial.credit_score > 450 and bank_location['cash_reserves'] > loan_amount_requested:
            # Approve loan
            loan = {
                "id": f"loan_{world.time}_{entity_id}",
                "amount": loan_amount_requested,
                "due_tick": world.time + 200, # Due in 200 ticks
                "interest_rate": 0.1,
                "repayment_per_tick": (loan_amount_requested * 1.1) / 200
            }
            financial.loans.append(loan)
            economy.money += loan_amount_requested
            bank_location['cash_reserves'] -= loan_amount_requested
            financial.credit_score -= 20 # Taking a loan slightly reduces score
            print(f"[BankingSystem] Entity {entity_id} approved for loan of {loan_amount_requested:.2f}")
        else:
            # Reject loan
            financial.credit_score -= 10 # Failed application hurts score
            print(f"[BankingSystem] Entity {entity_id} REJECTED for loan of {loan_amount_requested:.2f}")

        state.action = "IDLE"
        state.goal = None

    def _process_loan_repayments(self, world: World):
        """Periodically processes repayments and handles defaults for all entities."""
        entities_with_loans = world.get_entities_with_components(FinancialComponent, EconomyComponent, NeedsComponent)

        for entity_id in entities_with_loans:
            financial = world.get_component(entity_id, FinancialComponent)
            if not financial.loans:
                continue

            economy = world.get_component(entity_id, EconomyComponent)
            needs = world.get_component(entity_id, NeedsComponent)

            # Process each loan for the entity
            for loan in financial.loans[:]: # Iterate over a copy
                # 1. Make a payment if possible
                payment = loan['repayment_per_tick'] * 50 # Payment for 50 ticks
                if economy.money >= payment:
                    economy.money -= payment
                    loan['amount'] -= payment / 1.1 # Reduce principal
                    financial.credit_score += 2 # Regular payment improves score
                else:
                    # Not enough money, increase stress and lower credit
                    needs.needs['stress']['current'] += 10
                    financial.credit_score -= 5

                # 2. Check for default
                if world.time > loan['due_tick'] and loan['amount'] > 0:
                    print(f"[BankingSystem] Entity {entity_id} has DEFAULTED on loan {loan['id']}.")
                    financial.is_in_default = True
                    financial.credit_score -= 100 # Major penalty for default

                    # Impose forced labor
                    needs.demands.insert(0, "FORCED_LABOR")

                    financial.loans.remove(loan) # Remove the defaulted loan

            # Clamp scores
            financial.credit_score = max(300, min(850, financial.credit_score))

    def _handle_withdraw(self, world: World, entity_id: int, bank_location: dict):
        """Handles an NPC withdrawing money from a bank."""
        economy = world.get_component(entity_id, EconomyComponent)
        financial = world.get_component(entity_id, FinancialComponent)
        state = world.get_component(entity_id, StateComponent)

        # Example: withdraw half of their balance if they have no cash
        if financial.bank_balance > 0 and economy.money <= 0:
            withdraw_amount = financial.bank_balance / 2

            if bank_location['cash_reserves'] >= withdraw_amount:
                financial.bank_balance -= withdraw_amount
                bank_location['cash_reserves'] -= withdraw_amount
                economy.money += withdraw_amount
                print(f"[BankingSystem] Entity {entity_id} withdrew {withdraw_amount:.2f}. New balance: {financial.bank_balance:.2f}")
            else:
                print(f"[BankingSystem] Bank has insufficient funds for entity {entity_id} to withdraw.")

        # Action is complete, reset state
        state.action = "IDLE"
        state.goal = None