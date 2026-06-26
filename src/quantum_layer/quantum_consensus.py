"""
Quantum Consensus — Leaderless agreement via quantum randomness.
Unbiased leader selection using cryptographic entropy beacon.
"""
from typing import Set
import hashlib


class QuantumConsensus:
    """
    Quantum-random leader selection for consensus rounds.
    In production: quantum random number beacon (NIST/QRNG).
    """

    def __init__(self, validators: Set[str]):
        self.validators = validators

    def select_leader(self, round_number: int, prev_block_hash: str) -> str:
        """Deterministic but unpredictable leader selection."""
        entropy = f"{round_number}:{prev_block_hash}".encode()
        seed    = hashlib.sha256(entropy).digest()
        index   = int.from_bytes(seed[:4], "big") % len(self.validators)
        return sorted(self.validators)[index]

    def verify_leader(
        self, proposer: str, round_number: int, prev_block_hash: str
    ) -> bool:
        return proposer == self.select_leader(round_number, prev_block_hash)
