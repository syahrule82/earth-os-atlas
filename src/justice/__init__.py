"""ATLAS Justice System — Decentralized dispute resolution."""
from .arbitration import ArbitrationSystem, Dispute, Arbitrator, Ruling
from .evidence import EvidenceChain, EvidenceItem
from .precedent import PrecedentSystem, Precedent

__all__ = ["ArbitrationSystem", "Dispute", "Arbitrator", "Ruling",
           "EvidenceChain", "EvidenceItem",
           "PrecedentSystem", "Precedent"]
