"""Adoption curve model — S-curve diffusion with network effects."""
from dataclasses import dataclass
from typing import List
import numpy as np

class AdoptionCurve:
    """Models technology adoption using Bass diffusion model."""
    
    def __init__(self, market_potential: float = 1e6,
                 innovation_coeff: float = 0.003,
                 imitation_coeff: float = 0.4):
        self.M = market_potential  # Total potential adopters
        self.p = innovation_coeff  # Innovation coefficient (advertising)
        self.q = imitation_coeff   # Imitation coefficient (word of mouth)
    
    def simulate(self, periods: int = 365) -> List[dict]:
        """Simulate adoption over time periods."""
        adopted = 0
        results = []
        
        for t in range(periods):
            # Bass model: new adopters = p*(M - N_t) + q*(N_t/M)*(M - N_t)
            remaining = self.M - adopted
            innovators = self.p * remaining
            imitators = self.q * (adopted / self.M) * remaining if self.M > 0 else 0
            new_adopters = innovators + imitators
            adopted += new_adopters
            
            results.append({
                "period": t,
                "new_adopters": new_adopters,
                "total_adopted": adopted,
                "penetration": adopted / self.M if self.M > 0 else 0,
            })
        
        return results
    
    def time_to_critical_mass(self, threshold: float = 1000) -> int:
        """Estimate periods until critical mass adoption."""
        results = self.simulate()
        for r in results:
            if r["total_adopted"] >= threshold:
                return r["period"]
        return -1  # Never reaches

class NetworkEffectModel:
    """Models Metcalfe's law network effects for ATLAS."""
    
    def __init__(self):
        self.nodes_history: List[int] = []
    
    def network_value(self, n_nodes: int) -> float:
        """Metcalfe's law: V ∝ n²"""
        return n_nodes ** 2
    
    def value_per_node(self, n_nodes: int) -> float:
        """Value per node (V/n = n)."""
        return float(n_nodes)
    
    def critical_mass_value(self, critical_mass: int = 1000) -> float:
        """Network value at critical mass."""
        return self.network_value(critical_mass)
    
    def marginal_benefit(self, current_nodes: int, new_nodes: int = 1) -> float:
        """Marginal benefit of adding new nodes."""
        before = self.network_value(current_nodes)
        after = self.network_value(current_nodes + new_nodes)
        return after - before
