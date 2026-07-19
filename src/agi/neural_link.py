"""Neural-symbolic bridge — connects neural embeddings with symbolic rules."""
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

@dataclass
class EmbeddingEncoder:
    """Encodes actions/events into embedding vectors."""
    dim: int = 512

    def encode_text(self, text: str) -> np.ndarray:
        """Simple hash-based embedding (production: use transformer encoder)."""
        import hashlib
        vec = np.zeros(self.dim, dtype=np.float32)
        for i, word in enumerate(text.lower().split()):
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        norm = np.linalg.norm(vec) + 1e-9
        return vec / norm

    def encode_action(self, action_type: str, metadata: dict) -> np.ndarray:
        """Encode structured action into embedding."""
        text = f"{action_type} {' '.join(str(v) for v in metadata.values())}"
        return self.encode_text(text)

class NeuralSymbolicBridge:
    """
    Bridges neural pattern recognition with symbolic reasoning.
    Neural detects patterns → symbolic validates with rules.
    """

    def __init__(self, encoder: EmbeddingEncoder):
        self.encoder = encoder
        self.pattern_store: Dict[str, np.ndarray] = {}
        self.symbolic_mapping: Dict[str, str] = {}  # pattern_name -> rule_conclusion

    def register_pattern(self, name: str, example_text: str, symbolic_conclusion: str) -> None:
        embedding = self.encoder.encode_text(example_text)
        self.pattern_store[name] = embedding
        self.symbolic_mapping[name] = symbolic_conclusion

    def classify(self, text: str) -> Dict:
        """Classify text using neural pattern matching + symbolic mapping."""
        embedding = self.encoder.encode_text(text)
        best_name, best_sim = "unknown", 0.0
        for name, pattern in self.pattern_store.items():
            sim = float(np.dot(embedding, pattern))
            if sim > best_sim:
                best_name, best_sim = name, sim
        return {
            "pattern": best_name,
            "similarity": best_sim,
            "symbolic_conclusion": self.symbolic_mapping.get(best_name, "UNKNOWN"),
            "embedding_norm": float(np.linalg.norm(embedding)),
        }
