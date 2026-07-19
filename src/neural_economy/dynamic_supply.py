"""Dynamic Supply Engine — velocity-adjusted minting with burn."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional
import time

@dataclass
class BurnEvent:
    """An ATLAS burn event (removing tokens from circulation)."""
    burn_id: str
    amount: Decimal
    reason: str  # transaction_fee, penalty, voluntary, governance_decision
    burner: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class VelocityAdjuster:
    """Adjusts minting rate based on token velocity."""
    target_velocity: float = 5.0  # target ATLAS turnover per year
    current_velocity: float = 0.0
    adjustment_factor: float = 1.0
    
    def update(self, transaction_volume: Decimal, total_supply: Decimal) -> float:
        """Calculate velocity and adjustment factor."""
        if total_supply <= 0:
            self.current_velocity = 0
            return 1.0
        
        self.current_velocity = float(transaction_volume / total_supply)
        
        # If velocity too low (hoarding), increase minting to incentivize spending
        # If velocity too high (speculation), decrease minting
        if self.current_velocity < self.target_velocity * 0.5:
            self.adjustment_factor = 1.2  # 20% more minting
        elif self.current_velocity > self.target_velocity * 2.0:
            self.adjustment_factor = 0.8  # 20% less minting
        else:
            self.adjustment_factor = 1.0  # Normal
        
        return self.adjustment_factor

class DynamicSupplyEngine:
    """
    Manages ATLAS supply dynamics.
    
    Unlike Bitcoin's fixed supply, ATLAS uses:
    - Velocity-adjusted minting (more minting when velocity is low)
    - Selective burning (fees, penalties, governance)
    - Supply ceiling (never exceeds 1B)
    - Deflationary pressure via burns
    """
    
    GENESIS_SUPPLY = Decimal("1000000000")  # 1B hard cap
    
    def __init__(self):
        self.total_minted = Decimal("0")
        self.total_burned = Decimal("0")
        self.burns: List[BurnEvent] = []
        self.velocity_adjuster = VelocityAdjuster()
        self.mint_history: List[dict] = []
    
    @property
    def circulating_supply(self) -> Decimal:
        return self.total_minted - self.total_burned
    
    def adjusted_mint_rate(self, base_rate: Decimal) -> Decimal:
        """Apply velocity adjustment to base minting rate."""
        return base_rate * Decimal(str(self.velocity_adjuster.adjustment_factor))
    
    def mint(self, amount: Decimal, confidence: float = 1.0) -> Decimal:
        """Mint new ATLAS with velocity adjustment."""
        adjusted = self.adjusted_mint_rate(amount) * Decimal(str(confidence))
        if self.total_minted + adjusted > self.GENESIS_SUPPLY:
            remaining = self.GENESIS_SUPPLY - self.total_minted
            if remaining <= 0:
                return Decimal("0")
            adjusted = remaining
        self.total_minted += adjusted
        self.mint_history.append({"amount": str(adjusted), "timestamp": time.time()})
        return adjusted
    
    def burn(self, amount: Decimal, reason: str, burner: str) -> BurnEvent:
        """Burn ATLAS tokens (remove from circulation)."""
        if self.total_burned + amount > self.total_minted:
            raise ValueError("Cannot burn more than minted")
        event = BurnEvent(
            burn_id=f"burn_{int(time.time())}",
            amount=amount, reason=reason, burner=burner,
        )
        self.burns.append(event)
        self.total_burned += amount
        return event
    
    def update_velocity(self, tx_volume: Decimal) -> float:
        """Update velocity and return adjustment factor."""
        return self.velocity_adjuster.update(tx_volume, self.circulating_supply)
    
    def stats(self) -> dict:
        burn_rate = float(self.total_burned / self.total_minted) if self.total_minted > 0 else 0
        return {
            "total_minted": str(self.total_minted),
            "total_burned": str(self.total_burned),
            "circulating": str(self.circulating_supply),
            "burn_rate": burn_rate,
            "current_velocity": self.velocity_adjuster.current_velocity,
            "adjustment_factor": self.velocity_adjuster.adjustment_factor,
        }
