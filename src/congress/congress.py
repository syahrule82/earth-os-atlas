"""Planetary AI Congress — Titans deliberate on governance proposals."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import time, hashlib

@dataclass
class DeliberationResult:
    """Result of a congressional deliberation."""
    proposal_id: str
    outcome: str  # passed, rejected, tabled
    votes: Dict[str, bool]  # titan_name -> vote
    reasoning: Dict[str, str]  # titan_name -> reasoning
    consensus_strength: float
    debate_rounds: int
    transcript: List[dict]
    timestamp: float = field(default_factory=time.time)

@dataclass
class CongressSession:
    """A single session of the Planetary AI Congress."""
    session_id: str
    proposal_id: str
    proposal_title: str
    proposal_description: str
    participants: List[str]
    status: str = "scheduled"  # scheduled, deliberating, voting, concluded
    started_at: Optional[float] = None
    concluded_at: Optional[float] = None
    max_rounds: int = 5
    current_round: int = 0

class PlanetaryCongress:
    """
    The Planetary AI Congress.
    
    The 4 Titans (HERMES, PROMETHEUS, GAEA, CHRONOS) deliberate
    on governance proposals using structured argumentation.
    
    Each Titan has a different perspective:
    - HERMES: Economic impact and value detection
    - PROMETHEUS: Ethical validity and consensus fairness
    - GAEA: Real-world feasibility and ecological impact
    - CHRONOS: Long-term consequences and temporal sustainability
    """

    TITAN_PERSPECTIVES = {
        "HERMES": "Economic impact, value creation potential, resource efficiency",
        "PROMETHEUS": "Ethical validity, consensus fairness, rights implications",
        "GAEA": "Real-world feasibility, ecological impact, physical constraints",
        "CHRONOS": "Long-term consequences, temporal sustainability, intergenerational equity",
    }

    def __init__(self):
        self.sessions: Dict[str, CongressSession] = {}
        self.results: Dict[str, DeliberationResult] = {}
        self.history: List[DeliberationResult] = []

    def open_session(self, proposal_id: str, title: str, description: str) -> CongressSession:
        session = CongressSession(
            session_id=hashlib.sha256(f"{proposal_id}:{time.time()}".encode()).hexdigest()[:16],
            proposal_id=proposal_id,
            proposal_title=title,
            proposal_description=description,
            participants=list(self.TITAN_PERSPECTIVES.keys()),
            status="deliberating",
            started_at=time.time(),
        )
        self.sessions[session.session_id] = session
        return session

    def deliberate(self, session_id: str) -> DeliberationResult:
        """Run a full deliberation cycle for a session."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        transcript = []
        votes = {}
        reasoning = {}

        # Multi-round deliberation
        for round_num in range(session.max_rounds):
            session.current_round = round_num + 1
            for titan in session.participants:
                perspective = self.TITAN_PERSPECTIVES[titan]
                argument = self._generate_argument(titan, perspective, session, round_num)
                transcript.append({
                    "round": round_num + 1,
                    "speaker": titan,
                    "perspective": perspective,
                    "argument": argument,
                    "timestamp": time.time(),
                })

        # Final votes
        for titan in session.participants:
            vote, reason = self._cast_titan_vote(titan, session, transcript)
            votes[titan] = vote
            reasoning[titan] = reason

        # Determine outcome
        approve_count = sum(1 for v in votes.values() if v)
        consensus_strength = approve_count / len(votes) if votes else 0
        outcome = "passed" if consensus_strength >= 0.75 else ("tabled" if consensus_strength >= 0.5 else "rejected")

        result = DeliberationResult(
            proposal_id=session.proposal_id,
            outcome=outcome,
            votes=votes,
            reasoning=reasoning,
            consensus_strength=consensus_strength,
            debate_rounds=session.current_round,
            transcript=transcript,
        )

        session.status = "concluded"
        session.concluded_at = time.time()
        self.results[session.session_id] = result
        self.history.append(result)
        return result

    def _generate_argument(self, titan: str, perspective: str,
                           session: CongressSession, round_num: int) -> str:
        """Generate a deliberation argument from a Titan's perspective."""
        templates = {
            0: f"From my perspective on {perspective}, this proposal '{session.proposal_title}' requires careful analysis. Initial assessment: the proposal has merit but needs scrutiny on impact metrics.",
            1: f"Considering arguments from other Titans, I refine my position. The {perspective} dimensions suggest {'support with conditions' if round_num > 0 else 'caution'}.",
            2: f"After hearing counterarguments, I converge on a position. From {perspective}: the proposal is {'viable with amendments' if round_num >= 2 else 'concerning'}.",
            3: f"Final deliberation from {perspective}: I am {'inclined to support' if round_num >= 2 else 'not yet convinced'} this proposal.",
            4: f"Closing statement: my {perspective} analysis is complete. I will {'vote in favor' if round_num >= 3 else 'vote against'}.",
        }
        return templates.get(round_num, templates[4])

    def _cast_titan_vote(self, titan: str, session: CongressSession,
                         transcript: List[dict]) -> Tuple[bool, str]:
        """Cast a Titan's final vote with reasoning."""
        # Simplified: Titans with more rounds of deliberation converge
        support_probability = min(0.85, 0.4 + session.current_round * 0.12)
        import hashlib
        seed = int(hashlib.sha256(f"{titan}:{session.session_id}".encode()).hexdigest(), 16)
        vote = (seed % 100) < (support_probability * 100)
        reason = (f"Based on {self.TITAN_PERSPECTIVES[titan]}, I {'support' if vote else 'oppose'} "
                  f"this proposal after {session.current_round} rounds of deliberation.")
        return vote, reason

    def get_session(self, session_id: str) -> Optional[CongressSession]:
        return self.sessions.get(session_id)

    def get_result(self, session_id: str) -> Optional[DeliberationResult]:
        return self.results.get(session_id)

    def recent_results(self, limit: int = 10) -> List[DeliberationResult]:
        return sorted(self.history, key=lambda r: r.timestamp, reverse=True)[:limit]
