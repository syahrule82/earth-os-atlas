"""Python SDK for ATLAS."""
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional
from decimal import Decimal

@dataclass
class ContributionProof:
    proof_id: str
    creator: str
    category: str
    tier: str
    hours: float
    base_value: Decimal

class AtlasClient:
    """Synchronous ATLAS client."""
    def __init__(self, rpc_url: str = "http://localhost:9090"):
        self.rpc_url = rpc_url
        self._cache: Dict = {}

    def create_proof(self, creator: str, category: str, tier: str, 
                     hours: float, description: str = "") -> ContributionProof:
        # In production: RPC call to atlas node
        from src.atlas_core.value_recognition import ValueRecognizer, ValueCategory
        vr = ValueRecognizer()
        proof = vr.recognize(creator, ValueCategory[category], tier, Decimal(str(hours)), description)
        return ContributionProof(
            proof_id=proof.proof_id,
            creator=creator,
            category=category,
            tier=tier,
            hours=hours,
            base_value=proof.base_value,
        )

    def submit_for_attestation(self, proof_id: str, attesters: List[str]) -> bool:
        # Submit to attestation network
        return True

    def mint(self, proof_id: str, confidence: float = 0.9) -> Decimal:
        from src.ledger.mint import MintScheduler
        scheduler = MintScheduler()
        amount = scheduler.schedule_mint(Decimal(str(confidence * 100)), confidence)
        return amount

    def balance(self, address: str) -> Decimal:
        # Query ledger state
        return Decimal("0")

    def transfer(self, sender: str, recipient: str, amount: Decimal) -> bool:
        # Execute transfer
        return True

class AsyncAtlasClient(AtlasClient):
    """Async ATLAS client with connection pooling."""
    async def create_proof_async(self, creator: str, category: str, 
                                  tier: str, hours: float) -> ContributionProof:
        return self.create_proof(creator, category, tier, hours)

    async def mint_async(self, proof_id: str, confidence: float = 0.9) -> Decimal:
        return self.mint(proof_id, confidence)

    async def watch_events(self, event_type: str, callback):
        """WebSocket event subscription."""
        pass
