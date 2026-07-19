"""Domain Gateway — unified API for all cross-domain data sources."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
import time, hashlib

@dataclass
class DomainEvent:
    event_id: str
    domain: str  # weather, supply_chain, healthcare, agriculture, education
    event_type: str
    data: dict
    value_opportunities: List[dict] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

class DomainGateway:
    """
    Unified gateway for all cross-domain data sources.
    Routes events to appropriate bridges and collects value opportunities.
    """
    
    def __init__(self):
        self.bridges: Dict[str, object] = {}
        self.handlers: List[Callable] = []
        self.events: List[DomainEvent] = []
    
    def register_bridge(self, domain: str, bridge: object) -> None:
        self.bridges[domain] = bridge
    
    def on_event(self, handler: Callable) -> None:
        self.handlers.append(handler)
    
    def route(self, domain: str, raw_data: dict) -> DomainEvent:
        """Route raw data to appropriate domain bridge."""
        bridge = self.bridges.get(domain)
        if not bridge:
            raise ValueError(f"No bridge registered for domain: {domain}")
        
        # Ingest into domain-specific bridge
        ingested = bridge.ingest(raw_data)
        
        # Detect value opportunities
        detect_method = getattr(bridge, f"detect_{domain.split('_')[0]}_value", None)
        if not detect_method:
            # Try generic detection
            for attr in dir(bridge):
                if attr.startswith("detect_") and callable(getattr(bridge, attr)):
                    detect_method = getattr(bridge, attr)
                    break
        
        opportunities = []
        if detect_method:
            result = detect_method(ingested)
            if isinstance(result, dict):
                opportunities = result.get("opportunities", [result] if "category" in result else [])
        
        event = DomainEvent(
            event_id=hashlib.sha256(f"{domain}:{time.time()}".encode()).hexdigest()[:16],
            domain=domain,
            event_type=raw_data.get("type", "generic"),
            data=raw_data,
            value_opportunities=opportunities,
        )
        self.events.append(event)
        
        # Notify handlers
        for handler in self.handlers:
            handler(event)
        
        return event
    
    def stats(self) -> dict:
        by_domain = {}
        for e in self.events:
            by_domain[e.domain] = by_domain.get(e.domain, 0) + 1
        total_opportunities = sum(len(e.value_opportunities) for e in self.events)
        return {
            "total_events": len(self.events),
            "by_domain": by_domain,
            "total_value_opportunities": total_opportunities,
            "registered_bridges": list(self.bridges.keys()),
        }
