"""Delay-Tolerant Networking for interplanetary ATLAS mesh."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import hashlib, time, struct

@dataclass
class ContactWindow:
    """A scheduled communication window between two nodes."""
    window_id:      str
    source_node:    str
    dest_node:      str
    start_time:     float
    end_time:       float
    bandwidth_bps:  float
    one_way_delay:  float  # seconds (e.g., Earth-Mars: 4-24 min)
    priority:       int = 2

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def data_capacity_bytes(self) -> int:
        return int(self.bandwidth_bps * self.duration / 8)

    @property
    def is_active(self) -> bool:
        now = time.time()
        return self.start_time <= now <= self.end_time

@dataclass
class Bundle:
    """DTN bundle — unit of data in delay-tolerant network."""
    bundle_id:       str
    source:          str
    destination:     str
    payload:         bytes
    created_at:      float
    expires_at:      float
    hop_count:       int = 0
    max_hops:        int = 16
    custody:         bool = True  # reliable delivery
    priority:        int = 2  # 0=bulk, 1=normal, 2=expedited, 3=emergency
    fragmentation:   bool = False
    fragment_offset: int = 0
    total_length:    int = 0

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def can_forward(self) -> bool:
        return self.hop_count < self.max_hops and not self.is_expired()

    def checksum(self) -> str:
        return hashlib.sha256(self.payload).hexdigest()[:16]

class DelayTolerantNetwork:
    """
    Manages data delivery across interplanetary links with
    scheduled contact windows and custody transfer.
    """

    # Known interplanetary link delays (seconds)
    LINK_DELAYS = {
        "earth-moon":      1.3,
        "earth-mars-min":  240,    # 4 minutes (closest approach)
        "earth-mars-max":  1440,   # 24 minutes (farthest)
        "earth-venus":     300,
        "earth-asteroid":  600,
        "mars-moon":       0.5,    # Mars-Phobos
    }

    def __init__(self, local_node: str):
        self.local_node = local_node
        self.contact_schedule: List[ContactWindow] = []
        self.bundle_store: Dict[str, Bundle] = {}
        self.custody_bundles: Dict[str, Bundle] = {}
        self.delivered_bundles: set = set()
        self.statistics = {
            "bundles_sent": 0, "bundles_received": 0,
            "bundles_dropped": 0, "bytes_transferred": 0,
        }

    def schedule_contact(self, window: ContactWindow) -> None:
        self.contact_schedule.append(window)
        self.contact_schedule.sort(key=lambda w: w.start_time)

    def create_bundle(
        self, destination: str, payload: bytes,
        ttl: float = 86400, priority: int = 2,
    ) -> Bundle:
        bundle = Bundle(
            bundle_id   = hashlib.sha256(
                f"{self.local_node}:{destination}:{time.time()}".encode()
            ).hexdigest()[:24],
            source      = self.local_node,
            destination = destination,
            payload     = payload,
            created_at  = time.time(),
            expires_at  = time.time() + ttl,
            priority    = priority,
            total_length = len(payload),
        )
        self.bundle_store[bundle.bundle_id] = bundle
        return bundle

    def forward_bundle(self, bundle_id: str, next_hop: str) -> bool:
        """Forward a bundle to the next hop node."""
        bundle = self.bundle_store.get(bundle_id)
        if not bundle or not bundle.can_forward():
            return False
        if bundle.custody:
            self.custody_bundles[bundle_id] = bundle
        bundle.hop_count += 1
        self.statistics["bundles_sent"] += 1
        self.statistics["bytes_transferred"] += len(bundle.payload)
        return True

    def receive_bundle(self, bundle: Bundle) -> bool:
        """Receive a bundle from another node."""
        if bundle.is_expired():
            self.statistics["bundles_dropped"] += 1
            return False
        if bundle.destination == self.local_node:
            self.delivered_bundles.add(bundle.bundle_id)
            self.statistics["bundles_received"] += 1
            return True
        # Store for further forwarding
        self.bundle_store[bundle.bundle_id] = bundle
        return True

    def get_next_window(self, dest_node: str) -> Optional[ContactWindow]:
        """Find the next available contact window to a destination."""
        now = time.time()
        for w in self.contact_schedule:
            if w.dest_node == dest_node and w.end_time > now:
                return w
        return None

    def pending_bundles(self, dest_node: str = None) -> List[Bundle]:
        """Get bundles waiting for delivery."""
        bundles = [b for b in self.bundle_store.values() if b.can_forward()]
        if dest_node:
            bundles = [b for b in bundles if b.destination == dest_node]
        return sorted(bundles, key=lambda b: -b.priority)

    def estimate_delivery_time(self, dest_node: str) -> Optional[float]:
        """Estimate earliest delivery time to a destination."""
        window = self.get_next_window(dest_node)
        if not window:
            return None
        return window.start_time + window.one_way_delay
