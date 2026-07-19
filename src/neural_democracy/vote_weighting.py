"""Cognitive vote weighting — weights votes by cognitive state."""
from dataclasses import dataclass
from typing import Dict, List
import numpy as np

@dataclass
class VoteWeight:
    base_weight: float
    cognitive_multiplier: float
    final_weight: float
    factors: Dict[str, float]

class CognitiveVoteWeighter:
    """
    Weights neural votes based on cognitive state.
    
    Higher cognitive load and focus = higher vote weight.
    Low confidence or high stress = reduced weight.
    """

    def __init__(self):
        self.min_weight = 0.1
        self.max_weight = 2.0

    def weight_vote(self, confidence: float, cognitive_load: float,
                    stress_level: float = 0.0,
                    reputation: float = 1.0) -> VoteWeight:
        """Calculate weighted vote strength."""
        # Base weight from reputation
        base = max(self.min_weight, min(self.max_weight, reputation))

        # Cognitive multiplier: high focus + low stress = higher weight
        focus_factor = np.tanh(cognitive_load * 2)  # 0-1, higher = more focused
        stress_penalty = 1 - np.clip(stress_level, 0, 0.5)  # Reduce by up to 50%
        confidence_factor = np.clip(confidence, 0.3, 1.0)

        cognitive_multiplier = focus_factor * stress_penalty * confidence_factor

        final = np.clip(base * cognitive_multiplier, self.min_weight, self.max_weight)

        return VoteWeight(
            base_weight=base,
            cognitive_multiplier=float(cognitive_multiplier),
            final_weight=float(final),
            factors={
                "focus": float(focus_factor),
                "stress_penalty": float(stress_penalty),
                "confidence": float(confidence_factor),
                "reputation": float(reputation),
            },
        )

    def batch_weight(self, votes: List[dict]) -> List[VoteWeight]:
        """Weight multiple votes."""
        return [
            self.weight_vote(
                confidence=v.get("confidence", 0.5),
                cognitive_load=v.get("cognitive_load", 0.5),
                stress_level=v.get("stress_level", 0),
                reputation=v.get("reputation", 1.0),
            )
            for v in votes
        ]
