"""Genesis Protocol — Zero-to-One bootstrapping for ATLAS."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional
import time, hashlib

@dataclass
class GenesisAllocation:
    """A single genesis allocation."""
    recipient: str
    amount: Decimal
    category: str  # founder, contributor, liquidity, treasury, community
    vesting_days: int = 0  # 0 = no vesting
    claimed: bool = False
    allocation_id: str = field(default="")
    
    def __post_init__(self):
        if not self.allocation_id:
            self.allocation_id = hashlib.sha256(
                f"{self.recipient}:{self.category}:{time.time()}".encode()
            ).hexdigest()[:16]

@dataclass
class ColdStartSolver:
    """
    Solves the 'no users = no value' chicken-and-egg problem.
    
    Strategy:
    1. Seed with high-value contributors (founders, early adopters)
    2. Provide liquidity bootstrapping via bonding curve
    3. Incentivize first 1000 contributors with bonus multiplier
    4. Network effects kick in after critical mass
    """
    
    CRITICAL_MASS = 1000  # users needed for network effects
    EARLY_BONUS_MULTIPLIER = 2.0  # 2x for first 1000 contributors
    EARLY_BONUS_THRESHOLD = 1000
    
    def calculate_bonus(self, contributor_rank: int) -> float:
        """Calculate early adopter bonus multiplier."""
        if contributor_rank <= 100:
            return 3.0  # First 100 get 3x
        elif contributor_rank <= 500:
            return 2.5  # Next 400 get 2.5x
        elif contributor_rank <= self.EARLY_BONUS_THRESHOLD:
            return self.EARLY_BONUS_MULTIPLIER  # Next 500 get 2x
        return 1.0  # No bonus after critical mass
    
    def is_self_sustaining(self, metrics: dict) -> bool:
        """Check if the economy is self-sustaining."""
        users = metrics.get("active_users", 0)
        daily_value = metrics.get("daily_value_created", 0)
        retention = metrics.get("retention_rate", 0)
        
        return (
            users >= self.CRITICAL_MASS and
            daily_value > 0 and
            retention >= 0.5
        )
    
    def bootstrap_plan(self) -> List[dict]:
        """Generate a bootstrapping plan."""
        return [
            {"phase": 1, "name": "Genesis", "target": "10 founding contributors",
             "action": "Mint genesis allocations", "duration_days": 7},
            {"phase": 2, "name": "Seeding", "target": "100 early adopters",
             "action": "3x bonus multiplier, liquidity bootstrapping", "duration_days": 30},
            {"phase": 3, "name": "Growth", "target": "1000 contributors",
             "action": "2.5x bonus, partnership outreach", "duration_days": 90},
            {"phase": 4, "name": "Critical Mass", "target": "Self-sustaining",
             "action": "2x bonus for final push, remove training wheels", "duration_days": 180},
            {"phase": 5, "name": "Maturity", "target": "Network effects",
             "action": "Normal minting, full governance", "duration_days": 365},
        ]

class GenesisProtocol:
    """
    The ATLAS Genesis Protocol.
    Defines how the economy starts from an empty ledger.
    """
    
    TOTAL_GENESIS = Decimal("1000000000")  # 1B ATLAS
    
    ALLOCATION_SPLITS = {
        "contributors": Decimal("0.30"),   # 300M for founding contributors
        "treasury": Decimal("0.25"),        # 250M for DAO treasury
        "liquidity": Decimal("0.15"),       # 150M for AMM liquidity
        "community": Decimal("0.15"),       # 150M for community rewards
        "validators": Decimal("0.10"),      # 100M for validator incentives
        "team": Decimal("0.05"),            # 50M for core team (4-year vesting)
    }
    
    def __init__(self):
        self.allocations: List[GenesisAllocation] = []
        self.solver = ColdStartSolver()
        self.genesis_time: Optional[float] = None
    
    def generate_genesis(self, contributors: List[dict]) -> List[GenesisAllocation]:
        """Generate genesis block allocations."""
        self.genesis_time = time.time()
        
        # Contributor allocations (30% = 300M)
        contributor_pool = self.TOTAL_GENESIS * self.ALLOCATION_SPLITS["contributors"]
        per_contributor = contributor_pool / Decimal(str(len(contributors)))
        for i, c in enumerate(contributors):
            bonus = Decimal(str(self.solver.calculate_bonus(i + 1)))
            amount = per_contributor * bonus
            self.allocations.append(GenesisAllocation(
                recipient=c["did"], amount=amount,
                category="contributor", vesting_days=c.get("vesting", 365),
            ))
        
        # Treasury (25% = 250M)
        self.allocations.append(GenesisAllocation(
            recipient="did:atlas:treasury",
            amount=self.TOTAL_GENESIS * self.ALLOCATION_SPLITS["treasury"],
            category="treasury",
        ))
        
        # Liquidity (15% = 150M)
        self.allocations.append(GenesisAllocation(
            recipient="did:atlas:liquidity_pool",
            amount=self.TOTAL_GENESIS * self.ALLOCATION_SPLITS["liquidity"],
            category="liquidity",
        ))
        
        # Community (15% = 150M)
        self.allocations.append(GenesisAllocation(
            recipient="did:atlas:community_pool",
            amount=self.TOTAL_GENESIS * self.ALLOCATION_SPLITS["community"],
            category="community",
        ))
        
        # Validators (10% = 100M)
        self.allocations.append(GenesisAllocation(
            recipient="did:atlas:validator_pool",
            amount=self.TOTAL_GENESIS * self.ALLOCATION_SPLITS["validators"],
            category="validators",
        ))
        
        # Team (5% = 50M, 4-year vesting)
        self.allocations.append(GenesisAllocation(
            recipient="did:atlas:team",
            amount=self.TOTAL_GENESIS * self.ALLOCATION_SPLITS["team"],
            category="team", vesting_days=1460,  # 4 years
        ))
        
        return self.allocations
    
    def total_allocated(self) -> Decimal:
        return sum((a.amount for a in self.allocations), Decimal("0"))
    
    def summary(self) -> dict:
        by_category = {}
        for a in self.allocations:
            by_category[a.category] = by_category.get(a.category, Decimal("0")) + a.amount
        return {
            "total_allocated": str(self.total_allocated()),
            "allocations_count": len(self.allocations),
            "by_category": {k: str(v) for k, v in by_category.items()},
            "genesis_time": self.genesis_time,
            "bootstrap_plan": self.solver.bootstrap_plan(),
        }
