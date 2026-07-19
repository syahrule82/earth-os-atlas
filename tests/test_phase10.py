"""Phase 10 integration tests."""
import numpy as np
from decimal import Decimal
from src.knowledge_graph.graph import KnowledgeGraph, KnowledgeNode, KnowledgeType
from src.knowledge_graph.semantic_search import SemanticSearchEngine
from src.knowledge_graph.citations import CitationNetwork
from src.knowledge_graph.synthesis import KnowledgeSynthesizer
from src.knowledge_graph.provenance import ProvenanceTracker
from src.knowledge_graph.expert import ExpertDiscovery
from src.knowledge_graph.trends import TrendAnalyzer
import time

def _make_node(graph, title, creator, ktype, citations=0, rep=1.0, tags=None):
    node = KnowledgeNode(
        node_id=f"node_{len(graph.nodes)}",
        title=title, creator_did=creator,
        knowledge_type=ktype,
        embedding=np.random.randn(512).astype(np.float32),
        content_hash=f"hash_{len(graph.nodes)}",
        reputation_score=rep,
        citation_count=citations,
        tags=tags or [],
    )
    graph.add_node(node)
    return node

def test_knowledge_graph_basic():
    graph = KnowledgeGraph(embedding_dim=512)
    n1 = _make_node(graph, "ATLAS Protocol Spec", "did:atlas:alice", KnowledgeType.RESEARCH, tags=["atlas", "protocol"])
    n2 = _make_node(graph, "BCI Mesh Router", "did:atlas:bob", KnowledgeType.CODE, tags=["bci", "mesh"])
    assert len(graph.nodes) == 2
    graph.add_citation(n2.node_id, n1.node_id, "cites")
    assert n1.citation_count == 1
    assert n1.node_id in graph.get_cited_by(n2.node_id)
    assert n2.node_id in graph.get_citations(n1.node_id) is False  # n2 cites n1, not vice versa
    assert n2.node_id in graph.get_citations(n1.node_id) is False

def test_vector_search():
    graph = KnowledgeGraph(embedding_dim=128)
    for i in range(10):
        _make_node(graph, f"Node {i}", f"did:atlas:user{i}", KnowledgeType.RESEARCH)
    query = np.random.randn(128).astype(np.float32)
    results = graph.search_vector(query, k=5)
    assert len(results) <= 5
    assert all(isinstance(r[0], str) for r in results)
    assert all(0 <= r[1] <= 1.0 for r in results)

def test_semantic_search():
    graph = KnowledgeGraph(embedding_dim=128)
    engine = SemanticSearchEngine(graph)
    for i in range(10):
        node = _make_node(graph, f"Research paper {i}", f"did:atlas:author{i}", KnowledgeType.RESEARCH)
        engine.index_keywords(node.node_id, f"atlas research paper knowledge value creation {i}")
    results = engine.search("atlas research", query_embedding=np.random.randn(128).astype(np.float32), k=5)
    assert len(results) <= 5
    assert all(r.final_score > 0 for r in results)
    auto = engine.autocomplete("atla")
    assert "atlas" in auto

def test_citation_network():
    cn = CitationNetwork()
    cn.add_citation("A", "B")
    cn.add_citation("A", "C")
    cn.add_citation("D", "B")
    cn.add_citation("E", "B")
    cn.add_citation("F", "B")
    assert len(cn.in_edges.get("B", [])) == 3
    impact = cn.compute_impact("B")
    assert impact.total_citations == 3
    assert impact.h_index >= 0
    assert impact.influence_radius >= 0
    lineage = cn.lineage("A")
    assert len(lineage) > 0

def test_knowledge_synthesizer():
    graph = KnowledgeGraph(embedding_dim=128)
    synth = KnowledgeSynthesizer(graph)
    # Add some nodes
    for i in range(5):
        _make_node(graph, f"Node {i}", f"did:atlas:user{i}", KnowledgeType.RESEARCH)
    gaps = synth.detect_gaps()
    # Should detect unexplored areas (some types have 0 nodes)
    assert len(gaps) > 0
    # Generate proposal for first gap
    if gaps:
        proposal = synth.generate_proposal(gaps[0])
        assert proposal.title.startswith("Research:")
        assert 0 <= proposal.novelty_score <= 1.0
    # Literature review
    review = synth.literature_review(np.random.randn(128).astype(np.float32), k=5)
    assert "total_sources" in review

