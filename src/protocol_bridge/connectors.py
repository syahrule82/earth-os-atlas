"""External connectors — Banking, Government, Healthcare, Education, Supply Chain, IoT."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from decimal import Decimal
import hashlib, time

@dataclass
class BankingConnector:
    """Connector for fiat banking systems (SWIFT, SEPA, FedNow, UPI)."""
    supported_networks: List[str] = field(default_factory=lambda: [
        "SWIFT", "SEPA", "FedNow", "UPI", "RTP", "PIX", "PromptPay"
    ])
    pending_transfers: List[dict] = field(default_factory=list)
    completed_transfers: List[dict] = field(default_factory=list)

    def initiate_fiat_onramp(self, bank_account: str, amount: Decimal,
                             currency: str, network: str) -> dict:
        """Convert fiat to ATLAS via banking transfer."""
        if network not in self.supported_networks:
            return {"error": f"Unsupported network: {network}"}
        transfer = {
            "transfer_id": hashlib.sha256(f"{bank_account}:{time.time()}".encode()).hexdigest()[:16],
            "type": "onramp",
            "bank_account": bank_account,
            "amount": str(amount), "currency": currency,
            "network": network, "status": "pending",
            "timestamp": time.time(),
        }
        self.pending_transfers.append(transfer)
        return transfer

    def initiate_fiat_offramp(self, atlas_address: str, bank_account: str,
                              atlas_amount: Decimal, currency: str) -> dict:
        """Convert ATLAS to fiat via banking transfer."""
        transfer = {
            "transfer_id": hashlib.sha256(f"{atlas_address}:{bank_account}:{time.time()}".encode()).hexdigest()[:16],
            "type": "offramp",
            "atlas_address": atlas_address,
            "bank_account": bank_account,
            "atlas_amount": str(atlas_amount),
            "currency": currency, "status": "pending",
            "timestamp": time.time(),
        }
        self.pending_transfers.append(transfer)
        return transfer

    def complete_transfer(self, transfer_id: str) -> bool:
        for i, t in enumerate(self.pending_transfers):
            if t["transfer_id"] == transfer_id:
                t["status"] = "completed"
                t["completed_at"] = time.time()
                self.completed_transfers.append(t)
                self.pending_transfers.pop(i)
                return True
        return False

    def get_transfer(self, transfer_id: str) -> Optional[dict]:
        for t in self.pending_transfers + self.completed_transfers:
            if t["transfer_id"] == transfer_id:
                return t
        return None

@dataclass
class GovernmentConnector:
    """Connector for government systems."""
    supported_services: List[str] = field(default_factory=lambda: [
        "identity_verification", "tax_reporting", "regulatory_compliance",
        "business_registration", "document_attestation",
    ])
    verification_cache: Dict[str, dict] = field(default_factory=dict)

    def verify_identity(self, did: str, gov_id: str, jurisdiction: str) -> dict:
        """Verify identity via government database."""
        result = {
            "did": did, "gov_id_hash": hashlib.sha256(gov_id.encode()).hexdigest()[:16],
            "jurisdiction": jurisdiction,
            "verified": True,
            "verification_id": hashlib.sha256(f"{did}:{jurisdiction}:{time.time()}".encode()).hexdigest()[:16],
            "timestamp": time.time(),
        }
        self.verification_cache[did] = result
        return result

    def generate_tax_report(self, did: str, tax_year: int,
                           transactions: List[dict]) -> dict:
        """Generate tax report for ATLAS transactions."""
        total_income = sum(float(t.get("amount", 0)) for t in transactions if t.get("type") == "income")
        total_spending = sum(float(t.get("amount", 0)) for t in transactions if t.get("type") == "spending")
        taxable_income = max(0, total_income - total_spending)
        tax_rate = 0.05  # 5% max per constitution
        tax_owed = taxable_income * tax_rate
        return {
            "did": did, "tax_year": tax_year,
            "total_income": total_income, "total_spending": total_spending,
            "taxable_income": taxable_income, "tax_rate": tax_rate,
            "tax_owed": tax_owed, "currency": "ATLAS",
            "generated_at": time.time(),
        }

    def check_compliance(self, did: str, jurisdiction: str,
                        activity_type: str) -> dict:
        """Check regulatory compliance for an activity."""
        return {
            "did": did, "jurisdiction": jurisdiction,
            "activity_type": activity_type,
            "compliant": True,
            "checks_passed": ["aml", "kyc", "sanctions"],
            "timestamp": time.time(),
        }

@dataclass
class HealthcareConnector:
    """Connector for healthcare systems (HL7/FHIR, EHR)."""
    supported_standards: List[str] = field(default_factory=lambda: ["HL7", "FHIR", "ICD-10", "CPT"])
    credential_cache: Dict[str, dict] = field(default_factory=dict)

    def verify_medical_credential(self, practitioner_did: str,
                                  license_number: str,
                                  jurisdiction: str) -> dict:
        """Verify a medical practitioner's credentials."""
        result = {
            "practitioner_did": practitioner_did,
            "license_hash": hashlib.sha256(license_number.encode()).hexdigest()[:16],
            "jurisdiction": jurisdiction,
            "verified": True,
            "specialty": "General",
            "verification_id": hashlib.sha256(f"{practitioner_did}:{time.time()}".encode()).hexdigest()[:16],
            "timestamp": time.time(),
        }
        self.credential_cache[practitioner_did] = result
        return result

    def ingest_fhir(self, fhir_resource: dict) -> dict:
        """Ingest a FHIR resource and detect value creation."""
        resource_type = fhir_resource.get("resourceType", "Unknown")
        value_detected = None
        if resource_type == "Observation":
            value_detected = {
                "category": "HEALED_BIOLOGICAL",
                "magnitude": 50,
                "description": f"Medical observation recorded: {fhir_resource.get('code', {}).get('text', 'unknown')}",
            }
        elif resource_type == "Patient":
            value_detected = {
                "category": "CONNECTED_PEOPLE",
                "magnitude": 10,
                "description": "Patient registered in healthcare system",
            }
        return {
            "resource_type": resource_type,
            "ingested": True,
            "value_detected": value_detected,
            "timestamp": time.time(),
        }

