"""Phase 14 integration tests."""
from decimal import Decimal
from src.protocol_bridge.gateway import UniversalGateway, GatewayRoute, APIKey
from src.protocol_bridge.connectors import (BankingConnector, GovernmentConnector,
    HealthcareConnector, EducationConnector, SupplyChainConnector, IoTConnector)
from src.protocol_bridge.webhooks import WebhookSystem, WebhookEvent
from src.protocol_bridge.sdk_gen import SDKAutoGenerator
from src.protocol_bridge.adapters import LegacyAdapter, RESTAdapter
from src.protocol_bridge.normalizer import DataNormalizer, SchemaMapper
import time

def test_universal_gateway():
    gw = UniversalGateway()
    # Register a banking connector
    banking = BankingConnector()
    gw.register_connector("banking", banking)
    # Register a route
    route = GatewayRoute(
        route_id="r1", path="/v1/banking/onramp", method="POST",
        connector="banking", handler="initiate_fiat_onramp",
        required_scopes=["banking:write"],
    )
    gw.register_route(route)
    # Create API key
    key_id, raw_key = gw.create_api_key("did:atlas:alice", ["banking:write"], rate_limit=10)
    assert key_id is not None
    # Authenticate
    api_key = gw.authenticate(raw_key)
    assert api_key is not None
    assert api_key.consumer_did == "did:atlas:alice"
    # Route request
    result = gw.route_request("POST", "/v1/banking/onramp", api_key,
                              body={"bank_account": "12345", "amount": "100", "currency": "USD", "network": "SWIFT"})
    assert result["status"] == 200
    # Rate limit
    for _ in range(10):
        gw.route_request("POST", "/v1/banking/onramp", api_key, body={"bank_account": "12345", "amount": "100", "currency": "USD", "network": "SWIFT"})
    result = gw.route_request("POST", "/v1/banking/onramp", api_key, body={})
    assert result["status"] == 429  # Rate limited
    stats = gw.stats()
    assert stats["total_routes"] == 1

def test_banking_connector():
    banking = BankingConnector()
    # Onramp
    transfer = banking.initiate_fiat_onramp("acct_123", Decimal("1000"), "USD", "SWIFT")
    assert transfer["status"] == "pending"
    assert transfer["type"] == "onramp"
    # Complete
    assert banking.complete_transfer(transfer["transfer_id"])
    assert transfer["status"] == "completed"
    # Offramp
    offramp = banking.initiate_fiat_offramp("did:atlas:alice", "acct_456", Decimal("500"), "EUR")
    assert offramp["type"] == "offramp"

def test_government_connector():
    gov = GovernmentConnector()
    # Identity verification
    verification = gov.verify_identity("did:atlas:alice", "ID123456", "ID")
    assert verification["verified"] is True
    # Tax report
    transactions = [
        {"type": "income", "amount": 1000},
        {"type": "spending", "amount": 300},
    ]
    tax = gov.generate_tax_report("did:atlas:alice", 2026, transactions)
    assert tax["taxable_income"] == 700
    assert tax["tax_owed"] == 35  # 5% of 700
    # Compliance
    compliance = gov.check_compliance("did:atlas:alice", "ID", "transfer")
    assert compliance["compliant"] is True

def test_healthcare_connector():
    hc = HealthcareConnector()
    # Credential verification
    cred = hc.verify_medical_credential("did:atlas:doctor", "MD12345", "US")
    assert cred["verified"] is True
    # FHIR ingestion
    fhir_result = hc.ingest_fhir({"resourceType": "Observation", "code": {"text": "Blood Pressure"}})
    assert fhir_result["ingested"] is True
    assert fhir_result["value_detected"]["category"] == "HEALED_BIOLOGICAL"

def test_education_connector():
    edu = EducationConnector()
    # Credential verification
    cred = edu.verify_credential("did:atlas:student", "MIT", "PhD Computer Science", 2026)
    assert cred["accredited"] is True
    # Transcript attestation
    courses = [{"course": "CS101", "credits": 4, "grade": 4.0},
               {"course": "CS102", "credits": 3, "grade": 3.7}]
    transcript = edu.attest_transcript("did:atlas:student", courses)
    assert transcript["total_credits"] == 7
    assert transcript["gpa"] > 3.5

