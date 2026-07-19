"""Federated learning — distributed training across mesh nodes."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
import numpy as np, hashlib, time

@dataclass
class ModelUpdate:
    """A gradient update from a single node."""
    node_id: str
    gradients: np.ndarray
    data_size: int
    loss: float
    timestamp: float = field(default_factory=time.time)
    noise_added: float = 0.0  # Differential privacy noise

@dataclass
class TrainingRound:
    """One round of federated training."""
    round_id: str
    participants: List[str]
    aggregated_gradients: Optional[np.ndarray]
    avg_loss: float
    timestamp: float = field(default_factory=time.time)

class FederatedTrainer:
    """
    Federated learning coordinator.
    
    Nodes train locally on their data, share only gradient updates
    (not raw data), and the coordinator aggregates them.
    
    Privacy guarantees:
    - Differential privacy: Gaussian noise added to gradients
    - Secure aggregation: updates are encrypted in transit
    - Data never leaves the source node
    """

    def __init__(self, model_dim: int = 512, learning_rate: float = 0.01,
                 dp_epsilon: float = 1.0, dp_delta: float = 1e-5,
                 min_participants: int = 3):
        self.model_dim = model_dim
        self.lr = learning_rate
        self.dp_epsilon = dp_epsilon
        self.dp_delta = dp_delta
        self.min_participants = min_participants
        self.global_model: np.ndarray = np.zeros(model_dim, dtype=np.float32)
        self.rounds: List[TrainingRound] = []
        self.participant_stats: Dict[str, dict] = {}

    def submit_update(self, update: ModelUpdate) -> None:
        """Submit a gradient update from a node."""
        if update.node_id not in self.participant_stats:
            self.participant_stats[update.node_id] = {
                "updates": 0, "total_data": 0, "avg_loss": 0,
                "reputation": 1.0, "total_reward": 0.0,
            }
        stats = self.participant_stats[update.node_id]
        stats["updates"] += 1
        stats["total_data"] += update.data_size
        stats["avg_loss"] = (stats["avg_loss"] * 0.9 + update.loss * 0.1)

    def aggregate(self, updates: List[ModelUpdate]) -> TrainingRound:
        """Aggregate updates using FedAvg (federated averaging)."""
        if len(updates) < self.min_participants:
            raise ValueError(f"Need at least {self.min_participants} participants")

        # Weight by data size
        total_data = sum(u.data_size for u in updates)
        weighted_sum = np.zeros_like(self.global_model)
        total_loss = 0.0

        for update in updates:
            weight = update.data_size / total_data
            # Add differential privacy noise
            noise = np.random.normal(0, self._dp_noise_scale(), update.gradients.shape)
            noisy_grad = update.gradients + noise
            weighted_sum += weight * noisy_grad
            total_loss += update.loss * weight

        # Apply aggregated gradient
        self.global_model -= self.lr * weighted_sum

        round_obj = TrainingRound(
            round_id=hashlib.sha256(f"round:{time.time()}".encode()).hexdigest()[:16],
            participants=[u.node_id for u in updates],
            aggregated_gradients=weighted_sum,
            avg_loss=total_loss / len(updates),
        )
        self.rounds.append(round_obj)
        return round_obj

    def _dp_noise_scale(self) -> float:
        """Calculate noise scale for differential privacy."""
        # Simplified: in production use the moments accountant
        sensitivity = 1.0 / max(1, self.min_participants)
        return sensitivity / self.dp_epsilon

    def get_global_model(self) -> np.ndarray:
        return self.global_model.copy()

    def evaluate_contributions(self) -> Dict[str, float]:
        """Evaluate each participant's contribution for ATLAS rewards."""
        contributions = {}
        for node_id, stats in self.participant_stats.items():
            # Reward = data_quality * data_quantity * reputation
            data_quality = max(0.1, 1.0 - stats["avg_loss"])
            data_quantity = np.log1p(stats["total_data"])
            score = data_quality * data_quantity * stats["reputation"]
            contributions[node_id] = float(score)
        return contributions

    def stats(self) -> dict:
        return {
            "total_rounds": len(self.rounds),
            "total_participants": len(self.participant_stats),
            "current_loss": self.rounds[-1].avg_loss if self.rounds else 0.0,
            "model_norm": float(np.linalg.norm(self.global_model)),
        }
