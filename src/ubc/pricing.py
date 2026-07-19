"""Dynamic compute pricing."""
from decimal import Decimal
from typing import Dict
import time

class DynamicPricer:
    """Dynamic pricing for compute resources based on supply/demand."""

    def __init__(self, base_price: Decimal = Decimal("1.0")):
        self.base_price = base_price  # ATLAS per GFLOP-hour
        self.supply: float = 1e12  # 1 TFLOPS available
        self.demand: float = 0
        self.price_history: list = []

    def update_supply(self, available_flops: float) -> None:
        self.supply = available_flops

    def update_demand(self, requested_flops: float) -> None:
        self.demand = requested_flops

    def current_price(self) -> Decimal:
        """Calculate current dynamic price."""
        if self.supply <= 0:
            return self.base_price * Decimal("10")  # Scarcity premium
        utilization = self.demand / self.supply
        if utilization < 0.3:
            multiplier = Decimal("0.5")  # Discount when underutilized
        elif utilization < 0.7:
            multiplier = Decimal("1.0")  # Normal price
        elif utilization < 0.9:
            multiplier = Decimal("1.5")  # High demand premium
        else:
            multiplier = Decimal("3.0")  # Scarcity premium
        price = self.base_price * multiplier
        self.price_history.append({"price": str(price), "utilization": utilization, "timestamp": time.time()})
        return price

class ComputePricing:
    """Pricing tiers for compute resources."""
    TIERS = {
        "basic":   {"flops": 1e9,  "price": Decimal("0")},      # Free
        "standard": {"flops": 1e10, "price": Decimal("1.0")},    # 1 ATLAS/hr
        "premium": {"flops": 1e11, "price": Decimal("5.0")},    # 5 ATLAS/hr
        "enterprise": {"flops": 1e12, "price": Decimal("20.0")}, # 20 ATLAS/hr
    }

    @classmethod
    def get_tier(cls, tier_name: str) -> dict:
        return cls.TIERS.get(tier_name, cls.TIERS["basic"])

    @classmethod
    def list_tiers(cls) -> list:
        return [{"name": k, **v} for k, v in cls.TIERS.items()]
