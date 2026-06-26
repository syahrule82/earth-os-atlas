"""ATLAS Automated Market Maker — constant product pools."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Optional
import time

@dataclass
class LiquidityPosition:
    position_id:   str
    provider:      str
    token_a:       str
    token_b:       str
    amount_a:      Decimal
    amount_b:      Decimal
    fee_tier:      Decimal = Decimal("0.003")  # 0.3%
    created_at:    float = field(default_factory=time.time)

@dataclass
class ATLASPool:
    pool_id:       str
    token_a:       str
    token_b:       str
    reserve_a:     Decimal
    reserve_b:     Decimal
    fee_tier:      Decimal = Decimal("0.003")
    total_liquidity: Decimal = Decimal("0")
    positions:     Dict[str, LiquidityPosition] = field(default_factory=dict)

    def get_price(self, token_in: str) -> Decimal:
        """Price of token_in in terms of the other token."""
        if token_in == self.token_a:
            return self.reserve_b / self.reserve_a if self.reserve_a > 0 else Decimal("0")
        return self.reserve_a / self.reserve_b if self.reserve_b > 0 else Decimal("0")

    def swap(self, token_in: str, amount_in: Decimal) -> Decimal:
        """Execute swap. Returns amount_out."""
        fee = amount_in * self.fee_tier
        amount_after_fee = amount_in - fee
        
        if token_in == self.token_a:
            k = self.reserve_a * self.reserve_b
            new_reserve_a = self.reserve_a + amount_after_fee
            amount_out = self.reserve_b - k / new_reserve_a
            self.reserve_a = new_reserve_a
            self.reserve_b -= amount_out
        else:
            k = self.reserve_a * self.reserve_b
            new_reserve_b = self.reserve_b + amount_after_fee
            amount_out = self.reserve_a - k / new_reserve_b
            self.reserve_b = new_reserve_b
            self.reserve_a -= amount_out
        return amount_out

    def add_liquidity(self, provider: str, amount_a: Decimal, amount_b: Decimal) -> LiquidityPosition:
        # Proportional to current reserves
        ratio_a = amount_a / self.reserve_a if self.reserve_a > 0 else Decimal("1")
        ratio_b = amount_b / self.reserve_b if self.reserve_b > 0 else Decimal("1")
        
        pos = LiquidityPosition(
            position_id=f"pos_{len(self.positions)}",
            provider=provider,
            token_a=self.token_a,
            token_b=self.token_b,
            amount_a=amount_a,
            amount_b=amount_b,
            fee_tier=self.fee_tier,
        )
        self.reserve_a += amount_a
        self.reserve_b += amount_b
        self.positions[pos.position_id] = pos
        return pos

    def remove_liquidity(self, position_id: str) -> Optional[LiquidityPosition]:
        pos = self.positions.pop(position_id, None)
        if pos:
            self.reserve_a -= pos.amount_a
            self.reserve_b -= pos.amount_b
        return pos

class SwapRouter:
    """Routes swaps through multiple pools for best price."""
    def __init__(self):
        self.pools: Dict[str, ATLASPool] = {}
    
    def add_pool(self, pool: ATLASPool):
        self.pools[f"{pool.token_a}/{pool.token_b}"] = pool
    
    def get_best_path(self, token_in: str, token_out: str) -> Optional[list]:
        # Simple direct pool lookup; production: multi-hop routing
        key = f"{token_in}/{token_out}"
        if key in self.pools:
            return [self.pools[key]]
        rev = f"{token_out}/{token_in}"
        if rev in self.pools:
            return [self.pools[rev]]
        return None
