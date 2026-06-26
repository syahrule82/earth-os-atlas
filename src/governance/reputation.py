"""Soulbound reputation tokens and contribution records."""
from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum
import time, hashlib

class ContributionType(Enum):
    CODE = "code"
    RESEARCH = "research"
    MEDICAL = "medical"
    ECOLOGICAL = "ecological"
    EDUCATION = "education"
    GOVERNANCE = "governance"

@dataclass
class ContributionRecord:
    record_id: str
    contributor: str
    type: ContributionType
    magnitude: float
    proof_cid: str  # IPFS CID of proof
    timestamp: float
    validators: List[str]

@dataclass
class SoulboundToken:
    """Non-transferable reputation token."""
    token_id: str
    owner: str
    contribution: ContributionRecord
    issued_at: float
    revoked: bool = False

class ReputationSystem:
    """Tracks and computes reputation from contributions."""

    def __init__(self):
        self.records: Dict[str, List[ContributionRecord]] = {}
        self.soulbound: Dict[str, SoulboundToken] = {}

    def add_record(self, record: ContributionRecord) -> None:
        if record.contributor not in self.records:
            self.records[record.contributor] = []
        self.records[record.contributor].append(record)
        
        # Mint soulbound token
        sb = SoulboundToken(
            token_id=hashlib.sha256(f"{record.record_id}".encode()).hexdigest()[:16],
            owner=record.contributor,
            contribution=record,
            issued_at=time.time(),
        )
        self.soulbound[sb.token_id] = sb

    def get_reputation(self, contributor: str) -> float:
        """Calculate reputation score."""
        records = self.records.get(contributor, [])
        if not records:
            return 0.0
        # Weighted sum with recency decay
        score = 0.0
        now = time.time()
        for r in records:
            age_days = (now - r.timestamp) / 86400
            decay = max(0.1, 1.0 - age_days / 365)
            score += r.magnitude * decay
        return score

    def get_soulbound_tokens(self, owner: str) -> List[SoulboundToken]:
        return [s for s in self.soulbound.values() if s.owner == owner and not s.revoked]
