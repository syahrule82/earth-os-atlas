"""Phase 15 integration tests."""
from decimal import Decimal
from src.analytics_viz.dashboards import DashboardManager, DashboardWidget, WidgetType
from src.analytics_viz.value_viz import ValueFlowVisualizer, SankeyData, NetworkGraphData
from src.analytics_viz.forecasting import EconomicForecaster, ForecastScenario, StressTestResult
from src.analytics_viz.governance_analytics import GovernanceAnalytics
from src.analytics_viz.reports import ReportBuilder, ExportFormat
from src.analytics_viz.alerts import AlertEngine, AlertSeverity
import time

def test_dashboard_manager():
    dm = DashboardManager()
    # Default dashboards
    assert len(dm.dashboards) >= 5
    exec = dm.get_dashboard("executive")
    assert exec is not None
    assert len(exec.widgets) >= 6
    assert exec.widgets[0].widget_type == WidgetType.GAUGE
    # List
    listing = dm.list_dashboards()
    assert len(listing) >= 5
    # Custom dashboard
    custom = dm.create_custom_dashboard("My Dashboard", "Custom view", [
        DashboardWidget("cw1", "Custom KPI", WidgetType.KPI_CARD, "get_custom_kpi"),
    ])
    assert custom.category == "custom"
    assert dm.get_dashboard(custom.dashboard_id) is not None
    # Add widget
    assert dm.add_widget(custom.dashboard_id, DashboardWidget("cw2", "Another", WidgetType.COUNTER, "get_count"))
    assert len(custom.widgets) == 2
    stats = dm.stats()
    assert stats["total_dashboards"] >= 6

def test_value_flow_visualizer():
    viz = ValueFlowVisualizer()
    # Sankey
    flows = [
        {"source": "alice", "target": "bob", "amount": 100, "category": "CREATED_KNOWLEDGE"},
        {"source": "bob", "target": "charlie", "amount": 50, "category": "BUILT_INFRASTRUCTURE"},
        {"source": "alice", "target": "charlie", "amount": 30, "category": "CREATED_KNOWLEDGE"},
    ]
    sankey = viz.build_sankey(flows)
    assert len(sankey.nodes) == 3
    assert len(sankey.links) == 3
    assert sankey.links[0]["value"] == 100
    # Network graph
    contributors = [
        {"did": "alice", "name": "Alice", "contributions": 50, "collaborators": ["bob", "charlie"]},
        {"did": "bob", "name": "Bob", "contributions": 30, "collaborators": ["alice"]},
        {"did": "charlie", "name": "Charlie", "contributions": 10, "collaborators": ["alice"]},
    ]
    graph = viz.build_network_graph(contributors)
    assert len(graph.nodes) == 3
    assert len(graph.edges) == 3
    # Heat map
    geo_data = [
        {"region": "Jakarta", "lat": -6.2, "lon": 106.8, "value": 500},
        {"region": "Tokyo", "lat": 35.7, "lon": 139.7, "value": 1200},
    ]
    heat = viz.build_heat_map(geo_data)
    assert len(heat) == 2
    assert heat[1]["intensity"] == 1.0  # 1200/1000 capped at 1.0
    # Category distribution
    dist = viz.category_distribution(flows)
    assert len(dist) >= 2
    assert dist[0]["name"] == "CREATED_KNOWLEDGE"  # Highest total (130)
    # Time series
    ts = viz.time_series(flows, interval="daily")
    assert len(ts) >= 1
    assert all("timestamp" in t and "value" in t for t in ts)

def test_economic_forecaster():
    forecaster = EconomicForecaster()
    # Record data
    for i in range(10):
        forecaster.record_data({"supply": 1000 + i * 10, "velocity": 2.0 + i * 0.1})
    # Forecast
    scenarios = forecaster.forecast("supply", 1100, horizons=[1, 7, 30])
    assert len(scenarios) == 3  # bull, base, bear
    assert all(len(s.predictions) == 3 for s in scenarios)
    # Bull should be higher than base, base higher than bear
    bull = next(s for s in scenarios if s.scenario_name == "bull")
    bear = next(s for s in scenarios if s.scenario_name == "bear")
    assert bull.predictions[-1] > bear.predictions[-1]
    # Stress test
    result = forecaster.stress_test("Supply Shock Test", "supply_shock",
                                     {"supply": 1000, "price": 1.0, "validators": 10})
    assert result.shock_type == "supply_shock"
    assert result.post_shock_metrics["supply"] == 500
    assert result.severity == "severe"
    assert result.passed is True  # System still functional
    summary = forecaster.summary()
    assert summary["total_forecasts"] == 3
    assert summary["total_stress_tests"] == 1

