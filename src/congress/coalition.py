"""Coalition formation — Titans form voting coalitions."""
from dataclasses import dataclass, field
from typing import Dict, List, Set
import time, hashlib

@dataclass
class Coalition:
    coalition_id: str
    name: str
    members: List[str]
    platform: str
    formed_at: float = field(default_factory=time.time)
    voting_weight: float = 0.0
    active: bool = True

class CoalitionFormer:
    """Forms and dissolves coalitions among Congress participants."""

    def __init__(self):
        self.coalitions: Dict[str, Coalition] = {}
        self.member_coalitions: Dict[str, str] = {}  # member -> coalition_id

    def form_coalition(self, name: str, members: List[str],
                       platform: str, voting_weight: float) -> Coalition:
        coalition = Coalition(
            coalition_id=hashlib.sha256(f"{name}:{time.time()}".encode()).hexdigest()[:16],
            name=name, members=members, platform=platform,
            voting_weight=voting_weight,
        )
        self.coalitions[coalition.coalition_id] = coalition
        for member in members:
            self.member_coalitions[member] = coalition.coalition_id
        return coalition

    def dissolve_coalition(self, coalition_id: str) -> bool:
        coalition = self.coalitions.get(coalition_id)
        if not coalition:
            return False
        coalition.active = False
        for member in coalition.members:
            self.member_coalitions.pop(member, None)
        return True

    def get_coalition(self, member: str) -> Optional[Coalition]:
        cid = self.member_coalitions.get(member)
        return self.coalitions.get(cid) if cid else None

    def active_coalitions(self) -> List[Coalition]:
        return [c for c in self.coalitions.values() if c.active]

    def total_weight(self) -> float:
        return sum(c.voting_weight for c in self.active_coalitions())
