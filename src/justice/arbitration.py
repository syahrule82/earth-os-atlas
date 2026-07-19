"""Decentralized arbitration with 3-tier escalation."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import hashlib, time

class DisputeType(Enum):
    MINTING_DISPUTE = "minting_dispute"
    SLASHING_APPEAL = "slashing_appeal"
    RIGHTS_VIOLATION = "rights_violation"
    BRIDGE_DISPUTE = "bridge_dispute"
    GOVERNANCE_CHALLENGE = "governance_challenge"
    CONTRACT_DISPUTE = "contract_dispute"

class DisputeStatus(Enum):
    FILED = "filed"
    IN_REVIEW = "in_review"
    ARBITRATING = "arbitrating"
    RESOLVED = "resolved"
    APPEALED = "appealed"
    ESCALATED = "escalated"
    CLOSED = "closed"

@dataclass
class Arbitrator:
    arbitrator_id: str
    reputation: float
    specializations: List[DisputeType]
    tier: int  # 1, 2, or 3
    active: bool = True
    cases_resolved: int = 0
    accuracy_score: float = 1.0

@dataclass
class Ruling:
    ruling_id: str
    dispute_id: str
    arbitrator_id: str
    decision: str  # in_favor_of_claimant, in_favor_of_respondent, split
    reasoning: str
    damages: Optional[float] = None
    precedent_set: bool = False
    timestamp: float = field(default_factory=time.time)
    tier: int = 1

@dataclass
class Dispute:
    dispute_id: str
    dispute_type: DisputeType
    claimant: str
    respondent: str
    description: str
    evidence_ids: List[str]
    status: DisputeStatus = DisputeStatus.FILED
    tier: int = 1
    filed_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    ruling: Optional[Ruling] = None
    appeal_deadline: Optional[float] = None

class ArbitrationSystem:
    """
    3-tier decentralized arbitration:
    - Tier 1: 3 arbitrators, simple majority
    - Tier 2: 7 arbitrators, 2/3 supermajority
    - Tier 3: 21 arbitrators, 3/4 supermajority (final)
    """

    TIER_CONFIG = {
        1: {"arbitrators": 3, "threshold": 0.50, "appeal_days": 7},
        2: {"arbitrators": 7, "threshold": 0.67, "appeal_days": 14},
        3: {"arbitrators": 21, "threshold": 0.75, "appeal_days": 0},  # Final
    }

    def __init__(self):
        self.disputes: Dict[str, Dispute] = {}
        self.arbitrators: Dict[str, Arbitrator] = {}
        self.rulings: List[Ruling] = []

    def register_arbitrator(self, arbitrator_id: str, reputation: float,
                            specializations: List[DisputeType], tier: int = 1) -> Arbitrator:
        arb = Arbitrator(
            arbitrator_id=arbitrator_id,
            reputation=reputation,
            specializations=specializations,
            tier=tier,
        )
        self.arbitrators[arbitrator_id] = arb
        return arb

    def file_dispute(self, dispute_type: DisputeType, claimant: str,
                     respondent: str, description: str, evidence_ids: List[str]) -> Dispute:
        dispute = Dispute(
            dispute_id=hashlib.sha256(f"{claimant}:{respondent}:{time.time()}".encode()).hexdigest()[:16],
            dispute_type=dispute_type, claimant=claimant,
            respondent=respondent, description=description,
            evidence_ids=evidence_ids,
        )
        self.disputes[dispute.dispute_id] = dispute
        return dispute

    def assign_arbitrators(self, dispute_id: str) -> List[Arbitrator]:
        """Assign arbitrators to a dispute based on tier and specialization."""
        dispute = self.disputes.get(dispute_id)
        if not dispute:
            return []
        config = self.TIER_CONFIG[dispute.tier]
        eligible = [a for a in self.arbitrators.values()
                     if a.active and a.tier == dispute.tier
                     and dispute.dispute_type in a.specializations]
        # Sort by reputation and take top N
        eligible.sort(key=lambda a: a.reputation, reverse=True)
        selected = eligible[:config["arbitrators"]]
        dispute.status = DisputeStatus.ARBITRATING
        return selected

    def render_ruling(self, dispute_id: str, arbitrator_id: str,
                      decision: str, reasoning: str,
                      damages: float = None) -> Ruling:
        """Render a ruling on a dispute."""
        dispute = self.disputes.get(dispute_id)
        if not dispute:
            raise ValueError("Dispute not found")
        ruling = Ruling(
            ruling_id=hashlib.sha256(f"{dispute_id}:{arbitrator_id}:{time.time()}".encode()).hexdigest()[:16],
            dispute_id=dispute_id, arbitrator_id=arbitrator_id,
            decision=decision, reasoning=reasoning,
            damages=damages, tier=dispute.tier,
        )
        self.rulings.append(ruling)
        dispute.ruling = ruling
        dispute.status = DisputeStatus.RESOLVED
        dispute.resolved_at = time.time()
        config = self.TIER_CONFIG[dispute.tier]
        if config["appeal_days"] > 0:
            dispute.appeal_deadline = time.time() + config["appeal_days"] * 86400
        # Update arbitrator stats
        arb = self.arbitrators.get(arbitrator_id)
        if arb:
            arb.cases_resolved += 1
        return ruling

    def appeal(self, dispute_id: str) -> bool:
        """Appeal a ruling to the next tier."""
        dispute = self.disputes.get(dispute_id)
        if not dispute or dispute.status != DisputeStatus.RESOLVED:
            return False
        if dispute.tier >= 3:
            return False  # Already at highest tier
        if dispute.appeal_deadline and time.time() > dispute.appeal_deadline:
            return False
        dispute.tier += 1
        dispute.status = DisputeStatus.ESCALATED
        dispute.ruling = None
        dispute.resolved_at = None
        return True

    def get_disputes(self, party: str = None, status: DisputeStatus = None) -> List[Dispute]:
        results = list(self.disputes.values())
        if party:
            results = [d for d in results if d.claimant == party or d.respondent == party]
        if status:
            results = [d for d in results if d.status == status]
        return results
