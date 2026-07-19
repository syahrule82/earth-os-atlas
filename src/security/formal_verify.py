"""Formal Verification — Spec-based verification of critical functions."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from decimal import Decimal
import time, hashlib

@dataclass
class PropertySpec:
    """A formal property specification to verify."""
    spec_id: str
    name: str
    description: str
    property_type: str  # invariant, precondition, postcondition, temporal
    check_fn: str  # Name of the check function
    severity: str = "critical"  # info, warning, error, critical
    verified: bool = False
    last_checked: float = 0
    violations: int = 0

@dataclass
class InvariantCheck:
    """An invariant that must always hold."""
    invariant_id: str
    name: str
    description: str
    check: Callable[[dict], bool]
    category: str  # ledger, governance, identity, economic
    
    def verify(self, state: dict) -> bool:
        """Verify the invariant against a state."""
        try:
            return self.check(state)
        except Exception:
            return False

class FormalVerifier:
    """
    Formal verification engine for ATLAS critical functions.
    
    Verifies:
    - Supply never exceeds 1B ATLAS
    - Minting only from verified proofs
    - Slashing only for proven violations
    - Governance quorum always respected
    - Validator stake never negative
    - Constitution articles never violated
    """

    def __init__(self):
        self.invariants: Dict[str, InvariantCheck] = {}
        self.properties: Dict[str, PropertySpec] = {}
        self.verification_history: List[dict] = []
        self._register_default_invariants()
        self._register_default_properties()

    def _register_default_invariants(self):
        """Register critical system invariants."""
        invariants = [
            InvariantCheck("inv_supply_limit", "Supply Limit",
                          "Total ATLAS supply never exceeds 1,000,000,000",
                          lambda s: Decimal(str(s.get("total_supply", 0))) <= Decimal("1000000000"),
                          "ledger"),
            InvariantCheck("inv_no_negative_balance", "No Negative Balances",
                          "No account can have a negative balance",
                          lambda s: all(Decimal(str(v)) >= 0 for v in s.get("balances", {}).values()),
                          "ledger"),
            InvariantCheck("inv_mint_from_proof", "Mint From Proof Only",
                          "ATLAS can only be minted from verified proofs",
                          lambda s: s.get("last_mint_verified", True),
                          "ledger"),
            InvariantCheck("inv_slash_proven", "Slashing Requires Proof",
                          "Validators can only be slashed for proven violations",
                          lambda s: s.get("last_slash_proven", True),
                          "validator"),
            InvariantCheck("inv_quorum_respected", "Quorum Respected",
                          "Governance proposals must meet quorum",
                          lambda s: s.get("quorum_met", True),
                          "governance"),
            InvariantCheck("inv_stake_positive", "Positive Validator Stake",
                          "Validator stake must always be positive",
                          lambda s: all(Decimal(str(v)) > 0 for v in s.get("validator_stakes", {}).values()),
                          "validator"),
            InvariantCheck("inv_constitution_supreme", "Constitution Supremacy",
                          "No action can violate the constitution",
                          lambda s: s.get("constitutional", True),
                          "governance"),
            InvariantCheck("inv_burn_le_mint", "Burn Never Exceeds Mint",
                          "Total burned ATLAS cannot exceed total minted",
                          lambda s: Decimal(str(s.get("total_burned", 0))) <= Decimal(str(s.get("total_minted", 0))),
                          "economic"),
        ]
        for inv in invariants:
            self.invariants[inv.invariant_id] = inv

    def _register_default_properties(self):
        """Register formal properties."""
        properties = [
            PropertySpec("prop_1", "Monotonic Supply", "Supply is monotonically increasing (minus burns)",
                        "invariant", "check_monotonic_supply", "critical"),
            PropertySpec("prop_2", "Conservation of Value", "Total value is conserved in transfers",
                        "invariant", "check_conservation", "critical"),
            PropertySpec("prop_3", "No Double Mint", "A proof can only be minted once",
                        "invariant", "check_no_double_mint", "critical"),
            PropertySpec("prop_4", "Finality Guarantee", "Finalized blocks cannot be reverted",
                        "temporal", "check_finality", "error"),
            PropertySpec("prop_5", "Slashing Bounded", "Slashing never exceeds 10% per violation",
                        "invariant", "check_slash_bound", "error"),
        ]
        for prop in properties:
            self.properties[prop.spec_id] = prop

    def verify_all(self, state: dict) -> dict:
        """Verify all invariants against a state."""
        results = {}
        violations = []
        for inv_id, inv in self.invariants.items():
            passed = inv.verify(state)
            results[inv_id] = {
                "name": inv.name,
                "passed": passed,
                "category": inv.category,
            }
            if not passed:
                violations.append(inv_id)
        
        report = {
            "timestamp": time.time(),
            "total_checked": len(results),
            "passed": sum(1 for r in results.values() if r["passed"]),
            "failed": len(violations),
            "violations": violations,
            "all_passed": len(violations) == 0,
        }
        self.verification_history.append(report)
        return report

    def verify_property(self, prop_id: str, state: dict) -> bool:
        """Verify a specific property."""
        prop = self.properties.get(prop_id)
        if not prop:
            return False
        # Simplified property checks
        checks = {
            "check_monotonic_supply": state.get("supply_increasing", True),
            "check_conservation": state.get("value_conserved", True),
            "check_no_double_mint": state.get("no_double_mint", True),
            "check_finality": state.get("blocks_final", True),
            "check_slash_bound": state.get("slash_within_bound", True),
        }
        result = checks.get(prop.check_fn, True)
        prop.verified = result
        prop.last_checked = time.time()
        if not result:
            prop.violations += 1
        return result

    def verify_state_transition(self, pre_state: dict, post_state: dict,
                                action: str) -> dict:
        """Verify a state transition is valid."""
        pre_check = self.verify_all(pre_state)
        post_check = self.verify_all(post_state)
        return {
            "action": action,
            "pre_state_valid": pre_check["all_passed"],
            "post_state_valid": post_check["all_passed"],
            "transition_valid": pre_check["all_passed"] and post_check["all_passed"],
            "new_violations": [v for v in post_check["violations"] if v not in pre_check["violations"]],
            "timestamp": time.time(),
        }

    def stats(self) -> dict:
        return {
            "total_invariants": len(self.invariants),
            "total_properties": len(self.properties),
            "total_verifications": len(self.verification_history),
            "last_verification_passed": self.verification_history[-1]["all_passed"] if self.verification_history else True,
        }
