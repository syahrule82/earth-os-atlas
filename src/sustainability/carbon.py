"""Carbon Credit System — Tokenized carbon credits verified via GAEA."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional
import hashlib, time

@dataclass
class CarbonProject:
    """A carbon sequestration or reduction project."""
    project_id: str
    name: str
    project_type: str  # reforestation, direct_air_capture, renewable_energy, soil_carbon, ocean
    location: str  # ISO country code or coordinates
    area_hectares: float
    expected_tons_per_year: float
    verifier: str  # DID of verifying entity (GAEA)
    verification_sources: List[str]  # satellite, iot, drone, human_attestation
    start_date: float
    end_date: Optional[float] = None
    status: str = "pending"  # pending, verified, active, completed, revoked
    total_credits_issued: Decimal = Decimal("0")
    metadata: dict = field(default_factory=dict)

@dataclass
class CarbonCredit:
    """A single tokenized carbon credit (1 ton CO2e)."""
    credit_id: str
    project_id: str
    tons_co2e: Decimal
    vintage_year: int
    serial_number: str  # Unique serial per international registry
    owner: str
    verification_hash: str
    issued_at: float = field(default_factory=time.time)
    retired: bool = False
    retired_by: Optional[str] = None
    retired_at: Optional[float] = None
    price: Decimal = Decimal("25.0")  # ATLAS per ton

class CarbonCreditSystem:
    """
    Full carbon credit lifecycle: verification → issuance → trading → retirement.
    
    Verification chain:
    1. GAEA verifies project via satellite imagery + IoT sensors
    2. PROMETHEUS validates measurement data via consensus
    3. Credits are minted as ATLAS-backed tokens
    4. Credits can be traded or retired (burned to offset emissions)
    """

    def __init__(self):
        self.projects: Dict[str, CarbonProject] = {}
        self.credits: Dict[str, CarbonCredit] = {}
        self.transactions: List[dict] = []
        self.price_history: List[dict] = []
        self.current_price = Decimal("25.0")  # ATLAS per ton CO2e

    def register_project(self, project: CarbonProject) -> CarbonProject:
        self.projects[project.project_id] = project
        return project

    def verify_project(self, project_id: str, verifier: str,
                       sources: List[str]) -> bool:
        """Verify a carbon project via GAEA."""
        project = self.projects.get(project_id)
        if not project:
            return False
        if len(sources) < 2:  # Need at least 2 verification sources
            return False
        project.verifier = verifier
        project.verification_sources = sources
        project.status = "verified"
        return True

    def issue_credits(self, project_id: str, tons: Decimal,
                      owner: str) -> List[CarbonCredit]:
        """Issue carbon credits for a verified project."""
        project = self.projects.get(project_id)
        if not project or project.status != "verified":
            return []
        credits = []
        for i in range(int(tons)):
            credit = CarbonCredit(
                credit_id=hashlib.sha256(
                    f"{project_id}:{i}:{time.time()}".encode()
                ).hexdigest()[:16],
                project_id=project_id,
                tons_co2e=Decimal("1"),
                vintage_year=time.localtime().tm_year,
                serial_number=f"ATLAS-{project_id}-{i:06d}",
                owner=owner,
                verification_hash=hashlib.sha256(
                    f"{project.verifier}:{project.verification_sources}".encode()
                ).hexdigest()[:32],
                price=self.current_price,
            )
            self.credits[credit.credit_id] = credit
            credits.append(credit)
        project.total_credits_issued += tons
        project.status = "active"
        return credits

    def transfer_credit(self, credit_id: str, new_owner: str) -> bool:
        credit = self.credits.get(credit_id)
        if not credit or credit.retired:
            return False
        old_owner = credit.owner
        credit.owner = new_owner
        self.transactions.append({
            "type": "transfer", "credit_id": credit_id,
            "from": old_owner, "to": new_owner,
            "price": str(credit.price), "timestamp": time.time(),
        })
        return True

    def retire_credit(self, credit_id: str, retired_by: str) -> bool:
        """Retire (burn) a carbon credit to offset emissions."""
        credit = self.credits.get(credit_id)
        if not credit or credit.retired:
            return False
        credit.retired = True
        credit.retired_by = retired_by
        credit.retired_at = time.time()
        self.transactions.append({
            "type": "retirement", "credit_id": credit_id,
            "by": retired_by, "tons": str(credit.tons_co2e),
            "timestamp": time.time(),
        })
        return True

    def update_price(self, demand: Decimal, supply: Decimal) -> Decimal:
        """Dynamic carbon credit pricing based on supply/demand."""
        if supply <= 0:
            self.current_price = Decimal("100.0")  # Scarcity
        else:
            ratio = float(demand / supply)
            if ratio > 1.5:
                self.current_price = Decimal("45.0")
            elif ratio > 1.0:
                self.current_price = Decimal("35.0")
            elif ratio > 0.5:
                self.current_price = Decimal("25.0")
            else:
                self.current_price = Decimal("15.0")
        self.price_history.append({
            "price": str(self.current_price),
            "demand": str(demand), "supply": str(supply),
            "timestamp": time.time(),
        })
        return self.current_price

    def carbon_balance(self, address: str) -> dict:
        """Calculate net carbon footprint for an address."""
        owned = [c for c in self.credits.values() if c.owner == address and not c.retired]
        retired = [c for c in self.credits.values() if c.retired_by == address]
        credits_owned = sum((c.tons_co2e for c in owned), Decimal("0"))
        credits_retired = sum((c.tons_co2e for c in retired), Decimal("0"))
        return {
            "address": address,
            "credits_owned": str(credits_owned),
            "credits_retired": str(credits_retired),
            "net_offset_tons": str(credits_retired),
        }

    def stats(self) -> dict:
        active = [c for c in self.credits.values() if not c.retired]
        retired = [c for c in self.credits.values() if c.retired]
        return {
            "total_projects": len(self.projects),
            "verified_projects": sum(1 for p in self.projects.values() if p.status in ("verified", "active")),
            "total_credits": len(self.credits),
            "active_credits": len(active),
            "retired_credits": len(retired),
            "total_tons_retired": str(sum((c.tons_co2e for c in retired), Decimal("0"))),
            "current_price": str(self.current_price),
        }
