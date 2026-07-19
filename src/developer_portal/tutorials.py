"""Tutorial System — Interactive walkthroughs with progress tracking."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import hashlib, time

class TutorialLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class TutorialStep:
    """A single step in a tutorial."""
    step_number: int
    title: str
    instructions: str
    expected_code: str = ""
    expected_output: str = ""
    hint: str = ""
    validation: str = ""  # Validation rule

@dataclass
class TutorialBadge:
    """A badge earned by completing a tutorial."""
    badge_id: str
    name: str
    description: str
    icon: str = "🏆"
    tutorial_id: str = ""
    earned_at: float = field(default_factory=time.time)

@dataclass
class Tutorial:
    """A complete interactive tutorial."""
    tutorial_id: str
    title: str
    description: str
    level: TutorialLevel
    track: str  # "core", "governance", "economy", "advanced"
    steps: List[TutorialStep] = field(default_factory=list)
    estimated_minutes: int = 15
    badge: Optional[TutorialBadge] = None
    prerequisites: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

class TutorialSystem:
    """
    Interactive tutorial system with 7 levels.
    
    Tracks:
    - 1. ATLAS Basics (What is Proof-of-Value?)
    - 2. First Proof (Create your first contribution)
    - 3. Minting (Mint your first ATLAS)
    - 4. Governance (Vote on a proposal)
    - 5. Economy (Understand bonding curves & AMM)
    - 6. Identity (Set up DID + MFA)
    - 7. Advanced (Build a dApp on ATLAS)
    """

    def __init__(self):
        self.tutorials: Dict[str, Tutorial] = {}
        self.user_progress: Dict[str, Dict[str, int]] = {}  # user_did -> {tutorial_id: step}
        self.badges: Dict[str, List[TutorialBadge]] = {}  # user_did -> [badges]
        self._create_default_tutorials()

    def _create_default_tutorials(self):
        tutorials = [
            ("basics", "ATLAS Basics", "Learn what Proof-of-Value means",
             TutorialLevel.BEGINNER, "core", 10,
             [TutorialStep(1, "What is ATLAS?", "ATLAS is a value-creation currency. Unlike fiat (debt) or crypto (speculation), ATLAS is minted from verified human contribution.",
                          expected_output="Understanding confirmed"),
              TutorialStep(2, "The 4 Titans", "HERMES discovers value, PROMETHEUS validates it, GAEA verifies ground truth, CHRONOS predicts future trends.",
                          expected_output="Understanding confirmed"),
              TutorialStep(3, "12 Value Categories", "ATLAS recognizes 12 categories of value: from solving problems to creating beauty.",
                          expected_output="Understanding confirmed")]),
            ("first_proof", "Your First Proof", "Create your first contribution proof",
             TutorialLevel.BEGINNER, "core", 15,
             [TutorialStep(1, "Import the library", "Import ValueRecognizer from atlas_core.",
                          expected_code="from src.atlas_core.value_recognition import ValueRecognizer, ValueCategory",
                          expected_output="Import successful"),
              TutorialStep(2, "Create recognizer", "Initialize the ValueRecognizer.",
                          expected_code="vr = ValueRecognizer()",
                          expected_output="ValueRecognizer initialized"),
              TutorialStep(3, "Create proof", "Create a proof for 8 hours of knowledge creation.",
                          expected_code="proof = vr.recognize('did:atlas:you', ValueCategory.CREATED_KNOWLEDGE, 'medium', Decimal('8'))",
                          expected_output="Proof created with base value 200.0000")]),
            ("minting", "Mint Your First ATLAS", "Mint ATLAS from a verified proof",
             TutorialLevel.BEGINNER, "economy", 15,
             [TutorialStep(1, "Import MintScheduler", "Import the minting module.",
                          expected_code="from src.ledger.mint import MintScheduler"),
              TutorialStep(2, "Schedule mint", "Schedule a mint with 90% confidence.",
                          expected_code="scheduler = MintScheduler()\namount = scheduler.schedule_mint(Decimal('200'), confidence=0.9)",
                          expected_output="Minted: 90.0000 ATLAS")]),
            ("governance", "Participate in Governance", "Vote on a governance proposal",
             TutorialLevel.INTERMEDIATE, "governance", 20,
             [TutorialStep(1, "Create DAO", "Initialize the GovernanceDAO.",
                          expected_code="from src.governance.dao import GovernanceDAO\ndao = GovernanceDAO()"),
              TutorialStep(2, "Grant voice credits", "Grant voice credits to voters.",
                          expected_code="dao.grant_voice('alice', 200)"),
              TutorialStep(3, "Create proposal", "Create a governance proposal.",
                          expected_code="prop = dao.create_proposal('Title', 'Description', 'alice', 'protocol')"),
              TutorialStep(4, "Vote", "Cast your vote.",
                          expected_code="dao.vote(prop.proposal_id, 'alice', 50, True)"),
              TutorialStep(5, "Finalize", "Finalize the proposal.",
                          expected_code="passed = dao.finalize(prop.proposal_id)\nprint(f'Passed: {passed}')",
                          expected_output="Passed: True")]),
            ("economy", "Understanding the Economy", "Learn bonding curves and AMM",
             TutorialLevel.INTERMEDIATE, "economy", 25,
             [TutorialStep(1, "Bonding curves", "Create a linear bonding curve.",
                          expected_code="from src.economy.bonding import LinearCurve\nfrom decimal import Decimal\ncurve = LinearCurve(Decimal('1'), Decimal('0.01'))"),
              TutorialStep(2, "AMM pool", "Create an AMM pool.",
                          expected_code="from src.economy.amm import ATLASPool\npool = ATLASPool('p1', 'ATLAS', 'USDC', Decimal('1000'), Decimal('1000'))")]),
            ("identity", "Set Up Identity", "Create DID and multi-factor auth",
             TutorialLevel.ADVANCED, "core", 30,
             [TutorialStep(1, "Create DID", "Create a DID:atlas.",
                          expected_code="from src.identity_layer.did import AtlasDID\ndid = AtlasDID(public_key=b'my_key')\nprint(did.did)"),
              TutorialStep(2, "Register MFA", "Register multi-factor authentication.",
                          expected_code="from src.identity_layer.multifactor import MultiFactorAuth, FactorType\nmfa = MultiFactorAuth()\nmfa.register_factor(did.did, FactorType.CRYPTOGRAPHIC, 'pub_data')")]),
            ("advanced", "Build a dApp", "Build a complete dApp on ATLAS",
             TutorialLevel.EXPERT, "advanced", 45,
             [TutorialStep(1, "Set up project", "Create your dApp structure.",
                          expected_code="# Project structure\n# my_dapp/\n# ├── main.py\n# ├── config.py\n# └── requirements.txt"),
              TutorialStep(2, "Connect to ATLAS", "Connect to the ATLAS API.",
                          expected_code="from src.sdk.python_sdk import AtlasClient\nclient = AtlasClient('http://localhost:8000')"),
              TutorialStep(3, "Create value loop", "Implement a value creation loop.",
                          expected_code="# Create proof, get attestation, mint ATLAS\nproof = client.create_proof(...)\nminted = client.mint(proof.proof_id)")]),
        ]

        for tid, title, desc, level, track, minutes, steps in tutorials:
            badge = TutorialBadge(
                badge_id=f"badge_{tid}",
                name=f"{title} Complete",
                description=f"Completed the {title} tutorial",
                icon="🏆", tutorial_id=tid,
            )
            tutorial = Tutorial(
                tutorial_id=tid, title=title, description=desc,
                level=level, track=track, steps=steps,
                estimated_minutes=minutes, badge=badge,
            )
            self.tutorials[tid] = tutorial

    def get_tutorial(self, tutorial_id: str) -> Optional[Tutorial]:
        return self.tutorials.get(tutorial_id)

    def list_tutorials(self, track: str = None, level: TutorialLevel = None) -> List[dict]:
        results = list(self.tutorials.values())
        if track:
            results = [t for t in results if t.track == track]
        if level:
            results = [t for t in results if t.level == level]
        return [{"id": t.tutorial_id, "title": t.title, "level": t.level.value,
                 "track": t.track, "steps": len(t.steps), "minutes": t.estimated_minutes}
                for t in results]

    def start_tutorial(self, user_did: str, tutorial_id: str) -> bool:
        if tutorial_id not in self.tutorials:
            return False
        if user_did not in self.user_progress:
            self.user_progress[user_did] = {}
        self.user_progress[user_did][tutorial_id] = 0
        return True

    def complete_step(self, user_did: str, tutorial_id: str) -> int:
        """Complete the current step and advance. Returns new step number."""
        if user_did not in self.user_progress or tutorial_id not in self.user_progress[user_did]:
            return -1
        tutorial = self.tutorials.get(tutorial_id)
        if not tutorial:
            return -1
        current = self.user_progress[user_did][tutorial_id]
        if current < len(tutorial.steps) - 1:
            self.user_progress[user_did][tutorial_id] = current + 1
            return current + 1
        else:
            # Tutorial complete — award badge
            self._award_badge(user_did, tutorial.badge)
            return -1  # Completed

    def _award_badge(self, user_did: str, badge: TutorialBadge) -> None:
        if user_did not in self.badges:
            self.badges[user_did] = []
        self.badges[user_did].append(badge)

    def get_progress(self, user_did: str) -> dict:
        progress = self.user_progress.get(user_did, {})
        badges = self.badges.get(user_did, [])
        return {
            "tutorials_started": len(progress),
            "tutorials_completed": len(badges),
            "badges": [{"name": b.name, "icon": b.icon, "tutorial": b.tutorial_id} for b in badges],
            "progress": {tid: {"step": step, "total": len(self.tutorials[tid].steps)}
                        for tid, step in progress.items() if tid in self.tutorials},
        }

    def stats(self) -> dict:
        return {
            "total_tutorials": len(self.tutorials),
            "total_steps": sum(len(t.steps) for t in self.tutorials.values()),
            "tracks": list(set(t.track for t in self.tutorials.values())),
            "levels": list(set(t.level.value for t in self.tutorials.values())),
        }
