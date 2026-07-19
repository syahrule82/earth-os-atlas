"""Disaster Relief Protocol — HERMES-powered emergency resource allocation."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal
import time, hashlib

@dataclass
class DisasterEvent:
    event_id: str
    disaster_type: str  # earthquake, flood, wildfire, pandemic, famine
    region: str
    severity: float  # 0-1
    affected_population: int
    timestamp: float = field(default_factory=time.time)
    status: str = "active"  # active, responding, resolved

@dataclass
class ResourceAllocation:
    allocation_id: str
    disaster_id: str
    resource_type: str  # food, water, medical, shelter, compute
    amount: Decimal
    source: str
    destination: str
    priority: int  # 0=highest
    timestamp: float = field(default_factory=time.time)

class DisasterReliefProtocol:
    """
    HERMES-powered emergency resource allocation.
    
    When a disaster strikes:
    1. GAEA verifies the disaster via satellite/IoT
    2. HERMES routes available resources optimally
    3. PROMETHEUS validates allocations are fair
    4. CHRONOS predicts ongoing resource needs
    5. ATLAS mints emergency relief tokens (bypassing normal halving)
    """
    
    EMGENCY_MINT_MULTIPLIER = 3.0  # 3x normal minting rate for disaster relief
    
    def __init__(self):
        self.disasters: Dict[str, DisasterEvent] = {}
        self.allocations: List[ResourceAllocation] = []
    
    def declare_disaster(self, disaster_type: str, region: str,
                         severity: float, affected: int) -> DisasterEvent:
        """Declare a new disaster event."""
        event = DisasterEvent(
            event_id=hashlib.sha256(f"{disaster_type}:{region}:{time.time()}".encode()).hexdigest()[:16],
            disaster_type=disaster_type, region=region,
            severity=min(1.0, severity), affected_population=affected,
        )
        self.disasters[event.event_id] = event
        return event
    
    def allocate_resources(self, disaster_id: str, available: List[dict]) -> List[ResourceAllocation]:
        """Optimally allocate resources to affected regions."""
        disaster = self.disasters.get(disaster_id)
        if not disaster:
            return []
        
        allocations = []
        for resource in available:
            # Priority based on severity and scarcity
            priority = int((1 - disaster.severity) * 10)  # Higher severity = lower number = higher priority
            
            alloc = ResourceAllocation(
                allocation_id=hashlib.sha256(f"{disaster_id}:{resource['type']}:{time.time()}".encode()).hexdigest()[:16],
                disaster_id=disaster_id,
                resource_type=resource["type"],
                amount=Decimal(str(resource["amount"])),
                source=resource["source"],
                destination=disaster.region,
                priority=priority,
            )
            allocations.append(alloc)
            self.allocations.append(alloc)
        
        # Sort by priority
        allocations.sort(key=lambda a: a.priority)
        return allocations
    
    def emergency_mint(self, disaster_id: str, base_amount: Decimal) -> Decimal:
        """Mint emergency ATLAS for disaster relief."""
        disaster = self.disasters.get(disaster_id)
        if not disaster:
            return Decimal("0")
        emergency_amount = base_amount * Decimal(str(self.EMGENCY_MINT_MULTIPLIER))
        return emergency_amount
    
    def resolve_disaster(self, disaster_id: str) -> bool:
        disaster = self.disasters.get(disaster_id)
        if disaster:
            disaster.status = "resolved"
            return True
        return False
    
    def active_disasters(self) -> List[DisasterEvent]:
        return [d for d in self.disasters.values() if d.status == "active"]
    
    def stats(self) -> dict:
        return {
            "total_disasters": len(self.disasters),
            "active": len(self.active_disasters()),
            "total_allocations": len(self.allocations),
            "total_value_allocated": str(sum((a.amount for a in self.allocations), Decimal("0"))),
        }
