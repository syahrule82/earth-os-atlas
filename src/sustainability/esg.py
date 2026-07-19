"""ESG Scorer — Environmental, Social, Governance scoring for organizations."""
from dataclasses import dataclass, field
from typing import Dict, List
import time

@dataclass
class ESGReport:
    """Full ESG assessment report."""
    org_id: str
    environmental_score: float  # 0-100
    social_score: float
    governance_score: float
    overall_score: float
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

class ESGScorer:
    """Calculates ESG scores for organizations on the ATLAS network."""

    WEIGHTS = {"environmental": 0.40, "social": 0.30, "governance": 0.30}

    def __init__(self):
        self.reports: Dict[str, List[ESGReport]] = {}

    def assess(self, org_id: str, env_metrics: dict,
               social_metrics: dict, gov_metrics: dict) -> ESGReport:
        """Calculate ESG scores from raw metrics."""
        # Environmental: carbon footprint, renewable energy, waste, water
        env_score = self._calc_env(env_metrics)

        # Social: labor practices, community impact, health & safety, diversity
        social_score = self._calc_social(social_metrics)

        # Governance: board independence, transparency, ethics, rights
        gov_score = self._calc_governance(gov_metrics)

        overall = (env_score * self.WEIGHTS["environmental"] +
                   social_score * self.WEIGHTS["social"] +
                   gov_score * self.WEIGHTS["governance"])

        report = ESGReport(
            org_id=org_id,
            environmental_score=env_score,
            social_score=social_score,
            governance_score=gov_score,
            overall_score=overall,
            strengths=self._identify_strengths(env_score, social_score, gov_score),
            weaknesses=self._identify_weaknesses(env_score, social_score, gov_score),
            recommendations=self._generate_recommendations(env_score, social_score, gov_score),
        )
        if org_id not in self.reports:
            self.reports[org_id] = []
        self.reports[org_id].append(report)
        return report

    def _calc_env(self, m: dict) -> float:
        carbon = 100 - min(100, m.get("carbon_intensity", 50))
        renewable = m.get("renewable_energy_pct", 30)
        waste_reduction = m.get("waste_reduction_pct", 40)
        water_efficiency = m.get("water_efficiency_score", 50)
        return (carbon * 0.35 + renewable * 0.25 +
                waste_reduction * 0.20 + water_efficiency * 0.20)

    def _calc_social(self, m: dict) -> float:
        labor = m.get("labor_practices_score", 60)
        community = m.get("community_impact_score", 50)
        safety = m.get("health_safety_score", 70)
        diversity = m.get("diversity_score", 50)
        return (labor * 0.30 + community * 0.25 +
                safety * 0.25 + diversity * 0.20)

    def _calc_governance(self, m: dict) -> float:
        independence = m.get("board_independence_pct", 50)
        transparency = m.get("transparency_score", 60)
        ethics = m.get("ethics_score", 65)
        rights = m.get("rights_score", 60)
        return (independence * 0.30 + transparency * 0.25 +
                ethics * 0.25 + rights * 0.20)

    def _identify_strengths(self, env, soc, gov) -> List[str]:
        strengths = []
        if env > 70: strengths.append("Strong environmental practices")
        if soc > 70: strengths.append("Excellent social responsibility")
        if gov > 70: strengths.append("Robust governance framework")
        return strengths or ["No significant strengths identified"]

    def _identify_weaknesses(self, env, soc, gov) -> List[str]:
        weaknesses = []
        if env < 50: weaknesses.append("Environmental performance below threshold")
        if soc < 50: weaknesses.append("Social responsibility needs improvement")
        if gov < 50: weaknesses.append("Governance practices require strengthening")
        return weaknesses or ["No significant weaknesses identified"]

    def _generate_recommendations(self, env, soc, gov) -> List[str]:
        recs = []
        if env < 60: recs.append("Invest in renewable energy and carbon offset projects")
        if soc < 60: recs.append("Improve labor practices and community engagement")
        if gov < 60: recs.append("Enhance board independence and transparency reporting")
        return recs or ["Maintain current ESG performance levels"]

    def get_latest(self, org_id: str) -> ESGReport:
        reports = self.reports.get(org_id, [])
        return reports[-1] if reports else None

    def ranking(self, top_n: int = 10) -> List[tuple]:
        all_orgs = [(oid, reps[-1].overall_score)
                    for oid, reps in self.reports.items() if reps]
        return sorted(all_orgs, key=lambda x: x[1], reverse=True)[:top_n]
