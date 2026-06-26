"""
PROMETHEUS — The Fire-Bringer Titan
Decentralized consensus formation.
Liquid democracy + reputation-weighted voting.
"""
from dataclasses import dataclass
from typing import Dict, List
import time


@dataclass
class ConsensusRound:
    round_id:   str
    subject_id: str
    result:     bool
    confidence: float
    timestamp:  float


class PrometheusAgent:
    """Forms consensus on truth claims via weighted voting."""

    def __init__(self, min_voters: int = 7, threshold: float = 0.67):
        self.min_voters = min_voters
        self.threshold  = threshold
        self.reputation: Dict[str, float] = {}
        self.rounds: List[ConsensusRound] = []

    def register_voter(self, voter_id: str, rep: float = 1.0):
        self.reputation[voter_id] = rep

    def form_consensus(
        self, subject_id: str, votes: Dict[str, bool]
    ) -> ConsensusRound:
        total   = sum(self.reputation.get(v, 0.1) for v in votes)
        approve = sum(self.reputation.get(v, 0.1) for v, d in votes.items() if d)
        confidence = approve / total if total > 0 else 0.0
        result     = confidence >= self.threshold and len(votes) >= self.min_voters
        round_obj  = ConsensusRound(
            round_id   = f"round_{len(self.rounds)}",
            subject_id = subject_id,
            result     = result,
            confidence = confidence,
            timestamp  = time.time(),
        )
        self.rounds.append(round_obj)
        return round_obj
