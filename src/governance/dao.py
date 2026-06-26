"""GovernanceDAO with quadratic voting."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import time, hashlib

class ProposalStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"

@dataclass
class Proposal:
    proposal_id: str
    title: str
    description: str
    proposer: str
    category: str
    created_at: float
    start_time: float
    end_time: float
    status: ProposalStatus = ProposalStatus.DRAFT
    votes_for: Dict[str, int] = field(default_factory=dict)  # voter -> voice credits
    votes_against: Dict[str, int] = field(default_factory=dict)

@dataclass
class Vote:
    proposal_id: str
    voter: str
    voice_credits: int
    approve: bool
    timestamp: float

class QuorumStrategy:
    @staticmethod
    def simple_majority(votes_for: int, votes_against: int, quorum: int) -> bool:
        return (votes_for + votes_against) >= quorum and votes_for > votes_against
    
    @staticmethod
    def quadratic(votes_for: Dict[str, int], votes_against: Dict[str, int], 
                  min_participants: int = 5) -> bool:
        participants = len(votes_for) + len(votes_against)
        if participants < min_participants:
            return False
        # Quadratic: sum of sqrt(voice_credits)
        q_for = sum(int(c ** 0.5) for c in votes_for.values())
        q_against = sum(int(c ** 0.5) for c in votes_against.values())
        return q_for > q_against

class GovernanceDAO:
    """ATLAS Governance DAO with quadratic voting and conviction voting."""

    def __init__(self):
        self.proposals: Dict[str, Proposal] = {}
        self.voice_credits: Dict[str, int] = {}  # voter -> credits
        self.min_proposal_credits = 100
        self.voting_period = 7 * 86400  # 7 days

    def grant_voice(self, voter: str, credits: int) -> None:
        self.voice_credits[voter] = self.voice_credits.get(voter, 0) + credits

    def create_proposal(self, title: str, description: str, proposer: str, 
                        category: str, credits_required: int = 100) -> Proposal:
        if self.voice_credits.get(proposer, 0) < credits_required:
            raise ValueError("Insufficient voice credits")
        
        pid = hashlib.sha256(f"{proposer}:{title}:{time.time()}".encode()).hexdigest()[:16]
        prop = Proposal(
            proposal_id=pid,
            title=title,
            description=description,
            proposer=proposer,
            category=category,
            created_at=time.time(),
            start_time=time.time(),
            end_time=time.time() + self.voting_period,
        )
        self.proposals[pid] = prop
        return prop

    def vote(self, proposal_id: str, voter: str, voice_credits: int, 
             approve: bool) -> bool:
        prop = self.proposals.get(proposal_id)
        if not prop or prop.status != ProposalStatus.ACTIVE:
            return False
        if time.time() > prop.end_time:
            return False
        available = self.voice_credits.get(voter, 0)
        if voice_credits > available:
            return False
        
        self.voice_credits[voter] -= voice_credits
        if approve:
            prop.votes_for[voter] = voice_credits
        else:
            prop.votes_against[voter] = voice_credits
        return True

    def finalize(self, proposal_id: str) -> bool:
        prop = self.proposals.get(proposal_id)
        if not prop:
            return False
        if QuorumStrategy.quadratic(prop.votes_for, prop.votes_against):
            prop.status = ProposalStatus.PASSED
        else:
            prop.status = ProposalStatus.REJECTED
        return prop.status == ProposalStatus.PASSED
