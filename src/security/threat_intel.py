"""Threat Intelligence — Real-time threat feeds and incident response."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum
import time, hashlib

class ThreatLevel(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AttackPattern(Enum):
    """MITRE ATT&CK aligned patterns."""
    RECONNAISSANCE = "T1590"
    INITIAL_ACCESS = "T1078"
    EXECUTION = "T1059"
    PERSISTENCE = "T1098"
    PRIVILEGE_ESCALATION = "T1068"
    DEFENSE_EVASION = "T1027"
    CREDENTIAL_ACCESS = "T1110"
    LATERAL_MOVEMENT = "T1021"
    COLLECTION = "T1560"
    IMPACT = "T1486"

@dataclass
class ThreatFeed:
    """A real-time threat intelligence feed."""
    feed_id: str
    source: str  # e.g., "internal", "community", "commercial"
    threat_type: str  # ip, did, pattern, vulnerability
    indicator: str  # IP address, DID, pattern hash
    level: ThreatLevel
    description: str
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    occurrences: int = 1
    tags: List[str] = field(default_factory=list)

@dataclass
class IncidentResponse:
    """An incident response playbook."""
    incident_id: str
    threat_type: str
    severity: ThreatLevel
    affected_systems: List[str]
    detected_at: float = field(default_factory=time.time)
    status: str = "detected"  # detected, investigating, contained, resolved
    actions_taken: List[str] = field(default_factory=list)
    timeline: List[dict] = field(default_factory=list)
    resolution: str = ""
    resolved_at: Optional[float] = None

class ThreatIntelligence:
    """
    Threat intelligence platform for ATLAS.
    
    - Aggregates threat feeds from multiple sources
    - Scores reputation of IPs and DIDs
    - Recognizes attack patterns (MITRE ATT&CK)
    - Automated incident response playbooks
    """

    def __init__(self):
        self.threats: Dict[str, ThreatFeed] = {}  # indicator -> threat
        self.ip_reputation: Dict[str, float] = {}  # IP -> score (0=malicious, 1=clean)
        self.did_reputation: Dict[str, float] = {}  # DID -> score
        self.incidents: Dict[str, IncidentResponse] = {}
        self.playbooks: Dict[str, List[str]] = self._create_playbooks()

    def _create_playbooks(self) -> Dict[str, List[str]]:
        """Create incident response playbooks."""
        return {
            "ddos_attack": [
                "1. Detect anomalous traffic volume",
                "2. Identify attack sources via IP reputation",
                "3. Activate rate limiting on affected endpoints",
                "4. Block malicious IPs at firewall level",
                "5. Notify validator network",
                "6. Scale infrastructure to absorb traffic",
                "7. Document incident and update threat feeds",
            ],
            "sybil_attack": [
                "1. Detect multiple identities from same source",
                "2. Cross-reference neural fingerprints",
                "3. Freeze suspicious soulbound tokens",
                "4. Initiate PROMETHEUS investigation",
                "5. Slash fraudulent validators if applicable",
                "6. Update anti-sybil detection rules",
            ],
            "smart_contract_exploit": [
                "1. Detect anomalous transaction pattern",
                "2. Pause affected contract via emergency multisig",
                "3. Assess damage scope",
                "4. Deploy fix via governance fast-track",
                "5. Compensate affected users from treasury",
                "6. Post-mortem analysis and audit update",
            ],
            "validator_collusion": [
                "1. Detect correlated voting patterns",
                "2. Analyze validator network topology",
                "3. Identify colluding set",
                "4. Initiate slashing proceedings",
                "5. Reassign stake to honest validators",
                "6. Update consensus parameters",
            ],
            "key_compromise": [
                "1. Detect anomalous key usage",
                "2. Freeze affected identity",
                "3. Initiate social recovery",
                "4. Revoke compromised keys",
                "5. Notify guardian set",
                "6. Issue new keys via MFA",
            ],
        }

    def report_threat(self, source: str, threat_type: str, indicator: str,
                      level: ThreatLevel, description: str,
                      tags: List[str] = None) -> ThreatFeed:
        """Report a new threat indicator."""
        if indicator in self.threats:
            threat = self.threats[indicator]
            threat.last_seen = time.time()
            threat.occurrences += 1
            if level.value in ["critical", "high"]:
                threat.level = level
            return threat
        
        threat = ThreatFeed(
            feed_id=hashlib.sha256(f"threat:{indicator}:{time.time()}".encode()).hexdigest()[:16],
            source=source, threat_type=threat_type,
            indicator=indicator, level=level,
            description=description, tags=tags or [],
        )
        self.threats[indicator] = threat
        
        # Update reputation scores
        if threat_type == "ip":
            self.ip_reputation[indicator] = max(0, self.ip_reputation.get(indicator, 1.0) - 0.3)
        elif threat_type == "did":
            self.did_reputation[indicator] = max(0, self.did_reputation.get(indicator, 1.0) - 0.3)
        
        return threat

    def check_ip(self, ip: str) -> float:
        """Check IP reputation (1.0 = clean, 0.0 = malicious)."""
        return self.ip_reputation.get(ip, 1.0)

    def check_did(self, did: str) -> float:
        """Check DID reputation."""
        return self.did_reputation.get(did, 1.0)

    def is_blocked(self, indicator: str) -> bool:
        """Check if an indicator should be blocked."""
        threat = self.threats.get(indicator)
        if not threat:
            return False
        return threat.level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]

    def create_incident(self, threat_type: str, severity: ThreatLevel,
                       affected_systems: List[str]) -> IncidentResponse:
        """Create a new incident response."""
        incident = IncidentResponse(
            incident_id=hashlib.sha256(f"incident:{threat_type}:{time.time()}".encode()).hexdigest()[:16],
            threat_type=threat_type, severity=severity,
            affected_systems=affected_systems,
        )
        # Add timeline entry
        incident.timeline.append({
            "timestamp": time.time(),
            "event": "Incident detected",
            "details": f"{threat_type} affecting {', '.join(affected_systems)}",
        })
        # Auto-assign playbook
        playbook = self.playbooks.get(threat_type, [])
        if playbook:
            incident.actions_taken.append(f"Playbook activated: {threat_type}")
        self.incidents[incident.incident_id] = incident
        return incident

    def update_incident(self, incident_id: str, status: str,
                       action: str = "") -> bool:
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
        incident.status = status
        if action:
            incident.actions_taken.append(action)
        incident.timeline.append({
            "timestamp": time.time(),
            "event": status, "details": action,
        })
        if status == "resolved":
            incident.resolved_at = time.time()
        return True

    def active_incidents(self) -> List[IncidentResponse]:
        return [i for i in self.incidents.values() if i.status != "resolved"]

    def stats(self) -> dict:
        return {
            "total_threats": len(self.threats),
            "critical_threats": sum(1 for t in self.threats.values() if t.level == ThreatLevel.CRITICAL),
            "tracked_ips": len(self.ip_reputation),
            "tracked_dids": len(self.did_reputation),
            "total_incidents": len(self.incidents),
            "active_incidents": len(self.active_incidents()),
            "playbooks": len(self.playbooks),
        }
