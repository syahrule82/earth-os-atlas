"""
HERMES — The Messenger Titan
Discovers value signals across the global mesh.
Operates 24/7 across economic, ecological, and social dimensions.
"""
import time
from dataclasses import dataclass
from enum import Enum
from typing import List


class SignalType(Enum):
    ECONOMIC       = "economic"
    KNOWLEDGE      = "knowledge"
    INFRASTRUCTURE = "infrastructure"
    ECOLOGICAL     = "ecological"
    SOCIAL         = "social"


@dataclass
class ValueSignal:
    signal_id:     str
    signal_type:   SignalType
    magnitude:     float
    source_region: str
    confidence:    float
    timestamp:     float


class HermesAgent:
    """Global value-signal sensor. Runs 24/7 across the Synaptic Mesh."""

    def __init__(self, sensor_count: int = 10_000):
        self.sensor_count = sensor_count
        self.signals: List[ValueSignal] = []
        self.processed = 0

    def scan(self, n_samples: int = 100) -> List[ValueSignal]:
        """Simulate a sensor sweep and return new signals."""
        new_signals = []
        for i in range(n_samples):
            sig = ValueSignal(
                signal_id     = f"sig_{self.processed + i}",
                signal_type   = list(SignalType)[hash(str(i)) % len(SignalType)],
                magnitude     = 10 + (abs(hash(str(i))) % 990),
                source_region = f"region_{abs(hash(str(i))) % 195}",
                confidence    = 0.6 + (abs(hash(str(i))) % 40) / 100,
                timestamp     = time.time(),
            )
            new_signals.append(sig)
        self.signals.extend(new_signals)
        self.processed += n_samples
        return new_signals

    def high_confidence(self, threshold: float = 0.85) -> List[ValueSignal]:
        """Return signals above confidence threshold."""
        return [s for s in self.signals if s.confidence >= threshold]
