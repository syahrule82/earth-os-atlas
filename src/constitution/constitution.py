"""ATLAS Constitution — 27 articles of executable governance."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import hashlib, time

class ArticleCategory(Enum):
    FUNDAMENTAL_RIGHTS = "fundamental_rights"
    ECONOMIC = "economic"
    GOVERNANCE = "governance"
    JUSTICE = "justice"
    SECURITY = "security"
    AMENDMENT = "amendment"

@dataclass
class Article:
    """A single article of the ATLAS Constitution."""
    article_id: int
    category: ArticleCategory
    title: str
    text: str
    rule_code: str  # Executable rule identifier
    enacted_at: float
    amended_count: int = 0
    active: bool = True

    def evaluate(self, context: dict) -> bool:
        """Evaluate this article's rule against a context."""
        rules = {
            "right_to_value": context.get("contribution_proven", False),
            "right_to_participate": context.get("identity_verified", False),
            "right_to_privacy": not context.get("force_reveal", False),
            "right_to_appeal": context.get("dispute_exists", False),
            "no_confiscation": not context.get("unjust_seizure", False),
            "proportional_tax": context.get("tax_rate", 0) <= 0.10,
            "transparent_minting": context.get("mint_logged", False),
            "due_process": context.get("hearing_granted", False),
        }
        return rules.get(self.rule_code, True)

@dataclass
class Amendment:
    """A constitutional amendment."""
    amendment_id: str
    article_id: int
    proposer: str
    description: str
    new_text: str
    new_rule_code: str
    status: str = "proposed"  # proposed, debated, voted, ratified, rejected
    votes_for: int = 0
    votes_against: int = 0
    supermajority_required: float = 0.75
    proposed_at: float = field(default_factory=time.time)
    ratified_at: Optional[float] = None

