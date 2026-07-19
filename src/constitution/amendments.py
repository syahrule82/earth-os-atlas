"""Constitutional amendment process."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time, hashlib

@dataclass
class AmendmentProposal:
    proposal_id: str
    article_id: int
    proposer: str
    title: str
    description: str
    current_text: str
    proposed_text: str
    proposed_rule_code: str
    status: str = "draft"  # draft, open, debated, voting, ratified, rejected
    debate_period_days: int = 14
    voting_period_days: int = 7
    created_at: float = field(default_factory=time.time)
    debate_ends: Optional[float] = None
    voting_ends: Optional[float] = None
    votes_for: int = 0
    votes_against: int = 0
    debate_comments: List[dict] = field(default_factory=list)

class AmendmentProcess:
    """Formal process for amending the ATLAS Constitution."""

    PROTECTED_ARTICLES = {1, 2, 3, 4, 5}  # Fundamental Rights
    STANDARD_SUPERMAJORITY = 0.75
    PROTECTED_SUPERMAJORITY = 0.90
    MIN_DEBATE_PARTICIPANTS = 20
    MIN_VOTERS = 100

    def __init__(self):
        self.proposals: Dict[str, AmendmentProposal] = {}

    def create_proposal(self, article_id: int, proposer: str,
                        title: str, description: str,
                        current_text: str, proposed_text: str,
                        proposed_rule: str) -> AmendmentProposal:
        proposal = AmendmentProposal(
            proposal_id=hashlib.sha256(f"{article_id}:{proposer}:{time.time()}".encode()).hexdigest()[:16],
            article_id=article_id, proposer=proposer,
            title=title, description=description,
            current_text=current_text, proposed_text=proposed_text,
            proposed_rule_code=proposed_rule,
            status="open",
            debate_ends=time.time() + self.DEBATE_PERIOD_DAYS * 86400,
        )
        self.proposals[proposal.proposal_id] = proposal
        return proposal

    def add_debate_comment(self, proposal_id: str, commenter: str,
                           position: str, argument: str) -> None:
        proposal = self.proposals.get(proposal_id)
        if not proposal or proposal.status != "open":
            return
        proposal.debate_comments.append({
            "commenter": commenter,
            "position": position,  # support, oppose, neutral
            "argument": argument,
            "timestamp": time.time(),
        })

    def start_voting(self, proposal_id: str) -> bool:
        proposal = self.proposals.get(proposal_id)
        if not proposal or proposal.status != "open":
            return False
        if time.time() < proposal.debate_ends:
            return False
        if len(set(c["commenter"] for c in proposal.debate_comments)) < self.MIN_DEBATE_PARTICIPANTS:
            return False
        proposal.status = "voting"
        proposal.voting_ends = time.time() + proposal.voting_period_days * 86400
        return True

    def cast_vote(self, proposal_id: str, vote: bool) -> None:
        proposal = self.proposals.get(proposal_id)
        if not proposal or proposal.status != "voting":
            return
        if vote:
            proposal.votes_for += 1
        else:
            proposal.votes_against += 1

    def finalize(self, proposal_id: str) -> bool:
        proposal = self.proposals.get(proposal_id)
        if not proposal or proposal.status != "voting":
            return False
        total = proposal.votes_for + proposal.votes_against
        if total < self.MIN_VOTERS:
            proposal.status = "rejected"
            return False
        threshold = (self.PROTECTED_SUPERMAJORITY if proposal.article_id in self.PROTECTED_ARTICLES
                     else self.STANDARD_SUPERMAJORITY)
        ratio = proposal.votes_for / total
        if ratio >= threshold:
            proposal.status = "ratified"
            return True
        else:
            proposal.status = "rejected"
            return False

    def get_required_threshold(self, article_id: int) -> float:
        return self.PROTECTED_SUPERMAJORITY if article_id in self.PROTECTED_ARTICLES else self.STANDARD_SUPERMAJORITY
