"""
ATLAS Core — The Value Engine
Proof-of-Value Currency
"""
from .value_recognition import ValueRecognizer, ContributionProof, ValueCategory
from .validation_consensus import PROMETHEUSValidator, ValidationResult
from .atlas_minting import ATLASMinter, ATLASCoin

__all__ = [
    "ValueRecognizer", "ContributionProof", "ValueCategory",
    "PROMETHEUSValidator", "ValidationResult",
    "ATLASMinter", "ATLASCoin"
]
