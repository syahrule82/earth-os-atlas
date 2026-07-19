"""Reputation Graph — Global trust network with PageRank-style scoring."""
from dataclasses import dataclass, field
from typing import Dict, List, Set
from decimal import Decimal
import time, hashlib

@dataclass
class ReputationNode:
    did: str
    reputation: float = 1.0
    attestations_given: int = 0
    attestations_received: int = 0
    value_created: Decimal = Decimal("0")
    last_active: float = field(default_factory=time.time)

class ReputationGraph:
    """
    Global trust network using PageRank-style scoring.
    
    Reputation flows through attestation edges.
    Attesting to high-reputation nodes increases your reputation.
    Attesting to fraudulent nodes decreases your reputation.
    """
    
    def __init__(self, damping: float = 0.85, iterations: int = 20):
        self.nodes: Dict[str, ReputationNode] = {}
        self.attestations: List[tuple] = []  # (attester, attested, positive)
        self.damping = damping
        self.iterations = iterations
    
    def add_node(self, did: str) -> ReputationNode:
        if did not in self.nodes:
            self.nodes[did] = ReputationNode(did=did)
        return self.nodes[did]
    
    def add_attestation(self, attester: str, attested: str, positive: bool = True) -> None:
        self.add_node(attester)
        self.add_node(attested)
        self.attestations.append((attester, attested, positive))
        self.nodes[attester].attestations_given += 1
        self.nodes[attested].attestations_received += 1
    
    def compute_pagerank(self) -> Dict[str, float]:
        """Compute PageRank-style reputation scores."""
        n = len(self.nodes)
        if n == 0:
            return {}
        
        # Build adjacency from attestations
        out_links: Dict[str, List[str]] = {did: [] for did in self.nodes}
        in_links: Dict[str, List[str]] = {did: [] for did in self.nodes}
        
        for attester, attested, positive in self.attestations:
            if positive:
                out_links[attester].append(attested)
                in_links[attested].append(attester)
        
        # Initialize
        scores = {did: 1.0 / n for did in self.nodes}
        
        for _ in range(self.iterations):
            new_scores = {}
            for did in self.nodes:
                rank_sum = 0.0
                for source in in_links.get(did, []):
                    out_count = len(out_links.get(source, []))
                    if out_count > 0:
                        rank_sum += scores[source] / out_count
                new_scores[did] = (1 - self.damping) / n + self.damping * rank_sum
            scores = new_scores
        
        # Normalize to 0-2 range (1.0 = average)
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total * n for k, v in scores.items()}
        
        # Update node reputations
        for did, score in scores.items():
            self.nodes[did].reputation = score
        
        return scores
    
    def get_reputation(self, did: str) -> float:
        return self.nodes.get(did, ReputationNode(did=did)).reputation
    
    def top_reputable(self, n: int = 10) -> List[ReputationNode]:
        return sorted(self.nodes.values(), key=lambda x: x.reputation, reverse=True)[:n]
    
    def stats(self) -> dict:
        return {
            "total_nodes": len(self.nodes),
            "total_attestations": len(self.attestations),
            "avg_reputation": sum(n.reputation for n in self.nodes.values()) / max(1, len(self.nodes)),
            "top_reputable": [n.did for n in self.top_reputable(5)],
        }
