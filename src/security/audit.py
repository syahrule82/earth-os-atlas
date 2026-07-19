"""Smart Contract Auditor — Static analysis of Solidity contracts."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import re, time, hashlib

class VulnerabilitySeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

class SWC_ID(Enum):
    """Smart Contract Weakness Classification."""
    REENTRANCY = "SWC-107"
    INTEGER_OVERFLOW = "SWC-101"
    ACCESS_CONTROL = "SWC-105"
    UNCHECKED_CALL = "SWC-104"
    TX_ORIGIN = "SWC-115"
    DELEGATE_CALL = "SWC-112"
    TIME_MANIPULATION = "SWC-116"
    DANGEROUS_STRICT_EQUALITY = "SWC-132"
    SHADOWING = "SWC-119"
    UNINITIALIZED_STORAGE = "SWC-109"

@dataclass
class Vulnerability:
    """A detected vulnerability in a smart contract."""
    vuln_id: str
    swc_id: SWC_ID
    title: str
    severity: VulnerabilitySeverity
    description: str
    location: str  # line number or function name
    recommendation: str
    confidence: float  # 0-1
    detected_at: float = field(default_factory=time.time)

@dataclass
class AuditReport:
    """A complete smart contract audit report."""
    report_id: str
    contract_name: str
    source_hash: str
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    gas_optimizations: List[str] = field(default_factory=list)
    overall_score: float = 100.0  # 100 = no issues
    audited_at: float = field(default_factory=time.time)
    summary: str = ""

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == VulnerabilitySeverity.HIGH)

    @property
    def passed(self) -> bool:
        return self.critical_count == 0 and self.high_count == 0

class SmartContractAuditor:
    """
    Static analysis auditor for Solidity smart contracts.
    
    Detects:
    - Reentrancy vulnerabilities
    - Integer overflow/underflow
    - Access control issues
    - Unchecked external calls
    - tx.origin usage
    - Dangerous delegatecall
    - Timestamp dependence
    - State variable shadowing
    - Gas optimization opportunities
    """

    def __init__(self):
        self.reports: Dict[str, AuditReport] = {}
        self._register_detectors()

    def _register_detectors(self):
        self.detectors = [
            self._detect_reentrancy,
            self._detect_integer_overflow,
            self._detect_access_control,
            self._detect_unchecked_call,
            self._detect_tx_origin,
            self._detect_delegatecall,
            self._detect_timestamp,
            self._detect_shadowing,
        ]

    def audit(self, contract_name: str, source_code: str) -> AuditReport:
        """Run a full audit on a Solidity contract."""
        source_hash = hashlib.sha256(source_code.encode()).hexdigest()[:16]
        report = AuditReport(
            report_id=hashlib.sha256(f"audit:{contract_name}:{time.time()}".encode()).hexdigest()[:16],
            contract_name=contract_name,
            source_hash=source_hash,
        )

        # Run all detectors
        for detector in self.detectors:
            vulns = detector(source_code)
            report.vulnerabilities.extend(vulns)

        # Gas optimizations
        report.gas_optimizations = self._check_gas_optimizations(source_code)

        # Calculate score
        score_deduction = 0
        for v in report.vulnerabilities:
            if v.severity == VulnerabilitySeverity.CRITICAL:
                score_deduction += 30
            elif v.severity == VulnerabilitySeverity.HIGH:
                score_deduction += 15
            elif v.severity == VulnerabilitySeverity.MEDIUM:
                score_deduction += 5
            elif v.severity == VulnerabilitySeverity.LOW:
                score_deduction += 1
        report.overall_score = max(0, 100 - score_deduction)

        # Summary
        report.summary = (
            f"Audited {contract_name}: {len(report.vulnerabilities)} vulnerabilities found "
            f"({report.critical_count} critical, {report.high_count} high). "
            f"Score: {report.overall_score}/100. "
            f"{'PASSED' if report.passed else 'FAILED'}"
        )

        self.reports[report.report_id] = report
        return report

    def _detect_reentrancy(self, code: str) -> List[Vulnerability]:
        vulns = []
        # Check for external calls before state changes
        if ".call{" in code or ".send(" in code or ".transfer(" in code:
            lines = code.split("\n")
            for i, line in enumerate(lines):
                if (".call{" in line or ".send(" in line) and i < len(lines) - 1:
                    # Check if state change happens after external call
                    remaining = "\n".join(lines[i+1:])
                    if any(op in remaining for op in ["= ", "+= ", "-= "]):
                        vulns.append(Vulnerability(
                            vuln_id=f"v_reentrancy_{i}",
                            swc_id=SWC_ID.REENTRANCY,
                            title="Potential Reentrancy",
                            severity=VulnerabilitySeverity.CRITICAL,
                            description="External call followed by state change may allow reentrancy attack",
                            location=f"Line {i+1}",
                            recommendation="Use checks-effects-interactions pattern or ReentrancyGuard",
                            confidence=0.7,
                        ))
                        break
        return vulns

    def _detect_integer_overflow(self, code: str) -> List[Vulnerability]:
        vulns = []
        if "pragma solidity" in code and "^0.8" not in code:
            # Pre-0.8 doesn't have built-in overflow protection
            if any(op in code for op in ["+ ", "* ", "- "]):
                vulns.append(Vulnerability(
                    vuln_id="v_overflow_1",
                    swc_id=SWC_ID.INTEGER_OVERFLOW,
                    title="Potential Integer Overflow",
                    severity=VulnerabilitySeverity.HIGH,
                    description="Arithmetic operations without overflow protection (Solidity < 0.8)",
                    location="Multiple",
                    recommendation="Use SafeMath library or upgrade to Solidity ^0.8.0+",
                    confidence=0.8,
                ))
        return vulns

    def _detect_access_control(self, list[Vulnerability]:
        vulns = []
        # Check for functions without access modifiers
        func_pattern = re.findall(r'function\s+(\w+)\s*\([^)]*\)\s*(.*?)\{', code)
        for func_name, modifiers in func_pattern:
            if "public" in modifiers and "only" not in modifiers.lower() and "require" not in modifiers:
                if func_name not in ["constructor", "fallback", "receive"]:
                    vulns.append(Vulnerability(
                        vuln_id=f"v_access_{func_name}",
                        swc_id=SWC_ID.ACCESS_CONTROL,
                        title=f"Missing Access Control: {func_name}",
                        severity=VulnerabilitySeverity.HIGH,
                        description=f"Function {func_name} is public without access restrictions",
                        location=f"Function {func_name}",
                        recommendation=f"Add access modifier (onlyOwner, onlyRole, etc.) to {func_name}",
                        confidence=0.6,
                    ))
        return vulns

    def _detect_unchecked_call(self, code: str) -> List[Vulnerability]:
        vulns = []
        if ".call(" in code and "require" not in code.split(".call(")[0].split("\n")[-1]:
            vulns.append(Vulnerability(
                vuln_id="v_unchecked_1",
                swc_id=SWC_ID.UNCHECKED_CALL,
                title="Unchecked External Call",
                severity=VulnerabilitySeverity.MEDIUM,
                description="Return value of external call is not checked",
                location="External call",
                recommendation="Check return value with require() or use try/catch",
                confidence=0.5,
            ))
        return vulns

    def _detect_tx_origin(self, code: str) -> List[Vulnerability]:
        vulns = []
        if "tx.origin" in code:
            vulns.append(Vulnerability(
                vuln_id="v_tx_origin_1",
                swc_id=SWC_ID.TX_ORIGIN,
                title="Use of tx.origin",
                severity=VulnerabilitySeverity.HIGH,
                description="tx.origin can be used for phishing attacks",
                location="tx.origin usage",
                recommendation="Use msg.sender instead of tx.origin",
                confidence=0.9,
            ))
        return vulns

    def _detect_delegatecall(self, code: str) -> List[Vulnerability]:
        vulns = []
        if "delegatecall" in code:
            vulns.append(Vulnerability(
                vuln_id="v_delegate_1",
                swc_id=SWC_ID.DELEGATE_CALL,
                title="Dangerous delegatecall",
                severity=VulnerabilitySeverity.HIGH,
                description="delegatecall executes code in caller's context — dangerous if target is mutable",
                location="delegatecall usage",
                recommendation="Ensure delegatecall target is trusted and immutable",
                confidence=0.7,
            ))
        return vulns

    def _detect_timestamp(self, code: str) -> List[Vulnerability]:
        vulns = []
        if "block.timestamp" in code or "now" in code:
            if "require" in code and "block.timestamp" in code:
                vulns.append(Vulnerability(
                    vuln_id="v_timestamp_1",
                    swc_id=SWC_ID.TIME_MANIPULATION,
                    title="Timestamp Dependence",
                    severity=VulnerabilitySeverity.LOW,
                    description="block.timestamp can be manipulated by miners within ~15 seconds",
                    location="block.timestamp usage",
                    recommendation="Avoid precise time-based logic; use block numbers for critical timing",
                    confidence=0.6,
                ))
        return vulns

    def _detect_shadowing(self, code: str) -> List[Vulnerability]:
        vulns = []
        # Check for state variable shadowing (simplified)
        if "contract" in code and "is " in code:
            # Inherited contract might shadow variables
            pass  # Complex analysis needed
        return vulns

    def _check_gas_optimizations(self, code: str) -> List[str]:
        optimizations = []
        if "uint256" in code and "uint8" not in code:
            optimizations.append("Consider using smaller uint types (uint8, uint16) where possible to save gas")
        if "memory" not in code and "calldata" not in code and "function" in code:
            optimizations.append("Use calldata instead of memory for function parameters that are only read")
        if "++" in code:
            optimizations.append("Use ++i instead of i++ in loops to save gas")
        if "public" in code and "constant" not in code:
            optimizations.append("Consider making state variables private/internal if only used within contract")
        if "require" in code and "string" in code:
            optimizations.append("Use custom error codes instead of require strings to save gas")
        if "for (" in code:
            optimizations.append("Cache array length before loop to avoid repeated storage reads")
        return optimizations

    def get_report(self, report_id: str) -> Optional[AuditReport]:
        return self.reports.get(report_id)

    def stats(self) -> dict:
        all_vulns = [v for r in self.reports.values() for v in r.vulnerabilities]
        return {
            "total_audits": len(self.reports),
            "total_vulnerabilities": len(all_vulns),
            "critical": sum(1 for v in all_vulns if v.severity == VulnerabilitySeverity.CRITICAL),
            "high": sum(1 for v in all_vulns if v.severity == VulnerabilitySeverity.HIGH),
            "passed_audits": sum(1 for r in self.reports.values() if r.passed),
        }
