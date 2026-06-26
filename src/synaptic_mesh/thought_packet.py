"""
Thought Packet — The fundamental unit of neural communication.
Quantum-encrypted, latency-optimized, self-describing.
"""
from dataclasses import dataclass
from enum import Enum
import hashlib, time


class PacketPriority(Enum):
    EMERGENCY  = 0
    URGENT     = 1
    NORMAL     = 2
    BACKGROUND = 3


@dataclass(frozen=True)
class ThoughtPacket:
    packet_id:         str
    source_address:    str
    destination_address: str
    payload_hash:      str
    priority:          PacketPriority
    cognitive_signature: str
    timestamp_ns:      int
    ttl:               int  # hops remaining

    def checksum(self) -> str:
        data = f"{self.packet_id}:{self.source_address}:{self.timestamp_ns}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def is_expired(self, max_age_ms: int = 5000) -> bool:
        age_ms = (time.time_ns() - self.timestamp_ns) // 1_000_000
        return age_ms > max_age_ms or self.ttl <= 0
