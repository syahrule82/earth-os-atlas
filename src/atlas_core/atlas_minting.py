"""
ATLAS Minting Engine
Converts validated ContributionProofs into ATLAS coins.
Time-decaying reward curve (4-year halving).
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional
import hashlib, time, uuid


@dataclass(frozen=True)
class ATLASCoin:
    coin_id:          str
    proof_id:         str
    minted_for:       str
    value_basis:      Decimal
    minting_timestamp: float
    coin_hash:        str


class ATLASMinter:
    """
    Mints ATLAS from ContributionProofs.
    Genesis supply: 1,000,000,000 ATLAS.
    Halving every 4 years.
    """
    GENESIS_SUPPLY    = Decimal("1000000000")
    HALVING_INTERVAL  = 4 * 365 * 24 * 3600  # seconds

    def __init__(self):
        self.total_minted  = Decimal("0")
        self.coins: Dict[str, ATLASCoin] = {}
        self.minting_start = time.time()

    def current_reward(self) -> Decimal:
        elapsed  = time.time() - self.minting_start
        halvings = int(elapsed / self.HALVING_INTERVAL)
        return Decimal("100") / (2 ** halvings)

    def mint(
        self,
        proof_id:   str,
        creator_id: str,
        value:      Decimal,
        confidence: float = 1.0,
    ) -> Optional[ATLASCoin]:
        scaled = (self.current_reward() * Decimal(str(confidence))).quantize(Decimal("0.0001"))
        if self.total_minted + scaled > self.GENESIS_SUPPLY:
            return None
        coin = ATLASCoin(
            coin_id           = str(uuid.uuid4()),
            proof_id          = proof_id,
            minted_for        = creator_id,
            value_basis       = value,
            minting_timestamp = time.time(),
            coin_hash         = hashlib.sha256(
                f"{proof_id}:{time.time()}".encode()
            ).hexdigest()[:64],
        )
        self.coins[coin.coin_id] = coin
        self.total_minted += scaled
        return coin
