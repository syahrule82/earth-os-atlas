"""Governance Analytics — Proposal stats, voter metrics, deliberation history."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict
import time

@dataclass
class ProposalStats:
    """Statistics for governance proposals."""
    total_proposals: int = 0
    passed: int = 0
    rejected: int = 0
    tabled: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)
    avg_voting_period_days: float = 7.0
    success_rate: float = 0.0

@dataclass
class VoterMetrics:
    """Metrics about voter participation."""
    total_voters: int = 0
    active_voters_30d: int = 0
    avg_participation_rate: float = 0.0
    top_voters: List[dict] = field(default_factory=list)
    participation_trend: List[dict] = field(default_factory=list)
    quadratic_voting_distribution: List[dict] = field(default_factory=list)

class GovernanceAnalytics:
    """Analyzes governance data for dashboards and reports."""

    def __init__(self):
        self.proposals: List[dict] = []
        self.votes: List[dict] = []
        self.congress_results: List[dict] = []

    def record_proposal(self, proposal: dict) -> None:
        self.proposals.append(proposal)

    def record_vote(self, vote: dict) -> None:
        self.votes.append(vote)

    def record_congress_result(self, result: dict) -> None:
        self.congress_results.append(result)

    def proposal_stats(self) -> ProposalStats:
        """Calculate proposal statistics."""
        stats = ProposalStats(total_proposals=len(self.proposals))
        for p in self.proposals:
            status = p.get("status", "unknown")
            if status == "passed":
                stats.passed += 1
            elif status == "rejected":
                stats.rejected += 1
            elif status == "tabled":
                stats.tabled += 1
            cat = p.get("category", "uncategorized")
            stats.by_category[cat] = stats.by_category.get(cat, 0) + 1
        if stats.total_proposals > 0:
            stats.success_rate = stats.passed / stats.total_proposals
        return stats

    def voter_metrics(self) -> VoterMetrics:
        """Calculate voter participation metrics."""
        metrics = VoterMetrics()
        unique_voters = set(v.get("voter") for v in self.votes)
        metrics.total_voters = len(unique_voters)

        # Active in last 30 days
        cutoff = time.time() - 30 * 86400
        active = set(v.get("voter") for v in self.votes if v.get("timestamp", 0) >= cutoff)
        metrics.active_voters_30d = len(active)

        # Participation trend (monthly)
        monthly = defaultdict(int)
        for v in self.votes:
            month = int(v.get("timestamp", time.time()) // (30 * 86400))
            monthly[month] += 1
        metrics.participation_trend = [
            {"month": k, "votes": v} for k, v in sorted(monthly.items())
        ]

        # Top voters
        voter_counts = defaultdict(int)
        for v in self.votes:
            voter_counts[v.get("voter", "")] += 1
        metrics.top_voters = [
            {"voter": k, "vote_count": v}
            for k, v in sorted(voter_counts.items(), key=lambda x: -x[1])[:10]
        ]

        # Quadratic voting distribution
        voice_credits = defaultdict(int)
        for v in self.votes:
            voice_credits[v.get("voter", "")] += v.get("voice_credits", 1)
        metrics.quadratic_voting_distribution = [
            {"voter": k, "credits": v, "quadratic_power": int(v ** 0.5)}
            for k, v in sorted(voice_credits.items(), key=lambda x: -x[1])[:20]
        ]

        if metrics.total_voters > 0:
            metrics.avg_participation_rate = metrics.active_voters_30d / metrics.total_voters

        return metrics

    def congress_history(self) -> List[dict]:
        """Get Titan deliberation history."""
        return self.congress_results[-50:]  # Last 50 sessions

    def proposal_success_by_category(self) -> List[dict]:
        """Success rate by proposal category."""
        cat_stats = defaultdict(lambda: {"total": 0, "passed": 0})
        for p in self.proposals:
            cat = p.get("category", "uncategorized")
            cat_stats[cat]["total"] += 1
            if p.get("status") == "passed":
                cat_stats[cat]["passed"] += 1
        return [
            {"category": cat, "total": s["total"], "passed": s["passed"],
             "success_rate": s["passed"] / max(1, s["total"])}
            for cat, s in sorted(cat_stats.items(), key=lambda x: -x[1]["total"])
        ]

    def summary(self) -> dict:
        ps = self.proposal_stats()
        vm = self.voter_metrics()
        return {
            "total_proposals": ps.total_proposals,
            "proposal_success_rate": ps.success_rate,
            "total_voters": vm.total_voters,
            "active_voters_30d": vm.active_voters_30d,
            "participation_rate": vm.avg_participation_rate,
            "congress_sessions": len(self.congress_results),
        }
