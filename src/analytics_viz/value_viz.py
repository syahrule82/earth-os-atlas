"""Value Flow Visualization — Sankey diagrams, network graphs, heat maps."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
from decimal import Decimal
import time

@dataclass
class SankeyData:
    """Data for a Sankey diagram (flow visualization)."""
    nodes: List[dict] = field(default_factory=list)  # [{"id": "", "name": "", "color": ""}]
    links: List[dict] = field(default_factory=list)  # [{"source": 0, "target": 1, "value": 100}]

    def add_node(self, node_id: str, name: str, color: str = "") -> int:
        idx = len(self.nodes)
        self.nodes.append({"id": node_id, "name": name, "color": color})
        return idx

    def add_link(self, source_idx: int, target_idx: int, value: float) -> None:
        self.links.append({"source": source_idx, "target": target_idx, "value": value})

    def to_dict(self) -> dict:
        return {"nodes": self.nodes, "links": self.links}

@dataclass
class NetworkGraphData:
    """Data for a network graph visualization."""
    nodes: List[dict] = field(default_factory=list)
    edges: List[dict] = field(default_factory=list)

    def add_node(self, node_id: str, label: str, node_type: str = "node",
                 size: float = 10, color: str = "") -> None:
        self.nodes.append({
            "id": node_id, "label": label,
            "type": node_type, "size": size, "color": color,
        })

    def add_edge(self, source: str, target: str, weight: float = 1,
                 color: str = "") -> None:
        self.edges.append({
            "source": source, "target": target,
            "weight": weight, "color": color,
        })

    def to_dict(self) -> dict:
        return {"nodes": self.nodes, "edges": self.edges}

class ValueFlowVisualizer:
    """
    Generates visualization data for value flows across the ATLAS network.
    """

    def __init__(self):
        self.flow_history: List[dict] = []

    def build_sankey(self, flows: List[dict]) -> SankeyData:
        """Build Sankey diagram data from value flows.
        
        Args:
            flows: List of {"source": str, "target": str, "amount": float, "category": str}
        """
        sankey = SankeyData()
        node_map: Dict[str, int] = {}

        # Category colors
        colors = {
            "CREATED_KNOWLEDGE": "#3498db",
            "BUILT_INFRASTRUCTURE": "#e74c3c",
            "HEALED_BIOLOGICAL": "#2ecc71",
            "RESTORED_ECOLOGICAL": "#27ae60",
            "SOLVED_PROBLEM": "#f39c12",
            "OPTIMIZED_PROCESS": "#9b59b6",
        }

        for flow in flows:
            src = flow.get("source", "unknown")
            tgt = flow.get("target", "unknown")
            amount = float(flow.get("amount", 0))
            cat = flow.get("category", "UNKNOWN")
            color = colors.get(cat, "#95a5a6")

            if src not in node_map:
                node_map[src] = sankey.add_node(src, src, color)
            if tgt not in node_map:
                node_map[tgt] = sankey.add_node(tgt, tgt, color)

            sankey.add_link(node_map[src], node_map[tgt], amount)

        return sankey

    def build_network_graph(self, contributors: List[dict]) -> NetworkGraphData:
        """Build network graph from contributor relationships.
        
        Args:
            contributors: List of {"did": str, "name": str, "contributions": int, "collaborators": [str]}
        """
        graph = NetworkGraphData()
        for c in contributors:
            size = max(10, min(50, c.get("contributions", 1) * 2))
            graph.add_node(c["did"], c.get("name", c["did"]),
                          node_type="contributor", size=size)
            for collaborator in c.get("collaborators", []):
                graph.add_edge(c["did"], collaborator, weight=1)
        return graph

    def build_heat_map(self, geographic_data: List[dict]) -> List[dict]:
        """Build heat map data for geographic value distribution.
        
        Args:
            geographic_data: List of {"region": str, "lat": float, "lon": float, "value": float}
        """
        return [
            {"region": d["region"],
             "lat": d["lat"], "lon": d["lon"],
             "value": d["value"],
             "intensity": min(1.0, d["value"] / 1000)}
            for d in geographic_data
        ]

    def category_distribution(self, flows: List[dict]) -> List[dict]:
        """Build pie chart data for value category distribution."""
        from collections import defaultdict
        totals = defaultdict(float)
        for f in flows:
            totals[f.get("category", "UNKNOWN")] += float(f.get("amount", 0))
        return [{"name": k, "value": v} for k, v in sorted(totals.items(), key=lambda x: -x[1])]

    def time_series(self, flows: List[dict], interval: str = "daily") -> List[dict]:
        """Build time series data for value creation over time."""
        from collections import defaultdict
        buckets = defaultdict(float)
        for f in flows:
            ts = f.get("timestamp", time.time())
            if interval == "daily":
                bucket = int(ts // 86400) * 86400
            elif interval == "hourly":
                bucket = int(ts // 3600) * 3600
            else:
                bucket = int(ts)
            buckets[bucket] += float(f.get("amount", 0))
        return [{"timestamp": k, "value": v} for k, v in sorted(buckets.items())]
