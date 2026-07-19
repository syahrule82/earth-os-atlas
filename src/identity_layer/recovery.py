"""Social Recovery — M-of-N guardian-based identity recovery."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import hashlib, time

@dataclass
class GuardianSet:
    """A set of guardians who can help recover an identity."""
    owner_did: str
    guardian_dids: List[str]
    threshold: int  # M of N required
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    @property
    def total_guardians(self) -> int:
        return len(self.guardian_dids)

@dataclass
class RecoveryRequest:
    """A pending identity recovery request."""
    request_id: str
    owner_did: str
    new_public_key: str  # New key to replace lost one
    guardian_approvals: Set[str] = field(default_factory=set)  # guardian DIDs who approved
    threshold: int
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 7 * 86400)  # 7 days
    completed: bool = False

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def is_ready(self) -> bool:
        return len(self.guardian_approvals) >= self.threshold and not self.is_expired()

class SocialRecovery:
    """
    Social recovery for ATLAS identities.
    
    If a user loses their keys, they can recover their identity
    by getting M-of-N guardians to approve a new public key.
    """

    def __init__(self):
        self.guardian_sets: Dict[str, GuardianSet] = {}
        self.recovery_requests: Dict[str, RecoveryRequest] = {}
        self.completed_recoveries: List[dict] = []

    def set_guardians(self, owner_did: str, guardians: List[str],
                      threshold: int) -> GuardianSet:
        """Set or update guardians for an identity."""
        if threshold > len(guardians):
            raise ValueError("Threshold cannot exceed guardian count")
        if threshold < 1:
            raise ValueError("Threshold must be at least 1")
        gs = GuardianSet(
            owner_did=owner_did,
            guardian_dids=guardians,
            threshold=threshold,
        )
        self.guardian_sets[owner_did] = gs
        return gs

    def initiate_recovery(self, owner_did: str, new_public_key: str) -> RecoveryRequest:
        """Initiate an identity recovery."""
        gs = self.guardian_sets.get(owner_did)
        if not gs:
            raise ValueError("No guardian set found for this DID")
        request = RecoveryRequest(
            request_id=hashlib.sha256(f"recovery:{owner_did}:{time.time()}".encode()).hexdigest()[:16],
            owner_did=owner_did,
            new_public_key=new_public_key,
            threshold=gs.threshold,
        )
        self.recovery_requests[request.request_id] = request
        return request

    def guardian_approve(self, request_id: str, guardian_did: str) -> bool:
        """A guardian approves a recovery request."""
        request = self.recovery_requests.get(request_id)
        if not request or request.completed or request.is_expired():
            return False
        gs = self.guardian_sets.get(request.owner_did)
        if not gs or guardian_did not in gs.guardian_dids:
            return False
        if guardian_did in request.guardian_approvals:
            return False  # Already approved
        request.guardian_approvals.add(guardian_did)
        # Auto-complete if threshold met
        if request.is_ready():
            request.completed = True
            self.completed_recoveries.append({
                "owner": request.owner_did,
                "new_key": request.new_public_key,
                "approvals": list(request.guardian_approvals),
                "timestamp": time.time(),
            })
        return True

    def get_request(self, request_id: str) -> Optional[RecoveryRequest]:
        return self.recovery_requests.get(request_id)

    def pending_recoveries(self, guardian_did: str) -> List[RecoveryRequest]:
        """Get pending recovery requests that a guardian can approve."""
        results = []
        for req in self.recovery_requests.values():
            if req.completed or req.is_expired():
                continue
            gs = self.guardian_sets.get(req.owner_did)
            if gs and guardian_did in gs.guardian_dids and guardian_did not in req.guardian_approvals:
                results.append(req)
        return results
