"""Zero-Knowledge VM — RISC Zero proof verification for trustless attestation."""
from .prover import ZKProver, ZKProof, ZKProgram
from .verifier import ZKVerifier
from .circuits import ValueProofCircuit, AttestationCircuit

__all__ = ["ZKProver", "ZKProof", "ZKProgram", "ZKVerifier",
           "ValueProofCircuit", "AttestationCircuit"]