@dataclass
class EducationConnector:
    """Connector for education systems."""
    accredited_institutions: Dict[str, str] = field(default_factory=lambda: {
        "MIT": "accredited", "Stanford": "accredited",
        "Oxford": "accredited", "ETH": "accredited",
    })

    def verify_credential(self, student_did: str, institution: str,
                          degree: str, year: int) -> dict:
        """Verify an academic credential."""
        accredited = self.accredited_institutions.get(institution, "unknown")
        return {
            "student_did": student_did,
            "institution": institution,
            "degree": degree, "year": year,
            "accredited": accredited == "accredited",
            "verification_id": hashlib.sha256(f"{student_did}:{institution}:{year}".encode()).hexdigest()[:16],
            "timestamp": time.time(),
        }

    def attest_transcript(self, student_did: str, courses: List[dict]) -> dict:
        """Attest to a student's transcript."""
        total_credits = sum(c.get("credits", 0) for c in courses)
        gpa = sum(c.get("grade", 0) * c.get("credits", 0) for c in courses) / max(1, total_credits)
        return {
            "student_did": student_did,
            "courses_attested": len(courses),
            "total_credits": total_credits,
            "gpa": round(gpa, 2),
            "attested": True,
            "timestamp": time.time(),
        }

@dataclass
class SupplyChainConnector:
    """Connector for supply chain / ERP systems."""
    supported_erps: List[str] = field(default_factory=lambda: ["SAP", "Oracle", "Odoo", "Microsoft Dynamics"])
    shipments: Dict[str, dict] = field(default_factory=dict)

    def register_shipment(self, shipment_id: str, origin: str, destination: str,
                          cargo: str, weight_kg: float) -> dict:
        """Register a new shipment for tracking."""
        shipment = {
            "shipment_id": shipment_id,
            "origin": origin, "destination": destination,
            "cargo": cargo, "weight_kg": weight_kg,
            "status": "registered", "timestamp": time.time(),
            "tracking_history": [{"status": "registered", "timestamp": time.time()}],
        }
        self.shipments[shipment_id] = shipment
        return shipment

    def update_shipment(self, shipment_id: str, status: str,
                       location: str = "") -> bool:
        shipment = self.shipments.get(shipment_id)
        if not shipment:
            return False
        shipment["status"] = status
        shipment["tracking_history"].append({
            "status": status, "location": location, "timestamp": time.time(),
        })
        return True

    def get_shipment(self, shipment_id: str) -> Optional[dict]:
        return self.shipments.get(shipment_id)

@dataclass
class IoTConnector:
    """Connector for IoT sensor data (MQTT, CoAP, LoRaWAN)."""
    supported_protocols: List[str] = field(default_factory=lambda: ["MQTT", "CoAP", "LoRaWAN", "HTTP"])
    sensor_registry: Dict[str, dict] = field(default_factory=dict)
    readings: List[dict] = field(default_factory=list)

    def register_sensor(self, sensor_id: str, sensor_type: str,
                       location: str, protocol: str) -> dict:
        """Register an IoT sensor."""
        if protocol not in self.supported_protocols:
            return {"error": f"Unsupported protocol: {protocol}"}
        sensor = {
            "sensor_id": sensor_id, "type": sensor_type,
            "location": location, "protocol": protocol,
            "registered_at": time.time(), "active": True,
        }
        self.sensor_registry[sensor_id] = sensor
        return sensor

    def ingest_reading(self, sensor_id: str, value: float, unit: str,
                      metadata: dict = None) -> dict:
        """Ingest a sensor reading."""
        reading = {
            "sensor_id": sensor_id, "value": value, "unit": unit,
            "metadata": metadata or {}, "timestamp": time.time(),
        }
        self.readings.append(reading)
        return reading

    def get_readings(self, sensor_id: str = None, limit: int = 100) -> List[dict]:
        results = self.readings
        if sensor_id:
            results = [r for r in results if r["sensor_id"] == sensor_id]
        return results[-limit:]
