"""Dashboard Manager — Real-time dashboards with widgets."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import time, hashlib

class WidgetType(Enum):
    KPI_CARD = "kpi_card"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HEAT_MAP = "heat_map"
    TABLE = "table"
    GAUGE = "gauge"
    SANKEY = "sankey"
    NETWORK_GRAPH = "network_graph"
    COUNTER = "counter"
    ALERT_LIST = "alert_list"

@dataclass
class DashboardWidget:
    """A single widget on a dashboard."""
    widget_id: str
    title: str
    widget_type: WidgetType
    data_source: str  # function name or endpoint
    refresh_interval: int = 30  # seconds
    config: dict = field(default_factory=dict)
    position: dict = field(default_factory=dict)  # {"x": 0, "y": 0, "w": 6, "h": 4}
    last_updated: float = 0
    cached_data: Any = None

    def needs_refresh(self) -> bool:
        return time.time() - self.last_updated > self.refresh_interval

@dataclass
class Dashboard:
    """A complete dashboard with multiple widgets."""
    dashboard_id: str
    name: str
    description: str
    category: str  # executive, economic, governance, network, sustainability
    widgets: List[DashboardWidget] = field(default_factory=list)
    auto_refresh: bool = True
    refresh_interval: int = 30
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    access_level: str = "public"  # public, verified, admin

class DashboardManager:
    """
    Manages all ATLAS dashboards.
    Provides pre-built dashboards and custom dashboard creation.
    """

    def __init__(self):
        self.dashboards: Dict[str, Dashboard] = {}
        self._create_default_dashboards()

    def _create_default_dashboards(self):
        """Create the 5 default dashboards."""
        # Executive Dashboard
        exec_dash = Dashboard(
            dashboard_id="executive",
            name="Executive Overview",
            description="High-level KPIs and health metrics",
            category="executive",
            widgets=[
                DashboardWidget("w1", "Economic Health Index", WidgetType.GAUGE,
                               "get_ehi", 30, {"max": 100, "thresholds": [40, 70]}),
                DashboardWidget("w2", "Total ATLAS Supply", WidgetType.KPI_CARD,
                               "get_supply", 60),
                DashboardWidget("w3", "Active Contributors", WidgetType.COUNTER,
                               "get_active_contributors", 30),
                DashboardWidget("w4", "Value Created (24h)", WidgetType.KPI_CARD,
                               "get_daily_value", 60),
                DashboardWidget("w5", "Governance Participation", WidgetType.GAUGE,
                               "get_participation", 60, {"max": 100}),
                DashboardWidget("w6", "Planetary Health", WidgetType.GAUGE,
                               "get_planetary_health", 300, {"max": 100}),
            ],
        )
        self.dashboards["executive"] = exec_dash

        # Economic Dashboard
        econ_dash = Dashboard(
            dashboard_id="economic",
            name="Economic Engine",
            description="Minting, velocity, AMM, supply dynamics",
            category="economic",
            widgets=[
                DashboardWidget("w1", "Minting Rate (7d)", WidgetType.LINE_CHART,
                               "get_minting_history", 60, {"period": "7d"}),
                DashboardWidget("w2", "Token Velocity", WidgetType.LINE_CHART,
                               "get_velocity_history", 60),
                DashboardWidget("w3", "AMM Prices", WidgetType.TABLE,
                               "get_amm_prices", 30),
                DashboardWidget("w4", "Gini Coefficient", WidgetType.LINE_CHART,
                               "get_gini_history", 300),
                DashboardWidget("w5", "Burn Rate", WidgetType.BAR_CHART,
                               "get_burn_stats", 300),
                DashboardWidget("w6", "Supply Distribution", WidgetType.PIE_CHART,
                               "get_supply_distribution", 300),
            ],
        )
        self.dashboards["economic"] = econ_dash

        # Governance Dashboard
        gov_dash = Dashboard(
            dashboard_id="governance",
            name="Governance & DAO",
            description="Proposals, voting, treasury, constitution",
            category="governance",
            widgets=[
                DashboardWidget("w1", "Active Proposals", WidgetType.TABLE,
                               "get_active_proposals", 30),
                DashboardWidget("w2", "Vote Distribution", WidgetType.PIE_CHART,
                               "get_vote_distribution", 30),
                DashboardWidget("w3", "Treasury Balance", WidgetType.KPI_CARD,
                               "get_treasury_balance", 60),
                DashboardWidget("w4", "Constitution Amendments", WidgetType.COUNTER,
                               "get_amendment_count", 300),
                DashboardWidget("w5", "Voter Participation Trend", WidgetType.LINE_CHART,
                               "get_participation_trend", 300),
                DashboardWidget("w6", "Titan Deliberation History", WidgetType.TABLE,
                               "get_congress_results", 60),
            ],
        )
        self.dashboards["governance"] = gov_dash

        # Network Dashboard
        net_dash = Dashboard(
            dashboard_id="network",
            name="Network & Mesh",
            description="Mesh peers, packet throughput, consensus",
            category="network",
            widgets=[
                DashboardWidget("w1", "Connected Peers", WidgetType.COUNTER,
                               "get_peer_count", 10),
                DashboardWidget("w2", "Packet Throughput", WidgetType.LINE_CHART,
                               "get_packet_throughput", 10),
                DashboardWidget("w3", "Consensus Latency", WidgetType.LINE_CHART,
                               "get_consensus_latency", 30),
                DashboardWidget("w4", "Mesh Health", WidgetType.GAUGE,
                               "get_mesh_health", 30, {"max": 100}),
                DashboardWidget("w5", "Validator Status", WidgetType.TABLE,
                               "get_validators", 60),
                DashboardWidget("w6", "Geographic Distribution", WidgetType.HEAT_MAP,
                               "get_geo_distribution", 300),
            ],
        )
        self.dashboards["network"] = net_dash

        # Sustainability Dashboard
        sus_dash = Dashboard(
            dashboard_id="sustainability",
            name="Sustainability & Ecology",
            description="Carbon credits, biodiversity, planetary boundaries",
            category="sustainability",
            widgets=[
                DashboardWidget("w1", "Carbon Credits Issued", WidgetType.COUNTER,
                               "get_carbon_credits", 60),
                DashboardWidget("w2", "Carbon Retired", WidgetType.COUNTER,
                               "get_carbon_retired", 60),
                DashboardWidget("w3", "Planetary Boundaries", WidgetType.TABLE,
                               "get_boundaries", 300),
                DashboardWidget("w4", "Biodiversity Index", WidgetType.LINE_CHART,
                               "get_biodiversity_trend", 300),
                DashboardWidget("w5", "Air Quality (Global)", WidgetType.HEAT_MAP,
                               "get_air_quality", 300),
                DashboardWidget("w6", "Impact Bonds", WidgetType.TABLE,
                               "get_impact_bonds", 300),
            ],
        )
        self.dashboards["sustainability"] = sus_dash

    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        return self.dashboards.get(dashboard_id)

    def list_dashboards(self) -> List[dict]:
        return [{"id": d.dashboard_id, "name": d.name,
                 "category": d.category, "widgets": len(d.widgets)}
                for d in self.dashboards.values()]

    def create_custom_dashboard(self, name: str, description: str,
                                widgets: List[DashboardWidget]) -> Dashboard:
        """Create a custom dashboard."""
        dash = Dashboard(
            dashboard_id=hashlib.sha256(f"custom:{name}:{time.time()}".encode()).hexdigest()[:16],
            name=name, description=description,
            category="custom", widgets=widgets,
        )
        self.dashboards[dash.dashboard_id] = dash
        return dash

    def add_widget(self, dashboard_id: str, widget: DashboardWidget) -> bool:
        dash = self.dashboards.get(dashboard_id)
        if dash:
            dash.widgets.append(widget)
            dash.updated_at = time.time()
            return True
        return False

    def stats(self) -> dict:
        return {
            "total_dashboards": len(self.dashboards),
            "total_widgets": sum(len(d.widgets) for d in self.dashboards.values()),
            "categories": list(set(d.category for d in self.dashboards.values())),
        }
