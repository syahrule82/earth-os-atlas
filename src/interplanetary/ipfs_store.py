"""IPFS content store for ATLAS proof artifacts."""
from dataclasses import dataclass
from typing import Dict, Optional
import hashlib, time

@dataclass
class ContentID:
    cid:       str
    size:      int
    codec:     str = "dag-pb"
    version:   int = 1
    created:   float = 0

    def __post_init__(self):
        if self.created == 0:
            self.created = time.time()

class IPFSStore:
    """Local IPFS-compatible content store."""

    def __init__(self):
        self.blocks: Dict[str, bytes] = {}
        self.pins: set = set()
        self.stats = {"stored": 0, "retrieved": 0, "pinned": 0}

    def store(self, data: bytes, pin: bool = True) -> ContentID:
        """Store data and return ContentID."""
        cid = self._compute_cid(data)
        self.blocks[cid] = data
        if pin:
            self.pins.add(cid)
            self.stats["pinned"] += 1
        self.stats["stored"] += 1
        return ContentID(cid=cid, size=len(data))

    def retrieve(self, cid: str) -> Optional[bytes]:
        data = self.blocks.get(cid)
        if data:
            self.stats["retrieved"] += 1
        return data

    def pin(self, cid: str) -> bool:
        if cid in self.blocks:
            self.pins.add(cid)
            return True
        return False

    def unpin(self, cid: str) -> None:
        self.pins.discard(cid)

    def gc(self) -> int:
        """Remove unpinned blocks. Returns count removed."""
        removable = set(self.blocks.keys()) - self.pins
        for cid in removable:
            del self.blocks[cid]
        return len(removable)

    def _compute_cid(self, data: bytes) -> str:
        """Compute CIDv1 (simplified — real IPFS uses multihash + multicodec)."""
        digest = hashlib.sha256(data).hexdigest()
        return f"bafy{digest[:56]}"

    @property
    def storage_size(self) -> int:
        return sum(len(b) for b in self.blocks.values())
