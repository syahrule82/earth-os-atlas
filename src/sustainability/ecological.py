"""Ecological Tracker — Biodiversity, water, air quality monitoring."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time, hashlib

@dataclass
class BiodiversityIndex:
    """Biodiversity measurement for a region."""
    region: str
    species_count: int
    habitat_diversity: float  # 0-1 (Shannon index normalized)
    ecosystem_services: float  # 0-1 (pollination, water filtration, etc.)
    threat_level: str  # low, moderate, high, critical
    timestamp: float = field(default_factory=time.time)
    data_sources: List[str] = field(default_factory=list)

    @property
    def index_score(self) -> float:
        """Composite biodiversity score 0-100."""
        species_score = min(100, self.species_count / 10)
        return (species_score * 0.4 + self.habitat_diversity * 100 * 0.3 +
                self.ecosystem_services * 100 * 0.3)

@dataclass
class WaterQuality:
    """Water quality measurement."""
    location: str
    ph: float
    dissolved_oxygen: float  # mg/L
    turbidity: float  # NTU
    temperature: float  # Celsius
    contaminants: Dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    @property
    def quality_score(self) -> float:
        """Water quality score 0-100."""
        ph_score = 100 - abs(self.ph - 7.0) * 20
        do_score = min(100, self.dissolved_oxygen * 10)
        turb_score = max(0, 100 - self.turbidity * 5)
        return (ph_score + do_score + turb_score) / 3

    @property
    def is_safe(self) -> bool:
        return 6.5 <= self.ph <= 8.5 and self.dissolved_oxygen >= 5.0

@dataclass
class AirQuality:
    """Air quality measurement."""
    location: str
    pm25: float  # µg/m³
    pm10: float  # µg/m³
    ozone: float  # ppb
    no2: float  # ppb
    so2: float  # ppb
    co: float  # ppm
    timestamp: float = field(default_factory=time.time)

    @property
    def aqi(self) -> int:
        """Air Quality Index (0-500)."""
        # Simplified AQI based on PM2.5
        if self.pm25 <= 12:
            return int(self.pm25 * 4)  # 0-48 (Good)
        elif self.pm25 <= 35:
            return int(48 + (self.pm25 - 12) * 2)  # 49-94 (Moderate)
        elif self.pm25 <= 55:
            return int(94 + (self.pm25 - 35) * 2.5)  # 95-144 (Unhealthy for sensitive)
        elif self.pm25 <= 150:
            return int(144 + (self.pm25 - 55) * 1)  # 145-239 (Unhealthy)
        else:
            return min(500, int(239 + (self.pm25 - 150) * 1.5))  # 240+ (Very unhealthy)

    @property
    def category(self) -> str:
        aqi = self.aqi
        if aqi <= 50: return "Good"
        elif aqi <= 100: return "Moderate"
        elif aqi <= 150: return "Unhealthy for Sensitive Groups"
        elif aqi <= 200: return "Unhealthy"
        elif aqi <= 300: return "Very Unhealthy"
        return "Hazardous"

class EcologicalTracker:
    """Tracks ecological health metrics globally."""

    def __init__(self):
        self.biodiversity_records: Dict[str, List[BiodiversityIndex]] = {}
        self.water_records: Dict[str, List[WaterQuality]] = {}
        self.air_records: Dict[str, List[AirQuality]] = {}
        self.deforestation_alerts: List[dict] = []

    def record_biodiversity(self, bio: BiodiversityIndex) -> None:
        if bio.region not in self.biodiversity_records:
            self.biodiversity_records[bio.region] = []
        self.biodiversity_records[bio.region].append(bio)

    def record_water(self, wq: WaterQuality) -> None:
        if wq.location not in self.water_records:
            self.water_records[wq.location] = []
        self.water_records[wq.location].append(wq)

    def record_air(self, aq: AirQuality) -> None:
        if aq.location not in self.air_records:
            self.air_records[aq.location] = []
        self.air_records[aq.location].append(aq)

    def detect_deforestation(self, region: str, before_area: float,
                             after_area: float) -> Optional[dict]:
        """Detect deforestation from satellite imagery comparison."""
        loss = before_area - after_area
        if loss > 0.01:  # More than 1% loss
            alert = {
                "alert_id": hashlib.sha256(f"deforest:{region}:{time.time()}".encode()).hexdigest()[:16],
                "region": region,
                "area_lost_hectares": loss * 100,
                "percentage_lost": (loss / before_area) * 100,
                "severity": "critical" if loss > 0.1 else "high" if loss > 0.05 else "moderate",
                "timestamp": time.time(),
            }
            self.deforestation_alerts.append(alert)
            return alert
        return None

    def biodiversity_trend(self, region: str) -> str:
        records = self.biodiversity_records.get(region, [])
        if len(records) < 2:
            return "insufficient_data"
        recent = records[-1].index_score
        older = records[0].index_score
        delta = recent - older
        if delta > 5: return "improving"
        elif delta < -5: return "declining"
        return "stable"

    def global_health_score(self) -> float:
        """Composite global ecological health score 0-100."""
        bio_scores = [r.index_score for records in self.biodiversity_records.values()
                      for r in records[-1:]]
        water_scores = [r.quality_score for records in self.water_records.values()
                        for r in records[-1:]]
        air_scores = [100 - min(100, r.aqi / 5) for records in self.air_records.values()
                      for r in records[-1:]]
        all_scores = bio_scores + water_scores + air_scores
        return sum(all_scores) / max(1, len(all_scores))
