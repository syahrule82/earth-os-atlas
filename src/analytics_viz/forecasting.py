"""Economic Forecaster — CHRONOS-powered predictions and stress tests."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np, time

@dataclass
class ForecastScenario:
    """A single economic forecast scenario."""
    scenario_name: str  # bull, base, bear
    horizons: List[int]  # days ahead
    predictions: List[float]
    confidence_lower: List[float]
    confidence_upper: List[float]
    assumptions: Dict[str, float] = field(default_factory=dict)

@dataclass
class StressTestResult:
    """Result of an economic stress test."""
    test_name: str
    shock_type: str  # supply_shock, demand_collapse, validator_exit, liquidity_crisis
    pre_shock_metrics: Dict[str, float]
    post_shock_metrics: Dict[str, float]
    recovery_time_days: int
    severity: str  # minor, moderate, severe, critical
    passed: bool  # Whether system remained functional

class EconomicForecaster:
    """
    Economic forecasting powered by CHRONOS Titan.
    Provides multi-scenario predictions and stress testing.
    """

    def __init__(self):
        self.forecasts: List[ForecastScenario] = []
        self.stress_tests: List[StressTestResult] = []
        self.historical_data: List[dict] = []

    def record_data(self, metrics: dict) -> None:
        """Record historical economic data for forecasting."""
        self.historical_data.append({**metrics, "timestamp": time.time()})
        if len(self.historical_data) > 10000:
            self.historical_data = self.historical_data[-10000:]

    def forecast(self, variable: str, current_value: float,
                 horizons: List[int] = None) -> List[ForecastScenario]:
        """Generate multi-scenario forecasts."""
        if horizons is None:
            horizons = [1, 7, 30, 90, 365]

        scenarios = []

        # Base case: slight growth with noise
        base_preds = [current_value * (1.02 ** (h / 365)) for h in horizons]
        base_lower = [p * 0.9 for p in base_preds]
        base_upper = [p * 1.1 for p in base_preds]
        scenarios.append(ForecastScenario(
            scenario_name="base",
            horizons=horizons,
            predictions=base_preds,
            confidence_lower=base_lower,
            confidence_upper=base_upper,
            assumptions={"growth_rate": 0.02, "volatility": 0.1},
        ))

        # Bull case: strong growth
        bull_preds = [current_value * (1.15 ** (h / 365)) for h in horizons]
        bull_lower = [p * 0.85 for p in bull_preds]
        bull_upper = [p * 1.15 for p in bull_preds]
        scenarios.append(ForecastScenario(
            scenario_name="bull",
            horizons=horizons,
            predictions=bull_preds,
            confidence_lower=bull_lower,
            confidence_upper=bull_upper,
            assumptions={"growth_rate": 0.15, "volatility": 0.15},
        ))

        # Bear case: decline
        bear_preds = [current_value * (0.90 ** (h / 365)) for h in horizons]
        bear_lower = [p * 0.8 for p in bear_preds]
        bear_upper = [p * 1.05 for p in bear_preds]
        scenarios.append(ForecastScenario(
            scenario_name="bear",
            horizons=horizons,
            predictions=bear_preds,
            confidence_lower=bear_lower,
            confidence_upper=bear_upper,
            assumptions={"growth_rate": -0.10, "volatility": 0.2},
        ))

        self.forecasts.extend(scenarios)
        return scenarios

    def stress_test(self, test_name: str, shock_type: str,
                    pre_metrics: Dict[str, float]) -> StressTestResult:
        """Run an economic stress test."""
        post_metrics = dict(pre_metrics)
        recovery_days = 7

        if shock_type == "supply_shock":
            post_metrics["supply"] *= 0.5
            post_metrics["price"] *= 2.0
            recovery_days = 30
            severity = "severe"
        elif shock_type == "demand_collapse":
            post_metrics["velocity"] *= 0.3
            post_metrics["price"] *= 0.6
            recovery_days = 60
            severity = "critical"
        elif shock_type == "validator_exit":
            post_metrics["validators"] = max(1, int(post_metrics.get("validators", 10) * 0.7))
            post_metrics["consensus_latency"] *= 3
            recovery_days = 14
            severity = "moderate"
        elif shock_type == "liquidity_crisis":
            post_metrics["liquidity"] *= 0.2
            post_metrics["slippage"] *= 5
            recovery_days = 21
            severity = "severe"
        else:
            severity = "minor"
            recovery_days = 3

        # System passes if it doesn't completely collapse
        passed = (post_metrics.get("supply", 0) > 0 and
                  post_metrics.get("validators", 0) > 0)

        result = StressTestResult(
            test_name=test_name,
            shock_type=shock_type,
            pre_shock_metrics=pre_metrics,
            post_shock_metrics=post_metrics,
            recovery_time_days=recovery_days,
            severity=severity,
            passed=passed,
        )
        self.stress_tests.append(result)
        return result

    def get_forecast(self, variable: str, scenario: str = "base") -> Optional[ForecastScenario]:
        """Get the latest forecast for a variable and scenario."""
        matching = [f for f in self.forecasts if f.scenario_name == scenario]
        return matching[-1] if matching else None

    def summary(self) -> dict:
        return {
            "total_forecasts": len(self.forecasts),
            "total_stress_tests": len(self.stress_tests),
            "stress_tests_passed": sum(1 for s in self.stress_tests if s.passed),
            "stress_tests_failed": sum(1 for s in self.stress_tests if not s.passed),
            "data_points": len(self.historical_data),
        }
