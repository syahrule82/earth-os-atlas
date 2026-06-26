"""ATLAS Core tests"""
from decimal import Decimal
from src.atlas_core.value_recognition import ValueRecognizer, ValueCategory
from src.atlas_core.validation_consensus import PROMETHEUSValidator
from src.atlas_core.atlas_minting import ATLASMinter

def test_value_recognition():
    r = ValueRecognizer()
    proof = r.recognize("did:atlas:alice", ValueCategory.CREATED_KNOWLEDGE, "medium", Decimal("8"))
    assert proof.base_value == Decimal("200.0000")
    assert proof.can_mint is False

def test_prometheus_validation():
    v = PROMETHEUSValidator(min_consensus=0.67, min_voters=3)
    for i in range(5):
        v.register_voter(f"voter_{i}", 1.0)
    votes = {f"voter_{i}": True for i in range(4)}
    votes["voter_4"] = False
    result = v.validate("proof_001", votes)
    assert result.is_valid is True
    assert result.confidence >= 0.67

def test_minting():
    m = ATLASMinter()
    coin = m.mint("proof_001", "did:atlas:alice", Decimal("200"), confidence=0.9)
    assert coin is not None
    assert coin.minted_for == "did:atlas:alice"
    assert m.total_minted > 0
