"""Planetary Boundary Monitor — Tracks 9 Earth system boundaries."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import time

class BoundaryType(Enum):
    CLIMATE_CHANGE = "climate_change"
    BIOSPHERE_INTEGRITY = "biosphere_integrity"
    OCEAN_ACIDIFICATION = "ocean_acidification"
    LAND_SYSTEM_CHANGE = "land_system_change"
    FRESHWATER_USE = "freshwater_use"
    NITROGEN_PHOSPHORUS = "nitrogen_phosphorus"
    STRATOSPHERIC_OZONE = "stratospheric_ozone"
    ATMOSPHERIC_AEROSOLS = "atmospheric_aerosols"
    CHEMICAL_POLLUTION = "chemical_pollution"

@dataclass
class BoundaryStatus:
    """Status of a single planetary boundary."""
    boundary_type: BoundaryType
    current_value: float
    boundary_limit: float
    zone: str  # safe, warning, danger, breach
    trend: str  # improving, stable, worsening
    last_updated: float = field(default_factory=time.time)
    description: str = ""

    @property
    def utilization(self) -> float:
        """How close we are to the boundary (0=safe, 1=at limit, >1=breached)."""
        return self.current_value / self.boundary_limit if self.boundary_limit > 0 else 0

    @property
    def is_breached(self) -> bool:
        return self.current_value > self.boundary_limit

class PlanetaryBoundaryMonitor:
    """
    Monitors all 9 planetary boundaries.
    
    When a boundary is breached, an automatic governance proposal
    is generated to redirect ATLAS treasury resources.
    """

    BOUNDARIES = {
        BoundaryType.CLIMATE_CHANGE: {"limit": 350.0, "unit": "ppm CO2", "current": 420.0,
                                      "description": "Atmospheric CO2 concentration"},
        BoundaryType.BIOSPHERE_INTEGRITY: {"limit": 10.0, "unit": "extinctions/million/year", "current": 100.0,
                                           "description": "Species extinction rate"},
        BoundaryType.OCEAN_ACIDIFICATION: {"limit": 2.75, "unit": "aragonite saturation", "current": 2.9,
                                           "description": "Ocean aragonite saturation state"},
        BoundaryType.LAND_SYSTEM_CHANGE: {"limit": 75.0, "unit": "% forest cover", "current": 62.0,
                                          "description": "Global forest cover percentage"},
        BoundaryType.FRESHWATER_USE: {"limit": 4000.0, "unit": "km³/year", "current": 2600.0,
                                      "description": "Global freshwater consumption"},
        BoundaryType.NITROGEN_PHOSPHORUS: {"limit": 62.0, "unit": "Tg N/year", "current": 150.0,
                                           "description": "Industrial nitrogen fixation"},
        BoundaryType.STRATOSPHERIC_OZONE: {"limit": 275.0, "unit": "DU", "current": 285.0,
                                           "description": "Stratospheric ozone concentration"},
        BoundaryType.ATMOSPHERIC_AEROSOLS: {"limit": 0.25, "unit": "AOD", "current": 0.15,
                                            "description": "Atmospheric aerosol loading"},
        BoundaryType.CHEMICAL_POLLUTION: {"limit": 50.0, "unit": "index", "current": 70.0,
                                          "description": "Novel entities pollution index"},
    }

    def __init__(self):
        self.statuses: Dict[BoundaryType, BoundaryStatus] = {}
        self.alerts: List[dict] = []
        self.proposals_generated: List[dict] = []
        self._initialize()

    def _initialize(self):
        for bt, info in self.BOUNDARIES.items():
            util = info["current"] / info["limit"]
            if util > 1.0:
                zone = "breach"
            elif util > 0.9:
                zone = "danger"
            elif util > 0.75:
                zone = "warning"
            else:
                zone = "safe"
            self.statuses[bt] = BoundaryStatus(
                boundary_type=bt,
                current_value=info["current"],
                boundary_limit=info["limit"],
                zone=zone,
                trend="worsening" if zone in ("breach", "danger") else "stable",
                description=info["description"],
            )

    def update_boundary(self, bt: BoundaryType, current_value: float) -> BoundaryStatus:
        """Update a boundary's current value."""
        status = self.statuses.get(bt)
        if not status:
            return None
        old_zone = status.zone
        status.current_value = current_value
        util = current_value / status.boundary_limit
        if util > 1.0:
            status.zone = "breach"
        elif util > 0.9:
            status.zone = "danger"
        elif util > 0.75:
            status.zone = "warning"
        else:
            status.zone = "safe"
        status.last_updated = time.time()
        # Alert if zone worsened
        if status.zone != old_zone:
            self._generate_alert(bt, old_zone, status.zone)
        return status

    def _generate_alert(self, bt: BoundaryType, old_zone: str, new_zone: str):
        alert = {
            "alert_id": f"boundary_{bt.value}_{int(time.time())}",
            "boundary": bt.value,
            "old_zone": old_zone,
            "new_zone": new_zone,
            "severity": "critical" if new_zone == "breach" else "high" if new_zone == "danger" else "moderate",
            "timestamp": time.time(),
        }
        self.alerts.append(alert)
        # Auto-generate governance proposal for breaches
        if new_zone == "breach":
            proposal = {
                "proposal_id": f"emergency_{bt.value}_{int(time.time())}",
                "title": f"EMERGENCY: {bt.value} boundary breached",
                "description": f"Planetary boundary {bt.value} has crossed into breach zone. "
                              f"Current: {self.statuses[bt].current_value}, Limit: {self.statuses[bt].boundary_limit}",
                "type": "emergency_resource_allocation",
                "suggested_allocation": "25% of treasury to remediation",
            }
            self.proposals_generated.append(proposal)

    def breached_boundaries(self) -> List[BoundaryStatus]:
        return [s for s in self.statuses.values() if s.is_breached]

    def global_status(self) -> dict:
        zones = [s.zone for s in self.statuses.values()]
        return {
            "total_boundaries": len(self.statuses),
            "safe": zones.count("safe"),
            "warning": zones.count("warning"),
            "danger": zones.count("danger"),
            "breached": zones.count("breach"),
            "total_alerts": len(self.alerts),
            "emergency_proposals": len(self.proposals_generated),
        }
