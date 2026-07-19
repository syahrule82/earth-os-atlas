"""Identity Verification — Progressive verification levels."""
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import time

class VerificationLevel(Enum):
    BASIC = "Basic"        # Just created DID
    VERIFIED = "Verified"  # Has verified attributes
    TRUSTED = "Trusted"    # History of contributions
    SOVEREIGN = "Sovereign" # Fully self-sovereign, multi-factor

@dataclass
class VerificationResult:
    did: str
    level: VerificationLevel
    factors_verified: List[str]
    trust_score: float
    can_mint: bool
    can_vote: bool
    can_validate: bool
    can_admin: bool
    timestamp: float = time.time()

class IdentityVerifier:
    """
    Verifies identity and assigns verification levels.
    
    BASIC: Can create proofs but cannot mint
    VERIFIED: Can mint ATLAS (requires 2+ verified attributes)
    TRUSTED: Can become validator (requires 10+ contributions, 3.0+ reputation)
    SOVEREIGN: Full admin capabilities (requires 100+ contributions, 5.0+ reputation, all 4 factors)
    """

    LEVEL_REQUIREMENTS = {
        VerificationLevel.BASIC: {"min_attributes": 0, "min_contributions": 0, "min_reputation": 0, "min_factors": 0},
        VerificationLevel.VERIFIED: {"min_attributes": 2, "min_contributions": 0, "min_reputation": 1.0, "min_factors": 1},
        VerificationLevel.TRUSTED: {"min_attributes": 3, "min_contributions": 10, "min_reputation": 3.0, "min_factors": 2},
        VerificationLevel.SOVEREIGN: {"min_attributes": 5, "min_contributions": 100, "min_reputation": 5.0, "min_factors": 4},
    }

    PERMISSIONS = {
        VerificationLevel.BASIC: {"can_mint": False, "can_vote": True, "can_validate": False, "can_admin": False},
        VerificationLevel.VERIFIED: {"can_mint": True, "can_vote": True, "can_validate": False, "can_admin": False},
        VerificationLevel.TRUSTED: {"can_mint": True, "can_vote": True, "can_validate": True, "can_admin": False},
        VerificationLevel.SOVEREIGN: {"can_mint": True, "can_vote": True, "can_validate": True, "can_admin": True},
    }

    def __init__(self):
        self.verifications: Dict[str, List[VerificationResult]] = {}

    def verify(self, did: str, attributes_count: int, contributions: int,
               reputation: float, factors_count: int) -> VerificationResult:
        """Verify an identity and assign a verification level."""
        level = VerificationLevel.BASIC

        for v_level in [VerificationLevel.SOVEREIGN, VerificationLevel.TRUSTED,
                        VerificationLevel.VERIFIED, VerificationLevel.BASIC]:
            req = self.LEVEL_REQUIREMENTS[v_level]
            if (attributes_count >= req["min_attributes"] and
                contributions >= req["min_contributions"] and
                reputation >= req["min_reputation"] and
                factors_count >= req["min_factors"]):
                level = v_level
                break

        perms = self.PERMISSIONS[level]
        trust_score = (attributes_count * 0.2 + contributions * 0.01 +
                      reputation * 0.3 + factors_count * 0.25)

        result = VerificationResult(
            did=did, level=level,
            factors_verified=[f"factor_{i}" for i in range(factors_count)],
            trust_score=min(10.0, trust_score),
            can_mint=perms["can_mint"],
            can_vote=perms["can_vote"],
            can_validate=perms["can_validate"],
            can_admin=perms["can_admin"],
        )
        if did not in self.verifications:
            self.verifications[did] = []
        self.verifications[did].append(result)
        return result

    def get_latest(self, did: str) -> Optional[VerificationResult]:
        results = self.verifications.get(did, [])
        return results[-1] if results else None

    def can_perform(self, did: str, action: str) -> bool:
        result = self.get_latest(did)
        if not result:
            return False
        return getattr(result, f"can_{action}", False)
