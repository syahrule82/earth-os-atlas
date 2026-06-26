"""
Nanite Node — Individual nano-computation unit.
Simulates bio-molecular computing substrate.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List
import time


class NaniteState(Enum):
    IDLE          = "idle"
    PROCESSING    = "processing"
    COMMUNICATING = "communicating"
    REPAIRING     = "repairing"
    OFFLINE       = "offline"


@dataclass
class NaniteNode:
    node_id:              str
    position:             tuple        # (x, y, z) in micrometers
    energy_level:         float        # 0.0–1.0
    computational_capacity: float     # relative FLOPS
    neighbors:            List[str] = field(default_factory=list)
    state:                NaniteState = NaniteState.IDLE
    last_heartbeat:       float = field(default_factory=time.time)

    def is_alive(self, timeout_ms: float = 100.0) -> bool:
        return (time.time() - self.last_heartbeat) * 1000 < timeout_ms

    def cycle(self) -> None:
        """Advance one simulation cycle."""
        if self.state == NaniteState.PROCESSING:
            self.energy_level -= 0.001
        elif self.state == NaniteState.COMMUNICATING:
            self.energy_level -= 0.0005
        if self.energy_level < 0.05:
            self.state = NaniteState.IDLE
        self.last_heartbeat = time.time()
