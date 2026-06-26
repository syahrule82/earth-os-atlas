"""
Valence Tracker — Emotional State Monitor
Russell Circumplex Model: valence × arousal.
Data: EEG frontal alpha asymmetry, GSR, HRV.
"""
from dataclasses import dataclass, field
from typing import List, Tuple
import numpy as np, time


@dataclass
class ValenceReading:
    valence:   float   # -1 (negative) to +1 (positive)
    arousal:   float   # -1 (calm) to +1 (activated)
    timestamp: float = field(default_factory=time.time)
    source:    str = "biometric"

    @property
    def quadrant(self) -> str:
        if self.valence >= 0 and self.arousal >= 0: return "excited"
        if self.valence >= 0 and self.arousal <  0: return "content"
        if self.valence <  0 and self.arousal >= 0: return "distressed"
        return "depressed"


class ValenceTracker:
    def __init__(self, window: int = 256, alpha: float = 0.05):
        self.window  = window
        self.alpha   = alpha
        self._data:  List[ValenceReading] = []
        self._ema_v  = 0.0
        self._ema_a  = 0.0

    def ingest(self, valence: float, arousal: float, source: str = "biometric") -> ValenceReading:
        r = ValenceReading(
            valence=float(np.clip(valence, -1, 1)),
            arousal=float(np.clip(arousal, -1, 1)),
            source=source,
        )
        self._data.append(r)
        if len(self._data) > self.window:
            self._data.pop(0)
        self._ema_v = (1 - self.alpha) * self._ema_v + self.alpha * r.valence
        self._ema_a = (1 - self.alpha) * self._ema_a + self.alpha * r.arousal
        return r

    @property
    def current_quadrant(self) -> str:
        return ValenceReading(self._ema_v, self._ema_a).quadrant

    def distress_alert(self, threshold: float = -0.6) -> bool:
        return self._ema_v < threshold

    def stability(self) -> float:
        if len(self._data) < 4:
            return 1.0
        v = np.array([r.valence for r in self._data])
        a = np.array([r.arousal for r in self._data])
        return float(np.clip(1.0 - (v.std() + a.std()) / 2, 0, 1))
