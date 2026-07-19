"""Model interpretability — explainability for governance transparency."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

class ModelInterpreter:
    """
    Provides interpretability for AI models used in ATLAS governance.
    Ensures decisions are explainable and auditable.
    """

    def feature_importance(self, model_weights: np.ndarray) -> Dict[str, float]:
        """Compute feature importance from model weights."""
        abs_weights = np.abs(model_weights)
        total = abs_weights.sum() + 1e-9
        importances = {f"feature_{i}": float(w / total) for i, w in enumerate(abs_weights)}
        # Return top 10
        sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]
        return dict(sorted_imp)

    def decision_path(self, input_features: np.ndarray,
                      model_weights: np.ndarray) -> List[str]:
        """Trace decision path through the model."""
        steps = []
        for i, (feat, weight) in enumerate(zip(input_features, model_weights)):
            if abs(feat * weight) > 0.1:
                direction = "positive" if feat * weight > 0 else "negative"
                steps.append(f"Feature {i} ({direction}): contribution={feat * weight:.4f}")
        return steps

    def counterfactual(self, input_features: np.ndarray,
                       model_weights: np.ndarray,
                       target_output: float) -> np.ndarray:
        """Find minimal change to input to reach target output."""
        current = float(np.dot(input_features, model_weights))
        diff = target_output - current
        # Distribute change across least important features
        abs_weights = np.abs(model_weights) + 1e-9
        # Change the feature with smallest weight (cheapest to change)
        min_idx = np.argmin(abs_weights)
        modified = input_features.copy()
        modified[min_idx] += diff / model_weights[min_idx]
        return modified

    def bias_check(self, model_weights: np.ndarray,
                   protected_features: List[int]) -> Dict:
        """Check for bias in protected features."""
        abs_weights = np.abs(model_weights)
        total = abs_weights.sum() + 1e-9
        protected_influence = sum(abs_weights[i] for i in protected_features) / total
        return {
            "protected_features": protected_features,
            "influence_score": float(protected_influence),
            "threshold": 0.1,
            "biased": protected_influence > 0.1,
            "recommendation": "Retrain with fairness constraints" if protected_influence > 0.1 else "No bias detected",
        }
