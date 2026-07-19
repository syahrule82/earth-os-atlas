"""Sandbox Environment — Isolated test environment with mock data."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from decimal import Decimal
import hashlib, time, random

@dataclass
class MockDataGenerator:
    """Generates mock data for all 12 value categories."""

    CATEGORIES = [
        "SOLVED_PROBLEM", "CREATED_KNOWLEDGE", "BUILT_INFRASTRUCTURE",
        "HEALED_BIOLOGICAL", "PROTECTED_SYSTEMS", "OPTIMIZED_PROCESS",
        "CONNECTED_PEOPLE", "RESTORED_ECOLOGICAL", "ADVANCED_ART",
        "DISTRIBUTED_FAIRLY", "PREVENTED_HARM", "CREATED_BEAUTY",
    ]

    TIERS = ["micro", "small", "medium", "large", "massive", "planetary"]

    def generate_proofs(self, count: int = 10) -> List[dict]:
        """Generate mock contribution proofs."""
        proofs = []
        for i in range(count):
            proofs.append({
                "proof_id": f"mock_proof_{i}",
                "creator_id": f"did:atlas:user_{random.randint(1, 100)}",
                "category": random.choice(self.CATEGORIES),
                "tier": random.choice(self.TIERS),
                "hours": round(random.uniform(1, 40), 2),
                "base_value": str(round(random.uniform(10, 5000), 2)),
                "can_mint": random.random() > 0.3,
                "timestamp": time.time() - random.randint(0, 86400),
            })
        return proofs

    def generate_transactions(self, count: int = 20) -> List[dict]:
        """Generate mock ledger transactions."""
        txs = []
        for i in range(count):
            txs.append({
                "tx_id": f"mock_tx_{i}",
                "from": f"did:atlas:user_{random.randint(1, 100)}",
                "to": f"did:atlas:user_{random.randint(1, 100)}",
                "amount": str(round(random.uniform(1, 1000), 4)),
                "type": random.choice(["mint", "transfer", "stake", "reward"]),
                "timestamp": time.time() - random.randint(0, 3600),
            })
        return txs

    def generate_proposals(self, count: int = 5) -> List[dict]:
        """Generate mock governance proposals."""
        proposals = []
        for i in range(count):
            proposals.append({
                "proposal_id": f"mock_prop_{i}",
                "title": f"Mock Proposal {i}",
                "description": "This is a mock proposal for sandbox testing.",
                "proposer": f"did:atlas:user_{random.randint(1, 100)}",
                "status": random.choice(["active", "passed", "rejected"]),
                "votes_for": random.randint(10, 200),
                "votes_against": random.randint(5, 100),
                "timestamp": time.time() - random.randint(0, 86400 * 7),
            })
        return proposals

    def generate_users(self, count: int = 50) -> List[dict]:
        """Generate mock users with balances and reputation."""
        users = []
        for i in range(count):
            users.append({
                "did": f"did:atlas:user_{i}",
                "balance": str(round(random.uniform(0, 10000), 2)),
                "reputation": round(random.uniform(1.0, 10.0), 2),
                "contributions": random.randint(0, 500),
                "verification_level": random.choice(["Basic", "Verified", "Trusted", "Sovereign"]),
            })
        return users

@dataclass
class TransactionSimulator:
    """Simulates transactions against the sandbox."""
    scenarios: Dict[str, dict] = field(default_factory=dict)

    def create_scenario(self, name: str, description: str,
                       steps: List[dict]) -> str:
        scenario_id = hashlib.sha256(f"{name}:{time.time()}".encode()).hexdigest()[:16]
        self.scenarios[scenario_id] = {
            "name": name, "description": description,
            "steps": steps, "created_at": time.time(),
        }
        return scenario_id

    def run_scenario(self, scenario_id: str) -> dict:
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            return {"error": "Scenario not found"}
        results = []
        for i, step in enumerate(scenario["steps"]):
            results.append({
                "step": i + 1,
                "action": step.get("action", "unknown"),
                "params": step.get("params", {}),
                "result": "success",  # Simulated
                "timestamp": time.time(),
            })
        return {"scenario": scenario["name"], "steps_executed": len(results), "results": results}

class SandboxEnvironment:
    """
    Isolated test environment with pre-funded accounts.
    
    Features:
    - Pre-funded accounts with 10,000 ATLAS each
    - Mock data for all modules
    - Transaction simulator
    - State reset/restore
    """

    INITIAL_BALANCE = Decimal("10000")

    def __init__(self):
        self.accounts: Dict[str, Decimal] = {}
        self.mock_gen = MockDataGenerator()
        self.simulator = TransactionSimulator()
        self.state_history: List[dict] = []
        self._initialize_accounts()

    def _initialize_accounts(self):
        """Create pre-funded test accounts."""
        for i in range(10):
            did = f"did:atlas:sandbox_user_{i}"
            self.accounts[did] = self.INITIAL_BALANCE

    def get_balance(self, did: str) -> Decimal:
        return self.accounts.get(did, Decimal("0"))

    def transfer(self, sender: str, recipient: str, amount: Decimal) -> bool:
        if self.accounts.get(sender, Decimal("0")) < amount:
            return False
        self.accounts[sender] -= amount
        self.accounts[recipient] = self.accounts.get(recipient, Decimal("0")) + amount
        return True

    def mint(self, recipient: str, amount: Decimal) -> None:
        self.accounts[recipient] = self.accounts.get(recipient, Decimal("0")) + amount

    def save_state(self) -> str:
        state_id = hashlib.sha256(f"state:{time.time()}".encode()).hexdigest()[:16]
        self.state_history.append({
            "state_id": state_id,
            "accounts": dict(self.accounts),
            "timestamp": time.time(),
        })
        return state_id

    def restore_state(self, state_id: str) -> bool:
        state = next((s for s in self.state_history if s["state_id"] == state_id), None)
        if state:
            self.accounts = dict(state["accounts"])
            return True
        return False

    def reset(self) -> None:
        """Reset sandbox to initial state."""
        self.accounts.clear()
        self._initialize_accounts()

    def get_mock_data(self, data_type: str, count: int = 10) -> List[dict]:
        if data_type == "proofs":
            return self.mock_gen.generate_proofs(count)
        elif data_type == "transactions":
            return self.mock_gen.generate_transactions(count)
        elif data_type == "proposals":
            return self.mock_gen.generate_proposals(count)
        elif data_type == "users":
            return self.mock_gen.generate_users(count)
        return []

    def stats(self) -> dict:
        return {
            "total_accounts": len(self.accounts),
            "total_balance": str(sum(self.accounts.values(), Decimal("0"))),
            "saved_states": len(self.state_history),
            "scenarios": len(self.simulator.scenarios),
        }
