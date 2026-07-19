"""Phase 11 integration tests."""
import numpy as np
from decimal import Decimal
from src.learning_engine.federated import FederatedTrainer, ModelUpdate
from src.learning_engine.marketplace import ModelMarketplace, ModelCard, ModelEvaluation
from src.learning_engine.onchain_training import OnChainTrainer
from src.learning_engine.adaptive import AdaptivePolicyEngine
from src.learning_engine.data_valuation import DataValuator, ShapleyEstimator
from src.learning_engine.interpretability import ModelInterpreter

def test_federated_training():
    trainer = FederatedTrainer(model_dim=128, min_participants=3)
    # Submit updates from 3 nodes
    for i in range(3):
        update = ModelUpdate(
            node_id=f"node_{i}",
            gradients=np.random.randn(128).astype(np.float32) * 0.01,
            data_size=100 * (i + 1),
            loss=0.5 - i * 0.1,
        )
        trainer.submit_update(update)
    assert len(trainer.participant_stats) == 3
    # Aggregate
    updates = [
        ModelUpdate(node_id=f"node_{i}",
                    gradients=np.random.randn(128).astype(np.float32) * 0.01,
                    data_size=100 * (i + 1),
                    loss=0.4 - i * 0.05)
        for i in range(3)
    ]
    round_obj = trainer.aggregate(updates)
    assert round_obj.avg_loss > 0
    assert len(round_obj.participants) == 3
    # Contributions
    contribs = trainer.evaluate_contributions()
    assert len(contribs) == 3
    assert all(v >= 0 for v in contribs.values())
    stats = trainer.stats()
    assert stats["total_rounds"] == 1

def test_model_marketplace():
    mp = ModelMarketplace()
    card = ModelCard(
        model_id="model_1", name="ATLAS Value Classifier",
        creator="did:atlas:alice", description="Classifies value categories",
        model_type="classifier", input_dim=512, output_dim=12,
        weight_hash="abc123", price_per_use=Decimal("0.5"),
    )
    mp.register_model(card)
    # Use model
    price = mp.use_model("model_1", "did:atlas:bob")
    assert price == Decimal("0.5")
    assert card.downloads == 1
    # Add evaluation
    eval_obj = ModelEvaluation(
        eval_id="eval_1", model_id="model_1", evaluator="did:atlas:carol",
        dataset_name="test_set", accuracy=0.92, latency_ms=15.5, memory_mb=128,
    )
    mp.add_evaluation(eval_obj)
    assert card.rating == 0.92
    # Search
    results = mp.search_models(model_type="classifier", min_rating=0.9)
    assert len(results) == 1
    assert results[0].model_id == "model_1"
    stats = mp.stats()
    assert stats["total_models"] == 1

def test_onchain_training():
    trainer = OnChainTrainer()
    job = trainer.submit_job(
        requester="did:atlas:alice",
        model_type="classifier",
        dataset_cid="QmTest123",
        hyperparams={"epochs": 10, "lr": 0.01},
        compute_budget=Decimal("100"),
    )
    assert job.status == "pending"
    trainer.assign_nodes(job.job_id, ["node_1", "node_2"])
    assert job.status == "running"
    # Submit proof
    weights = np.random.randn(128).astype(np.float32)
    proof = trainer.submit_proof(job.job_id, "node_1", weights, epochs=10, final_loss=0.05)
    assert proof.verified is True
    assert proof.epochs_completed == 10
    assert trainer.verify_proof(proof) is True
    assert job.status == "completed"
    assert job.final_loss == 0.05

def test_adaptive_policy():
    engine = AdaptivePolicyEngine()
    # Record observations
    for i in range(10):
        engine.record_observation({"velocity": 1.5, "ehi": 75, "adoption_rate": 0.05})
    # Suggest minting rate
    adj = engine.suggest_minting_rate(1.0, {"velocity": 1.5, "ehi": 75, "adoption_rate": 0.05})
    assert adj.policy_name == "minting_rate"
    assert adj.confidence > 0
    # Suggest circuit breaker
    cb_adj = engine.suggest_circuit_breaker(0.1, {"anomaly_rate": 0.15, "recent_failures": 3})
    assert cb_adj.proposed_value < cb_adj.current_value  # Should tighten
    # Suggest quorum
    q_adj = engine.suggest_quorum(10, {"participation_rate": 0.2, "active_voters": 30})
    assert q_adj.proposed_value < q_adj.current_value  # Should reduce
    # Apply
    assert engine.apply_adjustment(adj.adjustment_id) is True
    assert adj.applied is True
    pending = engine.pending_adjustments()
    assert all(not a.applied for a in pending)

def test_data_valuation():
    valuator = DataValuator()
    # Simple eval function: sum of values in subset
    data_values = {0: 10, 1: 20, 2: 30, 3: 5, 4: 15}
    def eval_fn(subset):
        return sum(data_values.get(i, 0) for i in subset) / 100.0
    shapley = valuator.value_dataset("ds_1", list(data_values.keys()), eval_fn)
    assert len(shapley) == 5
    # Higher-value data should have higher Shapley
    top = valuator.top_contributors("ds_1", k=3)
    assert top[0][0] == 2  # data point with value 30
    total = valuator.total_value("ds_1")
    assert total > 0

def test_model_interpreter():
    interp = ModelInterpreter()
    weights = np.random.randn(20).astype(np.float32)
    features = np.random.randn(20).astype(np.float32)
    # Feature importance
    imp = interp.feature_importance(weights)
    assert len(imp) <= 10
    assert all(v >= 0 for v in imp.values())
    # Decision path
    path = interp.decision_path(features, weights)
    assert isinstance(path, list)
    # Counterfactual
    target = 1.0
    modified = interp.counterfactual(features, weights, target)
    assert len(modified) == len(features)
    # Bias check
    bias = interp.bias_check(weights, [0, 1, 2])
    assert "biased" in bias
    assert "recommendation" in bias

if __name__ == "__main__":
    test_federated_training()
    test_model_marketplace()
    test_onchain_training()
    test_adaptive_policy()
    test_data_valuation()
    test_model_interpreter()
    print("✅ All Phase 11 tests passed")
