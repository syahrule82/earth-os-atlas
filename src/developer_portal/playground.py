"""Code Playground — In-browser code execution against ATLAS API."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import hashlib, time

@dataclass
class PlaygroundExample:
    """A pre-built code example for the playground."""
    example_id: str
    title: str
    description: str
    language: str  # python, typescript, rust, go
    code: str
    expected_output: str = ""
    category: str = "basic"  # basic, intermediate, advanced
    tags: List[str] = field(default_factory=list)

@dataclass
class ExecutionResult:
    """Result of a playground code execution."""
    execution_id: str
    code: str
    language: str
    output: str
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    execution_time_ms: float = 0
    success: bool = True
    timestamp: float = field(default_factory=time.time)

class CodePlayground:
    """
    In-browser code playground for ATLAS.
    
    - Execute Python code against ATLAS API
    - Pre-built examples (create proof, mint, vote, query)
    - Shareable notebook links
    """

    def __init__(self):
        self.examples: Dict[str, PlaygroundExample] = {}
        self.executions: List[ExecutionResult] = []
        self._create_default_examples()

    def _create_default_examples(self):
        examples = [
            PlaygroundExample(
                example_id="create_proof",
                title="Create a Contribution Proof",
                description="Create a proof of value creation",
                language="python",
                code="from src.atlas_core.value_recognition import ValueRecognizer, ValueCategory\nfrom decimal import Decimal\n\nvr = ValueRecognizer()\nproof = vr.recognize(\n    creator_id='did:atlas:alice',\n    category=ValueCategory.CREATED_KNOWLEDGE,\n    tier='medium',\n    hours=Decimal('8'),\n)\nprint(f'Proof ID: {proof.proof_id}')\nprint(f'Base Value: {proof.base_value} ATLAS')\nprint(f'Can Mint: {proof.can_mint}')",
                expected_output="Proof ID: <uuid>\nBase Value: 200.0000 ATLAS\nCan Mint: False",
                category="basic",
                tags=["proof", "value", "beginner"],
            ),
            PlaygroundExample(
                example_id="mint_atlas",
                title="Mint ATLAS Tokens",
                description="Mint ATLAS from a verified proof",
                language="python",
                code="from src.ledger.mint import MintScheduler\nfrom decimal import Decimal\n\nscheduler = MintScheduler()\namount = scheduler.schedule_mint(Decimal('200'), confidence=0.9)\nprint(f'Minted: {amount} ATLAS')\nprint(f'Total minted: {scheduler.minted}')\nprint(f'Current rate: {scheduler.current_rate()}')",
                expected_output="Minted: 90.0000 ATLAS\nTotal minted: 90.0000\nCurrent rate: 100",
                category="basic",
                tags=["mint", "ledger", "beginner"],
            ),
            PlaygroundExample(
                example_id="governance_vote",
                title="Create & Vote on Proposal",
                description="Create a governance proposal and vote",
                language="python",
                code="from src.governance.dao import GovernanceDAO\n\ndao = GovernanceDAO()\ndao.grant_voice('alice', 200)\ndao.grant_voice('bob', 150)\n\nprop = dao.create_proposal('Upgrade Protocol', 'Upgrade to v4', 'alice', 'protocol')\ndao.vote(prop.proposal_id, 'alice', 50, True)\ndao.vote(prop.proposal_id, 'bob', 30, True)\n\npassed = dao.finalize(prop.proposal_id)\nprint(f'Proposal: {prop.title}')\nprint(f'Passed: {passed}')",
                expected_output="Proposal: Upgrade Protocol\nPassed: True",
                category="intermediate",
                tags=["governance", "dao", "voting"],
            ),
            PlaygroundExample(
                example_id="query_knowledge",
                title="Search the Knowledge Graph",
                description="Search contributions semantically",
                language="python",
                code="from src.knowledge_graph.graph import KnowledgeGraph, KnowledgeNode, KnowledgeType\nimport numpy as np\n\ngraph = KnowledgeGraph(embedding_dim=128)\n# Add some nodes\nfor i in range(5):\n    graph.add_node(KnowledgeNode(\n        node_id=f'node_{i}', title=f'Research Paper {i}',\n        creator_did=f'did:atlas:author_{i}',\n        knowledge_type=KnowledgeType.RESEARCH,\n        embedding=np.random.randn(128).astype(np.float32),\n        content_hash=f'hash_{i}'))\n# Search\nquery = np.random.randn(128).astype(np.float32)\nresults = graph.search_vector(query, k=3)\nprint(f'Found {len(results)} results')\nfor nid, sim in results:\n    print(f'  {graph.nodes[nid].title}: similarity={sim:.4f}')",
                expected_output="Found 3 results\n  Research Paper X: similarity=0.XXXX",
                category="advanced",
                tags=["knowledge", "search", "semantic"],
            ),
            PlaygroundExample(
                example_id="carbon_credits",
                title="Create & Retire Carbon Credits",
                description="Issue and retire carbon credits",
                language="python",
                code="from src.sustainability.carbon import CarbonCreditSystem, CarbonProject\nfrom decimal import Decimal\n\nsystem = CarbonCreditSystem()\nproject = CarbonProject(\n    project_id='proj_1', name='Amazon Reforestation',\n    project_type='reforestation', location='BR',\n    area_hectares=10000, expected_tons_per_year=5000,\n    verifier='', verification_sources=[],\n    start_date=__import__('time').time())\nsystem.register_project(project)\nsystem.verify_project('proj_1', 'gaea', ['satellite', 'iot'])\ncredits = system.issue_credits('proj_1', Decimal('10'), 'did:atlas:alice')\nprint(f'Issued {len(credits)} carbon credits')\nsystem.retire_credit(credits[0].credit_id, 'did:atlas:alice')\nprint(f'Retired 1 credit (1 ton CO2 offset)')\nprint(f'Stats: {system.stats()}')",
                expected_output="Issued 10 carbon credits\nRetired 1 credit (1 ton CO2 offset)",
                category="intermediate",
                tags=["sustainability", "carbon", "ecology"],
            ),
        ]
        for ex in examples:
            self.examples[ex.example_id] = ex

    def execute(self, code: str, language: str = "python") -> ExecutionResult:
        """Execute code in the playground (simulated)."""
        start = time.time()
        # In production: run in isolated sandbox container
        # Here: simulate execution
        output = self._simulate_execution(code)
        execution_time = (time.time() - start) * 1000

        result = ExecutionResult(
            execution_id=hashlib.sha256(f"exec:{time.time()}".encode()).hexdigest()[:16],
            code=code, language=language,
            output=output,
            execution_time_ms=execution_time,
            success="Error" not in output,
        )
        self.executions.append(result)
        return result

    def _simulate_execution(self, code: str) -> str:
        """Simulate code execution output."""
        if "create_proof" in code or "ValueRecognizer" in code:
            return "Proof ID: a1b2c3d4e5f6\nBase Value: 200.0000 ATLAS\nCan Mint: False"
        elif "schedule_mint" in code or "MintScheduler" in code:
            return "Minted: 90.0000 ATLAS\nTotal minted: 90.0000\nCurrent rate: 100"
        elif "GovernanceDAO" in code:
            return "Proposal: Upgrade Protocol\nPassed: True"
        elif "KnowledgeGraph" in code:
            return "Found 3 results\n  Research Paper 2: similarity=0.8234\n  Research Paper 0: similarity=0.7891\n  Research Paper 4: similarity=0.6543"
        elif "CarbonCreditSystem" in code:
            return "Issued 10 carbon credits\nRetired 1 credit (1 ton CO2 offset)\nStats: {'total_projects': 1, 'total_credits': 10, 'retired_credits': 1}"
        return "Execution completed."

    def get_example(self, example_id: str) -> Optional[PlaygroundExample]:
        return self.examples.get(example_id)

    def list_examples(self, category: str = None, language: str = None) -> List[dict]:
        results = list(self.examples.values())
        if category:
            results = [e for e in results if e.category == category]
        if language:
            results = [e for e in results if e.language == language]
        return [{"id": e.example_id, "title": e.title, "category": e.category,
                 "language": e.language, "tags": e.tags} for e in results]

    def share_link(self, code: str, language: str = "python") -> str:
        """Generate a shareable link for code."""
        link_id = hashlib.sha256(f"{code}:{time.time()}".encode()).hexdigest()[:16]
        return f"https://playground.atlas.kosasih.org/share/{link_id}"

    def stats(self) -> dict:
        return {
            "total_examples": len(self.examples),
            "total_executions": len(self.executions),
            "successful_executions": sum(1 for e in self.executions if e.success),
            "by_category": {cat: sum(1 for e in self.examples.values() if e.category == cat)
                           for cat in ["basic", "intermediate", "advanced"]},
        }
