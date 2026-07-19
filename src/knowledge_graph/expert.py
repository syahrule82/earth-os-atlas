"""Expert discovery — find top contributors by topic."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

class ExpertDiscovery:
    """Discover experts in specific knowledge domains."""

    def __init__(self, graph):
        self.graph = graph

    def find_experts(self, query_embedding: np.ndarray, k: int = 10) -> List[dict]:
        """Find top contributors for a given topic."""
        results = self.graph.search_vector(query_embedding, k=k*3)
        expert_scores: Dict[str, float] = {}
        expert_nodes: Dict[str, List[str]] = {}

        for node_id, similarity in results:
            node = self.graph.get_node(node_id)
            if not node:
                continue
            # Score = similarity * impact
            score = similarity * node.impact_score
            expert_scores[node.creator_did] = expert_scores.get(node.creator_did, 0) + score
            if node.creator_did not in expert_nodes:
                expert_nodes[node.creator_did] = []
            expert_nodes[node.creator_did].append(node_id)

        ranked = sorted(expert_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        return [{
            "expert_did": did,
            "score": score,
            "contribution_count": len(expert_nodes[did]),
            "top_contributions": expert_nodes[did][:3],
        } for did, score in ranked]

    def expert_profile(self, did: str) -> dict:
        """Build a full expert profile from their contributions."""
        nodes = [n for n in self.graph.nodes.values() if n.creator_did == did]
        if not nodes:
            return {"did": did, "contributions": 0}

        return {
            "did": did,
            "total_contributions": len(nodes),
            "total_citations": sum(n.citation_count for n in nodes),
            "avg_reputation": sum(n.reputation_score for n in nodes) / len(nodes),
            "knowledge_types": list(set(n.knowledge_type.value for n in nodes)),
            "top_works": sorted(nodes, key=lambda n: n.impact_score, reverse=True)[:5],
            "first_contribution": min(n.created_at for n in nodes),
            "latest_contribution": max(n.created_at for n in nodes),
        }
