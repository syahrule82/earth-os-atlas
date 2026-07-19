"""Developer Portal — Main portal structure and pages."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import hashlib, time

@dataclass
class PortalSection:
    """A section of the developer portal."""
    section_id: str
    title: str
    description: str
    icon: str = ""
    order: int = 0

@dataclass
class PortalPage:
    """A single page in the developer portal."""
    page_id: str
    title: str
    section_id: str
    content: str  # Markdown content
    content_type: str = "markdown"  # markdown, api_ref, interactive, playground
    api_endpoint: Optional[str] = None
    code_examples: Dict[str, str] = field(default_factory=dict)  # lang -> code
    last_updated: float = field(default_factory=time.time)
    views: int = 0

class DeveloperPortal:
    """
    The ATLAS Developer Portal.
    
    Sections:
    1. Getting Started (Quick start, installation, first proof)
    2. API Reference (All endpoints with try-it-now)
    3. Guides (Tutorials, walkthroughs, best practices)
    4. Playground (In-browser code execution)
    5. SDKs (Python, TypeScript, Rust, Go documentation)
    6. Architecture (System design, layer diagrams)
    7. Community (Examples, recipes, showcase)
    """

    def __init__(self):
        self.sections: Dict[str, PortalSection] = {}
        self.pages: Dict[str, PortalPage] = {}
        self._create_default_sections()
        self._create_default_pages()

    def _create_default_sections(self):
        sections = [
            ("getting_started", "Getting Started", "Quick start guides and installation", "🚀", 1),
            ("api_reference", "API Reference", "Complete REST API documentation", "📚", 2),
            ("guides", "Guides", "Tutorials and walkthroughs", "📖", 3),
            ("playground", "Playground", "In-browser code execution", "🎮", 4),
            ("sdks", "SDKs", "Client libraries for 4 languages", "📦", 5),
            ("architecture", "Architecture", "System design and diagrams", "🏗️", 6),
            ("community", "Community", "Examples, recipes, showcase", "🌟", 7),
        ]
        for sid, title, desc, icon, order in sections:
            self.sections[sid] = PortalSection(sid, title, desc, icon, order)

    def _create_default_pages(self):
        # Getting Started pages
        self._add_page("quick_start", "Quick Start", "getting_started", "markdown",
                       "# Quick Start\n\n## Install ATLAS\n```bash\ngit clone https://github.com/KOSASIH/earth-os-atlas\ncd earth-os-atlas\npip install -e .[dev]\n```\n\n## Create Your First Proof\n```python\nfrom src.atlas_core.value_recognition import ValueRecognizer, ValueCategory\nfrom decimal import Decimal\n\nvr = ValueRecognizer()\nproof = vr.recognize(\n    creator_id='did:atlas:you',\n    category=ValueCategory.CREATED_KNOWLEDGE,\n    tier='medium',\n    hours=Decimal('8'),\n)\nprint(f'Proof: {proof.proof_id}, Value: {proof.base_value}')\n```",
                       code_examples={
                           "python": "from src.atlas_core.value_recognition import ValueRecognizer, ValueCategory\nvr = ValueRecognizer()\nproof = vr.recognize('did:atlas:you', ValueCategory.CREATED_KNOWLEDGE, 'medium', Decimal('8'))",
                           "typescript": "const proof = await atlas.createProof('did:atlas:you', 'CREATED_KNOWLEDGE', 'medium', 8.0);",
                           "rust": "let proof = client.create_proof(\"did:atlas:you\", ValueCategory::CreatedKnowledge, ComplexityTier::Medium, 8.0).await?;",
                           "go": "proof, _ := client.CreateProof(ctx, \"did:atlas:you\", atlas.CategoryCreatedKnowledge, atlas.TierMedium, 8.0)",
                       })

        # API Reference pages
        self._add_page("api_proof", "Proof API", "api_reference", "api_ref",
                       "# Proof API\n\n## POST /v1/proof/create\nCreate a contribution proof.",
                       api_endpoint="/v1/proof/create")
        self._add_page("api_mint", "Mint API", "api_reference", "api_ref",
                       "# Mint API\n\n## POST /v1/ledger/mint\nMint ATLAS from a verified proof.",
                       api_endpoint="/v1/ledger/mint")
        self._add_page("api_balance", "Balance API", "api_reference", "api_ref",
                       "# Balance API\n\n## GET /v1/ledger/balance/{address}\nCheck ATLAS balance.",
                       api_endpoint="/v1/ledger/balance/{address}")
        self._add_page("api_governance", "Governance API", "api_reference", "api_ref",
                       "# Governance API\n\n## POST /v1/dao/propose\nCreate a governance proposal.",
                       api_endpoint="/v1/dao/propose")

        # Architecture pages
        self._add_page("architecture_overview", "Architecture Overview", "architecture", "markdown",
                       "# ATLAS Architecture\n\n27 layers from Cognitive State to Analytics & Visualization.\n\nSee the full architecture diagram in the README.")

    def _add_page(self, page_id: str, title: str, section_id: str,
                  content_type: str, content: str,
                  api_endpoint: str = None, code_examples: dict = None):
        self.pages[page_id] = PortalPage(
            page_id=page_id, title=title, section_id=section_id,
            content_type=content_type, content=content,
            api_endpoint=api_endpoint, code_examples=code_examples or {},
        )

    def get_page(self, page_id: str) -> Optional[PortalPage]:
        page = self.pages.get(page_id)
        if page:
            page.views += 1
        return page

    def pages_by_section(self, section_id: str) -> List[PortalPage]:
        return [p for p in self.pages.values() if p.section_id == section_id]

    def search(self, query: str) -> List[dict]:
        query_lower = query.lower()
        results = []
        for page in self.pages.values():
            if query_lower in page.title.lower() or query_lower in page.content.lower():
                results.append({"page_id": page.page_id, "title": page.title,
                               "section": page.section_id, "snippet": page.content[:200]})
        return results

    def add_page(self, page: PortalPage) -> None:
        self.pages[page.page_id] = page

    def stats(self) -> dict:
        return {
            "total_sections": len(self.sections),
            "total_pages": len(self.pages),
            "total_views": sum(p.views for p in self.pages.values()),
            "api_endpoints_documented": sum(1 for p in self.pages.values() if p.api_endpoint),
            "code_examples": sum(len(p.code_examples) for p in self.pages.values()),
        }
