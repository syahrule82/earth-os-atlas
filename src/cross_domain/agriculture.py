"""Agriculture bridge — crop yield and food security value."""
from dataclasses import dataclass, field
from typing import Dict
import time

@dataclass
class CropYield:
    yield_id: str
    crop_type: str
    region: str
    hectares: float
    tons_harvested: float
    water_used_liters: float
    timestamp: float = field(default_factory=time.time)

class AgricultureBridge:
    """Tracks agricultural output for value detection."""
    
    def __init__(self):
        self.yields: list = []
    
    def ingest(self, data: dict) -> CropYield:
        record = CropYield(
            yield_id=f"crop_{int(time.time() * 1000)}",
            crop_type=data.get("crop_type", "unknown"),
            region=data.get("region", "unknown"),
            hectares=float(data.get("hectares", 0)),
            tons_harvested=float(data.get("tons_harvested", 0)),
            water_used_liters=float(data.get("water_used_liters", 0)),
        )
        self.yields.append(record)
        return record
    
    def detect_agricultural_value(self, record: CropYield) -> Dict:
        """Detect agricultural and ecological value."""
        opportunities = []
        
        # Food production value
        yield_per_hectare = record.tons_harvested / max(1, record.hectares)
        if yield_per_hectare > 5:  # Good yield
            opportunities.append({
                "category": "BUILT_INFRASTRUCTURE",
                "magnitude": yield_per_hectare * 10,
                "description": f"Efficient {record.crop_type} production",
            })
        
        # Water efficiency (ecological)
        water_per_ton = record.water_used_liters / max(1, record.tons_harvested)
        if water_per_ton > 0 and water_per_ton < 500:  # Efficient water use
            opportunities.append({
                "category": "RESTORED_ECOLOGICAL",
                "magnitude": (500 - water_per_ton) / 10,
                "description": f"Water-efficient agriculture",
            })
        
        return {"yield": record.yield_id, "opportunities": opportunities}
