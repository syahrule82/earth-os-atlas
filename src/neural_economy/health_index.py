"""Economic Health Index — composite metric for ATLAS economy."""
from dataclasses import dataclass, field
from typing import Dict
import numpy as np

class EconomicHealthIndex:
    """
    Composite health metric combining:
    - Gini coefficient (equality)
    - Token velocity (economic activity)
    - Participation rate (governance engagement)
    - Innovation index (new value categories)
    - Network growth (new identities)
    """
    
    def __init__(self):
        self.history: list = []
    
    def calculate(self, metrics: Dict) -> float:
        """Calculate composite health index [0-100]."""
        
        # 1. Equality score (inverse Gini, scaled)
        gini = metrics.get("gini", 0.5)
        equality_score = max(0, 100 - gini * 200)  # Lower Gini = higher score
        
        # 2. Velocity score
        velocity = metrics.get("velocity", 0)
        target_velocity = 5.0
        velocity_score = min(100, (velocity / target_velocity) * 100)
        
        # 3. Participation rate
        participation = metrics.get("participation_rate", 0)  # 0-1
        participation_score = participation * 100
        
        # 4. Innovation index
        innovation = metrics.get("innovation_index", 0)  # 0-1
        innovation_score = innovation * 100
        
        # 5. Network growth
        growth = metrics.get("network_growth", 0)  # percentage
        growth_score = min(100, growth * 10)
        
        # Weighted average
        weights = {
            "equality": 0.25,
            "velocity": 0.20,
            "participation": 0.25,
            "innovation": 0.15,
            "growth": 0.15,
        }
        
        ehi = (
            equality_score * weights["equality"] +
            velocity_score * weights["velocity"] +
            participation_score * weights["participation"] +
            innovation_score * weights["innovation"] +
            growth_score * weights["growth"]
        )
        
        self.history.append({"ehi": ehi, "timestamp": metrics.get("timestamp", 0)})
        return ehi
    
    def trend(self, periods: int = 30) -> str:
        """Return trend direction over last N periods."""
        if len(self.history) < 2:
            return "stable"
        recent = self.history[-periodions:] if len(self.history) >= periods else self.history
        if len(recent) < 2:
            return "stable"
        delta = recent[-1]["ehi"] - recent[0]["ehi"]
        if delta > 2:
            return "improving"
        elif delta < -2:
            return "declining"
        return "stable"
