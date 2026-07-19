"""Phase 17 integration tests."""
from decimal import Decimal
from src.security.formal_verify import FormalVerifier, InvariantCheck, PropertySpec
from src.security.fuzzer import FuzzingFramework, FuzzTarget, CorpusManager
from src.security.audit import SmartContractAuditor, VulnerabilitySeverity, SWC_ID
from src.security.pentest import PenetrationTester, AttackType
from src.security.threat_intel import ThreatIntelligence, ThreatLevel, AttackPattern

def test_formal_verifier():
    verifier = FormalVerifier()
    assert len(verifier.invariants) >= 8
    assert len(verifier.properties) >= 5
    # Verify healthy state
    healthy = {
        "total_supply": "500000000",
        "total_minted": "500000000",
        "total_burned": "1000000",
        "balances": {"alice": "100", "bob": "50"},
        "validator_stakes": {"val1": "10000"},
        "last_mint_verified": True,
        "last_slash_proven": True,
        "quorum_met": True,
        "constitutional": True,
    }
    result = verifier.verify_all(healthy)
    assert result["all_passed"] is True
    assert result["failed"] == 0
    # Verify unhealthy state (supply exceeds limit)
    unhealthy = dict(healthy)
    unhealthy["total_supply"] = "2000000000"  # 2B > 1B limit
    result2 = verifier.verify_all(unhealthy)
    assert result2["all_passed"] is False
    assert "inv_supply_limit" in result2["violations"]
    # State transition
    transition = verifier.verify_state_transition(healthy, unhealthy, "excessive_mint")
    assert transition["transition_valid"] is False
    # Properties
    assert verifier.verify_property("prop_1", {"supply_increasing": True})
    stats = verifier.stats()
    assert stats["total_invariants"] >= 8

def test_fuzzing_framework():
    fuzzer = FuzzingFramework()
    target = FuzzTarget(
        target_id="api_proof_create",
        name="Proof Create API",
        endpoint="/v1/proof/create",
        method="POST",
        input_schema={"creator_id": "string", "category": "string", "hours": "float"},
        max_iterations=100,
    )
    fuzzer.register_target(target)
    # Run fuzzing
    result = fuzzer.fuzz("api_proof_create", iterations=100)
    assert result.iterations <= 100
    assert result.coverage_percent >= 0
    assert result.execution_time_s >= 0
    # Corpus should have grown
    assert result.corpus_size > 0
    stats = fuzzer.stats()
    assert stats["total_targets"] == 1

def test_corpus_manager():
    corpus = CorpusManager(max_size=5)
    # Add items
    for i in range(10):
        added = corpus.add({"input": f"test_{i}"}, f"hash_{i}")
        if i < 5:
            assert added is True  # New coverage
        # After 5, oldest gets removed
    assert corpus.size() <= 5
    # Sample
    sample = corpus.sample()
    assert sample is not None
    # Duplicate coverage hash not added
    added = corpus.add({"input": "dup"}, "hash_0")
    assert added is False

def test_smart_contract_auditor():
    auditor = SmartContractAuditor()
    # Audit a contract with tx.origin vulnerability
    vulnerable_code = '''
pragma solidity ^0.8.20;

contract Vulnerable {
    address owner;
    constructor() { owner = msg.sender; }
    
    function withdraw() public {
        require(tx.origin == owner, "Not authorized");
        payable(msg.sender).transfer(address(this).balance);
    }
    
    function externalCall(address target) public {
        target.call(abi.encodeWithSignature("execute()"));
    }
}
'''
    report = auditor.audit("Vulnerable", vulnerable_code)
    assert len(report.vulnerabilities) >= 1
    # Should detect tx.origin
    tx_origin_vuln = [v for v in report.vulnerabilities if v.swc_id == SWC_ID.TX_ORIGIN]
    assert len(tx_origin_vuln) >= 1
    assert tx_origin_vuln[0].severity == VulnerabilitySeverity.HIGH
    # Should have gas optimizations
    assert len(report.gas_optimizations) > 0
    # Score should be less than 100
    assert report.overall_score < 100
    # Audit a clean contract
    clean_code = '''
pragma solidity ^0.8.20;

contract Clean {
    address public immutable owner;
    constructor() { owner = msg.sender; }
    modifier onlyOwner() { require(msg.sender == owner, "Not authorized"); _; }
    function withdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}
'''
    clean_report = auditor.audit("Clean", clean_code)
    assert clean_report.overall_score > report.overall_score
    stats = auditor.stats()
    assert stats["total_audits"] == 2

def test_penetration_tester():
    pentest = PenetrationTester()
    endpoints = ["/v1/proof/create", "/v1/ledger/mint", "/v1/dao/vote"]
    # Run single attack
    sim = pentest.run_attack(AttackType.SQL_INJECTION, "/v1/proof/create")
    assert sim.attack_type == AttackType.SQL_INJECTION
    assert sim.result in ["blocked", "vulnerable"]
    # Run full scan
    scan_result = pentest.run_full_scan(endpoints)
    assert scan_result["total_attacks"] > 0
    assert scan_result["block_rate"] >= 0  # Some attacks may succeed
    # Stats
    stats = pentest.stats()
    assert stats["total_simulations"] > 0
    assert stats["blocked"] + stats["vulnerable"] == stats["total_simulations"]

def test_threat_intelligence():
    ti = ThreatIntelligence()
    # Report threat
    threat = ti.report_threat("internal", "ip", "192.168.1.100",
                              ThreatLevel.HIGH, "Suspicious API access pattern",
                              tags=["brute_force"])
    assert threat.level == ThreatLevel.HIGH
    assert threat.occurrences == 1
    # Report again (should increment)
    threat2 = ti.report_threat("internal", "ip", "192.168.1.100",
                               ThreatLevel.MEDIUM, "Repeated attempt")
    assert threat2.occurrences == 2
    # Check reputation
    rep = ti.check_ip("192.168.1.100")
    assert rep < 1.0  # Reputation reduced
    # Should be blocked
    assert ti.is_blocked("192.168.1.100") is True
    # Clean IP
    assert ti.check_ip("8.8.8.8") == 1.0
    assert ti.is_blocked("8.8.8.8") is False
    # Create incident
    incident = ti.create_incident("ddos_attack", ThreatLevel.CRITICAL,
                                  ["api_gateway", "validator_network"])
    assert incident.status == "detected"
    assert len(incident.actions_taken) >= 1  # Playbook activated
    assert len(incident.timeline) >= 1
    # Update incident
    assert ti.update_incident(incident.incident_id, "investigating", "Analyzing traffic patterns")
    assert incident.status == "investigating"
    assert len(incident.actions_taken) >= 2
    # Resolve
    assert ti.update_incident(incident.incident_id, "resolved", "Blocked malicious IPs")
    assert incident.resolved_at is not None
    # Active incidents
    active = ti.active_incidents()
    assert len(active) == 0  # All resolved
    # Playbooks
    assert len(ti.playbooks) >= 5
    stats = ti.stats()
    assert stats["total_threats"] >= 1

def test_attack_patterns():
    """Test MITRE ATT&CK pattern coverage."""
    patterns = list(AttackPattern)
    assert len(patterns) >= 10
    # Each should have a valid MITRE ID
    for p in patterns:
        assert p.value.startswith("T")

if __name__ == "__main__":
    test_formal_verifier()
    test_fuzzing_framework()
    test_corpus_manager()
    test_smart_contract_auditor()
    test_penetration_tester()
    test_threat_intelligence()
    test_attack_patterns()
    print("✅ All Phase 17 tests passed")
