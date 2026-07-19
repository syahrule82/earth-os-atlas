"""Knowledge synthesizer — AGI detects gaps and proposes research."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import numpy as np, time, hashlib

@dataclass
class KnowledgeGap:
    """A detected gap in the knowledge graph."""
    gap_id: str
    description: str
    related_nodes: List[str]
    gap_type: str  # missing_link, unexplored_area, broken_chain, stale_area
    severity: float  # 0-1
    suggested_research: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class ResearchProposal:
    """An AGI-generated research proposal."""
    proposal_id: str
    title: str
    description: str
    gap_id: str
    expected_value_category: str
    estimated_hours: float
    prerequisites: List[str]  # node_ids that should be studied first
    novelty_score: float  # 0-1
    timestamp: float = field(default_factory=time.time)

class KnowledgeSynthesizer:
    """
    AGI-powered knowledge synthesis.
    Detects gaps in the knowledge graph and proposes research to fill them.
    """

    def __init__(self, graph):
        self.graph = graph
        self.gaps: List[KnowledgeGap] = []
        self.proposals: List[ResearchProposal] = []

    def detect_gaps(self) -> List[KnowledgeGap]:
        """Detect gaps in the knowledge graph."""
        gaps = []

        # 1. Missing links: nodes that should be connected but aren't
        gaps.extend(self._detect_missing_links())

        # 2. Unexplored areas: categories with few nodes
        gaps.extend(self._detect_unexplored_areas())

        # 3. Stale areas: no new contributions in a long time
        gaps.extend(self._detect_stale_areas())

        # 4. Broken chains: citation chains that dead-end unexpectedly
        gaps.extend(self._detect_broken_chains())

        self.gaps.extend(gaps)
        return gaps

    def _detect_missing_links(self) -> List[KnowledgeGap]:
        """Find nodes with high semantic similarity but no citation link."""
        gaps = []
        node_ids = list(self.graph.nodes.keys())
        for i, nid_a in enumerate(node_ids[:100]):  # Limit for performance
            node_a = self.graph.nodes[nid_a]
            if node_a.embedding is None:
                continue
            results = self.graph.search_vector(node_a.embedding, k=5)
            for nid_b, sim in results:
                if nid_b == nid_a:
                    continue
                if sim > 0.8 and nid_b not in self.graph.get_citations(nid_a):
                    gap = KnowledgeGap(
                        gap_id=hashlib.sha256(f"gap:{nid_a}:{nid_b}:{time.time()}".encode()).hexdigest()[:16],
                        description=f"High similarity ({sim:.2f}) between '{node_a.title}' and '{self.graph.nodes[nid_b].title}' but no citation link",
                        related_nodes=[nid_a, nid_b],
                        gap_type="missing_link",
                        severity=float(sim),
                        suggested_research=f"Investigate connection between these contributions",
                    )
                    gaps.append(gap)
        return gaps

    def _detect_unexplored_areas(self) -> List[KnowledgeGap]:
        """Find value categories with few contributions."""
        gaps = []
        from .graph import KnowledgeType
        type_counts = {kt: 0 for kt in KnowledgeType}
        for node in self.graph.nodes.values():
            type_counts[node.knowledge_type] = type_counts.get(node.knowledge_type, 0) + 1
        for kt, count in type_counts.items():
            if count < 3:
                gap = KnowledgeGap(
                    gap_id=hashlib.sha256(f"gap:{kt.value}:{time.time()}".encode()).hexdigest()[:16],
                    description=f"Knowledge type '{kt.value}' has only {count} contributions",
                    related_nodes=[],
                    gap_type="unexplored_area",
                    severity=1.0 - count / 10,
                    suggested_research=f"Create more {kt.value} contributions",
                )
                gaps.append(gap)
        return gaps

    def _detect_stale_areas(self) -> List[KnowledgeGap]:
        """Find areas with no recent contributions."""
        gaps = []
        now = time.time()
        stale_threshold = 90 * 86400  # 90 days
        for node_id, node in self.graph.nodes.items():
            age = now - node.created_at
            if age > stale_threshold and node.citation_count > 5:
                gap = KnowledgeGap(
                    gap_id=hashlib.sha256(f"stale:{node_id}:{time.time()}".encode()).hexdigest()[:16],
                    description=f"'{node.title}' was last contributed {age/86400:.0f} days ago but has {node.citation_count} citations",
                    related_nodes=[node_id],
                    gap_type="stale_area",
                    severity=min(1.0, age / (365 * 86400)),
                    suggested_research=f"Update or extend '{node.title}'",
                )
                gaps.append(gap)
        return gaps[:10]  # Limit

    def _detect_broken_chains(self) -> List[KnowledgeGap]:
        """Find citation chains that dead-end (cited node doesn't exist)."""
        gaps = []
        for edge in self.graph.edges:
            if edge.target_id not in self.graph.nodes:
                gap = KnowledgeGap(
                    gap_id=hashlib.sha256(f"broken:{edge.edge_id}:{time.time()}".encode()).hexdigest()[:16],
                    description=f"Citation from {edge.source_id} to missing node {edge.target_id}",
                    related_nodes=[edge.source_id],
                    gap_type="broken_chain",
                    severity=0.5,
                    suggested_research=f"Recreate missing knowledge artifact",
                )
                gaps.append(gap)
        return gaps

    def generate_proposal(self, gap: KnowledgeGap) -> ResearchProposal:
        """Generate a research proposal to fill a knowledge gap."""
        novelty = 0.5
        if gap.gap_type == "unexplored_area":
            novelty = 0.9
        elif gap.gap_type == "missing_link":
            novelty = 0.7
        elif gap.gap_type == "stale_area":
            novelty = 0.4

        proposal = ResearchProposal(
            proposal_id=hashlib.sha256(f"prop:{gap.gap_id}:{time.time()}".encode()).hexdigest()[:16],
            title=f"Research: {gap.suggested_research}",
            description=gap.description,
            gap_id=gap.gap_id,
            expected_value_category="CREATED_KNOWLEDGE",
            estimated_hours=8.0 + gap.severity * 40,
            prerequisites=gap.related_nodes[:3],
            novelty_score=novelty,
        )
        self.proposals.append(proposal)
        return proposal

    def literature_review(self, topic_embedding: np.ndarray, k: int = 20) -> Dict:
        """Automatically synthesize a literature review for a topic."""
        results = self.graph.search_vector(topic_embedding, k=k)
        nodes = [self.graph.get_node(nid) for nid, _ in results]
        nodes = [n for n in nodes if n is not None]

        # Group by type
        from collections import defaultdict
        by_type = defaultdict(list)
        for n in nodes:
            by_type[n.knowledge_type.value].append(n)

        # Find common citations
        common_cited = set()
        if nodes:
            common_cited = set(self.graph.get_citations(nodes[0].node_id))
            for n in nodes[1:]:
                common_cited &= set(self.graph.get_citations(n.node_id))

        return {
            "total_sources": len(nodes),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "common_foundations": list(common_cited)[:5],
            "top_cited": [n.title for n in sorted(nodes, key=lambda x: x.citation_count, reverse=True)[:5]],
            "timeline": sorted([(n.title, n.created_at) for n in nodes], key=lambda x: x[1]),
        }
