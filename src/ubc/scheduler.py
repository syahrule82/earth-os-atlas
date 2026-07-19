"""UBS Scheduler — allocates compute resources fairly."""
from dataclasses import dataclass, field
from typing import Dict, List
from decimal import Decimal
import time

@dataclass
class ComputeAllocation:
    allocation_id: str
    provider:      str
    requester:     str
    flops:         float
    cost:          Decimal
    start_time:    float
    end_time:      float
    status:        str = "pending"  # pending, running, completed, failed

class UBSScheduler:
    """Universal Basic Compute scheduler with fair allocation."""

    def __init__(self, basic_allocation_flops: float = 1e9):
        self.basic_flops = basic_allocation_flops  # 1 GFLOPS free for every identity
        self.allocations: Dict[str, ComputeAllocation] = {}
        self.usage_history: Dict[str, List[dict]] = {}

    def allocate_basic(self, identity: str) -> ComputeAllocation:
        """Allocate universal basic compute to every identity."""
        alloc = ComputeAllocation(
            allocation_id=f"ubc_{identity}_{int(time.time())}",
            provider="nanite_mesh",
            requester=identity,
            flops=self.basic_flops,
            cost=Decimal("0"),  # Free
            start_time=time.time(),
            end_time=time.time() + 3600,  # 1 hour
            status="running",
        )
        self.allocations[alloc.allocation_id] = alloc
        return alloc

    def allocate_premium(self, identity: str, flops: float, cost: Decimal) -> ComputeAllocation:
        """Allocate additional compute for ATLAS payment."""
        alloc = ComputeAllocation(
            allocation_id=f"prem_{identity}_{int(time.time())}",
            provider="nanite_mesh",
            requester=identity,
            flops=flops,
            cost=cost,
            start_time=time.time(),
            end_time=time.time() + 3600,
            status="running",
        )
        self.allocations[alloc.allocation_id] = alloc
        return alloc

    def get_utilization(self) -> dict:
        active = [a for a in self.allocations.values() if a.status == "running"]
        return {
            "active_allocations": len(active),
            "total_flops_allocated": sum(a.flops for a in active),
            "basic_users": sum(1 for a in active if a.cost == 0),
            "premium_users": sum(1 for a in active if a.cost > 0),
        }
