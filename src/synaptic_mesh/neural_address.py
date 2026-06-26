"""
Neural Addressing System
BCI-compatible hierarchical addressing.
Protocol: neural://{subnet}/{region}/{node_id}/{interface}
"""
from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class NeuralAddress:
    subnet:    str   # e.g. "global", "asia", "private"
    region:    str   # e.g. "prefrontal", "motor"
    node_id:   str   # unique node identifier
    interface: str   # "pni-v3", "eeg", "implant"

    PREFIX = "neural://"

    @property
    def full_address(self) -> str:
        return f"{self.PREFIX}{self.subnet}/{self.region}/{self.node_id}/{self.interface}"

    @classmethod
    def from_string(cls, addr: str) -> "NeuralAddress":
        if addr.startswith(cls.PREFIX):
            addr = addr[len(cls.PREFIX):]
        parts = addr.split("/")
        return cls(subnet=parts[0], region=parts[1], node_id=parts[2], interface=parts[3])

    def compress(self) -> bytes:
        """16-byte wire format."""
        return hashlib.sha256(self.full_address.encode()).digest()[:16]
