"""
HERMES Value Recognition Layer
12 categories of human contribution.
Money = Verifiable proof of civilizational value.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum, auto
from typing import List, Optional
import hashlib, time, uuid


class ValueCategory(Enum):
    """The 12 recognized forms of value contribution."""
    SOLVED_PROBLEM       = auto()
    CREATED_KNOWLEDGE    = auto()
    BUILT_INFRASTRUCTURE = auto()
    HEALED_BIOLOGICAL    = auto()
    PROTECTED_SYSTEMS    = auto()
    OPTIMIZED_PROCESS    = auto()
    CONNECTED_PEOPLE     = auto()
    RESTORED_ECOLOGICAL  = auto()
    ADVANCED_ART         = auto()
    DISTRIBUTED_FAIRLY   = auto()
    PREVENTED_HARM       = auto()
    CREATED_BEAUTY       = auto()


# Multipliers per complexity tier
COMPLEXITY_TIERS = {
    "micro":     Decimal("1.0"),
    "small":     Decimal("5.0"),
    "medium":    Decimal("25.0"),
    "large":     Decimal("125.0"),
    "massive":   Decimal("625.0"),
    "planetary": Decimal("3125.0"),
}


@dataclass(frozen=True)
class ContributionProof:
    """Immutable proof that value was created."""
    proof_id:          str
    creator_id:        str
    category:          ValueCategory
    complexity_tier:   str
    raw_hours:         Decimal
    attestation_count: int
    base_value:        Decimal
    timestamp:         float

    @property
    def can_mint(self) -> bool:
        return self.attestation_count >= 2


class ValueRecognizer:
    """HERMES: the sensor layer that recognizes value creation."""

    def recognize(
        self,
        creator_id: str,
        category: ValueCategory,
        tier: str,
        hours: Decimal,
        description: str = "",
    ) -> ContributionProof:
        if tier not in COMPLEXITY_TIERS:
            raise ValueError(f"Invalid tier: {tier!r}")
        base = (COMPLEXITY_TIERS[tier] * hours).quantize(Decimal("0.0001"), ROUND_HALF_UP)
        return ContributionProof(
            proof_id          = str(uuid.uuid4()),
            creator_id        = creator_id,
            category          = category,
            complexity_tier   = tier,
            raw_hours         = hours.quantize(Decimal("0.01")),
            attestation_count = 0,
            base_value        = base,
            timestamp         = time.time(),
        )
