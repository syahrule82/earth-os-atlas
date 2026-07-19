"""Argumentation framework — structured debate with support/attack relations."""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
import hashlib, time

@dataclass
class Argument:
    arg_id: str
    claim: str
    proponent: str
    evidence: List[str] = field(default_factory=list)
    strength: float = 0.5
    timestamp: float = field(default_factory=time.time)

@dataclass
class AttackRelation:
    source_id: str  # attacking argument
    target_id: str  # attacked argument
    rebuttal: str
    strength: float = 0.5

@dataclass
class SupportRelation:
    source_id: str  # supporting argument
    target_id: str  # supported argument
    endorsement: str
    strength: float = 0.5

class ArgumentGraph:
    """
    Bipolar argumentation framework with support and attack relations.
    Computes acceptability of arguments using gradual semantics.
    """

    def __init__(self):
        self.arguments: Dict[str, Argument] = {}
        self.attacks: List[AttackRelation] = []
        self.supports: List[SupportRelation] = []

    def add_argument(self, arg: Argument) -> None:
        self.arguments[arg.arg_id] = arg

    def add_attack(self, attack: AttackRelation) -> None:
        self.attacks.append(attack)

    def add_support(self, support: SupportRelation) -> None:
        self.supports.append(support)

    def get_attackers(self, arg_id: str) -> List[AttackRelation]:
        return [a for a in self.attacks if a.target_id == arg_id]

    def get_supporters(self, arg_id: str) -> List[SupportRelation]:
        return [s for s in self.supports if s.target_id == arg_id]

    def compute_acceptability(self, arg_id: str, max_iterations: int = 20) -> float:
        """
        Compute gradual acceptability score [0-1] using
        the combined support/attack semantics.
        """
        if arg_id not in self.arguments:
            return 0.0

        scores: Dict[str, float] = {aid: 0.5 for aid in self.arguments}

        for _ in range(max_iterations):
            new_scores = {}
            for aid, arg in self.arguments.items():
                attackers = self.get_attackers(aid)
                supporters = self.get_supporters(aid)

                attack_force = sum(scores[a.source_id] * a.strength for a in attackers)
                support_force = sum(scores[s.source_id] * s.strength for s in supporters)

                # Update: base + support - attack
                base = arg.strength
                influence = support_force - attack_force
                new_scores[aid] = max(0.0, min(1.0, base + influence * 0.3))

            converged = all(abs(new_scores[k] - scores[k]) < 0.001 for k in scores)
            scores = new_scores
            if converged:
                break

        return scores.get(arg_id, 0.0)

    def get_winning_arguments(self, threshold: float = 0.6) -> List[Argument]:
        """Get all arguments with acceptability above threshold."""
        winners = []
        for aid in self.arguments:
            score = self.compute_acceptability(aid)
            if score >= threshold:
                winners.append(self.arguments[aid])
        return sorted(winners, key=lambda a: self.compute_acceptability(a.arg_id), reverse=True)

    def summary(self) -> dict:
        return {
            "total_arguments": len(self.arguments),
            "total_attacks": len(self.attacks),
            "total_supports": len(self.supports),
            "avg_strength": sum(a.strength for a in self.arguments.values()) / max(1, len(self.arguments)),
        }
