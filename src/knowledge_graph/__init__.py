"""ATLAS Knowledge Graph — Global contribution indexing and semantic search."""
from .graph import KnowledgeGraph, KnowledgeNode, KnowledgeEdge
from .semantic_search import SemanticSearchEngine, SearchResult
from .citations import CitationNetwork, Citation, CitationImpact
from .synthesis import KnowledgeSynthesizer, KnowledgeGap, ResearchProposal
from .provenance import ProvenanceTracker, ProvenanceRecord
from .expert import ExpertDiscovery, ExpertProfile
from .trends import TrendAnalyzer, TrendReport

__all__ = ["KnowledgeGraph", "KnowledgeNode", "KnowledgeEdge",
           "SemanticSearchEngine", "SearchResult",
           "CitationNetwork", "Citation", "CitationImpact",
           "KnowledgeSynthesizer", "KnowledgeGap", "ResearchProposal",
           "ProvenanceTracker", "ProvenanceRecord",
           "ExpertDiscovery", "ExpertProfile",
           "TrendAnalyzer", "TrendReport"]
