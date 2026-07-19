"""Citation network — tracks contribution dependencies and impact."""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
from decimal import Decimal
import time, hashlib

@dataclass
class Citation:
    """A citation from one contribution to another."""
    citation_id: str
    citing_node: str
    cited_node: str
    citation_type: str  # cites, extends, refutes, replicates
    context: str = ""
    timestamp: float = field(default_factory=time.time)

@dataclass
class CitationImpact:
    """Impact metrics for a node in the citation network."""
    node_id: str
    total_citations: int
    h_index: float
    i10_index: int
    citation_velocity: float  # citations per day
    influence_radius: int  # max path length to any citing node
    lineage_depth: int  # how deep the citation tree goes

class CitationNetwork:
    """
    Citation network with impact scoring.
    Adapts academic citation metrics (h-index, i10) for ATLAS.
    """

    def __init__(self):
        self.citations: List[Citation] = []
        self.out_edges: Dict[str, List[str]] = {}  # node -> nodes it cites
        self.in_edges: Dict[str, List[str]] = {}   # node -> nodes citing it

    def add_citation(self, citing: str, cited: str,
                     citation_type: str = "cites", context: str = "") -> Citation:
        """Record a citation."""
        citation = Citation(
            citation_id=hashlib.sha256(f"{citing}:{cited}:{time.time()}".encode()).hexdigest()[:16],
            citing_node=citing, cited_node=cited,
            citation_type=citation_type, context=context,
        )
        self.citations.append(citation)
        if citing not in self.out_edges:
            self.out_edges[citing] = []
        self.out_edges[citing].append(cited)
        if cited not in self.in_edges:
            self.in_edges[cited] = []
        self.in_edges[cited].append(citing)
        return citation

    def compute_h_index(self, node_id: str) -> float:
        """Compute h-index: h papers with at least h citations each."""
        citers = self.in_edges.get(node_id, [])
        if not citers:
            return 0.0
        # Count citations per citing node
        from collections import Counter
        counts = Counter(citers)
        citation_counts = sorted(counts.values(), reverse=True)
        h = 0
        for i, count in enumerate(citation_counts):
            if count >= i + 1:
                h = i + 1
            else:
                break
        return float(h)

    def compute_i10_index(self, node_id: str) -> int:
        """Number of citing nodes with at least 10 citations."""
        citers = self.in_edges.get(node_id, [])
        from collections import Counter
        counts = Counter(citers)
        return sum(1 for c in counts.values() if c >= 10)

    def citation_velocity(self, node_id: str, window_days: int = 30) -> float:
        """Citations per day in recent window."""
        cutoff = time.time() - window_days * 86400
        recent = [c for c in self.citations
                  if c.cited_node == node_id and c.timestamp >= cutoff]
        return len(recent) / max(1, window_days)

    def influence_radius(self, node_id: str, max_depth: int = 10) -> int:
        """How far does this node's influence spread via citations?"""
        visited: Set[str] = {node_id}
        frontier = {node_id}
        for depth in range(max_depth):
            next_frontier = set()
            for nid in frontier:
                for citer in self.in_edges.get(nid, []):
                    if citer not in visited:
                        visited.add(citer)
                        next_frontier.add(citer)
            if not next_frontier:
                return depth
            frontier = next_frontier
        return max_depth

    def lineage(self, node_id: str, max_depth: int = 5) -> List[List[str]]:
        """Trace the lineage of what this node built upon."""
        paths = []
        def dfs(current: str, path: List[str], depth: int):
            if depth >= max_depth:
                paths.append(path[:])
                return
            cited = self.out_edges.get(current, [])
            if not cited:
                paths.append(path[:])
                return
            for target in cited:
                path.append(target)
                dfs(target, path, depth + 1)
                path.pop()
        dfs(node_id, [node_id], 0)
        return paths

    def compute_impact(self, node_id: str) -> CitationImpact:
        """Compute full impact metrics for a node."""
        return CitationImpact(
            node_id=node_id,
            total_citations=len(self.in_edges.get(node_id, [])),
            h_index=self.compute_h_index(node_id),
            i10_index=self.compute_i10_index(node_id),
            citation_velocity=self.citation_velocity(node_id),
            influence_radius=self.influence_radius(node_id),
            lineage_depth=max((len(p) for p in self.lineage(node_id)), default=1) - 1,
        )

    def top_impact_nodes(self, k: int = 10) -> List[Tuple[str, CitationImpact]]:
        """Get nodes with highest overall impact."""
        all_nodes = set(self.in_edges.keys()) | set(self.out_edges.keys())
        impacts = [(nid, self.compute_impact(nid)) for nid in all_nodes]
        impacts.sort(key=lambda x: x[1].total_citations, reverse=True)
        return impacts[:k]
