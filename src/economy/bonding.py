"""Bonding curves for ATLAS token pricing."""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Tuple

class BondingCurve(ABC):
    """Abstract bonding curve — price as function of supply."""
    @abstractmethod
    def price(self, supply: Decimal) -> Decimal:
        pass
    
    @abstractmethod
    def buy_price(self, supply: Decimal, amount: Decimal) -> Tuple[Decimal, Decimal]:
        """Returns (total_cost, new_price)."""
        pass
    
    @abstractmethod
    def sell_price(self, supply: Decimal, amount: Decimal) -> Tuple[Decimal, Decimal]:
        """Returns (total_received, new_price)."""
        pass

class LinearCurve(BondingCurve):
    """P = base + slope * supply"""
    def __init__(self, base: Decimal, slope: Decimal):
        self.base, self.slope = base, slope
    
    def price(self, supply: Decimal) -> Decimal:
        return self.base + self.slope * supply
    
    def buy_price(self, supply: Decimal, amount: Decimal) -> Tuple[Decimal, Decimal]:
        avg_price = self.base + self.slope * (supply + amount / 2)
        return avg_price * amount, self.price(supply + amount)
    
    def sell_price(self, supply: Decimal, amount: Decimal) -> Tuple[Decimal, Decimal]:
        avg_price = self.base + self.slope * (supply - amount / 2)
        return avg_price * amount, self.price(supply - amount)

class ExponentialCurve(BondingCurve):
    """P = base * exp(k * supply) — aggressive price discovery"""
    def __init__(self, base: Decimal, k: Decimal):
        self.base, self.k = base, k
    
    def price(self, supply: Decimal) -> Decimal:
        import math
        return self.base * Decimal(str(math.exp(float(self.k * supply))))
    
    def buy_price(self, supply: Decimal, amount: Decimal) -> Tuple[Decimal, Decimal]:
        import math
        k = self.k
        cost = (self.base / k) * (Decimal(str(math.exp(float(k * (supply + amount))))) - 
                                     Decimal(str(math.exp(float(k * supply)))))
        return cost, self.price(supply + amount)
    
    def sell_price(self, supply: Decimal, amount: Decimal) -> Tuple[Decimal, Decimal]:
        import math
        k = self.k
        recv = (self.base / k) * (Decimal(str(math.exp(float(k * supply)))) - 
                                     Decimal(str(math.exp(float(k * (supply - amount))))))
        return recv, self.price(supply - amount)

class LogarithmicCurve(BondingCurve):
    """P = a * ln(b * supply + 1) — diminishing returns"""
    def __init__(self, a: Decimal, b: Decimal):
        self.a, self.b = a, b
    
    def price(self, supply: Decimal) -> Decimal:
        import math
        return self.a * Decimal(str(math.log(float(self.b * supply) + 1)))
    
    def buy_price(self, supply: Decimal, amount: Decimal) -> Tuple[Decimal, Decimal]:
        import math
        def integral(s):
            return self.a * (Decimal(str(math.log(float(self.b * s) + 1))) * s - 
                              Decimal(str(float(s - (1/self.b) * math.log(float(self.b * s) + 1)))))
        cost = integral(supply + amount) - integral(supply)
        return cost, self.price(supply + amount)
    
    def sell_price(self, supply: Decimal, amount: Decimal) -> Tuple[Decimal, Decimal]:
        import math
        def integral(s):
            return self.a * (Decimal(str(math.log(float(self.b * s) + 1))) * s - 
                              Decimal(str(float(s - (1/self.b) * math.log(float(self.b * s) + 1)))))
        recv = integral(supply) - integral(supply - amount)
        return recv, self.price(supply - amount)
