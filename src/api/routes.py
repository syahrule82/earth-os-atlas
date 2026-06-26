"""API route handlers."""
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel

try:
    from fastapi import APIRouter, HTTPException
    proof_router      = APIRouter()
    ledger_router     = APIRouter()
    governance_router = APIRouter()
    analytics_router  = APIRouter()
except ImportError:
    class FallbackRouter:
        def get(self, *a, **kw): return lambda f: f
        def post(self, *a, **kw): return lambda f: f
    proof_router = ledger_router = governance_router = analytics_router = FallbackRouter()

# --- Schemas ---
class ProofRequest(BaseModel):
    creator_id: str
    category: str
    tier: str
    hours: float
    description: str = ""

class MintRequest(BaseModel):
    proof_id: str
    confidence: float = 0.9

class TransferRequest(BaseModel):
    sender: str
    recipient: str
    amount: float

class VoteRequest(BaseModel):
    proposal_id: str
    voter: str
    voice_credits: int
    approve: bool

# --- Proof Endpoints ---
@proof_router.post("/create")
def create_proof(req: ProofRequest):
    from src.atlas_core.value_recognition import ValueRecognizer, ValueCategory
    vr    = ValueRecognizer()
    proof = vr.recognize(req.creator_id, ValueCategory[req.category],
                         req.tier, Decimal(str(req.hours)), req.description)
    return {"proof_id": proof.proof_id, "base_value": str(proof.base_value),
            "can_mint": proof.can_mint, "category": proof.category.name}

@proof_router.get("/{proof_id}")
def get_proof(proof_id: str):
    return {"proof_id": proof_id, "status": "active", "attestations": 0}

@proof_router.post("/{proof_id}/attest")
def attest_proof(proof_id: str, attester: str):
    return {"proof_id": proof_id, "attester": attester, "status": "attestation_submitted"}

# --- Ledger Endpoints ---
@ledger_router.post("/mint")
def mint_atlas(req: MintRequest):
    from src.ledger.mint import MintScheduler
    sched  = MintScheduler()
    amount = sched.schedule_mint(Decimal("100"), req.confidence)
    if amount is None:
        return {"error": "supply_exhausted"}
    return {"proof_id": req.proof_id, "minted": str(amount), "confidence": req.confidence}

@ledger_router.get("/balance/{address}")
def get_balance(address: str):
    from src.ledger.state import LedgerState
    state = LedgerState()
    return {"address": address, "balance": str(state.get(address).balance)}

@ledger_router.post("/transfer")
def transfer(req: TransferRequest):
    from src.ledger.state import LedgerState
    state = LedgerState()
    ok    = state.transfer(req.sender, req.recipient, Decimal(str(req.amount)))
    return {"status": "ok" if ok else "insufficient_funds", "amount": req.amount}

# --- Governance Endpoints ---
@governance_router.post("/propose")
def create_proposal(title: str, description: str, proposer: str, category: str):
    from src.governance.dao import GovernanceDAO
    dao = GovernanceDAO()
    dao.grant_voice(proposer, 200)
    prop = dao.create_proposal(title, description, proposer, category)
    return {"proposal_id": prop.proposal_id, "status": "created"}

@governance_router.post("/vote")
def vote(req: VoteRequest):
    from src.governance.dao import GovernanceDAO
    dao = GovernanceDAO()
    dao.grant_voice(req.voter, req.voice_credits + 100)
    ok  = dao.vote(req.proposal_id, req.voter, req.voice_credits, req.approve)
    return {"status": "voted" if ok else "vote_failed"}

# --- Analytics Endpoints ---
@analytics_router.get("/network")
def network_stats():
    return {
        "peers": 42,
        "mesh_health": 0.98,
        "value_events_last_hour": 1337,
        "atlas_minted_today": "15420.5000",
        "top_categories": ["BUILT_INFRASTRUCTURE", "CREATED_KNOWLEDGE", "HEALED_BIOLOGICAL"],
    }

@analytics_router.get("/price")
def price_feed():
    return {
        "symbol": "ATLAS/USDC",
        "price": "1.0042",
        "change_24h": "+0.42%",
        "volume_24h": "2441900",
        "market_cap": "1004200000",
    }
