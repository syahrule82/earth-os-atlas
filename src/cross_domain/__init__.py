"""Cross-Domain Integration — bridges to real-world data sources."""
from .weather import WeatherBridge, WeatherEvent
from .supply_chain import SupplyChainBridge, ShipmentEvent
from .healthcare import HealthcareBridge, HealthOutcome
from .agriculture import AgricultureBridge, CropYield
from .education import EducationBridge, LearningRecord
from .gateway import DomainGateway, DomainEvent

__all__ = ["WeatherBridge", "WeatherEvent",
           "SupplyChainBridge", "ShipmentEvent",
           "HealthcareBridge", "HealthOutcome",
           "AgricultureBridge", "CropYield",
           "EducationBridge", "LearningRecord",
           "DomainGateway", "DomainEvent"]
