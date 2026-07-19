"""Semantic search engine — hybrid keyword + vector + citation search."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np, hashlib, time
from .graph import KnowledgeGraph, KnowledgeType

@dataclass
class SearchResult:
    node_id: str
    title: str
    creator: str
    similarity: float
    keyword_score: float
    citation_score: float
    final_score: float
    knowledge_type: str
    highlights: List[str] = field(default_factory=list)

class SemanticSearchEngine:
    """
    Hybrid search engine combining:
    - Vector similarity (semantic meaning)
    - Keyword matching (exact terms)
    - Citation weighting (impact)
    - Freshness boost (recent contributions)
    - Reputation boost (trusted creators)
    """

    WEIGHTS = {
        "semantic": 0.40,
        "keyword": 0.25,
        "citation": 0.15,
        "freshness": 0.10,
        "reputation": 0.10,
    }

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph
        self.keyword_index: Dict[str, List[str]] = {}  # keyword -> [node_ids]

    def index_keywords(self, node_id: str, text: str) -> None:
        """Build keyword index from text content."""
        words = set(text.lower().split())
        for word in words:
            if len(word) < 3:
                continue
            if word not in self.keyword_index:
                self.keyword_index[word] = []
            if node_id not in self.keyword_index[word]:
                self.keyword_index[word].append(node_id)

    def search(self, query: str, query_embedding: Optional[np.ndarray] = None,
               k: int = 10, knowledge_type: Optional[KnowledgeType] = None) -> List[SearchResult]:
        """Hybrid search across the knowledge graph."""
        # 1. Semantic search
        semantic_results: Dict[str, float] = {}
        if query_embedding is not None:
            vec_results = self.graph.search_vector(query_embedding, k=k*3)
            semantic_results = {nid: sim for nid, sim in vec_results}

        # 2. Keyword search
        query_words = set(query.lower().split())
        keyword_scores: Dict[str, float] = {}
        for word in query_words:
            if word in self.keyword_index:
                for node_id in self.keyword_index[word]:
                    keyword_scores[node_id] = keyword_scores.get(node_id, 0) + 1.0
        max_kw = max(keyword_scores.values()) if keyword_scores else 1.0
        keyword_scores = {k: v / max_kw for k, v in keyword_scores.items()}

        # 3. Combine candidate sets
        all_candidates = set(semantic_results.keys()) | set(keyword_scores.keys())
        if knowledge_type:
            all_candidates = {nid for nid in all_candidates
                            if self.graph.get_node(nid) and
                            self.graph.get_node(nid).knowledge_type == knowledge_type}

        # 4. Score each candidate
        results: List[SearchResult] = []
        now = time.time()
        for node_id in all_candidates:
            node = self.graph.get_node(node_id)
            if not node:
                continue

            sem_score = semantic_results.get(node_id, 0.0)
            kw_score = keyword_scores.get(node_id, 0.0)
            cit_score = min(1.0, node.citation_count / 10.0)
            age_days = (now - node.created_at) / 86400
            fresh_score = max(0, 1.0 - age_days / 365)  # Decay over 1 year
            rep_score = min(1.0, node.reputation_score / 2.0)

            final = (
                sem_score * self.WEIGHTS["semantic"] +
                kw_score * self.WEIGHTS["keyword"] +
                cit_score * self.WEIGHTS["citation"] +
                fresh_score * self.WEIGHTS["freshness"] +
                rep_score * self.WEIGHTS["reputation"]
            )

            results.append(SearchResult(
                node_id=node_id,
                title=node.title,
                creator=node.creator_did,
                similarity=sem_score,
                keyword_score=kw_score,
                citation_score=cit_score,
                final_score=final,
                knowledge_type=node.knowledge_type.value,
            ))

        return sorted(results, key=lambda r: r.final_score, reverse=True)[:k]

    def autocomplete(self, prefix: str, limit: int = 5) -> List[str]:
        """Suggest completions for a search prefix."""
        prefix_lower = prefix.lower()
        matches = [kw for kw in self.keyword_index if kw.startswith(prefix_lower)]
        return sorted(matches, key=lambda kw: len(self.keyword_index[kw]), reverse=True)[:limit]