def test_governance_analytics():
    ga = GovernanceAnalytics()
    # Record proposals
    for i in range(10):
        ga.record_proposal({
            "id": f"prop_{i}", "title": f"Proposal {i}",
            "category": "protocol" if i < 5 else "economic",
            "status": "passed" if i < 6 else "rejected",
        })
    # Record votes
    for i in range(20):
        ga.record_vote({
            "voter": f"did:atlas:voter_{i % 5}",
            "proposal_id": f"prop_{i % 10}",
            "voice_credits": 10 + i,
            "timestamp": time.time() - i * 3600,
        })
    # Record congress results
    ga.record_congress_result({"session_id": "s1", "outcome": "passed", "consensus": 0.85})
    ga.record_congress_result({"session_id": "s2", "outcome": "rejected", "consensus": 0.3})
    # Stats
    stats = ga.proposal_stats()
    assert stats.total_proposals == 10
    assert stats.passed == 6
    assert stats.rejected == 4
    assert stats.success_rate == 0.6
    assert stats.by_category["protocol"] == 5
    # Voter metrics
    vm = ga.voter_metrics()
    assert vm.total_voters == 5
    assert vm.active_voters_30d == 5
    assert len(vm.top_voters) <= 5
    assert len(vm.quadratic_voting_distribution) <= 5
    # Congress history
    history = ga.congress_history()
    assert len(history) == 2
    # Success by category
    cat_stats = ga.proposal_success_by_category()
    assert len(cat_stats) == 2
    assert any(c["category"] == "protocol" for c in cat_stats)
    summary = ga.summary()
    assert summary["total_proposals"] == 10

def test_report_builder():
    rb = ReportBuilder()
    report = rb.create_report("Q3 Economic Report", "Quarterly analysis", "did:atlas:analyst")
    # Add sections
    rb.add_section(report.report_id, "Supply Metrics", {"total": "1000000", "circulating": "850000"}, "table")
    rb.add_section(report.report_id, "Top Contributors", ["alice", "bob", "charlie"], "bar_chart")
    assert len(report.sections) == 2
    # Export JSON
    json_export = rb.export(report.report_id, ExportFormat.JSON)
    assert json_export is not None
    assert '"title"' in json_export
    # Export CSV
    csv_export = rb.export(report.report_id, ExportFormat.CSV)
    assert csv_export is not None
    assert "section_title,key,value" in csv_export
    # Export Markdown
    md_export = rb.export(report.report_id, ExportFormat.MARKDOWN)
    assert md_export is not None
    assert "# Q3 Economic Report" in md_export
    # Export HTML
    html_export = rb.export(report.report_id, ExportFormat.HTML)
    assert html_export is not None
    assert "<html>" in html_export
    # List
    listing = rb.list_reports()
    assert len(listing) == 1

def test_alert_engine():
    engine = AlertEngine()
    # Default rules
    assert len(engine.rules) >= 8
    # Check with healthy metrics (no alerts)
    healthy = {"ehi": 80, "velocity": 3.0, "mesh_health": 95, "participation": 0.6,
               "boundaries_breached": 0, "consensus_latency_ms": 1000}
    alerts = engine.check(healthy)
    assert len(alerts) == 0  # All healthy
    # Check with unhealthy metrics
    unhealthy = {"ehi": 35, "velocity": 0.5, "mesh_health": 70, "participation": 0.2,
                 "boundaries_breached": 2, "consensus_latency_ms": 6000}
    alerts = engine.check(unhealthy)
    assert len(alerts) >= 5  # Multiple alerts triggered
    severities = [a.severity for a in alerts]
    assert AlertSeverity.EMERGENCY in severities  # boundary breach
    assert AlertSeverity.CRITICAL in severities  # ehi low + mesh unhealthy
    # Acknowledge
    if alerts:
        assert engine.acknowledge(alerts[0].alert_id)
        assert alerts[0].acknowledged is True
        assert engine.resolve(alerts[0].alert_id)
        assert alerts[0].resolved is True
    # Active alerts
    active = engine.active_alerts()
    assert len(active) >= 4  # At least 4 unresolved
    stats = engine.stats()
    assert stats["total_alerts"] >= 5
    # Add custom rule
    custom_rule = engine.rules[list(engine.rules.keys())[0]]
    assert custom_rule.enabled is True
    stats = engine.stats()
    assert stats["enabled_rules"] >= 8

if __name__ == "__main__":
    test_dashboard_manager()
    test_value_flow_visualizer()
    test_economic_forecaster()
    test_governance_analytics()
    test_report_builder()
    test_alert_engine()
    print("✅ All Phase 15 tests passed")
