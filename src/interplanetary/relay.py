"""Interplanetary relay for routing bundles across planetary links."""
from dataclasses import dataclass
from typing import Dict, List, Optional
import time

@dataclass
class RelayConfig:
    relay_id:       str
    planet:         str  # earth, mars, moon, venus
    antenna_gain:   float  # dBi
    transmit_power: float  # watts
    min_elevation:  float  # degrees

@dataclass
class InterplanetaryRelay:
    """
    Routes ATLAS bundles across interplanetary links.
    Handles orbit prediction and contact scheduling.
    """
    config:     RelayConfig
    dtn:        object  # DelayTolerantNetwork
    uplink_queue:   List[dict] = None
    downlink_queue: List[dict] = None

    def __post_init__(self):
        self.uplink_queue = []
        self.downlink_queue = []

    def queue_uplink(self, bundle_id: str, dest_planet: str, priority: int = 2) -> None:
        self.uplink_queue.append({
            "bundle_id": bundle_id,
            "dest": dest_planet,
            "priority": priority,
            "queued_at": time.time(),
        })
        self.uplink_queue.sort(key=lambda x: (-x["priority"], x["queued_at"]))

    def process_uplink(self, window: object) -> List[str]:
        """Process queued bundles during a contact window."""
        sent = []
        capacity = window.data_capacity_bytes
        remaining = capacity
        i = 0
        while i < len(self.uplink_queue) and remaining > 0:
            item = self.uplink_queue[i]
            bundle = self.dtn.bundle_store.get(item["bundle_id"])
            if bundle and len(bundle.payload) <= remaining:
                self.dtn.forward_bundle(item["bundle_id"], window.dest_node)
                sent.append(item["bundle_id"])
                remaining -= len(bundle.payload)
                self.uplink_queue.pop(i)
            else:
                i += 1
        return sent

    def estimate_queue_delay(self, dest_planet: str) -> float:
        """Estimate delay for pending uplink bundles."""
        queued = [q for q in self.uplink_queue if q["dest"] == dest_planet]
        if not queued:
            return 0.0
        window = self.dtn.get_next_window(dest_planet)
        if not window:
            return float('inf')
        return window.start_time - time.time()
