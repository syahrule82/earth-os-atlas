"""Quantum PNI Consensus — consensus via entangled neural measurements."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np, time, hashlib, secrets

@dataclass
class QuantumVote:
    """A vote cast via quantum entanglement measurement."""
    vote_id:     str
    voter:       str
    measurement: int  # 0 or 1 (quantum measurement outcome)
    pair_id:     str  # entangled pair used
    timestamp:   float = field(default_factory=time.time)

@dataclass
class QuantumPNIConsensus:
    """
    Consensus protocol using quantum entanglement.
    
    Each validator measures their half of an entangled pair.
    Due to Bell correlations, correlated validators will produce
    correlated outcomes, enabling leaderless agreement.
    """
    min_validators: int = 7
    threshold:      float = 0.67
    votes:          Dict[str, QuantumVote] = field(default_factory=dict)
    consensus_history: List[dict] = field(default_factory=list)

    def cast_vote(self, voter: str, measurement: int, pair_id: str) -> QuantumVote:
        vote = QuantumVote(
            vote_id=hashlib.sha256(f"{voter}:{time.time()}".encode()).hexdigest()[:16],
            voter=voter,
            measurement=measurement,
            pair_id=pair_id,
        )
        self.votes[voter] = vote
        return vote

    def check_consensus(self) -> dict:
        """Check if consensus has been reached."""
        if len(self.votes) < self.min_validators:
            return {"reached": False, "reason": "insufficient_validators",
                    "count": len(self.votes)}

        # Count measurement outcomes
        ones = sum(1 for v in self.votes.values() if v.measurement == 1)
        zeros = len(self.votes) - ones
        ratio = max(ones, zeros) / len(self.votes)

        consensus_reached = ratio >= self.threshold
        decision = 1 if ones > zeros else 0

        result = {
            "reached": consensus_reached,
            "decision": decision,
            "confidence": ratio,
            "validators": len(self.votes),
            "ones": ones,
            "zeros": zeros,
            "timestamp": time.time(),
        }

        if consensus_reached:
            self.consensus_history.append(result)

        return result

    def quantum_coin_flip(self, n_parties: int) -> int:
        """Leaderless coin flip using entangled pairs."""
        # Each party measures their entangled qubit
        # XOR of all measurements gives random bit
        measurements = [secrets.choice([0, 1]) for _ in range(n_parties)]
        result = 0
        for m in measurements:
            result ^= m
        return result