def test_provenance_tracker():
    tracker = ProvenanceTracker()
    tracker.record("node_1", "created", "did:atlas:alice")
    tracker.record("node_1", "cited", "did:atlas:bob")
    tracker.record("node_1", "extended", "did:atlas:charlie")
    history = tracker.get_history("node_1")
    assert len(history) == 3
    assert tracker.verify_chain("node_1") is True
    assert tracker.who_created("node_1") == "did:atlas:alice"

def test_expert_discovery():
    graph = KnowledgeGraph(embedding_dim=128)
    discovery = ExpertDiscovery(graph)
    # Alice contributes 5 papers, Bob contributes 1
    for i in range(5):
        _make_node(graph, f"Alice paper {i}", "did:atlas:alice", KnowledgeType.RESEARCH, citations=i)
    _make_node(graph, "Bob paper", "did:atlas:bob", KnowledgeType.CODE, citations=0)
    experts = discovery.find_experts(np.random.randn(128).astype(np.float32), k=5)
    assert len(experts) >= 1
    alice_profile = discovery.expert_profile("did:atlas:alice")
    assert alice_profile["total_contributions"] == 5
    assert alice_profile["total_citations"] == sum(range(5))

def test_trend_analyzer():
    graph = KnowledgeGraph(embedding_dim=128)
    analyzer = TrendAnalyzer(graph)
    # Add recent nodes
    for i in range(5):
        _make_node(graph, f"Recent {i}", f"did:atlas:new{i}", KnowledgeType.RESEARCH, tags=["ai", "quantum"])
    # Add old nodes
    for i in range(3):
        node = _make_node(graph, f"Old {i}", f"did:atlas:old{i}", KnowledgeType.MEDICAL)
        node.created_at = time.time() - 200 * 86400  # 200 days ago
    report = analyzer.analyze(window_days=30)
    assert report.period == "30d"
    assert len(report.emerging_categories) >= 0
    assert "ai" in report.hot_topics or "quantum" in report.hot_topics

def test_top_cited_and_impact():
    graph = KnowledgeGraph(embedding_dim=128)
    n1 = _make_node(graph, "Highly cited", "did:atlas:alice", KnowledgeType.RESEARCH, citations=50, rep=1.5)
    n2 = _make_node(graph, "Low cited", "did:atlas:bob", KnowledgeType.CODE, citations=2, rep=0.8)
    top = graph.top_cited(k=2)
    assert top[0].node_id == n1.node_id
    impact = graph.top_impact(k=2)
    assert impact[0].node_id == n1.node_id

def test_collaborative_clusters():
    graph = KnowledgeGraph(embedding_dim=128)
    a = _make_node(graph, "A", "u1", KnowledgeType.RESEARCH)
    b = _make_node(graph, "B", "u2", KnowledgeType.RESEARCH)
    c = _make_node(graph, "C", "u3", KnowledgeType.RESEARCH)
    d = _make_node(graph, "D", "u4", KnowledgeType.CODE)  # Isolated
    graph.add_citation(a.node_id, b.node_id)
    graph.add_citation(b.node_id, c.node_id)
    clusters = graph.collaborative_clusters(min_size=2)
    assert len(clusters) >= 1
    # A, B, C should be in one cluster, D alone
    big_cluster = max(clusters, key=len)
    assert a.node_id in big_cluster
    assert b.node_id in big_cluster
    assert c.node_id in big_cluster

def test_graph_stats():
    graph = KnowledgeGraph(embedding_dim=128)
    for i in range(10):
        _make_node(graph, f"Node {i}", f"u{i}", KnowledgeType.RESEARCH)
    stats = graph.stats()
    assert stats["total_nodes"] == 10
    assert "by_type" in stats
    assert stats["by_type"]["research"] == 10

if __name__ == "__main__":
    test_knowledge_graph_basic()
    test_vector_search()
    test_semantic_search()
    test_citation_network()
    test_knowledge_synthesizer()
    test_provenance_tracker()
    test_expert_discovery()
    test_trend_analyzer()
    test_top_cited_and_impact()
    test_collaborative_clusters()
    test_graph_stats()
    print("✅ All Phase 10 tests passed")
