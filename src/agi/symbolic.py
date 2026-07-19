"""Symbolic reasoning engine for value taxonomy."""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

@dataclass
class Rule:
    rule_id:   str
    condition: str
    action:    str
    priority:  int = 1
    active:    bool = True

@dataclass
class FactBase:
    facts: Dict[str, object] = field(default_factory=dict)

    def add(self, key: str, value: object) -> None:
        self.facts[key] = value

    def get(self, key: str) -> Optional[object]:
        return self.facts.get(key)

    def has(self, key: str) -> bool:
        return key in self.facts

    def query(self, pattern: str) -> List[str]:
        return [k for k in self.facts if pattern in k]

class SymbolicEngine:
    """Forward-chaining rule engine for value reasoning."""

    def __init__(self):
        self.rules: List[Rule] = []
        self.facts: FactBase = FactBase()
        self.inference_count = 0

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)
        self.rules.sort(key=lambda r: -r.priority)

    def infer(self, max_rounds: int = 10) -> List[str]:
        """Run forward chaining until no new facts are derived."""
        derived = []
        for _ in range(max_rounds):
            new_facts = False
            for rule in self.rules:
                if not rule.active:
                    continue
                if self._evaluate(rule.condition):
                    if not self.facts.has(rule.action):
                        self.facts.add(rule.action, True)
                        derived.append(rule.action)
                        new_facts = True
                        self.inference_count += 1
            if not new_facts:
                break
        return derived

    def _evaluate(self, condition: str) -> bool:
        """Evaluate a simple condition against the fact base."""
        # Simplified: check if all tokens in condition exist as facts
        tokens = condition.split(" AND ")
        return all(self.facts.has(t.strip()) for t in tokens)

    def load_value_rules(self) -> None:
        """Load default value taxonomy rules."""
        rules = [
            Rule("r1", "code_committed AND reviewed", "BUILT_INFRASTRUCTURE", 2),
            Rule("r2", "research_published AND peer_reviewed", "CREATED_KNOWLEDGE", 2),
            Rule("r3", "patient_treated AND recovery_confirmed", "HEALED_BIOLOGICAL", 3),
            Rule("r4", "efficiency_improved AND measured", "OPTIMIZED_PROCESS", 1),
            Rule("r5", "carbon_captured AND verified", "RESTORED_ECOLOGICAL", 2),
            Rule("r6", "BUILT_INFRASTRUCTURE AND large_scale", "high_value", 1),
            Rule("r7", "HEALED_BIOLOGICAL AND high_severity", "high_value", 1),
        ]
        for r in rules:
            self.add_rule(r)
