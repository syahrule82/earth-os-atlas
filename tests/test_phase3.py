# Phase 3 Integration Tests

import asyncio
from decimal import Decimal
from src.economy.bonding import LinearCurve, ExponentialCurve
from src.economy.amm import ATLASPool, SwapRouter
from src.economy.pricing import TWAPOracle
from src.economy.treasury import Treasury, AllocationStrategy
from src.governance.dao import GovernanceDAO, QuorumStrategy
from src.governance.reputation import ReputationSystem, ContributionType
from src.governance.identity import DIDAtlas, ZKProver
from src.sdk.python_sdk import AtlasClient, ContributionProof
from src.bridges import EthereumBridge, BridgeConfig
from src.pni_bridge import OpenBCIAdapter, EEGReading
from src.simulation import EconomicSimulator
import time

def test_bonding_curves():
    linear = LinearCurve(Decimal("1.0"), Decimal("0.01"))
    price = linear.price(Decimal("100000"))
    assert price == Decimal("1001.0")
    cost, new_price = linear.buy_price(Decimal("100000"), Decimal("1000"))
    assert cost > 0
    assert new_price > price

def test_amm_pool():
    pool = ATLASPool("pool_1", "ATLAS", "USDC", Decimal("1000000"), Decimal("1000000"))
    price = pool.get_price("ATLAS")
    assert abs(price - Decimal("1.0")) < Decimal("0.01")
    out = pool.swap("ATLAS", Decimal("1000"))
    assert out > 0
    assert pool.reserve_a > Decimal("1000000")

def test_twap_oracle():
    oracle = TWAPOracle(window_seconds=60)
    oracle.update("ATLAS/USDC", Decimal("1.0"))
    oracle.update("ATLAS/USDC", Decimal("1.1"))
    twap = oracle.get_twap("ATLAS/USDC")
    assert Decimal("1.0") < twap < Decimal("1.1")

def test_treasury_quadratic():
    treasury = Treasury()
    treasury.deposit(Decimal("10000"))
    prop = treasury.create_proposal("fund_dev", "Fund developers", 
                                    Decimal("1000"), ["alice", "bob"], 
                                    AllocationStrategy.QUADRATIC)
    treasury.vote("fund_dev", "voter1", Decimal("100"), True)
    treasury.vote("fund_dev", "voter2", Decimal("100"), True)
    treasury.vote("fund_dev", "voter3", Decimal("100"), False)
    executed = treasury.execute("fund_dev")
    assert executed

def test_governance_dao():
    dao = GovernanceDAO()
    dao.grant_voice("alice", 100)
    dao.grant_voice("bob", 100)
    prop = dao.create_proposal("upgrade", "Upgrade protocol", "alice", "protocol")
    dao.vote("upgrade", "alice", 50, True)
    dao.vote("upgrade", "bob", 30, True)
    passed = dao.finalize("upgrade")
    assert passed

def test_reputation():
    rep = ReputationSystem()
    rep.add_record(ContributionRecord(
        record_id="rec_1", contributor="alice", 
        type=ContributionType.CODE, magnitude=100.0,
        proof_cid="Qm123", timestamp=time.time(), validators=["bob"]
    ))
    score = rep.get_reputation("alice")
    assert score > 0

def test_zk_prover():
    prover = ZKProver()
    proof = prover.prove_contribution({"category": "CODE", "magnitude": 100}, "private_key")
    assert proof["verified"] is True
    assert prover.verify_proof(proof)

def test_atlas_client():
    client = AtlasClient()
    proof = client.create_proof("did:atlas:alice", "CREATED_KNOWLEDGE", "medium", 8.0)
    assert proof.base_value > 0
    assert proof.can_mint is False

def test_ethereum_bridge():
    config = BridgeConfig("ethereum", "http://localhost:8545", "0xBridge", "ETH")
    bridge = EthereumBridge(config)
    transfer = bridge.lock_and_mint("0xAlice", "did:atlas:alice", Decimal("1.0"))
    assert transfer.status == "pending"

def test_openbci_adapter():
    async def _test():
        adapter = OpenBCIAdapter()
        await adapter.connect()
        reading = await adapter.stream()
        assert isinstance(reading, EEGReading)
        assert len(reading.channels) == 8
        await adapter.disconnect()
    asyncio.run(_test())

def test_economic_simulator():
    sim = EconomicSimulator(n_agents=100)
    result = sim.run(steps=10)
    assert result.total_atlas_minted > 0
    assert 0 <= result.gini_coefficient <= 1

# Performance benchmark
print("Running economic stress test...")
sim = EconomicSimulator(n_agents=1000)
result = sim.stress_test("supply_shock")
print(f"Gini after shock: {result.gini_coefficient:.3f}")
print(f"Supply after shock: {result.total_atlas_minted}")
