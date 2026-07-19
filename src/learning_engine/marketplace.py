"""AI Model Marketplace — on-chain model registry and trading."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal
import hashlib, time

@dataclass
class ModelCard:
    """Metadata for an AI model on the marketplace."""
    model_id: str
    name: str
    creator: str
    description: str
    model_type: str  # classifier, regressor, generator, embedder
    input_dim: int
    output_dim: int
    weight_hash: str  # Hash of model weights (commitment)
    ipfs_cid: Optional[str] = None
    price_per_use: Decimal = Decimal("0.1")  # ATLAS per inference
    license_type: str = "MIT"
    created_at: float = field(default_factory=time.time)
    downloads: int = 0
    rating: float = 0.0
    evaluations: List[str] = field(default_factory=list)

@dataclass
class ModelEvaluation:
    """Evaluation result for a model."""
    eval_id: str
    model_id: str
    evaluator: str
    dataset_name: str
    accuracy: float
    latency_ms: float
    memory_mb: float
    timestamp: float = field(default_factory=time.time)
    notes: str = ""

class ModelMarketplace:
    """
    Decentralized marketplace for AI models.
    Models are registered on-chain, stored on IPFS, and paid for with ATLAS.
    """

    def __init__(self):
        self.models: Dict[str, ModelCard] = {}
        self.evaluations: Dict[str, List[ModelEvaluation]] = {}
        self.revenue: Dict[str, Decimal] = {}  # model_id -> total earned

    def register_model(self, card: ModelCard) -> None:
        self.models[card.model_id] = card
        self.evaluations[card.model_id] = []
        self.revenue[card.model_id] = Decimal("0")

    def use_model(self, model_id: str, user: str) -> Optional[Decimal]:
        """Pay for and use a model. Returns price charged."""
        model = self.models.get(model_id)
        if not model:
            return None
        model.downloads += 1
        self.revenue[model_id] += model.price_per_use
        return model.price_per_use

    def add_evaluation(self, eval_obj: ModelEvaluation) -> None:
        if eval_obj.model_id not in self.evaluations:
            self.evaluations[eval_obj.model_id] = []
        self.evaluations[eval_obj.model_id].append(eval_obj)
        # Update model rating
        evals = self.evaluations[eval_obj.model_id]
        model = self.models.get(eval_obj.model_id)
        if model and evals:
            model.rating = sum(e.accuracy for e in evals) / len(evals)
            model.evaluations.append(eval_obj.eval_id)

    def search_models(self, model_type: str = None, min_rating: float = 0.0,
                      sort_by: str = "rating") -> List[ModelCard]:
        results = list(self.models.values())
        if model_type:
            results = [m for m in results if m.model_type == model_type]
        results = [m for m in results if m.rating >= min_rating]
        if sort_by == "rating":
            results.sort(key=lambda m: m.rating, reverse=True)
        elif sort_by == "downloads":
            results.sort(key=lambda m: m.downloads, reverse=True)
        return results

    def top_earners(self, k: int = 10) -> List[tuple]:
        return sorted(self.revenue.items(), key=lambda x: x[1], reverse=True)[:k]

    def stats(self) -> dict:
        return {
            "total_models": len(self.models),
            "total_downloads": sum(m.downloads for m in self.models.values()),
            "total_revenue": str(sum(self.revenue.values(), Decimal("0"))),
            "avg_rating": sum(m.rating for m in self.models.values()) / max(1, len(self.models)),
        }
