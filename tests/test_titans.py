"""Titan Agent tests"""
from src.titans.hermes import HermesAgent
from src.titans.prometheus import PrometheusAgent
from src.titans.gaea import GaeaAgent
from src.titans.chronos import ChronosAgent

def test_hermes_scan():
    h = HermesAgent()
    signals = h.scan(20)
    assert len(signals) == 20
    assert all(0 < s.confidence <= 1.0 for s in signals)

def test_prometheus_consensus():
    p = PrometheusAgent(min_voters=3, threshold=0.67)
    for i in range(5):
        p.register_voter(f"v{i}", 1.0)
    votes = {f"v{i}": (i < 4) for i in range(5)}
    r = p.form_consensus("claim_001", votes)
    assert r.result is True

def test_gaea_verify():
    g = GaeaAgent()
    truth = g.verify("Rice price in Papua = $1.20/kg", ["satellite", "iot_sensor"])
    assert truth.confidence > 0

def test_chronos_forecast():
    c = ChronosAgent()
    fc = c.forecast("atlas_price", 1.0, horizons=[1, 7, 30])
    assert len(fc.predictions) == 3
    assert len(fc.ci_lower) == 3
