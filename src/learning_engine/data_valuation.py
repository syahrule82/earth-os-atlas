"""Data valuation — Shapley value estimation for training data."""
from dataclasses import dataclass
from typing import Dict, List
import numpy as np

class ShapleyEstimator:
    """
    Estimates Shapley values for training data contributions.
    
    Shapley value = marginal contribution of a data point
    averaged over all possible orderings of the dataset.
    """

    def __init__(self, max_samples: int = 100):
        self.max_samples = max_samples

    def estimate(self, data_indices: List[int], eval_fn) -> Dict[int, float]:
        """
        Estimate Shapley values using Monte Carlo sampling.
        
        Args:
            data_indices: List of data point indices
            eval_fn: Function(subset_indices) -> performance score
        
        Returns:
            Dict mapping data_index -> Shapley value
        """
        n = len(data_indices)
        if n == 0:
            return {}

        shapley = {idx: 0.0 for idx in data_indices}
        
        for _ in range(self.max_samples):
            # Random permutation
            perm = list(data_indices)
            np.random.shuffle(perm)
            
            prev_score = 0.0
            for i, idx in enumerate(perm):
                subset = perm[:i+1]
                current_score = eval_fn(subset)
                marginal = current_score - prev_score
                shapley[idx] += marginal
                prev_score = current_score
        
        # Average over samples
        for idx in shapley:
            shapley[idx] /= self.max_samples
        
        return shapley

class DataValuator:
    """Values training data for ATLAS reward calculation."""

    def __init__(self):
        self.estimator = ShapleyEstimator(max_samples=50)
        self.valuations: Dict[str, Dict[int, float]] = {}  # dataset_id -> valuations

    def value_dataset(self, dataset_id: str, data_indices: List[int],
                      eval_fn) -> Dict[int, float]:
        """Compute Shapley values for a dataset."""
        shapley = self.estimator.estimate(data_indices, eval_fn)
        self.valuations[dataset_id] = shapley
        return shapley

    def top_contributors(self, dataset_id: str, k: int = 10) -> List[tuple]:
        """Get top-k most valuable data points."""
        vals = self.valuations.get(dataset_id, {})
        return sorted(vals.items(), key=lambda x: x[1], reverse=True)[:k]

    def total_value(self, dataset_id: str) -> float:
        """Total Shapley value (should equal dataset performance)."""
        return sum(self.valuations.get(dataset_id, {}).values())
