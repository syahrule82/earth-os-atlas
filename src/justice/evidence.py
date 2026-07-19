"""Evidence chain — cryptographically verified evidence."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import hashlib, time

@dataclass
class EvidenceItem:
    evidence_id: str
    evidence_type: str  # document, neural_recording, transaction_log, witness_statement, ipfs_artifact
    submitted_by: str
    content_hash: str
    ipfs_cid: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    verified: bool = False
    chain_hash: Optional[str] = None  # Links to previous evidence in chain

class EvidenceChain:
    """
    Cryptographic chain of evidence for dispute resolution.
    Each piece of evidence is linked to the previous via hash chain.
    """

    def __init__(self):
        self.evidence: Dict[str, EvidenceItem] = {}
        self.chain_order: List[str] = []
        self.last_hash: str = "genesis"

    def submit(self, evidence_type: str, submitted_by: str,
               content: bytes, ipfs_cid: str = None,
               metadata: dict = None) -> EvidenceItem:
        """Submit a new piece of evidence."""
        content_hash = hashlib.sha256(content).hexdigest()
        chain_hash = hashlib.sha256(
            (self.last_hash + content_hash).encode()
        ).hexdigest()

        item = EvidenceItem(
            evidence_id=hashlib.sha256(f"{submitted_by}:{time.time()}".encode()).hexdigest()[:16],
            evidence_type=evidence_type,
            submitted_by=submitted_by,
            content_hash=content_hash,
            ipfs_cid=ipfs_cid,
            metadata=metadata or {},
            verified=True,
            chain_hash=chain_hash,
        )
        self.evidence[item.evidence_id] = item
        self.chain_order.append(item.evidence_id)
        self.last_hash = chain_hash
        return item

    def verify_chain(self) -> bool:
        """Verify the integrity of the entire evidence chain."""
        expected_hash = "genesis"
        for eid in self.chain_order:
            item = self.evidence[eid]
            computed = hashlib.sha256(
                (expected_hash + item.content_hash).encode()
            ).hexdigest()
            if item.chain_hash != computed:
                return False
            expected_hash = item.chain_hash
        return True

    def get_chain(self) -> List[EvidenceItem]:
        return [self.evidence[eid] for eid in self.chain_order]

    def get_by_type(self, evidence_type: str) -> List[EvidenceItem]:
        return [e for e in self.evidence.values() if e.evidence_type == evidence_type]
