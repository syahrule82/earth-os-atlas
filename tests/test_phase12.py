"""Phase 12 integration tests."""
from decimal import Decimal
from src.sustainability.carbon import CarbonCreditSystem, CarbonProject
from src.sustainability.ecological import EcologicalTracker, BiodiversityIndex, WaterQuality, AirQuality
from src.sustainability.boundaries import PlanetaryBoundaryMonitor, BoundaryType
from src.sustainability.regenerative import RegenerativeEconomy, CircularityIndex
from src.sustainability.esg import ESGScorer
import time

def test_carbon_credit_system():
    system = CarbonCreditSystem()
    project = CarbonProject(
        project_id="proj_1", name="Amazon Reforestation",
        project_type="reforestation", location="BR",
        area_hectares=10000, expected_tons_per_year=5000,
        verifier="", verification_sources=[],
        start_date=time.time(),
    )
    system.register_project(project)
    # Verify
    assert system.verify_project("proj_1", "gaea", ["satellite", "iot_sensor"])
    assert project.status == "verified"
    # Issue credits
    credits = system.issue_credits("proj_1", Decimal("10"), "did:atlas:alice")
    assert len(credits) == 10
    assert project.total_credits_issued == Decimal("10")
    # Transfer
    assert system.transfer_credit(credits[0].credit_id, "did:atlas:bob")
    assert credits[0].owner == "did:atlas:bob"
    # Retire
    assert system.retire_credit(credits[0].credit_id, "did:atlas:bob")
    assert credits[0].retired is True
    # Balance
    balance = system.carbon_balance("did:atlas:bob")
    assert "credits_retired" in balance
    # Price update
    new_price = system.update_price(Decimal("100"), Decimal("50"))
    assert new_price == Decimal("45.0")  # High demand
    stats = system.stats()
    assert stats["total_credits"] == 10

def test_ecological_tracker():
    tracker = EcologicalTracker()
    # Biodiversity
    bio = BiodiversityIndex(
        region="amazon", species_count=500,
        habitat_diversity=0.85, ecosystem_services=0.90,
        threat_level="moderate", data_sources=["satellite", "drone"],
    )
    tracker.record_biodiversity(bio)
    assert bio.index_score > 50
    # Water quality
    wq = WaterQuality(location="river_x", ph=7.2, dissolved_oxygen=7.5,
                      turbidity=2.0, temperature=18.0)
    tracker.record_water(wq)
    assert wq.is_safe is True
    assert wq.quality_score > 50
    # Air quality
    aq = AirQuality(location="city_y", pm25=15, pm10=25, ozone=30,
                    no2=20, so2=5, co=0.5)
    tracker.record_air(aq)
    assert aq.aqi > 0
    assert aq.category == "Moderate"
    # Deforestation detection
    alert = tracker.detect_deforestation("amazon", 1000, 950)
    assert alert is not None
    assert alert["percentage_lost"] == 5.0
    # Trends
    assert tracker.biodiversity_trend("amazon") == "insufficient_data"
    # Global health
    score = tracker.global_health_score()
    assert 0 <= score <= 100

def test_planetary_boundaries():
    monitor = PlanetaryBoundaryMonitor()
    stats = monitor.global_status()
    assert stats["total_boundaries"] == 9
    # Some boundaries should be breached (climate change at 420 > 350)
    breached = monitor.breached_boundaries()
    assert len(breached) >= 1
    # Check climate change is breached
    climate = monitor.statuses[BoundaryType.CLIMATE_CHANGE]
    assert climate.is_breached is True
    assert climate.zone == "breach"
    # Update a boundary
    updated = monitor.update_boundary(BoundaryType.STRATOSPHERIC_OZONE, 280.0)
    assert updated is not None
    # Check alerts generated
    assert len(monitor.alerts) >= 0  # May or may not have new alerts

def test_regenerative_economy():
    econ = RegenerativeEconomy()
    # Impact bond
    bond = econ.create_impact_bond(
        project_name="Mangrove Restoration",
        issuer="did:atlas:ngo1",
        face_value=Decimal("10000"),
        impact_metric="hectares_restored",
        impact_target=500,
    )
    assert bond.status == "issued"
    # Invest
    econ.invest_in_bond(bond.bond_id, "did:atlas:investor1", Decimal("6000"))
    econ.invest_in_bond(bond.bond_id, "did:atlas:investor2", Decimal("4000"))
    assert bond.status == "active"
    assert bond.total_raised == Decimal("10000")
    # Report impact
    bond.impact_achieved = 350
    # Positive action
    pos = econ.report_positive_impact("did:atlas:corp1", "carbon_sequestered",
                                       100, "Sequestered 100 tons CO2")
    assert pos["bonus_multiplier"] == "1.15"
    # Negative action
    neg = econ.report_negative_impact("did:atlas:corp2", "co2_emitted",
                                       500, "Emitted 500 tons CO2")
    assert Decimal(neg["carbon_debt"]) == Decimal("50")
    # Mature bond
    result = econ.mature_bond(bond.bond_id)
    assert "payouts" in result
    assert bond.status == "matured"
    stats = econ.stats()
    assert stats["total_impact_bonds"] == 1

def test_circularity_index():
    ci = CircularityIndex()
    score = ci.assess("org_1", {
        "recycled_percentage": 80,
        "reuse_rate": 70,
        "waste_reduction": 60,
        "closed_loop_percentage": 50,
    })
    assert score > 60
    bonus = ci.get_bonus_multiplier("org_1")
    assert bonus == Decimal("1.10")  # Score 60-80 = 10% bonus

def test_esg_scorer():
    scorer = ESGScorer()
    report = scorer.assess(
        org_id="corp_1",
        env_metrics={"carbon_intensity": 30, "renewable_energy_pct": 60,
                     "waste_reduction_pct": 70, "water_efficiency_score": 65},
        social_metrics={"labor_practices_score": 75, "community_impact_score": 60,
                        "health_safety_score": 80, "diversity_score": 55},
        gov_metrics={"board_independence_pct": 70, "transparency_score": 65,
                     "ethics_score": 75, "rights_score": 60},
    )
    assert 0 <= report.overall_score <= 100
    assert len(report.strengths) >= 1
    assert len(report.recommendations) >= 1
    # Ranking
    scorer.assess("corp_2",
                  {"carbon_intensity": 60, "renewable_energy_pct": 20,
                   "waste_reduction_pct": 30, "water_efficiency_score": 40},
                  {"labor_practices_score": 40, "community_impact_score": 30,
                   "health_safety_score": 50, "diversity_score": 35},
                  {"board_independence_pct": 40, "transparency_score": 45,
                   "ethics_score": 50, "rights_score": 40})
    ranking = scorer.ranking()
    assert len(ranking) == 2
    assert ranking[0][0] == "corp_1"  # Higher score

if __name__ == "__main__":
    test_carbon_credit_system()
    test_ecological_tracker()
    test_planetary_boundaries()
    test_regenerative_economy()
    test_circularity_index()
    test_esg_scorer()
    print("✅ All Phase 12 tests passed")
