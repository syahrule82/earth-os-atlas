"""
Cognitive State Machine
Tracks macro cognitive modes of a PNI user in real time.
States: IDLE | COMPOSING | RECEIVING | DEEP_FOCUS | DREAMING | EMERGENCY
"""
from __future__ import annotations
import asyncio, time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, List, Optional
import numpy as np


class CogState(Enum):
    IDLE       = auto()
    COMPOSING  = auto()
    RECEIVING  = auto()
    DEEP_FOCUS = auto()
    DREAMING   = auto()
    EMERGENCY  = auto()


VALID = {
    CogState.IDLE:       [CogState.COMPOSING, CogState.RECEIVING, CogState.DEEP_FOCUS, CogState.DREAMING, CogState.EMERGENCY],
    CogState.COMPOSING:  [CogState.IDLE, CogState.EMERGENCY],
    CogState.RECEIVING:  [CogState.IDLE, CogState.COMPOSING, CogState.EMERGENCY],
    CogState.DEEP_FOCUS: [CogState.IDLE, CogState.EMERGENCY],
    CogState.DREAMING:   [CogState.IDLE, CogState.EMERGENCY],
    CogState.EMERGENCY:  [CogState.IDLE],
}


@dataclass
class CognitiveSnapshot:
    state:       CogState
    timestamp:   float
    confidence:  float
    theta_power: float
    alpha_power: float
    beta_power:  float
    gamma_power: float


class CognitiveStateMachine:
    def __init__(self, node_id: str, history_depth: int = 128):
        self.node_id     = node_id
        self._state      = CogState.IDLE
        self._history:   List[CognitiveSnapshot] = []
        self._depth      = history_depth
        self._listeners: Dict[CogState, List[Callable]] = {s: [] for s in CogState}

    @property
    def state(self) -> CogState:
        return self._state

    @property
    def current(self) -> Optional[CognitiveSnapshot]:
        return self._history[-1] if self._history else None

    async def transition(
        self,
        new_state:  CogState,
        confidence: float = 1.0,
        eeg:        Optional[Dict[str, float]] = None,
    ) -> CognitiveSnapshot:
        if new_state not in VALID[self._state]:
            raise ValueError(f"Illegal: {self._state.name} -> {new_state.name}")
        eeg = eeg or {}
        snap = CognitiveSnapshot(
            state=new_state, timestamp=time.time(),
            confidence=float(np.clip(confidence, 0, 1)),
            theta_power=eeg.get("theta", 0.0),
            alpha_power=eeg.get("alpha", 0.0),
            beta_power=eeg.get("beta", 0.0),
            gamma_power=eeg.get("gamma", 0.0),
        )
        self._state = new_state
        self._history.append(snap)
        if len(self._history) > self._depth:
            self._history.pop(0)
        return snap

    def cognitive_load(self) -> float:
        if not self._history:
            return 0.0
        recent = np.array([[s.beta_power, s.gamma_power] for s in self._history[-16:]])
        return float(np.clip(recent.mean(), 0, 1))
