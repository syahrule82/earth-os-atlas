"""Value Flow Graph — real-time global value flow visualization."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal
import time, hashlib

@dataclass
class FlowNode:
    """A node in the value flow graph (person, region, category)."""
    node_id: str
    node_type: str  # person, region, category, titan
    label: str
    total_inflow: Decimal = Decimal("0")
    total_outflow: Decimal = Decimal("0")
    connections: int = 0

@dataclass
class FlowEdge:
    """A directed edge representing value flow between nodes."""
    source: str
    target: str
    amount: Decimal
    category: str
    timestamp: float = field(default_factory=time.time)

class ValueFlowGraph:
    """
    Tracks the flow of ATLAS value across the network.
    Enables real-time visualization of value creation and transfer.
    """
    
    def __init__(self):
        self.nodes: Dict[str, FlowNode] = {}
        self.edges: List[FlowEdge] = []
        self.max_edges = 100000  # Rolling window
    
    def add_flow(self, source: str, target: str, amount: Decimal,
                 category: str, node_type: str = "person") -> None:
        """Record a value flow."""
        # Ensure nodes exist
        if source not in self.nodes:
            self.nodes[source] = FlowNode(source, node_type, source)
        if target not in self.nodes:
            self.nodes[target] = FlowNode(target, node_type, target)
        
        # Update node stats
        self.nodes[source].total_outflow += amount
        self.nodes[target].total_inflow += amount
        self.nodes[source].connections += 1
        self.nodes[target].connections += 1
        
        # Add edge
        self.edges.append(FlowEdge(source, target, amount, category))
        
        # Trim old edges
        if len(self.edges) > self.max_edges:
            self.edges = self.edges[-self.max_edges:]
    
    def top_creators(self, n: int = 10) -> List[FlowNode]:
        """Get top value creators by total outflow."""
        return sorted(self.nodes.values(), key=lambda n: n.total_outflow, reverse=True)[:n]
    
    def top_recipients(self, n: int = 10) -> List[FlowNode]:
        """Get top value recipients by total inflow."""
        return sorted(self.nodes.values(), key=lambda n: n.total_inflow, reverse=True)[:n]
    
    def flow_by_category(self) -> Dict[str, Decimal]:
        """Aggregate flows by value category."""
        from collections import defaultdict
        totals = defaultdict(lambda: Decimal("0"))
        for edge in self.edges:
            totals[edge.category] += edge.amount
        return dict(totals)
    
    def flow_by_region(self, region_map: Dict[str, str]) -> Dict[str, Decimal]:
        """Aggregate flows by region."""
        from collections import defaultdict
        totals = defaultdict(lambda: Decimal("0"))
        for edge in self.edges:
            region = region_map.get(edge.source, "unknown")
            totals[region] += edge.amount
        return dict(totals)
    
    def stats(self) -> dict:
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "total_flow": str(sum(e.amount for e in self.edges)),
            "avg_flow": str(sum(e.amount for e in self.edges) / max(1, len(self.edges))),
        }
