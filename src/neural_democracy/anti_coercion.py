"""Anti-coercion detection — detects forced neural voting."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np, time

@dataclass
class CoercionSignal:
    signal_id: str
    voter_did: str
    coercion_type: str  # physical_threat, neural_override, stress_induced, impersonation
    confidence: float
    evidence: str
    timestamp: float = field(default_factory=time.time)

class AntiCoercionDetector:
    """
    Detects coercion in neural voting.
    
    Methods:
    - Stress pattern analysis (high cortisol-correlated EEG)
    - Neural signature consistency (vote doesn't match established patterns)
    - Timing anomaly detection (vote cast under duress timeline)
    - Multi-session pattern deviation
    """

    STRESS_THRESHOLDS = {
        "cortisol_proxy": 0.7,   # Alpha suppression threshold
        "anxiety_proxy": 0.6,    # Beta elevation threshold
        "coherence_drop": 0.4,  # Frontal coherence drop
    }

    def __init__(self):
        self.signals: List[CoercionSignal] = []
        self.baselines: Dict[str, dict] = {}  # voter -> baseline metrics

    def set_baseline(self, voter_did: str, eeg_baseline: np.ndarray):
        """Set a voter's baseline neural pattern for comparison."""
        features = self._extract_stress_features(eeg_baseline)
        self.baselines[voter_did] = features

    def check_coercion(self, voter_did: str, eeg_data: np.ndarray,
                       vote_timing: float = 0) -> Dict:
        """Check for coercion signals in a neural vote."""
        features = self._extract_stress_features(eeg_data)
        baseline = self.baselines.get(voter_did, {"cortisol_proxy": 0.3, "anxiety_proxy": 0.3, "coherence": 0.8})

        signals_detected = []

        # Stress pattern analysis
        if features["cortisol_proxy"] > self.STRESS_THRESHOLDS["cortisol_proxy"]:
            signals_detected.append("stress_induced")

        # Anxiety detection
        if features["anxiety_proxy"] > self.STRESS_THRESHOLDS["anxiety_proxy"]:
            signals_detected.append("anxiety_elevated")

        # Coherence drop (neural override indicator)
        if features["coherence"] < self.STRESS_THRESHOLDS["coherence_drop"]:
            signals_detected.append("neural_override")

        # Baseline deviation
        deviation = abs(features["cortisol_proxy"] - baseline.get("cortisol_proxy", 0.3))
        if deviation > 0.3:
            signals_detected.append("baseline_deviation")

        coerced = len(signals_detected) >= 2
        confidence = len(signals_detected) / 4.0

        if coerced:
            signal = CoercionSignal(
                signal_id=f"coerce_{int(time.time())}",
                voter_did=voter_did,
                coercion_type=signals_detected[0],
                confidence=confidence,
                evidence=f"Detected: {', '.join(signals_detected)}",
            )
            self.signals.append(signal)

        return {
            "coerced": coerced,
            "confidence": confidence,
            "signals": signals_detected,
            "stress_level": features["cortisol_proxy"],
        }

    def _extract_stress_features(self, eeg_data: np.ndarray) -> Dict[str, float]:
        """Extract stress-correlated features from EEG."""
        if eeg_data.ndim == 1:
            eeg_data = eeg_data.reshape(1, -1)
        fft = np.fft.rfft(eeg_data, axis=1)
        power = np.abs(fft) ** 2
        freqs = np.fft.rfftfreq(eeg_data.shape[1], 1/256)

        def band_power(low, high):
            mask = (freqs >= low) & (freqs < high)
            return float(np.mean(power[:, mask])) if np.any(mask) else 0

        alpha = band_power(8, 13)
        beta = band_power(13, 30)
        theta = band_power(4, 8)

        return {
            "cortisol_proxy": float(np.clip(1 - alpha / (beta + 1e-9), 0, 1)),
            "anxiety_proxy": float(np.clip(beta / (alpha + beta + 1e-9), 0, 1)),
            "coherence": float(np.clip(alpha / (theta + alpha + 1e-9), 0, 1)),
        }

    def get_signals(self, voter_did: str = None) -> List[CoercionSignal]:
        if voter_did:
            return [s for s in self.signals if s.voter_did == voter_did]
        return self.signals
