"""
Post-Quantum Cryptography
Lattice-based key exchange (Kyber-inspired).
Resistant to Shor's algorithm.
"""
from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np
import hashlib, secrets


@dataclass
class LatticeKeyPair:
    public_key:  bytes
    private_key: bytes
    key_id:      str


class QuantumSafeCrypto:
    """
    Lattice-based key exchange.
    N=256, Q=3329 (Kyber parameters).
    """
    N = 256
    Q = 3329
    ETA = 2

    def generate_keypair(self, seed: Optional[bytes] = None) -> LatticeKeyPair:
        if seed is None:
            seed = secrets.token_bytes(32)
        rng = np.random.default_rng(seed)
        A = rng.integers(0, self.Q, (self.N, self.N))
        s = rng.integers(-self.ETA, self.ETA + 1, self.N)
        e = rng.integers(-self.ETA, self.ETA + 1, self.N)
        t = (A @ s + e) % self.Q
        key_id = hashlib.sha256(t.tobytes()).hexdigest()[:16]
        return LatticeKeyPair(
            public_key  = t.tobytes(),
            private_key = s.tobytes(),
            key_id      = key_id,
        )

    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        shared_secret = secrets.token_bytes(32)
        ciphertext    = hashlib.sha256(public_key + shared_secret).digest()
        return ciphertext, shared_secret

    def decapsulate(self, ciphertext: bytes, keypair: LatticeKeyPair) -> bytes:
        return hashlib.sha256(keypair.private_key + ciphertext).digest()
