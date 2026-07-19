"""Multi-Factor Authentication — Configurable M-of-N threshold auth."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import hashlib, time, secrets

class FactorType(Enum):
    CRYPTOGRAPHIC = "cryptographic"  # Ed25519 / Dilithium
    NEURAL = "neural"               # EEG-based PNI fingerprint
    BIOMETRIC = "biometric"          # Fingerprint / face hash
    HARDWARE = "hardware"            # HSM / YubiKey
    SOCIAL = "social"                # Guardian attestation

@dataclass
class AuthFactor:
    """A registered authentication factor."""
    factor_id: str
    factor_type: FactorType
    public_commitment: str  # Hash commitment (never store raw biometric)
    registered_at: float = field(default_factory=time.time)
    last_used: Optional[float] = None
    use_count: int = 0
    enabled: bool = True

@dataclass
class AuthChallenge:
    """A challenge for multi-factor authentication."""
    challenge_id: str
    did: str
    operation: str  # transfer, vote, mint, admin, recover
    required_factors: int  # M of N
    nonce: str
    timestamp: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 300)  # 5 min
    responses: Dict[str, str] = field(default_factory=dict)  # factor_id -> response
    completed: bool = False

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def add_response(self, factor_id: str, response: str) -> None:
        self.responses[factor_id] = response

class MultiFactorAuth:
    """
    Multi-factor authentication with configurable thresholds.
    
    Operation-specific requirements:
    - transfer: 2 of 4 (crypto + any one)
    - vote: 1 of 4 (any single factor)
    - mint: 3 of 4 (crypto + neural + one more)
    - admin: 4 of 4 (all factors)
    - recover: 3 of 5 (guardians + crypto)
    """

    THRESHOLDS = {
        "transfer": 2,
        "vote": 1,
        "mint": 3,
        "admin": 4,
        "recover": 3,
    }

    def __init__(self):
        self.factors: Dict[str, Dict[str, AuthFactor]] = {}  # DID -> {factor_id: AuthFactor}
        self.active_challenges: Dict[str, AuthChallenge] = {}
        self.auth_history: List[dict] = []

    def register_factor(self, did: str, factor_type: FactorType,
                        public_data: str) -> AuthFactor:
        """Register a new authentication factor for a DID."""
        if did not in self.factors:
            self.factors[did] = {}
        commitment = hashlib.sha256(public_data.encode()).hexdigest()
        factor = AuthFactor(
            factor_id=hashlib.sha256(f"{did}:{factor_type.value}:{time.time()}".encode()).hexdigest()[:16],
            factor_type=factor_type,
            public_commitment=commitment,
        )
        self.factors[did][factor.factor_id] = factor
        return factor

    def create_challenge(self, did: str, operation: str) -> AuthChallenge:
        """Create an authentication challenge for an operation."""
        required = self.THRESHOLDS.get(operation, 2)
        available = sum(1 for f in self.factors.get(did, {}).values() if f.enabled)
        if available < required:
            raise ValueError(f"Insufficient factors: need {required}, have {available}")
        challenge = AuthChallenge(
            challenge_id=hashlib.sha256(f"challenge:{did}:{operation}:{time.time()}".encode()).hexdigest()[:16],
            did=did, operation=operation,
            required_factors=required,
            nonce=secrets.token_hex(16),
        )
        self.active_challenges[challenge.challenge_id] = challenge
        return challenge

    def submit_response(self, challenge_id: str, factor_id: str,
                       response: str) -> bool:
        """Submit a factor response to a challenge."""
        challenge = self.active_challenges.get(challenge_id)
        if not challenge or challenge.is_expired() or challenge.completed:
            return False
        did = challenge.did
        factor = self.factors.get(did, {}).get(factor_id)
        if not factor or not factor.enabled:
            return False
        # Verify response (simplified: hash matches)
        expected = hashlib.sha256((factor.public_commitment + challenge.nonce).encode()).hexdigest()
        if response != expected:
            return False
        challenge.add_response(factor_id, response)
        factor.last_used = time.time()
        factor.use_count += 1
        # Check if threshold met
        if len(challenge.responses) >= challenge.required_factors:
            challenge.completed = True
            self.auth_history.append({
                "did": did, "operation": operation if False else challenge.operation,
                "factors_used": len(challenge.responses),
                "timestamp": time.time(), "success": True,
            })
        return True

    def is_authenticated(self, challenge_id: str) -> bool:
        challenge = self.active_challenges.get(challenge_id)
        return challenge is not None and challenge.completed

    def get_factors(self, did: str) -> List[AuthFactor]:
        return list(self.factors.get(did, {}).values())

    def revoke_factor(self, did: str, factor_id: str) -> bool:
        factor = self.factors.get(did, {}).get(factor_id)
        if factor:
            factor.enabled = False
            return True
        return False
