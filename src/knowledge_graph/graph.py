"""Knowledge Graph — Global index of all ATLAS contributions."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from decimal import Decimal
from enum import Enum
import numpy as np, hashlib, time

class KnowledgeType(Enum):
    CODE = "code"
    DOCUMENTATION = "documentation"
    RESEARCH = "research"
    MEDICAL = "medical"
    ECOLOGICAL = "ecological"
    EDUCATIONAL = "educational"
    ARTISTIC = "artistic"
    INFRASTRUCTURE = "infrastructure"

@dataclass
class KnowledgeNode:
    """A single knowledge artifact in the graph."""
    node_id: str
    title: str
    knowledge_type: KnowledgeType
    creator_did: str
    embedding: np.ndarray
    content_hash: str
    ipfs_cid: Optional[str] = None
    value_category: str = ""
    base_value: Decimal = Decimal("0")
    reputation_score: float = 1.0
    created_at: float = field(default_factory=time.time)
    citation_count: int = 0
    cited_by: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def impact_score(self) -> float:
        """Impact = reputation * log(1 + citations)."""
        import math
        return self.reputation_score * math.log1p(self.citation_count)

@dataclass
class KnowledgeEdge:
    """Directed edge: source cites target (source built on target's work)."""
    edge_id: str
    source_id: str  # citing node
    target_id: str  # cited node
    edge_type: str  # cites, extends, refutes, replicates
    weight: float = 1.0
    created_at: float = field(default_factory=time.time)

class KnowledgeGraph:
    """
    Global knowledge graph indexing all ATLAS contributions.
    Supports semantic search, citation tracking, and knowledge synthesis.
    """

    def __init__(self, embedding_dim: int = 512):
        self.embedding_dim = embedding_dim
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []
        self.adjacency: Dict[str, List[str]] = {}  # node_id -> cited node_ids
        self.reverse_adjacency: Dict[str, List[str]] = {}  # node_id -> citing node_ids
        self._index_dirty = True
        self._embedding_matrix: Optional[np.ndarray] = None
        self._node_id_list: List[str] = []

    def add_node(self, node: KnowledgeNode) -> None:
        """Add a knowledge node to the graph."""
        if len(node.embedding) != self.embedding_dim:
            node.embedding = np.zeros(self.embedding_dim, dtype=np.float32)
        self.nodes[node.node_id] = node
        if node.node_id not in self.adjacency:
            self.adjacency[node.node_id] = []
        if node.node_id not in self.reverse_adjacency:
            self.reverse_adjacency[node.node_id] = []
        self._index_dirty = True

    def add_citation(self, source_id: str, target_id: str,
                     edge_type: str = "cites", weight: float = 1.0) -> KnowledgeEdge:
        """Record that source_id cites target_id."""
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Both source and target nodes must exist")
        edge = KnowledgeEdge(
            edge_id=hashlib.sha256(f"{source_id}:{target_id}:{time.time()}".encode()).hexdigest()[:16],
            source_id=source_id, target_id=target_id,
            edge_type=edge_type, weight=weight,
        )
        self.edges.append(edge)
        if target_id not in self.adjacency.get(source_id, []):
            self.adjacency[source_id].append(target_id)
        if source_id not in self.reverse_adjacency.get(target_id, []):
            self.reverse_adjacency[target_id].append(source_id)
        self.nodes[target_id].citation_count += 1
        self.nodes[target_id].cited_by.append(source_id)
        return edge

    def _rebuild_index(self) -> None:
        """Rebuild the embedding matrix for vector search."""
        self._node_id_list = list(self.nodes.keys())
        if not self._node_id_list:
            self._embedding_matrix = np.zeros((0, self.embedding_dim), dtype=np.float32)
            self._index_dirty = False
            return
        self._embedding_matrix = np.stack([
            self.nodes[nid].embedding for nid in self._node_id_list
        ])
        self._index_dirty = False

    def search_vector(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[str, float]]:
        """Vector similarity search. Returns list of (node_id, similarity)."""
        if self._index_dirty:
            self._rebuild_index()
        if self._embedding_matrix.shape[0] == 0:
            return []
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-9)
        matrix_norms = np.linalg.norm(self._embedding_matrix, axis=1, keepdims=True) + 1e-9
        normalized = self._embedding_matrix / matrix_norms
        similarities = normalized @ query_norm
        top_indices = np.argsort(similarities)[::-1][:k]
        return [(self._node_id_list[i], float(similarities[i])) for i in top_indices]

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        return self.nodes.get(node_id)

    def get_citations(self, node_id: str) -> List[str]:
        """Get nodes that this node cites."""
        return self.adjacency.get(node_id, [])

    def get_cited_by(self, node_id: str) -> List[str]:
        """Get nodes that cite this node."""
        return self.reverse_adjacency.get(node_id, [])

    def top_cited(self, k: int = 10, knowledge_type: Optional[KnowledgeType] = None) -> List[KnowledgeNode]:
        """Get top-cited nodes, optionally filtered by type."""
        nodes = list(self.nodes.values())
        if knowledge_type:
            nodes = [n for n in nodes if n.knowledge_type == knowledge_type]
        return sorted(nodes, key=lambda n: n.citation_count, reverse=True)[:k]

    def top_impact(self, k: int = 10) -> List[KnowledgeNode]:
        """Get nodes with highest impact score."""
        return sorted(self.nodes.values(), key=lambda n: n.impact_score, reverse=True)[:k]

    def collaborative_clusters(self, min_size: int = 3) -> List[Set[str]]:
        """Detect clusters of nodes that frequently cite each other."""
        visited: Set[str] = set()
        clusters: List[Set[str]] = []
        for node_id in self.nodes:
            if node_id in visited:
                continue
            cluster = self._bfs_cluster(node_id, visited)
            if len(cluster) >= min_size:
                clusters.append(cluster)
        return clusters

    def _bfs_cluster(self, start: str, visited: Set[str]) -> Set[str]:
        cluster = set()
        queue = [start]
        while queue:
            nid = queue.pop(0)
            if nid in visited:
                continue
            visited.add(nid)
            cluster.add(nid)
            for neighbor in self.adjacency.get(nid, []) + self.reverse_adjacency.get(nid, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        return cluster

    def stats(self) -> dict:
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "total_citations": sum(n.citation_count for n in self.nodes.values()),
            "avg_citations": sum(n.citation_count for n in self.nodes.values()) / max(1, len(self.nodes)),
            "by_type": {kt.value: sum(1 for n in self.nodes.values() if n.knowledge_type == kt) for kt in KnowledgeType},
            "clusters": len(self.collaborative_clusters()),
        }
