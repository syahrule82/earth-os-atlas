"""Alert Engine — Threshold-based alerting."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
import time, hashlib

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class AlertRule:
    """A rule that triggers an alert when conditions are met."""
    rule_id: str
    name: str
    metric: str  # e.g., "ehi", "velocity", "mesh_health"
    condition: str  # "lt", "gt", "eq", "change_pct"
    threshold: float
    severity: AlertSeverity = AlertSeverity.WARNING
    cooldown_minutes: int = 30  # Min time between alerts for same rule
    enabled: bool = True
    last_triggered: float = 0
    trigger_count: int = 0

@dataclass
class AlertEvent:
    """A triggered alert event."""
    alert_id: str
    rule_id: str
    rule_name: str
    metric: str
    value: float
    threshold: float
    severity: AlertSeverity
    message: str
    timestamp: float = field(default_factory=time.time)
    acknowledged: bool = False
    resolved: bool = False

class AlertEngine:
    """
    Threshold-based alerting system for ATLAS metrics.
    """

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.events: List[AlertEvent] = []
        self.handlers: List[Callable] = []
        self._create_default_rules()

    def _create_default_rules(self):
        """Create default alert rules."""
        defaults = [
            ("ehi_low", "Economic Health Index Low", "ehi", "lt", 40, AlertSeverity.CRITICAL),
            ("ehi_warning", "EHI Warning", "ehi", "lt", 60, AlertSeverity.WARNING),
            ("velocity_low", "Token Velocity Low", "velocity", "lt", 1.0, AlertSeverity.WARNING),
            ("velocity_high", "Token Velocity High", "velocity", "gt", 10.0, AlertSeverity.WARNING),
            ("mesh_unhealthy", "Mesh Health Critical", "mesh_health", "lt", 80, AlertSeverity.CRITICAL),
            ("participation_low", "Governance Participation Low", "participation", "lt", 0.3, AlertSeverity.WARNING),
            ("boundary_breach", "Planetary Boundary Breach", "boundaries_breached", "gt", 0, AlertSeverity.EMERGENCY),
            ("consensus_slow", "Consensus Latency High", "consensus_latency_ms", "gt", 5000, AlertSeverity.WARNING),
        ]
        for rid, name, metric, cond, threshold, severity in defaults:
            self.rules[rid] = AlertRule(
                rule_id=rid, name=name, metric=metric,
                condition=cond, threshold=threshold, severity=severity,
            )

    def add_rule(self, rule: AlertRule) -> None:
        self.rules[rule.rule_id] = rule

    def remove_rule(self, rule_id: str) -> bool:
        return self.rules.pop(rule_id, None) is not None

    def check(self, metrics: Dict[str, float]) -> List[AlertEvent]:
        """Check all rules against current metrics and trigger alerts."""
        triggered = []
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            # Check cooldown
            if time.time() - rule.last_triggered < rule.cooldown_minutes * 60:
                continue
            value = metrics.get(rule.metric)
            if value is None:
                continue
            # Check condition
            should_alert = False
            if rule.condition == "lt" and value < rule.threshold:
                should_alert = True
            elif rule.condition == "gt" and value > rule.threshold:
                should_alert = True
            elif rule.condition == "eq" and value == rule.threshold:
                should_alert = True
            if should_alert:
                event = AlertEvent(
                    alert_id=hashlib.sha256(f"alert:{rule.rule_id}:{time.time()}".encode()).hexdigest()[:16],
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    metric=rule.metric,
                    value=value,
                    threshold=rule.threshold,
                    severity=rule.severity,
                    message=f"{rule.name}: {rule.metric}={value} (threshold: {rule.condition} {rule.threshold})",
                )
                self.events.append(event)
                triggered.append(event)
                rule.last_triggered = time.time()
                rule.trigger_count += 1
                # Notify handlers
                for handler in self.handlers:
                    handler(event)
        return triggered

    def add_handler(self, handler: Callable) -> None:
        self.handlers.append(handler)

    def acknowledge(self, alert_id: str) -> bool:
        event = next((e for e in self.events if e.alert_id == alert_id), None)
        if event:
            event.acknowledged = True
            return True
        return False

    def resolve(self, alert_id: str) -> bool:
        event = next((e for e in self.events if e.alert_id == alert_id), None)
        if event:
            event.resolved = True
            return True
        return False

    def active_alerts(self) -> List[AlertEvent]:
        return [e for e in self.events if not e.resolved]

    def stats(self) -> dict:
        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules.values() if r.enabled),
            "total_alerts": len(self.events),
            "active_alerts": len(self.active_alerts()),
            "critical_alerts": sum(1 for e in self.events if e.severity == AlertSeverity.CRITICAL and not e.resolved),
            "emergency_alerts": sum(1 for e in self.events if e.severity == AlertSeverity.EMERGENCY and not e.resolved),
        }
