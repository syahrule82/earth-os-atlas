"""ATLAS Identity Layer — Decentralized DID, soulbound tokens, cross-chain portability."""
from .did import AtlasDID, DIDResolver, DIDDocument
from .soulbound import SoulboundIdentity, IdentityAttribute, SBTRegistry
from .multifactor import MultiFactorAuth, AuthFactor, AuthChallenge
from .recovery import SocialRecovery, GuardianSet, RecoveryRequest
from .portability import CrossChainIdentity, IdentityBridge, PortableCredential
from .verification import IdentityVerifier, VerificationLevel, VerificationResult
from .zk_identity import ZKIdentityProof, ZKIdentityCircuit

__all__ = ["AtlasDID", "DIDResolver", "DIDDocument",
           "SoulboundIdentity", "IdentityAttribute", "SBTRegistry",
           "MultiFactorAuth", "AuthFactor", "AuthChallenge",
           "SocialRecovery", "GuardianSet", "RecoveryRequest",
           "CrossChainIdentity", "IdentityBridge", "PortableCredential",
           "IdentityVerifier", "VerificationLevel", "VerificationResult",
           "ZKIdentityProof", "ZKIdentityCircuit"]
