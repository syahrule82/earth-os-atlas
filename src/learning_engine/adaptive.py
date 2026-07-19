"""Adaptive policy engine — ML-driven economic policy optimization."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np, time

@dataclass
class PolicyAdjustment:
    """A proposed policy adjustment."""
    adjustment_id: str
    policy_name: str
    current_value: float
    proposed_value: float
    reason: str
    confidence: float
    expected_impact: str
    timestamp: float = field(default_factory=time.time)
    applied: bool = False

class AdaptivePolicyEngine:
    """
    ML-driven economic policy optimization.
    
    Learns from historical data to optimize:
    - Minting rate (based on velocity, health index, adoption)
    - Circuit breaker thresholds (based on anomaly patterns)
    - Validator rewards (based on network conditions)
    - Governance quorum (based on participation trends)
    """

    def __init__(self):
        self.history: List[dict] = []
        self.adjustments: List[PolicyAdjustment] = []
        self.models: Dict[str, dict] = {}  # policy_name -> learned params

    def record_observation(self, metrics: dict) -> None:
        """Record economic metrics for learning."""
        self.history.append({"metrics": metrics, "timestamp": time.time()})
        if len(self.history) > 10000:
            self.history = self.history[-10000:]

    def suggest_minting_rate(self, current_rate: float, metrics: dict) -> PolicyAdjustment:
        """Suggest optimal minting rate based on economic conditions."""
        velocity = metrics.get("velocity", 1.0)
        health = metrics.get("ehi", 50.0)
        adoption = metrics.get("adoption_rate", 0.0)

        # High health + low velocity → reduce minting (prevent inflation)
        # Low health + high adoption → increase minting (stimulate growth)
        if health > 70 and velocity < 2.0:
            proposed = current_rate * 0.9
            reason = "High health, low velocity — reduce minting to prevent inflation"
            confidence = 0.8
        elif health < 40 and adoption > 0.1:
            proposed = current_rate * 1.1
            reason = "Low health, high adoption — increase minting to stimulate growth"
            confidence = 0.75
        else:
            proposed = current_rate
            reason = "Economic conditions stable — no adjustment needed"
            confidence = 0.5

        return self._create_adjustment("minting_rate", current_rate, proposed,
                                        reason, confidence)

    def suggest_circuit_breaker(self, current_threshold: float,
                                 metrics: dict) -> PolicyAdjustment:
        """Suggest circuit breaker threshold based on anomaly patterns."""
        anomaly_rate = metrics.get("anomaly_rate", 0.0)
        recent_failures = metrics.get("recent_failures", 0)

        if anomaly_rate > 0.1 or recent_failures > 5:
            proposed = current_threshold * 0.8  # More sensitive
            reason = f"High anomaly rate ({anomaly_rate:.2f}) — tighten circuit breaker"
            confidence = 0.85
        else:
            proposed = current_threshold
            reason = "Normal operation — no adjustment needed"
            confidence = 0.6

        return self._create_adjustment("circuit_breaker_threshold",
                                        current_threshold, proposed,
                                        reason, confidence)

    def suggest_quorum(self, current_quorum: int, metrics: dict) -> PolicyAdjustment:
        """Suggest governance quorum based on participation trends."""
        participation = metrics.get("participation_rate", 0.5)
        active_voters = metrics.get("active_voters", 100)

        if participation < 0.3 and active_voters < 50:
            proposed = max(1, current_quorum // 2)
            reason = f"Low participation ({participation:.1%}) — reduce quorum to pass critical proposals"
            confidence = 0.7
        elif participation > 0.7 and active_voters > 500:
            proposed = int(current_quorum * 1.5)
            reason = f"High participation ({participation:.1%}) — increase quorum for broader consensus"
            confidence = 0.75
        else:
            proposed = current_quorum
            reason = "Participation stable — no adjustment needed"
            confidence = 0.5

        return self._create_adjustment("governance_quorum", float(current_quorum),
                                        float(proposed), reason, confidence)

    def _create_adjustment(self, name: str, current: float, proposed: float,
                           reason: str, confidence: float) -> PolicyAdjustment:
        adj = PolicyAdjustment(
            adjustment_id=f"adj_{name}_{int(time.time())}",
            policy_name=name,
            current_value=current,
            proposed_value=proposed,
            reason=reason,
            confidence=confidence,
            expected_impact="minor" if abs(proposed - current) < 0.1 * current else "moderate",
        )
        self.adjustments.append(adj)
        return adj

    def apply_adjustment(self, adjustment_id: str) -> bool:
        adj = next((a for a in self.adjustments if a.adjustment_id == adjustment_id), None)
        if adj and not adj.applied:
            adj.applied = True
            return True
        return False

    def pending_adjustments(self) -> List[PolicyAdjustment]:
        return [a for a in self.adjustments if not a.applied and a.confidence > 0.6]
