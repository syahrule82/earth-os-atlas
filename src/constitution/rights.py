"""Digital Rights Engine — enforces ATLAS citizen rights."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum
import time, hashlib

class RightType(Enum):
    FREEDOM_OF_EXPRESSION = "freedom_of_expression"
    FREEDOM_OF_ASSOCIATION = "freedom_of_association"
    RIGHT_TO_VALUE = "right_to_value"
    RIGHT_TO_PRIVACY = "right_to_privacy"
    RIGHT_TO_PARTICIPATE = "right_to_participate"
    RIGHT_TO_APPEAL = "right_to_appeal"
    RIGHT_TO_COMPUTE = "right_to_compute"
    RIGHT_TO_IDENTITY = "right_to_identity"
    PROTECTION_FROM_CONFISCATION = "protection_from_confiscation"
    PROTECTION_FROM_COERCION = "protection_from_coercion"

@dataclass
class Right:
    right_type: RightType
    description: str
    limitations: List[str] = field(default_factory=list)
    protected: bool = True  # Protected rights require 90% supermajority to amend

@dataclass
class RightsViolation:
    violation_id: str
    citizen: str
    right_violated: RightType
    violator: str
    evidence: str
    severity: str  # minor, moderate, severe
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False
    resolution: Optional[str] = None

class RightsEngine:
    """Enforces digital rights for all ATLAS citizens."""

    def __init__(self):
        self.rights: Dict[RightType, Right] = self._initialize_rights()
        self.violations: List[RightsViolation] = []
        self.citizens: Set[str] = set()
        self.suspensions: Dict[str, List[RightType]] = {}  # citizen -> suspended rights

    def _initialize_rights(self) -> Dict[RightType, Right]:
        return {
            RightType.FREEDOM_OF_EXPRESSION: Right(
                RightType.FREEDOM_OF_EXPRESSION,
                "Every citizen may express any thought through the PNI mesh.",
                limitations=["Direct incitement to violence", "Coercive neural manipulation"],
            ),
            RightType.FREEDOM_OF_ASSOCIATION: Right(
                RightType.FREEDOM_OF_ASSOCIATION,
                "Citizens may form voluntary associations and collectives.",
            ),
            RightType.RIGHT_TO_VALUE: Right(
                RightType.RIGHT_TO_VALUE,
                "Verified value creation earns ATLAS. No entity may prevent this.",
                protected=True,
            ),
            RightType.RIGHT_TO_PRIVACY: Right(
                RightType.RIGHT_TO_PRIVACY,
                "Neural data is sovereign. No entity may access without consent.",
                protected=True,
            ),
            RightType.RIGHT_TO_PARTICIPATE: Right(
                RightType.RIGHT_TO_PARTICIPATE,
                "Every citizen may vote, propose, and hold office.",
                protected=True,
            ),
            RightType.RIGHT_TO_APPEAL: Right(
                RightType.RIGHT_TO_APPEAL,
                "Every governance decision is appealable.",
                protected=True,
            ),
            RightType.RIGHT_TO_COMPUTE: Right(
                RightType.RIGHT_TO_COMPUTE,
                "Every identity receives 1 GFLOPS of compute guaranteed.",
            ),
            RightType.RIGHT_TO_IDENTITY: Right(
                RightType.RIGHT_TO_IDENTITY,
                "Every human has the right to a DID:atlas identity.",
                protected=True,
            ),
            RightType.PROTECTION_FROM_CONFISCATION: Right(
                RightType.PROTECTION_FROM_CONFISCATION,
                "ATLAS holdings cannot be seized without due process.",
                protected=True,
            ),
            RightType.PROTECTION_FROM_COERCION: Right(
                RightType.PROTECTION_FROM_COERCION,
                "No citizen may be forced to vote against their will.",
                protected=True,
            ),
        }

    def register_citizen(self, did: str) -> None:
        self.citizens.add(did)

    def check_right(self, citizen: str, right_type: RightType, context: dict) -> bool:
        """Check if a citizen's right is being respected."""
        if citizen not in self.citizens:
            return False
        suspended = self.suspensions.get(citizen, [])
        if right_type in suspended:
            return False
        right = self.rights.get(right_type)
        if not right:
            return False
        # Check limitations
        for limitation in right.limitations:
            if limitation.lower() in str(context).lower():
                return False
        return True

    def report_violation(self, citizen: str, right_type: RightType,
                         violator: str, evidence: str, severity: str = "moderate") -> RightsViolation:
        violation = RightsViolation(
            violation_id=hashlib.sha256(f"{citizen}:{right_type.value}:{time.time()}".encode()).hexdigest()[:16],
            citizen=citizen, right_violated=right_type,
            violator=violator, evidence=evidence, severity=severity,
        )
        self.violations.append(violation)
        return violation

    def resolve_violation(self, violation_id: str, resolution: str) -> bool:
        v = next((v for v in self.violations if v.violation_id == violation_id), None)
        if v:
            v.resolved = True
            v.resolution = resolution
            return True
        return False

    def suspend_right(self, citizen: str, right_type: RightType) -> None:
        """Suspend a right (only via due process)."""
        if citizen not in self.suspensions:
            self.suspensions[citizen] = []
        if right_type not in self.suspensions[citizen]:
            self.suspensions[citizen].append(right_type)

    def restore_right(self, citizen: str, right_type: RightType) -> None:
        if citizen in self.suspensions:
            self.suspensions[citizen] = [r for r in self.suspensions[citizen] if r != right_type]

    def get_violations(self, citizen: str = None, unresolved_only: bool = False) -> List[RightsViolation]:
        results = self.violations
        if citizen:
            results = [v for v in results if v.citizen == citizen]
        if unresolved_only:
            results = [v for v in results if not v.resolved]
        return results
