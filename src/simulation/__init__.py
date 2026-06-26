"""Economic simulator for agent-based modeling."""
import random
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict

@dataclass
class Agent:
    agent_id: str
    balance: Decimal = Decimal("1000")
    reputation: float = 1.0
    strategy: str = "honest"

@dataclass
class SimulationResult:
    total_value_created: Decimal
    total_atlas_minted: Decimal
    gini_coefficient: float
    participation_rate: float
    avg_transaction_size: Decimal

class EconomicSimulator:
    """Agent-based economic simulator for ATLAS."""

    def __init__(self, n_agents: int = 1000):
        self.agents: List[Agent] = [Agent(agent_id=f"agent_{i}") for i in range(n_agents)]
        self.total_supply = Decimal("0")
        self.transactions: List[dict] = []

    def step(self) -> None:
        """Run one simulation step."""
        for _ in range(100):  # 100 interactions per step
            a, b = random.sample(self.agents, 2)
            if a.balance > Decimal("10"):
                amount = Decimal(str(random.uniform(1, float(a.balance / 10))))
                if a.strategy == "honest" or random.random() > 0.1:
                    a.balance -= amount
                    b.balance += amount
                    self.transactions.append({"from": a.agent_id, "to": b.agent_id, "amount": amount})
                    # 10% chance of value creation triggering mint
                    if random.random() < 0.1:
                        minted = amount * Decimal("0.1")
                        a.balance += minted
                        self.total_supply += minted

    def run(self, steps: int = 100) -> SimulationResult:
        for _ in range(steps):
            self.step()
        return self.analyze()

    def analyze(self) -> SimulationResult:
        balances = sorted([float(a.balance) for a in self.agents])
        n = len(balances)
        # Gini coefficient
        cumsum = sum((i + 1) * b for i, b in enumerate(balances))
        gini = (2 * cumsum) / (n * sum(balances)) - (n + 1) / n if sum(balances) > 0 else 0
        
        return SimulationResult(
            total_value_created=Decimal(str(len(self.transactions))) * Decimal("0.1"),
            total_atlas_minted=self.total_supply,
            gini_coefficient=gini,
            participation_rate=1.0,
            avg_transaction_size=Decimal(str(sum(t["amount"] for t in self.transactions) / max(1, len(self.transactions)))),
        )

    def stress_test(self, shock: str = "supply_shock") -> SimulationResult:
        """Apply economic shock and measure resilience."""
        if shock == "supply_shock":
            for a in self.agents:
                a.balance *= Decimal("0.5")  # 50% balance haircut
        elif shock == "confidence_crisis":
            for a in self.agents:
                if random.random() < 0.3:
                    a.strategy = "hoard"
        return self.run(50)
