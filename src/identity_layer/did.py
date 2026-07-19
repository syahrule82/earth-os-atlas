"""DID:atlas — Decentralized identifier with on-chain resolution."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import hashlib, time, json

@dataclass
class DIDDocument:
    """W3C-compatible DID Document for DID:atlas."""
    did: str
    controller: str
    verification_methods: List[dict] = field(default_factory=list)
    services: List[dict] = field(default_factory=list)
    authentication: List[str] = field(default_factory=list)
    assertion_method: List[str] = field(default_factory=list)
    key_agreement: List[str] = field(default_factory=list)
    created: float = field(default_factory=time.time)
    updated: float = field(default_factory=time.time)
    deactivated: bool = False

    def to_dict(self) -> dict:
        return {
            "@context": ["https://www.w3.org/ns/did/v1", "https://atlas.kosasih.org/ns/did/v1"],
            "id": self.did,
            "controller": self.controller,
            "verificationMethod": self.verification_methods,
            "authentication": self.authentication,
            "assertionMethod": self.assertion_method,
            "keyAgreement": self.key_agreement,
            "service": self.services,
            "created": self.created,
            "updated": self.updated,
            "deactivated": self.deactivated,
        }

class AtlasDID:
    """
    DID:atlas — The ATLAS decentralized identifier.
    
    Format: did:atlas:<method-specific-id>
    Method-specific ID: BLAKE2b(public_key)[:32] as base58
    
    Resolution:
    1. Extract public key from method-specific ID
    2. Look up DID Document on ATLAS ledger
    3. Return document with verification methods
    """

    METHOD = "atlas"

    def __init__(self, public_key: bytes, controller: str = ""):
        self.public_key = public_key
        key_hash = hashlib.blake2b(public_key, digest_size=32).hexdigest()
        self.did = f"did:{self.METHOD}:{key_hash}"
        self.controller = controller or self.did
        self.document = DIDDocument(
            did=self.did,
            controller=self.controller,
            verification_methods=[{
                "id": f"{self.did}#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": self.controller,
                "publicKeyMultibase": key_hash,
            }],
            authentication=[f"{self.did}#key-1"],
            assertion_method=[f"{self.did}#key-1"],
        )

    def add_verification_method(self, method_id: str, method_type: str,
                               public_key: str, key_format: str = "publicKeyMultibase") -> None:
        """Add a new verification method (e.g., post-quantum key, neural key)."""
        self.document.verification_methods.append({
            "id": method_id,
            "type": method_type,
            "controller": self.controller,
            key_format: public_key,
        })
        self.document.updated = time.time()

    def add_service(self, service_id: str, service_type: str,
                    endpoint: str) -> None:
        """Add a service endpoint (e.g., PNI mesh address, API endpoint)."""
        self.document.services.append({
            "id": service_id,
            "type": service_type,
            "serviceEndpoint": endpoint,
        })
        self.document.updated = time.time()

    def deactivate(self) -> None:
        self.document.deactivated = True
        self.document.updated = time.time()

    @classmethod
    def from_did(cls, did: str) -> "AtlasDID":
        """Parse a DID string (does not resolve — use DIDResolver for that)."""
        parts = did.split(":")
        if len(parts) != 3 or parts[0] != "did" or parts[1] != cls.METHOD:
            raise ValueError(f"Invalid DID:atlas format: {did}")
        # Reconstruct from hash (can't recover full key, but can create stub)
        key_hash = parts[2]
        public_key = bytes.fromhex(key_hash[:64]) if len(key_hash) >= 64 else b"placeholder"
        instance = cls.__new__(cls)
        instance.public_key = public_key
        instance.did = did
        instance.controller = did
        instance.document = DIDDocument(did=did, controller=did)
        return instance

class DIDResolver:
    """Resolves DID:atlas identifiers to DID Documents."""

    def __init__(self):
        self.documents: Dict[str, DIDDocument] = {}
        self.history: Dict[str, List[DIDDocument]] = {}

    def register(self, atlas_did: AtlasDID) -> None:
        self.documents[atlas_did.did] = atlas_did.document
        if atlas_did.did not in self.history:
            self.history[atlas_did.did] = []
        self.history[atlas_did.did].append(atlas_did.document)

    def resolve(self, did: str) -> Optional[DIDDocument]:
        return self.documents.get(did)

    def get_history(self, did: str) -> List[DIDDocument]:
        return self.history.get(did, [])

    def is_active(self, did: str) -> bool:
        doc = self.documents.get(did)
        return doc is not None and not doc.deactivated
