"""Phase 13 integration tests."""
from decimal import Decimal
from src.identity_layer.did import AtlasDID, DIDResolver
from src.identity_layer.soulbound import SBTRegistry, IdentityAttribute
from src.identity_layer.multifactor import MultiFactorAuth, FactorType
from src.identity_layer.recovery import SocialRecovery
from src.identity_layer.portability import CrossChainIdentity
from src.identity_layer.verification import IdentityVerifier, VerificationLevel
from src.identity_layer.zk_identity import ZKIdentityProver
import time, hashlib

def test_did_creation_resolution():
    pub_key = b"test_public_key_1234567890"
    did = AtlasDID(public_key=pub_key)
    assert did.did.startswith("did:atlas:")
    assert len(did.document.verification_methods) >= 1
    # Add service
    did.add_service(f"{did.did}#pni", "PNIEndpoint", "neural://global/prefrontal/node/pni-v3")
    assert len(did.document.services) == 1
    # Resolver
    resolver = DIDResolver()
    resolver.register(did)
    resolved = resolver.resolve(did.did)
    assert resolved is not None
    assert resolved.did == did.did
    assert resolver.is_active(did.did) is True
    did.deactivate()
    assert resolver.is_active(did.did) is False  # Still in registry but deactivated

def test_did_from_string():
    did_str = "did:atlas:abc123def456"
    did = AtlasDID.from_did(did_str)
    assert did.did == did_str

def test_soulbound_identity():
    registry = SBTRegistry()
    token = registry.mint("did:atlas:alice")
    assert token.owner_did == "did:atlas:alice"
    assert token.verification_level == "Basic"
    assert token.is_transferable() is False
    # Add attributes
    token.add_attribute(IdentityAttribute(
        name="email", value="alice@atlas.org", issuer="did:atlas:verifier"))
    token.add_attribute(IdentityAttribute(
        name="nationality", value="ID", issuer="did:atlas:gaea"))
    token.add_attribute(IdentityAttribute(
        name="neural_fingerprint", value="abc123", issuer="did:atlas:pni"))
    assert token.verification_level == "Verified"  # 3+ attributes
    # Record contributions
    for i in range(15):
        token.record_contribution(Decimal("10"))
    assert token.contribution_count == 15
    assert token.reputation_score > 1.0
    assert token.verification_level in ["Verified", "Trusted"]
    # Anti-sybil
    assert registry.anti_sybil_check("did:atlas:alice", b"abc123") is True
    assert registry.anti_sybil_check("did:atlas:alice", b"different") is False
    # Cannot mint twice
    try:
        registry.mint("did:atlas:alice")
        assert False, "Should not allow double minting"
    except ValueError:
        pass
    stats = registry.stats()
    assert stats["total_identities"] == 1

def test_multifactor_auth():
    mfa = MultiFactorAuth()
    did = "did:atlas:alice"
    # Register 4 factors
    for ft in [FactorType.CRYPTOGRAPHIC, FactorType.NEURAL,
              FactorType.BIOMETRIC, FactorType.HARDWARE]:
        mfa.register_factor(did, ft, f"public_data_{ft.value}")
    factors = mfa.get_factors(did)
    assert len(factors) == 4
    # Create challenge for transfer (2 of 4)
    challenge = mfa.create_challenge(did, "transfer")
    assert challenge.required_factors == 2
    assert challenge.operation == "transfer"
    # Submit responses
    for factor in factors[:2]:
        expected = hashlib.sha256(
            (factor.public_commitment + challenge.nonce).encode()
        ).hexdigest()
        assert mfa.submit_response(challenge.challenge_id, factor.factor_id, expected)
    assert mfa.is_authenticated(challenge.challenge_id) is True
    # Admin requires 4 of 4
    admin_challenge = mfa.create_challenge(did, "admin")
    assert admin_challenge.required_factors == 4
    # Revoke a factor
    mfa.revoke_factor(did, factors[3].factor_id)
    assert factors[3].enabled is False

