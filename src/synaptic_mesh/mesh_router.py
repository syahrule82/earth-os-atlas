"""
Mesh Router — Synaptic Network Layer
Routes thought packets through the neural mesh.
Dijkstra pathfinding with latency minimization.
"""
from typing import Dict, List, Optional, Set, Tuple
import heapq


class MeshRouter:
    """Neural packet router with latency-aware pathfinding."""

    def __init__(self, max_hops: int = 16):
        self.max_hops   = max_hops
        self.routes:    Dict[str, List[str]]           = {}
        self.latencies: Dict[Tuple[str, str], float]  = {}

    def add_route(
        self, source: str, destinations: List[str], latencies: List[float]
    ) -> None:
        self.routes[source] = destinations
        for dest, lat in zip(destinations, latencies):
            self.latencies[(source, dest)] = lat

    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """Dijkstra pathfinding — returns None if no path within max_hops."""
        if source == target:
            return [source]
        pq: List[Tuple[float, str, List[str]]] = [(0.0, source, [source])]
        visited: Set[str] = set()
        while pq:
            cost, node, path = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)
            if node == target:
                return path if len(path) <= self.max_hops else None
            for neighbor in self.routes.get(node, []):
                if neighbor not in visited:
                    new_cost = cost + self.latencies.get((node, neighbor), 100.0)
                    heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))
        return None
