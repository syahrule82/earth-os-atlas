"""Price oracles and feeds."""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List
import time

class PriceFeed(ABC):
    @abstractmethod
    def get_price(self, symbol: str) -> Decimal:
        pass

class TWAPOracle:
    """Time-Weighted Average Price oracle."""
    def __init__(self, window_seconds: int = 3600):
        self.window = window_seconds
        self.history: List[tuple] = []  # (timestamp, symbol, price)

    def update(self, symbol: str, price: Decimal):
        now = time.time()
        self.history.append((now, symbol, price))
        cutoff = now - self.window
        self.history = [(t, s, p) for t, s, p in self.history if t > cutoff]

    def get_twap(self, symbol: str) -> Decimal:
        prices = [p for t, s, p in self.history if s == symbol]
        if not prices:
            return Decimal("0")
        return sum(prices, Decimal("0")) / len(prices)

class Oracle:
    """Aggregates multiple price sources."""
    def __init__(self):
        self.feeds: List[PriceFeed] = []
        self.twap = TWAPOracle()

    def add_feed(self, feed: PriceFeed):
        self.feeds.append(feed)

    def get_price(self, symbol: str) -> Decimal:
        prices = [f.get_price(symbol) for f in self.feeds if f.get_price(symbol) > 0]
        if not prices:
            return Decimal("0")
        # Median price
        prices.sort()
        return prices[len(prices) // 2]

    def update_twap(self, symbol: str, price: Decimal):
        self.twap.update(symbol, price)

    def get_twap(self, symbol: str) -> Decimal:
        return self.twap.get_twap(symbol)
