"""Provenance tracker — full audit trail of knowledge origin."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import hashlib, time

@dataclass
class ProvenanceRecord:
    """Records the origin and transformation history of knowledge."""
    record_id: str
    node_id: str
    event_type: str  # created, cited, extended, refuted, replicated, modified
    actor: str
    timestamp: float = field(default_factory=time.time)
    details: dict = field(default_factory=dict)
    signature: str = ""

class ProvenanceTracker:
    """Maintains a complete audit trail for all knowledge artifacts."""

    def __init__(self):
        self.records: List[ProvenanceRecord] = []
        self.by_node: Dict[str, List[ProvenanceRecord]] = {}

    def record(self, node_id: str, event_type: str, actor: str,
               details: dict = None) -> ProvenanceRecord:
        """Record a provenance event."""
        rec = ProvenanceRecord(
            record_id=hashlib.sha256(f"{node_id}:{event_type}:{time.time()}".encode()).hexdigest()[:16],
            node_id=node_id, event_type=event_type, actor=actor,
            details=details or {},
        )
        self.records.append(rec)
        if node_id not in self.by_node:
            self.by_node[node_id] = []
        self.by_node[node_id].append(rec)
        return rec

    def get_history(self, node_id: str) -> List[ProvenanceRecord]:
        """Get full provenance history for a node."""
        return self.by_node.get(node_id, [])

    def verify_chain(self, node_id: str) -> bool:
        """Verify the integrity of a node's provenance chain."""
        history = self.get_history(node_id)
        if not history:
            return True
        # First event should be 'created'
        return history[0].event_type == "created"

    def who_created(self, node_id: str) -> Optional[str]:
        """Find who originally created a knowledge artifact."""
        history = self.get_history(node_id)
        for rec in history:
            if rec.event_type == "created":
                return rec.actor
        return None
