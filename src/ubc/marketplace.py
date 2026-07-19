"""Compute marketplace — buy/sell computation on the nanite mesh."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional
import time, hashlib

@dataclass
class ComputeOffer:
    offer_id:     str
    provider:     str
    compute_flops: float  # available FLOPS
    price_per_hour: Decimal  # ATLAS per hour
    region:       str
    uptime_guarantee: float
    trust_score:  float
    created_at:   float = field(default_factory=time.time)

@dataclass
class ComputeRequest:
    request_id:   str
    requester:    str
    required_flops: float
    max_budget:   Decimal
    duration_hours: float
    deadline:     float
    region_pref:  Optional[str] = None
    created_at:   float = field(default_factory=time.time)

@dataclass
class ComputeMatch:
    match_id:     str
    offer:        ComputeOffer
    request:      ComputeRequest
    total_cost:   Decimal
    timestamp:    float = field(default_factory=time.time)

class ComputeMarketplace:
    """Marketplace for matching compute supply with demand."""

    def __init__(self):
        self.offers: Dict[str, ComputeOffer] = {}
        self.requests: Dict[str, ComputeRequest] = {}
        self.matches: List[ComputeMatch] = []

    def list_offer(self, offer: ComputeOffer) -> None:
        self.offers[offer.offer_id] = offer

    def submit_request(self, request: ComputeRequest) -> List[ComputeMatch]:
        """Match a compute request with available offers."""
        matches = []
        for offer in self.offers.values():
            if offer.compute_flops >= request.required_flops:
                cost = offer.price_per_hour * Decimal(str(request.duration_hours))
                if cost <= request.max_budget:
                    if not request.region_pref or offer.region == request.region_pref:
                        match = ComputeMatch(
                            match_id=hashlib.sha256(
                                f"{offer.offer_id}:{request.request_id}:{time.time()}".encode()
                            ).hexdigest()[:16],
                            offer=offer,
                            request=request,
                            total_cost=cost,
                        )
                        matches.append(match)
                        self.matches.append(match)
        return sorted(matches, key=lambda m: m.total_cost)[:5]

    def get_stats(self) -> dict:
        total_flops = sum(o.compute_flops for o in self.offers.values())
        avg_price = (
            sum(o.price_per_hour for o in self.offers.values()) / len(self.offers)
            if self.offers else Decimal("0")
        )
        return {
            "total_offers": len(self.offers),
            "total_flops_available": total_flops,
            "avg_price_per_hour": str(avg_price),
            "total_matches": len(self.matches),
        }