def test_supply_chain_connector():
    sc = SupplyChainConnector()
    # Register shipment
    shipment = sc.register_shipment("ship_001", "Jakarta", "Tokyo", "Electronics", 500)
    assert shipment["status"] == "registered"
    # Update
    sc.update_shipment("ship_001", "in_transit", "Singapore")
    sc.update_shipment("ship_001", "delivered", "Tokyo")
    updated = sc.get_shipment("ship_001")
    assert updated["status"] == "delivered"
    assert len(updated["tracking_history"]) == 3

def test_iot_connector():
    iot = IoTConnector()
    # Register sensor
    sensor = iot.register_sensor("sensor_001", "temperature", "Jakarta", "MQTT")
    assert sensor["active"] is True
    # Ingest readings
    for i in range(5):
        iot.ingest_reading("sensor_001", 25 + i, "celsius")
    readings = iot.get_readings("sensor_001")
    assert len(readings) == 5
    assert readings[-1]["value"] == 29

def test_webhook_system():
    wh = WebhookSystem()
    # Subscribe
    sub = wh.subscribe("did:atlas:alice", "https://example.com/webhook",
                       ["proof.created", "atlas.minted"])
    assert sub.active is True
    # Emit event
    events = wh.emit("proof.created", {"proof_id": "proof_123", "value": 100})
    assert len(events) == 1
    assert events[0].event_type == "proof.created"
    # Deliver
    assert wh.deliver(events[0])
    assert events[0].delivered is True
    # Stats
    stats = wh.stats()
    assert stats["delivered_events"] == 1
    # Unsubscribe
    assert wh.unsubscribe(sub.subscription_id)
    assert not sub.active

def test_sdk_auto_generator():
    gen = SDKAutoGenerator()
    # Generate Python SDK
    python_sdk = gen.generate("python")
    assert "class AtlasClient" in python_sdk
    assert "def " in python_sdk
    # Generate TypeScript SDK
    ts_sdk = gen.generate("typescript")
    assert "export class AtlasClient" in ts_sdk
    # Generate Rust SDK
    rust_sdk = gen.generate("rust")
    assert "pub struct AtlasClient" in rust_sdk
    # Generate Go SDK
    go_sdk = gen.generate("go")
    assert "type Client struct" in go_sdk
    # Get OpenAPI spec
    spec = gen.get_openapi_json()
    assert '"openapi"' in spec
    assert len(gen.spec.endpoints) >= 5

def test_protocol_adapters():
    # Legacy adapter
    legacy = LegacyAdapter()
    adapted = legacy.adapt_inbound({"format": "SOAP", "data": "test"})
    assert adapted["atlas_event"] is True
    outbound = legacy.adapt_outbound({"event": "test"})
    assert outbound["format"] == "legacy"
    # REST adapter
    rest = RESTAdapter(base_url="https://api.example.com")
    adapted = rest.adapt_inbound({"data": "test"})
    assert adapted["source"] == "rest"
    outbound = rest.adapt_outbound({"event": "test"})
    assert outbound["method"] == "POST"

def test_data_normalizer():
    normalizer = DataNormalizer()
    # Register mapper
    mapper = SchemaMapper(
        mapping_name="banking",
        source_schema={"account_number": "bank_account", "amount_cents": "amount", "customer_id": "did"},
        transformations={"amount_cents": "to_decimal", "customer_id": "to_did"},
    )
    normalizer.register_mapper(mapper)
    # Normalize
    data = {"account_number": "12345", "amount_cents": 10000, "customer_id": "alice"}
    normalized = normalizer.normalize(data, "banking")
    assert normalized["bank_account"] == "12345"
    assert normalized["amount"] == "10000"
    assert normalized["did"].startswith("did:atlas:")
    # Currency conversion
    usd = normalizer.convert_currency(100, "EUR", "USD")
    assert usd > 100  # EUR > USD
    # Unit conversion
    grams = normalizer.convert_unit(5, "kg_to_g")
    assert grams == 5000
    # Address normalization
    did = normalizer.normalize_address("alice")
    assert did == "did:atlas:alice"

if __name__ == "__main__":
    test_universal_gateway()
    test_banking_connector()
    test_government_connector()
    test_healthcare_connector()
    test_education_connector()
    test_supply_chain_connector()
    test_iot_connector()
    test_webhook_system()
    test_sdk_auto_generator()
    test_protocol_adapters()
    test_data_normalizer()
    print("✅ All Phase 14 tests passed")
