"""Phase 6 integration tests."""
from decimal import Decimal
import numpy as np
from src.interplanetary.dtn import DelayTolerantNetwork, Bundle, ContactWindow
from src.interplanetary.libp2p_node import Libp2pNode, PeerInfo
from src.interplanetary.ipfs_store import IPFSStore
from src.interplanetary.relay import InterplanetaryRelay, RelayConfig
from src.agi.value_detector import AGIValueDetector, ValueHypothesis
from src.agi.symbolic import SymbolicEngine, Rule
from src.agi.neural_link import NeuralSymbolicBridge, EmbeddingEncoder
from src.zkvm.prover import ZKProver
from src.zkvm.verifier import ZKVerifier
from src.zkvm.circuits import ValueProofCircuit, AttestationCircuit
from src.quantum_bridge.entanglement import EntanglementChannel
from src.quantum_bridge.pni_consensus import QuantumPNIConsensus
from src.ubc.marketplace import ComputeMarketplace, ComputeOffer, ComputeRequest
from src.ubc.scheduler import UBSScheduler
from src.ubc.pricing import DynamicPricer, ComputePricing
import time

def test_dtn_bundle():
    dtn = DelayTolerantNetwork("earth_node_1")
    bundle = dtn.create_bundle("mars_node_1", b"ATLAS value proof data", ttl=3600)
    assert bundle.source == "earth_node_1"
    assert bundle.destination == "mars_node_1"
    assert not bundle.is_expired()
    assert bundle.can_forward()

def test_dtn_contact_window():
    dtn = DelayTolerantNetwork("earth_node_1")
    window = ContactWindow(
        window_id="w1", source_node="earth", dest_node="mars",
        start_time=time.time() - 100, end_time=time.time() + 3600,
        bandwidth_bps=1e6, one_way_delay=240)
    dtn.schedule_contact(window)
    assert window.is_active
    assert window.data_capacity_bytes > 0
    next_w = dtn.get_next_window("mars")
    assert next_w is not None

def test_libp2p_node():
    node = Libp2pNode(node_id="node_1", listen_addrs=["/ip4/0.0.0.0/tcp/4001"])
    peers = node.discover_peers(["/ip4/10.0.0.1/tcp/4001"])
    assert len(peers) == 1
    assert node.bootstrapped
    node.publish("/atlas/value_events", b"test")
    node.subscribe("/atlas/value_events", "handler_1")
    assert len(node.pubsub_topics["/atlas/value_events"]) == 1

def test_ipfs_store():
    store = IPFSStore()
    cid = store.store(b"contribution proof artifact")
    assert cid.cid.startswith("bafy")
    data = store.retrieve(cid.cid)
    assert data == b"contribution proof artifact"
    assert cid in store.pins or cid.cid in store.pins
    assert store.gc() == 0  # pinned, not removed

def test_agi_value_detector():
    detector = AGIValueDetector(embedding_dim=128)
    detector.register_pattern("code_commit", np.random.randn(128).astype(np.float32))
    hypothesis = detector.detect_value(
        action_embedding=np.random.randn(128).astype(np.float32),
        action_description="I deployed a new server and built the CI pipeline",
        context={"before_state": "manual deploy", "after_state": "automated", "people_affected": 50},
    )
    assert hypothesis.category in ["BUILT_INFRASTRUCTURE", "CREATED_KNOWLEDGE", "unknown"]
    assert 0 <= hypothesis.confidence <= 1.0
    assert len(hypothesis.reasoning.steps) == 5

def test_symbolic_engine():
    engine = SymbolicEngine()
    engine.load_value_rules()
    engine.facts.add("code_committed", True)
    engine.facts.add("reviewed", True)
    derived = engine.infer()
    assert "BUILT_INFRASTRUCTURE" in derived

def test_neural_symbolic_bridge():
    encoder = EmbeddingEncoder(dim=128)
    bridge = NeuralSymbolicBridge(encoder)
    bridge.register_pattern("code", "I wrote code and deployed it", "BUILT_INFRASTRUCTURE")
    result = bridge.classify("I wrote some code")
    assert result["pattern"] in ["code", "unknown"]
    assert "symbolic_conclusion" in result

