"""Soulbound Identity Tokens — Non-transferable identity NFTs."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from decimal import Decimal
import hashlib, time

@dataclass
class IdentityAttribute:
    """A single attribute bound to a soulbound identity token."""
    name: str
    value: str
    issuer: str  # DID of attesting entity
    issued_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    revocable: bool = True
    revoked: bool = False
    proof_hash: str = ""  # ZK proof hash

    def is_valid(self) -> bool:
        if self.revoked:
            return False
        if self.expires_at and time.time() > self.expires_at:
            return False
        return True

@dataclass
class SoulboundIdentity:
    """
    Non-transferable identity token (SBT-Identity).
    
    Bound to a single DID permanently.
    Cannot be sold, transferred, or copied.
    Accumulates attributes over time (reputation, contributions, etc.).
    """
    token_id: str
    owner_did: str
    minted_at: float = field(default_factory=time.time)
    attributes: Dict[str, IdentityAttribute] = field(default_factory=dict)
    verification_level: str = "Basic"  # Basic, Verified, Trusted, Sovereign
    contribution_count: int = 0
    governance_participation: int = 0
    total_value_created: Decimal = Decimal("0")
    reputation_score: float = 1.0
    locked: bool = False  # Locked if under investigation

    def add_attribute(self, attr: IdentityAttribute) -> None:
        self.attributes[attr.name] = attr
        self._update_verification_level()

    def revoke_attribute(self, name: str) -> bool:
        attr = self.attributes.get(name)
        if attr and attr.revocable:
            attr.revoked = True
            return True
        return False

    def record_contribution(self, value: Decimal) -> None:
        self.contribution_count += 1
        self.total_value_created += value
        self.reputation_score = min(10.0, self.reputation_score + 0.01)
        self._update_verification_level()

    def record_governance(self) -> None:
        self.governance_participation += 1
        self._update_verification_level()

    def _update_verification_level(self) -> None:
        if self.contribution_count >= 100 and self.reputation_score >= 5.0:
            self.verification_level = "Sovereign"
        elif self.contribution_count >= 50 and self.reputation_score >= 3.0:
            self.verification_level = "Trusted"
        elif self.contribution_count >= 10 or len(self.attributes) >= 3:
            self.verification_level = "Verified"
        else:
            self.verification_level = "Basic"

    def is_transferable(self) -> bool:
        return False  # Soulbound tokens are never transferable

    def to_dict(self) -> dict:
        return {
            "token_id": self.token_id,
            "owner": self.owner_did,
            "verification_level": self.verification_level,
            "contribution_count": self.contribution_count,
            "governance_participation": self.governance_participation,
            "total_value_created": str(self.total_value_created),
            "reputation_score": self.reputation_score,
            "attributes": {k: v.value for k, v in self.attributes.items() if v.is_valid()},
            "locked": self.locked,
        }

class SBTRegistry:
    """Global registry of soulbound identity tokens."""

    def __init__(self):
        self.tokens: Dict[str, SoulboundIdentity] = {}
        self.owner_index: Dict[str, str] = {}  # DID -> token_id

    def mint(self, owner_did: str) -> SoulboundIdentity:
        """Mint a new soulbound identity token for a DID."""
        if owner_did in self.owner_index:
            raise ValueError(f"DID {owner_did} already has a soulbound token")
        token = SoulboundIdentity(
            token_id=hashlib.sha256(f"sbt:{owner_did}:{time.time()}".encode()).hexdigest()[:16],
            owner_did=owner_did,
        )
        self.tokens[token.token_id] = token
        self.owner_index[owner_did] = token.token_id
        return token

    def get_by_owner(self, did: str) -> Optional[SoulboundIdentity]:
        token_id = self.owner_index.get(did)
        return self.tokens.get(token_id) if token_id else None

    def get_by_token(self, token_id: str) -> Optional[SoulboundIdentity]:
        return self.tokens.get(token_id)

    def lock_identity(self, did: str) -> bool:
        token = self.get_by_owner(did)
        if token:
            token.locked = True
            return True
        return False

    def unlock_identity(self, did: str) -> bool:
        token = self.get_by_owner(did)
        if token:
            token.locked = False
            return True
        return False

    def anti_sybil_check(self, did: str, neural_fingerprint: bytes) -> bool:
        """Check that this DID hasn't already been registered with a different identity."""
        token = self.get_by_owner(did)
        if not token:
            return True  # No existing token, allow
        # Check if neural fingerprint matches registered one
        existing_fp = token.attributes.get("neural_fingerprint")
        if existing_fp and existing_fp.value != neural_fingerprint.hex():
            return False  # Different neural fingerprint = possible sybil
        return True

    def stats(self) -> dict:
        levels = {t.verification_level for t in self.tokens.values()}
        level_counts = {}
        for t in self.tokens.values():
            level_counts[t.verification_level] = level_counts.get(t.verification_level, 0) + 1
        return {
            "total_identities": len(self.tokens),
            "verification_levels": level_counts,
            "total_contributions": sum(t.contribution_count for t in self.tokens.values()),
            "locked_identities": sum(1 for t in self.tokens.values() if t.locked),
        }