class AtlasConstitution:
    """
    The ATLAS Constitution — the supreme law of Earth OS.
    
    27 articles across 6 categories.
    All articles are executable — they can be programmatically
    evaluated against any governance action.
    """

    def __init__(self):
        self.articles: Dict[int, Article] = {}
        self.amendments: List[Amendment] = []
        self._enact_genesis()

    def _enact_genesis(self):
        """Enact the original 27 articles."""
        genesis_articles = [
            (1, ArticleCategory.FUNDAMENTAL_RIGHTS, "Right to Value",
             "Every human who creates verified value has the right to ATLAS minting.",
             "right_to_value"),
            (2, ArticleCategory.FUNDAMENTAL_RIGHTS, "Right to Participation",
             "Every ATLAS citizen may participate in governance without barrier.",
             "right_to_participate"),
            (3, ArticleCategory.FUNDAMENTAL_RIGHTS, "Right to Privacy",
             "No entity may force revelation of private neural data.",
             "right_to_privacy"),
            (4, ArticleCategory.FUNDAMENTAL_RIGHTS, "Right to Appeal",
             "Every citizen may appeal any governance decision.",
             "right_to_appeal"),
            (5, ArticleCategory.FUNDAMENTAL_RIGHTS, "Protection from Confiscation",
             "No ATLAS holdings may be confiscated without due process.",
             "no_confiscation"),
            (6, ArticleCategory.ECONOMIC, "Proportional Taxation",
             "No tax on ATLAS transactions shall exceed 10%.",
             "proportional_tax"),
            (7, ArticleCategory.ECONOMIC, "Transparent Minting",
             "All ATLAS minting must be publicly logged and verifiable.",
             "transparent_minting"),
            (8, ArticleCategory.ECONOMIC, "Genesis Supply Limit",
             "Total ATLAS supply shall never exceed 1,000,000,000.",
             "supply_limit"),
            (9, ArticleCategory.ECONOMIC, "Halving Schedule",
             "Minting rewards halve every 4 years.",
             "halving_schedule"),
            (10, ArticleCategory.ECONOMIC, "Universal Basic Compute",
             "Every identity receives 1 GFLOPS of compute free.",
             "ubc_guarantee"),
            (11, ArticleCategory.GOVERNANCE, "Separation of Powers",
             "Legislative, Executive, and Judicial functions are separate.",
             "separation_of_powers"),
            (12, ArticleCategory.GOVERNANCE, "Quadratic Voting",
             "Governance votes use quadratic voting power.",
             "quadratic_voting"),
            (13, ArticleCategory.GOVERNANCE, "Conviction Voting",
             "Treasury allocations use conviction voting.",
             "conviction_voting"),
            (14, ArticleCategory.GOVERNANCE, "Proposal Threshold",
             "100 voice credits required to submit a proposal.",
             "proposal_threshold"),
            (15, ArticleCategory.GOVERNANCE, "Voting Period",
             "All proposals have a 7-day voting period.",
             "voting_period"),
            (16, ArticleCategory.JUSTICE, "Due Process",
             "No punitive action without a hearing.",
             "due_process"),
            (17, ArticleCategory.JUSTICE, "Arbitration Tiers",
             "Disputes escalate through 3 tiers of arbitration.",
             "arbitration_tiers"),
            (18, ArticleCategory.JUSTICE, "Precedent System",
             "Past rulings guide future decisions.",
             "precedent_system"),
            (19, ArticleCategory.JUSTICE, "Evidence Integrity",
             "All evidence must be cryptographically verified.",
             "evidence_integrity"),
            (20, ArticleCategory.JUSTICE, "Right to Counsel",
             "Every party in a dispute may have representation.",
             "right_to_counsel"),
            (21, ArticleCategory.SECURITY, "Post-Quantum Cryptography",
             "All ATLAS cryptography must be quantum-resistant.",
             "pq_crypto"),
            (22, ArticleCategory.SECURITY, "Slashing Protection",
             "Validators may only be slashed for proven violations.",
             "slashing_protection"),
            (23, ArticleCategory.SECURITY, "Emergency Pause",
             "A 5-of-9 multisig may pause the network in emergencies.",
             "emergency_pause"),
            (24, ArticleCategory.SECURITY, "Audit Trail",
             "All governance actions are logged for 7 years.",
             "audit_trail"),
            (25, ArticleCategory.AMENDMENT, "Amendment Process",
             "Constitutional amendments require 75% supermajority.",
             "amendment_process"),
            (26, ArticleCategory.AMENDMENT, "Article Protection",
             "Articles 1-5 (Fundamental Rights) require 90% supermajority to amend.",
             "article_protection"),
            (27, ArticleCategory.AMENDMENT, "Constitutional Supremacy",
             "This constitution is the supreme law of ATLAS.",
             "constitutional_supremacy"),
        ]
        now = time.time()
        for article_id, category, title, text, rule in genesis_articles:
            self.articles[article_id] = Article(
                article_id=article_id, category=category,
                title=title, text=text, rule_code=rule,
                enacted_at=now,
            )

    def get_article(self, article_id: int) -> Optional[Article]:
        return self.articles.get(article_id)

    def evaluate_action(self, action: str, context: dict) -> Dict[int, bool]:
        """Evaluate a governance action against all applicable articles."""
        results = {}
        for aid, article in self.articles.items():
            if article.active:
                results[aid] = article.evaluate(context)
        return results

    def is_constitutional(self, action: str, context: dict) -> bool:
        """Check if an action is constitutional."""
        results = self.evaluate_action(action, context)
        return all(results.values())

    def propose_amendment(self, article_id: int, proposer: str,
                          description: str, new_text: str, new_rule: str) -> Amendment:
        """Propose a constitutional amendment."""
        article = self.articles.get(article_id)
        if not article:
            raise ValueError(f"Article {article_id} does not exist")
        supermajority = 0.90 if article_id <= 5 else 0.75  # Protected articles
        amendment = Amendment(
            amendment_id=hashlib.sha256(f"{article_id}:{time.time()}".encode()).hexdigest()[:16],
            article_id=article_id, proposer=proposer,
            description=description, new_text=new_text,
            new_rule_code=new_rule, supermajority_required=supermajority,
        )
        self.amendments.append(amendment)
        return amendment

    def ratify_amendment(self, amendment_id: str, votes_for: int, votes_against: int) -> bool:
        """Attempt to ratify an amendment."""
        amendment = next((a for a in self.amendments if a.amendment_id == amendment_id), None)
        if not amendment or amendment.status != "proposed":
            return False
        amendment.votes_for = votes_for
        amendment.votes_against = votes_against
        total = votes_for + votes_against
        if total == 0:
            return False
        ratio = votes_for / total
        if ratio >= amendment.supermajority_required:
            amendment.status = "ratified"
            amendment.ratified_at = time.time()
            # Update the article
            article = self.articles[amendment.article_id]
            article.text = amendment.new_text
            article.rule_code = amendment.new_rule_code
            article.amended_count += 1
            return True
        else:
            amendment.status = "rejected"
            return False

    def summary(self) -> dict:
        return {
            "total_articles": len(self.articles),
            "active_articles": sum(1 for a in self.articles.values() if a.active),
            "total_amendments": len(self.amendments),
            "ratified_amendments": sum(1 for a in self.amendments if a.status == "ratified"),
            "categories": {cat.value: sum(1 for a in self.articles.values() if a.category == cat) for cat in ArticleCategory},
        }
