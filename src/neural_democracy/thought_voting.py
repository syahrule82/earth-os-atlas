"""Neural voting — thought-to-vote translation pipeline."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np, time, hashlib

@dataclass
class NeuralVote:
    vote_id: str
    voter_did: str
    proposal_id: str
    decoded_intent: bool  # True=approve, False=reject
    confidence: float
    neural_signature: str  # hash of neural pattern
    cognitive_load: float
    timestamp: float = field(default_factory=time.time)

class IntentDecoder:
    """
    Decodes cognitive intent from EEG/PNI signals.
    Translates neural patterns into vote decisions.
    """

    def __init__(self, sample_rate: int = 256):
        self.sample_rate = sample_rate
        self.calibration_data: Dict[str, np.ndarray] = {}  # voter -> calibration
        self.intent_patterns = {
            "approve": np.array([0.8, 0.3, 0.9, 0.2], dtype=np.float32),  # theta, alpha, beta, gamma
            "reject": np.array([0.2, 0.9, 0.3, 0.8], dtype=np.float32),
        }

    def calibrate(self, voter_did: str, approve_signal: np.ndarray, reject_signal: np.ndarray):
        """Calibrate decoder with known approve/reject signals."""
        self.calibration_data[f"{voter_did}:approve"] = approve_signal
        self.calibration_data[f"{voter_did}:reject"] = reject_signal

    def decode(self, voter_did: str, eeg_data: np.ndarray) -> Dict:
        """Decode intent from EEG signal."""
        # Extract band powers
        features = self._extract_features(eeg_data)

        # Match against patterns
        approve_sim = self._cosine_similarity(features, self.intent_patterns["approve"])
        reject_sim = self._cosine_similarity(features, self.intent_patterns["reject"])

        # Use calibration if available
        cal_approve = self.calibration_data.get(f"{voter_did}:approve")
        cal_reject = self.calibration_data.get(f"{voter_did}:reject")
        if cal_approve is not None:
            approve_sim = (approve_sim + self._cosine_similarity(features, cal_approve)) / 2
        if cal_reject is not None:
            reject_sim = (reject_sim + self._cosine_similarity(features, cal_reject)) / 2

        intent = approve_sim > reject_sim
        confidence = abs(approve_sim - reject_sim)
        cognitive_load = float(np.mean(features[2:]))  # beta + gamma

        return {
            "intent": intent,
            "confidence": float(confidence),
            "approve_similarity": float(approve_sim),
            "reject_similarity": float(reject_sim),
            "cognitive_load": cognitive_load,
            "neural_signature": hashlib.sha256(features.tobytes()).hexdigest()[:32],
        }

    def _extract_features(self, eeg_data: np.ndarray) -> np.ndarray:
        """Extract band power features from EEG."""
        if eeg_data.ndim == 1:
            eeg_data = eeg_data.reshape(1, -1)
        fft = np.fft.rfft(eeg_data, axis=1)
        power = np.abs(fft) ** 2
        freqs = np.fft.rfftfreq(eeg_data.shape[1], 1/self.sample_rate)

        bands = {"theta": (4, 8), "alpha": (8, 13), "beta": (13, 30), "gamma": (30, 100)}
        features = []
        for name, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs < high)
            features.append(np.mean(power[:, mask]) if np.any(mask) else 0)
        return np.array(features, dtype=np.float32)

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        norm_a, norm_b = np.linalg.norm(a) + 1e-9, np.linalg.norm(b) + 1e-9
        return float(np.dot(a, b) / (norm_a * norm_b))

class NeuralVotingSystem:
    """
    Complete neural voting pipeline: EEG -> intent decode -> anti-coercion check -> vote.
    """

    def __init__(self):
        self.decoder = IntentDecoder()
        self.votes: Dict[str, NeuralVote] = {}
        self.vote_count = 0

    def cast_neural_vote(self, voter_did: str, proposal_id: str,
                         eeg_data: np.ndarray,
                         coercion_check: Optional[dict] = None) -> NeuralVote:
        """Cast a vote via neural intent detection."""
        decoded = self.decoder.decode(voter_did, eeg_data)

        # If coercion check provided, verify no coercion
        if coercion_check and coercion_check.get("coerced", False):
            raise ValueError("Vote rejected: coercion detected")

        vote = NeuralVote(
            vote_id=hashlib.sha256(f"{voter_did}:{proposal_id}:{time.time()}".encode()).hexdigest()[:16],
            voter_did=voter_did,
            proposal_id=proposal_id,
            decoded_intent=decoded["intent"],
            confidence=decoded["confidence"],
            neural_signature=decoded["neural_signature"],
            cognitive_load=decoded["cognitive_load"],
        )
        self.votes[vote.vote_id] = vote
        self.vote_count += 1
        return vote

    def tally(self, proposal_id: str) -> Dict:
        """Tally votes for a proposal."""
        prop_votes = [v for v in self.votes.values() if v.proposal_id == proposal_id]
        approve = sum(1 for v in prop_votes if v.decoded_intent)
        reject = len(prop_votes) - approve
        avg_confidence = sum(v.confidence for v in prop_votes) / max(1, len(prop_votes))
        return {
            "proposal_id": proposal_id,
            "total_votes": len(prop_votes),
            "approve": approve,
            "reject": reject,
            "passing": approve > reject,
            "avg_confidence": avg_confidence,
        }
