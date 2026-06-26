"""
PROMETHEUS Validation Layer
Decentralized consensus for validating value creation.
Liquid democracy + reputation-weighted voting.
"""
from dataclasses import dataclass
from typing import Dict, Set
import hashlib, time


@dataclass
class ValidationResult:
    proof_id:   str
    is_valid:   bool
    confidence: float
    timestamp:  float
    result_hash: str


class PROMETHEUSValidator:
    """Consensus engine for truth validation."""

    def __init__(self, min_consensus: float = 0.67, min_voters: int = 3):
        self.min_consensus = min_consensus
        self.min_voters    = min_voters
        self.reputation: Dict[str, float] = {}
        self.validated: Set[str] = set()

    def register_voter(self, voter_id: str, rep: float = 1.0) -> None:
        self.reputation[voter_id] = rep

    def validate(self, proof_id: str, votes: Dict[str, bool]) -> ValidationResult:
        total   = sum(self.reputation.get(v, 0.1) for v in votes)
        approve = sum(self.reputation.get(v, 0.1) for v, d in votes.items() if d)
        confidence = approve / total if total > 0 else 0.0
        is_valid   = confidence >= self.min_consensus and len(votes) >= self.min_voters
        if is_valid:
            self.validated.add(proof_id)
        result_hash = hashlib.sha256(f"{proof_id}:{confidence:.4f}".encode()).hexdigest()[:16]
        return ValidationResult(
            proof_id=proof_id, is_valid=is_valid,
            confidence=confidence, timestamp=time.time(),
            result_hash=result_hash,
        )
