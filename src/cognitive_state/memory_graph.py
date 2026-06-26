"""
Working Memory Graph
Directed weighted graph of active memory traces.
Spreading activation + cosine-similarity search.
"""
from __future__ import annotations
import time, uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class MemoryTrace:
    trace_id:    str
    content:     str
    embedding:   np.ndarray
    activation:  float
    created_at:  float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    tags:        List[str] = field(default_factory=list)

    def decay(self, now: float, rate: float = 0.05) -> None:
        dt = now - self.last_active
        self.activation = float(np.clip(self.activation * np.exp(-rate * dt), 0, 1))


class WorkingMemoryGraph:
    def __init__(self, max_nodes: int = 64, decay_rate: float = 0.05):
        self.max_nodes  = max_nodes
        self.decay_rate = decay_rate
        self._nodes: Dict[str, MemoryTrace] = {}
        self._edges: List[dict] = []

    def add_trace(
        self, content: str, embedding: Optional[np.ndarray] = None,
        activation: float = 1.0, tags: Optional[List[str]] = None,
    ) -> MemoryTrace:
        if len(self._nodes) >= self.max_nodes:
            self._evict()
        t = MemoryTrace(
            trace_id   = str(uuid.uuid4()),
            content    = content,
            embedding  = embedding if embedding is not None else np.zeros(512, np.float32),
            activation = activation,
            tags       = tags or [],
        )
        self._nodes[t.trace_id] = t
        return t

    def most_active(self, k: int = 5) -> List[MemoryTrace]:
        self._decay_all()
        return sorted(self._nodes.values(), key=lambda t: t.activation, reverse=True)[:k]

    def semantic_search(
        self, query: np.ndarray, k: int = 5
    ) -> List[Tuple[MemoryTrace, float]]:
        self._decay_all()
        q = query / (np.linalg.norm(query) + 1e-9)
        scored = [
            (t, float(np.dot(q, t.embedding / (np.linalg.norm(t.embedding) + 1e-9))) * t.activation)
            for t in self._nodes.values()
        ]
        return sorted(scored, key=lambda x: x[1], reverse=True)[:k]

    def _decay_all(self):
        now = time.time()
        for t in self._nodes.values():
            t.decay(now, self.decay_rate)

    def _evict(self):
        self._decay_all()
        least = min(self._nodes.values(), key=lambda t: t.activation)
        del self._nodes[least.trace_id]
        self._edges = [e for e in self._edges if e["src"] != least.trace_id and e["tgt"] != least.trace_id]
