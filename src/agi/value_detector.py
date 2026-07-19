"""AGI Value Detector — Autonomous value recognition via neural-symbolic reasoning."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np, time, hashlib

@dataclass
class ReasoningChain:
    """A chain of logical steps leading to a value assessment."""
    chain_id:   str
    steps:      List[str]
    conclusion: str
    confidence: float
    evidence:   List[str]
    timestamp:  float = field(default_factory=time.time)

@dataclass
class ValueHypothesis:
    """A hypothesis about the value of an observed action."""
    hypothesis_id:  str
    category:       str
    magnitude:      float
    confidence:     float
    reasoning:      ReasoningChain
    counterfactual: Optional[str] = None  # what would have happened without this action
    timestamp:      float = field(default_factory=time.time)

class AGIValueDetector:
    """
    Uses neural-symbolic reasoning to autonomously detect and
    categorize value creation events without human attestation.
    
    Combines:
    - Neural pattern recognition (embedding similarity)
    - Symbolic logical rules (formal value taxonomy)
    - Counterfactual reasoning (what would have happened otherwise)
    """

    def __init__(self, embedding_dim: int = 512):
        self.embedding_dim = embedding_dim
        self.known_patterns: Dict[str, np.ndarray] = {}
        self.hypothesis_history: List[ValueHypothesis] = []
        self.detection_count = 0

    def detect_value(
        self,
        action_embedding: np.ndarray,
        action_description: str,
        context: dict,
    ) -> ValueHypothesis:
        """Detect and categorize value from an observed action."""
        # Step 1: Neural pattern matching
        best_match = self._pattern_match(action_embedding)

        # Step 2: Symbolic rule evaluation
        category, rule_conf = self._apply_rules(action_description, context)

        # Step 3: Counterfactual reasoning
        counterfactual = self._counterfactual(context)

        # Step 4: Magnitude estimation
        magnitude = self._estimate_magnitude(action_embedding, context)

        # Step 5: Confidence aggregation
        confidence = (best_match[1] * 0.4 + rule_conf * 0.3 + 
                       (1.0 if counterfactual else 0.5) * 0.3)

        chain = ReasoningChain(
            chain_id=hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:16],
            steps=[
                f"Neural pattern match: {best_match[0]} (sim={best_match[1]:.3f})",
                f"Symbolic rule evaluation: category={category} (conf={rule_conf:.3f})",
                f"Counterfactual analysis: {counterfactual or 'baseline'}",
                f"Magnitude estimation: {magnitude:.2f}",
                f"Confidence aggregation: {confidence:.3f}",
            ],
            conclusion=f"Value detected: {category} with magnitude {magnitude:.2f}",
            confidence=confidence,
            evidence=[action_description, str(context)],
        )

        hypothesis = ValueHypothesis(
            hypothesis_id=hashlib.sha256(f"{self.detection_count}:{time.time()}".encode()).hexdigest()[:16],
            category=category,
            magnitude=magnitude,
            confidence=confidence,
            reasoning=chain,
            counterfactual=counterfactual,
        )
        self.hypothesis_history.append(hypothesis)
        self.detection_count += 1
        return hypothesis

    def register_pattern(self, name: str, embedding: np.ndarray) -> None:
        self.known_patterns[name] = embedding

    def _pattern_match(self, embedding: np.ndarray) -> Tuple[str, float]:
        if not self.known_patterns:
            return ("unknown", 0.5)
        best_name, best_sim = "unknown", 0.0
        norm_e = embedding / (np.linalg.norm(embedding) + 1e-9)
        for name, pattern in self.known_patterns.items():
            norm_p = pattern / (np.linalg.norm(pattern) + 1e-9)
            sim = float(np.dot(norm_e, norm_p))
            if sim > best_sim:
                best_name, best_sim = name, sim
        return (best_name, best_sim)

    def _apply_rules(self, description: str, context: dict) -> Tuple[str, float]:
        """Apply symbolic rules to determine value category."""
        rules = {
            "BUILT_INFRASTRUCTURE": ["deploy", "build", "construct", "code", "server"],
            "CREATED_KNOWLEDGE": ["research", "paper", "documentation", "teach"],
            "HEALED_BIOLOGICAL": ["patient", "treatment", "medicine", "therapy"],
            "OPTIMIZED_PROCESS": ["optimize", "efficiency", "automate", "faster"],
            "RESTORED_ECOLOGICAL": ["carbon", "tree", "pollution", "renewable"],
        }
        words = description.lower().split()
        best_cat, best_score = "CREATED_KNOWLEDGE", 0.0
        for cat, kws in rules.items():
            score = sum(w in words for w in kws) / max(1, len(words))
            if score > best_score:
                best_cat, best_score = cat, score
        return best_cat, min(1.0, best_score * 10)

    def _counterfactual(self, context: dict) -> Optional[str]:
        """What would have happened without this action?"""
        if context.get("before_state") and context.get("after_state"):
            return f"Without action: {context['before_state']} would persist"
        return None

    def _estimate_magnitude(self, embedding: np.ndarray, context: dict) -> float:
        """Estimate value magnitude from embedding norm and context."""
        base = float(np.linalg.norm(embedding)) * 10
        people_affected = context.get("people_affected", 1)
        duration_hours = context.get("duration_hours", 1)
        return base * np.log1p(people_affected) * np.log1p(duration_hours)
