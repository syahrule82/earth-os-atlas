"""Healthcare bridge — medical outcome value tracking."""
from dataclasses import dataclass, field
from typing import Dict, List
import time

@dataclass
class HealthOutcome:
    outcome_id: str
    patient_count: int
    treatment_type: str
    recovery_rate: float  # 0-1
    region: str
    severity_treated: float  # 1-10
    timestamp: float = field(default_factory=time.time)

class HealthcareBridge:
    """Tracks healthcare outcomes for HEALED_BIOLOGICAL value."""
    
    def __init__(self):
        self.outcomes: List[HealthOutcome] = []
    
    def ingest(self, data: dict) -> HealthOutcome:
        outcome = HealthOutcome(
            outcome_id=f"health_{int(time.time() * 1000)}",
            patient_count=data.get("patient_count", 1),
            treatment_type=data.get("treatment_type", "general"),
            recovery_rate=float(data.get("recovery_rate", 0)),
            region=data.get("region", "global"),
            severity_treated=float(data.get("severity", 5)),
        )
        self.outcomes.append(outcome)
        return outcome
    
    def detect_healing_value(self, outcome: HealthOutcome) -> Dict:
        """Detect HEALED_BIOLOGICAL value from healthcare outcomes."""
        # Magnitude = patients × severity × recovery_rate × 10
        magnitude = outcome.patient_count * outcome.severity_treated * outcome.recovery_rate * 10
        
        return {
            "category": "HEALED_BIOLOGICAL",
            "magnitude": magnitude,
            "confidence": min(0.95, outcome.recovery_rate + 0.1),
            "multiplier": 1.25,  # HEALED_BIOLOGICAL multiplier
            "description": f"{outcome.patient_count} patients treated ({outcome.treatment_type}), "
                          f"recovery rate: {outcome.recovery_rate:.1%}",
        }
