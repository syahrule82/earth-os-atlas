"""Phase 9 integration tests."""
from decimal import Decimal
from src.neural_economy.ava import AutonomousValueAgent, AVARegistry
from src.neural_economy.dynamic_supply import DynamicSupplyEngine, VelocityAdjuster
from src.neural_economy.health_index import EconomicHealthIndex
from src.neural_economy.value_flow import ValueFlowGraph
from src.genesis.genesis import GenesisProtocol, ColdStartSolver
from src.genesis.adoption import AdoptionCurve, NetworkEffectModel
from src.cross_domain.gateway import DomainGateway
from src.cross_domain.weather import WeatherBridge
from src.cross_domain.supply_chain import SupplyChainBridge
from src.cross_domain.healthcare import HealthcareBridge
from src.disaster_relief import DisasterReliefProtocol
from src.reputation_graph import ReputationGraph
import time

def test_ava_registry():
    registry = AVARegistry()
    agent = AutonomousValueAgent(
        agent_id="ava_1", name="DocuBot",
        specialization=["CREATED_KNOWLEDGE", "SOLVED_PROBLEM"],
        owner="did:atlas:alice")
    registry.register(agent)
    
    context = {"unindexed_content": True, "bug_reported": True}
    actions = registry.run_cycle(context)
    assert len(actions) >= 1
    assert actions[0].category in ["CREATED_KNOWLEDGE", "SOLVED_PROBLEM"]
    stats = registry.get_stats()
    assert stats["active_agents"] == 1

def test_dynamic_supply():
    engine = DynamicSupplyEngine()
    # Mint some ATLAS
    minted = engine.mint(Decimal("1000"), confidence=0.9)
    assert minted > 0
    assert engine.total_minted > 0
    
    # Burn some
    burned = engine.burn(Decimal("100"), "transaction_fee", "did:atlas:user")
    assert burned.amount == Decimal("100")
    assert engine.total_burned == Decimal("100")
    assert engine.circulating_supply == engine.total_minted - Decimal("100")
    
    # Velocity adjustment
    adj = engine.update_velocity(Decimal("5000"))
    assert isinstance(adj, float)
    stats = engine.stats()
    assert "burn_rate" in stats

def test_economic_health_index():
    ehi = EconomicHealthIndex()
    score = ehi.calculate({
        "gini": 0.4,
        "velocity": 4.0,
        "participation_rate": 0.6,
        "innovation_index": 0.7,
        "network_growth": 5.0,
    })
    assert 0 <= score <= 100

def test_value_flow_graph():
    graph = ValueFlowGraph()
    graph.add_flow("alice", "bob", Decimal("100"), "CREATED_KNOWLEDGE")
    graph.add_flow("bob", "charlie", Decimal("50"), "SOLVED_PROBLEM")
    graph.add_flow("alice", "charlie", Decimal("30"), "BUILT_INFRASTRUCTURE")
    
    creators = graph.top_creators()
    assert len(creators) > 0
    assert creators[0].total_outflow >= Decimal("100")
    
    by_cat = graph.flow_by_category()
    assert "CREATED_KNOWLEDGE" in by_cat
    assert by_cat["CREATED_KNOWLEDGE"] == Decimal("100")

def test_genesis_protocol():
    protocol = GenesisProtocol()
    contributors = [
        {"did": "did:atlas:founder1", "vesting": 365},
        {"did": "did:atlas:founder2", "vesting": 365},
        {"did": "did:atlas:founder3", "vesting": 730},
    ]
    allocations = protocol.generate_genesis(contributors)
    assert len(allocations) > 3  # Contributors + treasury + liquidity + community + validators + team
    total = protocol.total_allocated()
    assert total > 0
    summary = protocol.summary()
    assert "treasury" in summary["by_category"]

def test_cold_start_solver():
    solver = ColdStartSolver()
    bonus_1 = solver.calculate_bonus(1)  # First contributor
    bonus_500 = solver.calculate_bonus(500)
    bonus_2000 = solver.calculate_bonus(2000)
    assert bonus_1 > bonus_500 > bonus_2000
    assert bonus_2000 == 1.0  # No bonus after critical mass
    
    plan = solver.bootstrap_plan()
    assert len(plan) == 5
    assert plan[0]["name"] == "Genesis"

def test_adoption_curve():
    curve = AdoptionCurve(market_potential=10000)
    results = curve.simulate(periods=100)
    assert len(results) == 100
    assert results[-1]["total_adopted"] > results[0]["total_adopted"]
    assert results[-1]["penetration"] > 0

def test_network_effects():
    model = NetworkEffectModel()
    v100 = model.network_value(100)
    v1000 = model.network_value(1000)
    assert v1000 > v100 * 50  # Nonlinear growth
    marginal = model.marginal_benefit(100, 1)
    assert marginal > 0

def test_domain_gateway():
    gateway = DomainGateway()
    gateway.register_bridge("weather", WeatherBridge())
    gateway.register_bridge("healthcare", HealthcareBridge())
    
    # Route weather event
    weather_event = gateway.route("weather", {
        "type": "drought", "region": "africa", "severity": 0.8,
    })
    assert weather_event.domain == "weather"
    
    # Route healthcare event
    health_event = gateway.route("healthcare", {
        "patient_count": 50, "treatment_type": "vaccination",
        "recovery_rate": 0.95, "region": "asia", "severity": 3,
    })
    assert health_event.domain == "healthcare"
    
    stats = gateway.stats()
    assert stats["total_events"] == 2

def test_disaster_relief():
    protocol = DisasterReliefProtocol()
    disaster = protocol.declare_disaster("earthquake", "pacific", 0.9, 50000)
    assert disaster.status == "active"
    
    allocations = protocol.allocate_resources(disaster.event_id, [
        {"type": "food", "amount": 10000, "source": "warehouse_a"},
        {"type": "medical", "amount": 5000, "source": "hospital_b"},
    ])
    assert len(allocations) == 2
    
    emergency = protocol.emergency_mint(disaster.event_id, Decimal("1000"))
    assert emergency == Decimal("3000")  # 3x multiplier
    
    protocol.resolve_disaster(disaster.event_id)
    assert len(protocol.active_disasters()) == 0

def test_reputation_graph():
    graph = ReputationGraph()
    # Build a simple network: alice attests to bob, bob attests to charlie
    graph.add_attestation("alice", "bob", positive=True)
    graph.add_attestation("bob", "charlie", positive=True)
    graph.add_attestation("alice", "charlie", positive=True)
    
    scores = graph.compute_pagerank()
    assert len(scores) == 3
    # All should have positive reputation
    assert all(s > 0 for s in scores.values())
    
    top = graph.top_reputable(3)
    assert len(top) == 3
    # Charlie should have high reputation (most attestations received)
    charlie_rep = graph.get_reputation("charlie")
    assert charlie_rep > 0

if __name__ == "__main__":
    test_ava_registry()
    test_dynamic_supply()
    test_economic_health_index()
    test_value_flow_graph()
    test_genesis_protocol()
    test_cold_start_solver()
    test_adoption_curve()
    test_network_effects()
    test_domain_gateway()
    test_disaster_relief()
    test_reputation_graph()
    print("✅ All Phase 9 tests passed")