def test_social_recovery():
    sr = SocialRecovery()
    # Set guardians
    guardians = [f"did:atlas:g{i}" for i in range(5)]
    sr.set_guardians("did:atlas:alice", guardians, threshold=3)
    # Initiate recovery
    request = sr.initiate_recovery("did:atlas:alice", "new_pub_key_123")
    assert request.threshold == 3
    assert not request.is_ready()
    # 2 approvals (not enough)
    sr.guardian_approve(request.request_id, guardians[0])
    sr.guardian_approve(request.request_id, guardians[1])
    assert not request.is_ready()
    # 3rd approval (enough)
    sr.guardian_approve(request.request_id, guardians[2])
    assert request.is_ready()
    assert request.completed is True
    assert len(sr.completed_recoveries) == 1
    # Pending for guardian 3
    pending = sr.pending_recoveries(guardians[3])
    assert len(pending) == 0  # Recovery already completed

def test_cross_chain_identity():
    cci = CrossChainIdentity()
    # Issue credential
    cred = cci.issue_credential(
        issuer="did:atlas:verifier",
        subject="did:atlas:alice",
        claims={"citizenship": "verified", "age_over_18": "true"},
    )
    assert cci.verify_credential(cred.credential_id) is True
    # Port to Ethereum
    mapping_id = cci.port_to_chain(
        "did:atlas:alice", "ethereum",
        "0x1234567890abcdef",
        {"type": "address_ownership", "sig": "abc"},
    )
    assert mapping_id is not None
    # Verify mapping
    bridge = cci.bridges["ethereum"]
    assert bridge.verify_mapping(mapping_id) is True
    # Resolve
    addr = cci.resolve("did:atlas:alice", "ethereum")
    assert addr == "0x1234567890abcdef"
    # Get credentials
    creds = cci.get_credentials_for("did:atlas:alice")
    assert len(creds) == 1
    # Revoke
    cci.revoke_credential(cred.credential_id)
    assert cci.verify_credential(cred.credential_id) is False

def test_identity_verification():
    verifier = IdentityVerifier()
    # Basic level
    r1 = verifier.verify("did:atlas:new", attributes_count=0, contributions=0,
                         reputation=0.5, factors_count=0)
    assert r1.level == VerificationLevel.BASIC
    assert r1.can_mint is False
    assert r1.can_vote is True
    # Verified level
    r2 = verifier.verify("did:atlas:user", attributes_count=3, contributions=5,
                         reputation=1.5, factors_count=2)
    assert r2.level == VerificationLevel.VERIFIED
    assert r2.can_mint is True
    # Trusted level
    r3 = verifier.verify("did:atlas:active", attributes_count=5, contributions=20,
                         reputation=3.5, factors_count=3)
    assert r3.level == VerificationLevel.TRUSTED
    assert r3.can_validate is True
    # Sovereign level
    r4 = verifier.verify("did:atlas:elite", attributes_count=6, contributions=150,
                         reputation=6.0, factors_count=4)
    assert r4.level == VerificationLevel.SOVEREIGN
    assert r4.can_admin is True
    # Permissions check
    assert verifier.can_perform("did:atlas:elite", "admin") is True
    assert verifier.can_perform("did:atlas:new", "mint") is False

def test_zk_identity_proofs():
    prover = ZKIdentityProver()
    # Age threshold proof
    birth = time.time() - 25 * 365.25 * 86400  # 25 years old
    age_proof = prover.prove_age_threshold(birth, threshold_years=18)
    assert age_proof.public_outputs["valid"] is True
    assert prover.verify_proof(age_proof) is True
    # Reputation threshold proof
    rep_proof = prover.prove_reputation(actual_reputation=5.0, threshold=3.0)
    assert rep_proof.public_outputs["meets_threshold"] is True
    # Uniqueness proof
    unique_proof = prover.prove_uniqueness("my_secret_identity_key")
    assert "nullifier" in unique_proof.public_outputs
    assert prover.verify_proof(unique_proof) is True
    # Verify all circuits registered
    assert len(prover.circuits) == 4

if __name__ == "__main__":
    test_did_creation_resolution()
    test_did_from_string()
    test_soulbound_identity()
    test_multifactor_auth()
    test_social_recovery()
    test_cross_chain_identity()
    test_identity_verification()
    test_zk_identity_proofs()
    print("✅ All Phase 13 tests passed")
