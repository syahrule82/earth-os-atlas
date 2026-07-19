"""Cross-Chain Identity Portability — Use DID:atlas on other chains."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import hashlib, time, json

@dataclass
class PortableCredential:
    """A W3C Verifiable Credential portable across chains."""
    credential_id: str
    issuer: str  # DID:atlas of issuer
    subject: str  # DID:atlas of subject
    claims: Dict[str, str]
    proof: dict  # ZK proof or signature
    issued_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    revoked: bool = False

    def to_vc(self) -> dict:
        """Convert to W3C Verifiable Credential format."""
        return {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "id": self.credential_id,
            "type": ["VerifiableCredential", "AtlasCredential"],
            "issuer": self.issuer,
            "subject": self.subject,
            "claims": self.claims,
            "proof": self.proof,
            "issuanceDate": self.issued_at,
            "expirationDate": self.expires_at,
        }

@dataclass
class IdentityBridge:
    """Bridge for cross-chain identity portability."""
    source_chain: str  # "atlas"
    target_chain: str  # "ethereum", "solana", "cosmos"
    bridge_contract: str  # Address on target chain
    verified_mappings: Dict[str, str] = field(default_factory=dict)  # atlas_did -> target_address
    pending_mappings: Dict[str, dict] = field(default_factory=dict)

    def create_mapping(self, atlas_did: str, target_address: str,
                       proof: dict) -> str:
        """Create a cross-chain identity mapping."""
        mapping_id = hashlib.sha256(f"{atlas_did}:{self.target_chain}:{time.time()}".encode()).hexdigest()[:16]
        self.pending_mappings[mapping_id] = {
            "atlas_did": atlas_did,
            "target_address": target_address,
            "target_chain": self.target_chain,
            "proof": proof,
            "timestamp": time.time(),
        }
        return mapping_id

    def verify_mapping(self, mapping_id: str) -> bool:
        """Verify and finalize a cross-chain mapping."""
        pending = self.pending_mappings.get(mapping_id)
        if not pending:
            return False
        # In production: verify proof via bridge contract on target chain
        self.verified_mappings[pending["atlas_did"]] = pending["target_address"]
        del self.pending_mappings[mapping_id]
        return True

    def resolve_cross_chain(self, atlas_did: str) -> Optional[str]:
        """Resolve DID:atlas to target chain address."""
        return self.verified_mappings.get(atlas_did)

class CrossChainIdentity:
    """
    Manages cross-chain identity portability.
    Allows DID:atlas to be used on Ethereum, Solana, Cosmos.
    """

    SUPPORTED_CHAINS = ["ethereum", "solana", "cosmos", "polygon", "arbitrum"]

    def __init__(self):
        self.bridges: Dict[str, IdentityBridge] = {}
        self.credentials: Dict[str, PortableCredential] = {}
        for chain in self.SUPPORTED_CHAINS:
            self.bridges[chain] = IdentityBridge(
                source_chain="atlas", target_chain=chain,
                bridge_contract=f"0x{hashlib.sha256(chain.encode()).hexdigest()[:40]}",
            )

    def issue_credential(self, issuer: str, subject: str,
                         claims: Dict[str, str]) -> PortableCredential:
        """Issue a portable verifiable credential."""
        proof = {
            "type": "Ed25519Signature2020",
            "verification_method": f"{issuer}#key-1",
            "proof_value": hashlib.sha256(
                f"{issuer}:{subject}:{json.dumps(claims, sort_keys=True)}:{time.time()}".encode()
            ).hexdigest(),
        }
        cred = PortableCredential(
            credential_id=hashlib.sha256(f"cred:{issuer}:{subject}:{time.time()}".encode()).hexdigest()[:16],
            issuer=issuer, subject=subject,
            claims=claims, proof=proof,
        )
        self.credentials[cred.credential_id] = cred
        return cred

    def verify_credential(self, credential_id: str) -> bool:
        cred = self.credentials.get(credential_id)
        if not cred or cred.revoked:
            return False
        if cred.expires_at and time.time() > cred.expires_at:
            return False
        return True

    def revoke_credential(self, credential_id: str) -> bool:
        cred = self.credentials.get(credential_id)
        if cred:
            cred.revoked = True
            return True
        return False

    def port_to_chain(self, atlas_did: str, target_chain: str,
                      target_address: str, proof: dict) -> Optional[str]:
        """Port an ATLAS identity to another chain."""
        bridge = self.bridges.get(target_chain)
        if not bridge:
            return None
        return bridge.create_mapping(atlas_did, target_address, proof)

    def resolve(self, atlas_did: str, target_chain: str) -> Optional[str]:
        """Resolve ATLAS DID to a target chain address."""
        bridge = self.bridges.get(target_chain)
        if bridge:
            return bridge.resolve_cross_chain(atlas_did)
        return None

    def get_credentials_for(self, did: str) -> List[PortableCredential]:
        """Get all credentials issued to a DID."""
        return [c for c in self.credentials.values() if c.subject == did and not c.revoked]
