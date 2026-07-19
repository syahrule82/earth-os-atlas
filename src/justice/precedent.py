"""Precedent system — past rulings guide future decisions."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time, hashlib

@dataclass
class Precedent:
    precedent_id: str
    dispute_type: str
    ruling_summary: str
    legal_principle: str
    ruling_id: str
    tier: int
    citations: List[str] = field(default_factory=list)  # other precedents cited
    authority: float = 1.0  # higher = more authoritative
    established_at: float = field(default_factory=time.time)

class PrecedentSystem:
    """
    Maintains a body of precedent for consistent dispute resolution.
    Precedents from higher tiers override lower tiers.
    """

    def __init__(self):
        self.precedents: Dict[str, Precedent] = {}
        self.by_type: Dict[str, List[str]] = {}  # dispute_type -> [precedent_ids]

    def register_precedent(self, dispute_type: str, ruling_summary: str,
                           legal_principle: str, ruling_id: str,
                           tier: int = 1, citations: List[str] = None) -> Precedent:
        authority = tier / 3.0  # Tier 3 = 1.0, Tier 1 = 0.33
        precedent = Precedent(
            precedent_id=hashlib.sha256(f"{ruling_id}:{time.time()}".encode()).hexdigest()[:16],
            dispute_type=dispute_type,
            ruling_summary=ruling_summary,
            legal_principle=legal_principle,
            ruling_id=ruling_id,
            tier=tier,
            citations=citations or [],
            authority=authority,
        )
        self.precedents[precedent.precedent_id] = precedent
        if dispute_type not in self.by_type:
            self.by_type[dispute_type] = []
        self.by_type[dispute_type].append(precedent.precedent_id)
        return precedent

    def find_precedents(self, dispute_type: str, limit: int = 5) -> List[Precedent]:
        """Find relevant precedents for a dispute type."""
        ids = self.by_type.get(dispute_type, [])
        precedents = [self.precedents[pid] for pid in ids if pid in self.precedents]
        # Sort by authority then recency
        precedents.sort(key=lambda p: (p.authority, p.established_at), reverse=True)
        return precedents[:limit]

    def get_precedent(self, precedent_id: str) -> Optional[Precedent]:
        return self.precedents.get(precedent_id)

    def total_precedents(self) -> int:
        return len(self.precedents)

    def summary(self) -> dict:
        return {
            "total_precedents": len(self.precedents),
            "by_type": {k: len(v) for k, v in self.by_type.items()},
            "avg_authority": sum(p.authority for p in self.precedents.values()) / max(1, len(self.precedents)),
        }
