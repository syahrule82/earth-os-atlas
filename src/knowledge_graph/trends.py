"""Trend analyzer — detect emerging research directions."""
from dataclasses import dataclass, field
from typing import Dict, List
from collections import defaultdict
import time

@dataclass
class TrendReport:
    period: str
    emerging_categories: List[dict]
    declining_categories: List[dict]
    hot_topics: List[str]
    top_new_contributors: List[str]
    citation_trends: Dict[str, float]
    timestamp: float = field(default_factory=time.time)

class TrendAnalyzer:
    """Analyzes trends in the knowledge graph over time."""

    def __init__(self, graph):
        self.graph = graph
        self.history: List[TrendReport] = []

    def analyze(self, window_days: int = 30) -> TrendReport:
        """Generate a trend report for the last N days."""
        now = time.time()
        cutoff = now - window_days * 86400

        # Recent vs older contributions by type
        recent_by_type: Dict[str, int] = defaultdict(int)
        older_by_type: Dict[str, int] = defaultdict(int)
        new_contributors: set = set()

        for node in self.graph.nodes.values():
            if node.created_at >= cutoff:
                recent_by_type[node.knowledge_type.value] += 1
                new_contributors.add(node.creator_did)
            else:
                older_by_type[node.knowledge_type.value] += 1

        # Emerging: recent proportion higher than historical
        emerging = []
        for kt, recent_count in recent_by_type.items():
            older_count = older_by_type.get(kt, 1)
            growth_rate = (recent_count - older_count / max(1, window_days / 30)) / max(1, older_count)
            if growth_rate > 0.2:
                emerging.append({"category": kt, "growth_rate": growth_rate, "count": recent_count})

        # Declining
        declining = []
        for kt, older_count in older_by_type.items():
            recent_count = recent_by_type.get(kt, 0)
            if older_count > 5 and recent_count < older_count / 3:
                declining.append({"category": kt, "decline_rate": 1 - recent_count / older_count})

        # Hot topics from tags
        tag_counts: Dict[str, int] = defaultdict(int)
        for node in self.graph.nodes.values():
            if node.created_at >= cutoff:
                for tag in node.tags:
                    tag_counts[tag] += 1
        hot_topics = sorted(tag_counts.keys(), key=lambda t: tag_counts[t], reverse=True)[:10]

        # Citation trends
        citation_trends: Dict[str, float] = {}
        for node in self.graph.nodes.values():
            if node.created_at >= cutoff and node.citation_count > 0:
                kt = node.knowledge_type.value
                citation_trends[kt] = citation_trends.get(kt, 0) + node.citation_count

        report = TrendReport(
            period=f"{window_days}d",
            emerging_categories=sorted(emerging, key=lambda x: x["growth_rate"], reverse=True)[:5],
            declining_categories=sorted(declining, key=lambda x: x["decline_rate"], reverse=True)[:5],
            hot_topics=hot_topics,
            top_new_contributors=list(new_contributors)[:10],
            citation_trends=citation_trends,
        )
        self.history.append(report)
        return report
