"""Regenerative Economy — Positive externality minting, impact bonds, circularity."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional
import hashlib, time

@dataclass
class ImpactBond:
    """ATLAS-backed bond for ecological restoration projects."""
    bond_id: str
    project_name: str
    issuer: str
    face_value: Decimal  # ATLAS
    impact_metric: str  # tons_co2, hectares_restored, species_saved
    impact_target: float
    impact_achieved: float = 0.0
    maturity_date: float
    yield_rate: Decimal = Decimal("0.05")  # 5% annual yield
    status: str = "issued"  # issued, active, matured, defaulted
    investors: Dict[str, Decimal] = field(default_factory=dict)  # investor -> amount
    created_at: float = field(default_factory=time.time)

    @property
    def progress(self) -> float:
        return self.impact_achieved / max(1, self.impact_target)

    @property
    def total_raised(self) -> Decimal:
        return sum(self.investors.values(), Decimal("0"))

class CircularityIndex:
    """Measures how circular a resource system is."""

    def __init__(self):
        self.organizations: Dict[str, dict] = {}

    def assess(self, org_id: str, metrics: dict) -> float:
        """Calculate circularity index 0-100."""
        # Metrics: recycled_percentage, reuse_rate, waste_reduction, closed_loop_percentage
        recycled = metrics.get("recycled_percentage", 0)
        reuse = metrics.get("reuse_rate", 0)
        waste_reduction = metrics.get("waste_reduction", 0)
        closed_loop = metrics.get("closed_loop_percentage", 0)

        score = (recycled * 0.3 + reuse * 0.25 +
                 waste_reduction * 0.25 + closed_loop * 0.2)

        self.organizations[org_id] = {
            "score": score, "metrics": metrics,
            "timestamp": time.time(),
        }
        return score

    def get_bonus_multiplier(self, org_id: str) -> Decimal:
        """ATLAS minting bonus for high circularity."""
        score = self.organizations.get(org_id, {}).get("score", 0)
        if score > 80: return Decimal("1.20")  # 20% bonus
        elif score > 60: return Decimal("1.10")
        elif score > 40: return Decimal("1.05")
        return Decimal("1.00")

class RegenerativeEconomy:
    """
    Regenerative economics: rewards ecological restoration, penalizes pollution.
    
    Positive externalities → bonus ATLAS minting
    Negative externalities → carbon debt burns
    """

    POSITIVE_BONUS = Decimal("1.15")  # 15% bonus for ecological value
    NEGATIVE_PENALTY = Decimal("0.10")  # 10% burn for pollution

    def __init__(self):
        self.impact_bonds: Dict[str, ImpactBond] = {}
        self.circularity = CircularityIndex()
        self.positive_actions: List[dict] = []
        self.negative_actions: List[dict] = []

    def create_impact_bond(self, project_name: str, issuer: str,
                           face_value: Decimal, impact_metric: str,
                           impact_target: float, maturity_days: int = 365) -> ImpactBond:
        bond = ImpactBond(
            bond_id=hashlib.sha256(f"{project_name}:{issuer}:{time.time()}".encode()).hexdigest()[:16],
            project_name=project_name, issuer=issuer,
            face_value=face_value, impact_metric=impact_metric,
            impact_target=impact_target,
            maturity_date=time.time() + maturity_days * 86400,
        )
        self.impact_bonds[bond.bond_id] = bond
        return bond

    def invest_in_bond(self, bond_id: str, investor: str,
                       amount: Decimal) -> bool:
        bond = self.impact_bonds.get(bond_id)
        if not bond or bond.status != "issued":
            return False
        bond.investors[investor] = bond.investors.get(investor, Decimal("0")) + amount
        if bond.total_raised >= bond.face_value:
            bond.status = "active"
        return True

    def report_positive_impact(self, entity: str, category: str,
                               magnitude: float, description: str) -> dict:
        """Report a positive ecological externality."""
        action = {
            "action_id": hashlib.sha256(f"pos:{entity}:{time.time()}".encode()).hexdigest()[:16],
            "entity": entity,
            "category": category,  # carbon_sequestered, trees_planted, species_protected
            "magnitude": magnitude,
            "description": description,
            "bonus_multiplier": str(self.POSITIVE_BONUS),
            "timestamp": time.time(),
        }
        self.positive_actions.append(action)
        return action

    def report_negative_impact(self, entity: str, category: str,
                               magnitude: float, description: str) -> dict:
        """Report a negative ecological externality (pollution)."""
        action = {
            "action_id": hashlib.sha256(f"neg:{entity}:{time.time()}".encode()).hexdigest()[:16],
            "entity": entity,
            "category": category,  # co2_emitted, waste_generated, water_polluted
            "magnitude": magnitude,
            "description": description,
            "burn_rate": str(self.NEGATIVE_PENALTY),
            "carbon_debt": str(Decimal(str(magnitude)) * self.NEGATIVE_PENALTY),
            "timestamp": time.time(),
        }
        self.negative_actions.append(action)
        return action

    def mature_bond(self, bond_id: str) -> dict:
        """Mature an impact bond and calculate payouts."""
        bond = self.impact_bonds.get(bond_id)
        if not bond or bond.status != "active":
            return {}
        bond.status = "matured"
        payouts = {}
        for investor, amount in bond.investors.items():
            # Yield based on impact achieved
            yield_multiplier = Decimal("1") + bond.yield_rate * Decimal(str(bond.progress))
            payout = amount * yield_multiplier
            payouts[investor] = str(payout)
        return {"bond_id": bond_id, "payouts": payouts, "impact_progress": bond.progress}

    def stats(self) -> dict:
        return {
            "total_impact_bonds": len(self.impact_bonds),
            "active_bonds": sum(1 for b in self.impact_bonds.values() if b.status == "active"),
            "total_positive_actions": len(self.positive_actions),
            "total_negative_actions": len(self.negative_actions),
            "total_invested": str(sum(b.total_raised for b in self.impact_bonds.values(), Decimal("0"))),
        }
