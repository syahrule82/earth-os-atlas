"""Synaptic Mesh tests"""
from src.synaptic_mesh.thought_packet import ThoughtPacket, PacketPriority
from src.synaptic_mesh.neural_address import NeuralAddress
from src.synaptic_mesh.mesh_router import MeshRouter
import time

def test_neural_address():
    addr = NeuralAddress("global", "prefrontal", "node_7f3a", "pni-v3")
    full = addr.full_address
    assert full.startswith("neural://")
    recovered = NeuralAddress.from_string(full)
    assert recovered == addr

def test_thought_packet():
    pkt = ThoughtPacket(
        packet_id="pkt_001", source_address="neural://g/pfc/a/pni",
        destination_address="neural://g/motor/b/pni",
        payload_hash="abc123", priority=PacketPriority.NORMAL,
        cognitive_signature="sig_x", timestamp_ns=time.time_ns(), ttl=8
    )
    assert not pkt.is_expired(max_age_ms=5000)

def test_mesh_routing():
    router = MeshRouter(max_hops=8)
    router.add_route("A", ["B", "C"], [5.0, 10.0])
    router.add_route("B", ["D"], [3.0])
    path = router.find_path("A", "D")
    assert path == ["A", "B", "D"]
