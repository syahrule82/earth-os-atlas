"""Treasury management for ATLAS DAO."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List
from enum import Enum
import time

class AllocationStrategy(Enum):
    PROPORTIONAL = "proportional"
    QUADRATIC = "quadratic"
    CONVICTION = "conviction"

@dataclass
class Allocation:
    proposal_id: str
    recipient:   str
    amount:      Decimal
    strategy:    AllocationStrategy
    timestamp:   float

class Treasury:
    """Manages ATLAS DAO treasury with programmable allocations."""

    def __init__(self):
        self.balance = Decimal("0")
        self.allocations: List[Allocation] = []
        self.proposals: Dict[str, dict] = {}

    def deposit(self, amount: Decimal) -> None:
        self.balance += amount

    def withdraw(self, amount: Decimal, recipient: str) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

    def create_proposal(self, proposal_id: str, description: str, amount: Decimal, 
                        recipients: List[str], strategy: AllocationStrategy) -> dict:
        prop = {
            "id": proposal_id,
            "description": description,
            "total_amount": amount,
            "recipients": recipients,
            "strategy": strategy,
            "votes_for": Decimal("0"),
            "votes_against": Decimal("0"),
            "status": "pending",
            "created": time.time(),
        }
        self.proposals[proposal_id] = prop
        return prop

    def vote(self, proposal_id: str, voter: str, weight: Decimal, approve: bool) -> None:
        prop = self.proposals.get(proposal_id)
        if not prop or prop["status"] != "pending":
            return
        if approve:
            prop["votes_for"] += weight
        else:
            prop["votes_against"] += weight

    def execute(self, proposal_id: str, quorum: Decimal = Decimal("0.1")) -> bool:
        prop = self.proposals.get(proposal_id)
        if not prop or prop["status"] != "pending":
            return False
        total = prop["votes_for"] + prop["votes_against"]
        if total < quorum:
            prop["status"] = "failed_quorum"
            return False
        if prop["votes_for"] / total < Decimal("0.5"):
            prop["status"] = "rejected"
            return False
        
        # Calculate allocations per strategy
        strategy = prop["strategy"]
        recipients = prop["recipients"]
        n = len(recipients)
        
        if strategy == AllocationStrategy.PROPORTIONAL:
            per_rec = prop["total_amount"] / n
            for r in recipients:
                self.withdraw(per_rec, r)
        elif strategy == AllocationStrategy.QUADRATIC:
            # Equal split (quadratic would need vote weights)
            per_rec = prop["total_amount"] / n
            for r in recipients:
                self.withdraw(per_rec, r)
        
        prop["status"] = "executed"
        return True