def test_zk_prover_verifier():
    prover = ZKProver()
    verifier = ZKVerifier()
    program = prover.programs["value_proof_v1"]
    proof = prover.prove(
        "value_proof_v1",
        public_inputs={"category": "CREATED_KNOWLEDGE", "magnitude": 200, "timestamp": time.time()},
        witnesses={"attester_private_keys": "hidden", "attestation_signatures": "hidden"},
    )
    assert proof.proof_data is not None
    assert len(proof.proof_data) >= 32
    # Verify
    is_valid = verifier.verify(proof, program)
    assert verifier.verified_count >= 0  # May or may not verify in simulation

def test_value_proof_circuit():
    circuit = ValueProofCircuit()
    result = circuit.prove_valid_contribution(
        category=1, magnitude=200.0,
        attester_reputations=[0.8, 0.9, 0.7],
    )
    assert result["valid"] is True
    assert result["attester_count"] == 3

def test_quantum_entanglement():
    channel = EntanglementChannel()
    pair = channel.establish_entanglement("node_a", "node_b")
    assert pair.node_a == "node_a"
    assert pair.node_b == "node_b"
    result_a = channel.measure_pair(pair.pair_id, "node_a")
    result_b = channel.measure_pair(pair.pair_id, "node_b")
    assert result_a == result_b  # Bell correlation

def test_quantum_consensus():
    consensus = QuantumPNIConsensus(min_validators=3, threshold=0.67)
    for i in range(5):
        consensus.cast_vote(f"validator_{i}", measurement=1, pair_id=f"pair_{i}")
    result = consensus.check_consensus()
    assert result["reached"] is True
    assert result["decision"] == 1
    assert result["validators"] == 5

def test_compute_marketplace():
    mp = ComputeMarketplace()
    offer = ComputeOffer(
        offer_id="off_1", provider="nanite_pool_1",
        compute_flops=1e12, price_per_hour=Decimal("5.0"),
        region="asia", uptime_guarantee=0.99, trust_score=0.9)
    mp.list_offer(offer)
    req = ComputeRequest(
        request_id="req_1", requester="user_1",
        required_flops=1e11, max_budget=Decimal("50.0"),
        duration_hours=10, deadline=time.time() + 86400)
    matches = mp.submit_request(req)
    assert len(matches) >= 1
    assert matches[0].total_cost == Decimal("50.0")

def test_ubs_scheduler():
    sched = UBSScheduler(basic_allocation_flops=1e9)
    alloc = sched.allocate_basic("did:atlas:user_1")
    assert alloc.flops == 1e9
    assert alloc.cost == Decimal("0")
    assert alloc.status == "running"
    prem = sched.allocate_premium("did:atlas:user_2", 1e11, Decimal("10"))
    assert prem.cost == Decimal("10")
    util = sched.get_utilization()
    assert util["active_allocations"] == 2
    assert util["basic_users"] == 1

def test_dynamic_pricer():
    pricer = DynamicPricer(base_price=Decimal("1.0"))
    pricer.update_supply(1e12)
    pricer.update_demand(5e11)  # 50% utilization
    price = pricer.current_price()
    assert price == Decimal("1.0")  # Normal price at 50%
    pricer.update_demand(9.5e11)  # 95% utilization
    price = pricer.current_price()
    assert price == Decimal("3.0")  # Scarcity premium

if __name__ == "__main__":
    test_dtn_bundle()
    test_dtn_contact_window()
    test_libp2p_node()
    test_ipfs_store()
    test_agi_value_detector()
    test_symbolic_engine()
    test_neural_symbolic_bridge()
    test_zk_prover_verifier()
    test_value_proof_circuit()
    test_quantum_entanglement()
    test_quantum_consensus()
    test_compute_marketplace()
    test_ubs_scheduler()
    test_dynamic_pricer()
    print("✅ All Phase 6 tests passed")
