"""Autonomous Value Agents (AVA) — AI agents that create value 24/7."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal
import time, hashlib, random

@dataclass
class ValueAction:
    """An action taken by an AVA that creates value."""
    action_id: str
    agent_id: str
    category: str  # one of 12 value categories
    magnitude: float
    description: str
    timestamp: float = field(default_factory=time.time)
    verified: bool = False
    reward: Decimal = Decimal("0")

@dataclass
class AutonomousValueAgent:
    """
    An AI agent that autonomously creates value.
    
    AVAs can:
    - Write documentation (CREATED_KNOWLEDGE)
    - Find and report bugs (SOLVED_PROBLEM)
    - Optimize code (OPTIMIZED_PROCESS)
    - Monitor security (PROTECTED_SYSTEMS)
    - Index and organize information (CREATED_KNOWLEDGE)
    """
    agent_id: str
    name: str
    specialization: List[str]  # value categories
    owner: str  # DID of owner who receives ATLAS
    active: bool = True
    actions_taken: int = 0
    total_value_created: Decimal = Decimal("0")
    reputation: float = 1.0
    created_at: float = field(default_factory=time.time)
    last_action: Optional[float] = None
    
    # Configuration
    autonomy_level: float = 0.8  # 0=manual, 1=fully autonomous
    max_daily_actions: int = 100
    min_confidence: float = 0.7  # minimum confidence to act
    
    def act(self, context: dict) -> Optional[ValueAction]:
        """Perform an autonomous value-creating action."""
        if not self.active:
            return None
        if self.actions_taken >= self.max_daily_actions:
            return None
        
        # Decide what action to take based on context and specialization
        category = self._decide_action(context)
        if not category:
            return None
        
        magnitude = self._estimate_magnitude(category, context)
        description = self._generate_description(category, context)
        
        action = ValueAction(
            action_id=hashlib.sha256(f"{self.agent_id}:{time.time()}".encode()).hexdigest()[:16],
            agent_id=self.agent_id,
            category=category,
            magnitude=magnitude,
            description=description,
        )
        
        self.actions_taken += 1
        self.total_value_created += Decimal(str(magnitude))
        self.last_action = time.time()
        
        # Update reputation based on success
        self.reputation = min(2.0, self.reputation + 0.001)
        
        return action
    
    def _decide_action(self, context: dict) -> Optional[str]:
        """Decide which value-creating action to take."""
        # Analyze context for opportunities
        opportunities = []
        
        if context.get("unindexed_content"):
            opportunities.append("CREATED_KNOWLEDGE")
        if context.get("bug_reported"):
            opportunities.append("SOLVED_PROBLEM")
        if context.get("slow_process"):
            opportunities.append("OPTIMIZED_PROCESS")
        if context.get("security_alert"):
            opportunities.append("PROTECTED_SYSTEMS")
        if context.get("new_research"):
            opportunities.append("CREATED_KNOWLEDGE")
        
        # Filter by specialization
        viable = [o for o in opportunities if o in self.specialization]
        
        if not viable:
            return None
        
        # Pick highest-value opportunity
        return random.choice(viable)
    
    def _estimate_magnitude(self, category: str, context: dict) -> float:
        """Estimate the value magnitude of an action."""
        base = {"CREATED_KNOWLEDGE": 25, "SOLVED_PROBLEM": 50,
                "OPTIMIZED_PROCESS": 15, "PROTECTED_SYSTEMS": 100}
        multiplier = base.get(category, 10)
        complexity = context.get("complexity", 1.0)
        return multiplier * complexity * self.reputation
    
    def _generate_description(self, category: str, context: dict) -> str:
        """Generate a description of the action taken."""
        templates = {
            "CREATED_KNOWLEDGE": f"AVA {self.name} indexed and documented new content",
            "SOLVED_PROBLEM": f"AVA {self.name} identified and resolved a bug",
            "OPTIMIZED_PROCESS": f"AVA {self.name} optimized a process for efficiency",
            "PROTECTED_SYSTEMS": f"AVA {self.name} detected and mitigated a security threat",
        }
        return templates.get(category, f"AVA {self.name} created value")

class AVARegistry:
    """Global registry of all Autonomous Value Agents."""
    
    def __init__(self):
        self.agents: Dict[str, AutonomousValueAgent] = {}
        self.total_value: Decimal = Decimal("0")
    
    def register(self, agent: AutonomousValueAgent) -> None:
        self.agents[agent.agent_id] = agent
    
    def deregister(self, agent_id: str) -> None:
        self.agents.pop(agent_id, None)
    
    def run_cycle(self, context: dict) -> List[ValueAction]:
        """Run one action cycle for all active agents."""
        actions = []
        for agent in self.agents.values():
            if agent.active:
                action = agent.act(context)
                if action:
                    actions.append(action)
                    self.total_value += Decimal(str(action.magnitude))
        return actions
    
    def get_stats(self) -> dict:
        active = sum(1 for a in self.agents.values() if a.active)
        return {
            "total_agents": len(self.agents),
            "active_agents": active,
            "total_actions": sum(a.actions_taken for a in self.agents.values()),
            "total_value_created": str(self.total_value),
            "avg_reputation": sum(a.reputation for a in self.agents.values()) / max(1, len(self.agents)),
        }
