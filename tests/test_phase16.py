"""Phase 16 integration tests."""
from decimal import Decimal
from src.developer_portal.portal import DeveloperPortal, PortalPage
from src.developer_portal.sandbox import SandboxEnvironment, MockDataGenerator, TransactionSimulator
from src.developer_portal.playground import CodePlayground, PlaygroundExample
from src.developer_portal.tutorials import TutorialSystem, TutorialLevel
from src.developer_portal.doc_generator import DocGenerator, MermaidDiagramGenerator

def test_developer_portal():
    portal = DeveloperPortal()
    assert len(portal.sections) >= 7
    assert len(portal.pages) >= 5
    # Get page
    page = portal.get_page("quick_start")
    assert page is not None
    assert page.title == "Quick Start"
    assert page.views == 1  # Incremented on access
    assert len(page.code_examples) >= 4  # Python, TS, Rust, Go
    # Pages by section
    api_pages = portal.pages_by_section("api_reference")
    assert len(api_pages) >= 4
    # Search
    results = portal.search("proof")
    assert len(results) >= 1
    stats = portal.stats()
    assert stats["total_sections"] >= 7

def test_sandbox_environment():
    sandbox = SandboxEnvironment()
    # Pre-funded accounts
    assert len(sandbox.accounts) == 10
    assert sandbox.get_balance("did:atlas:sandbox_user_0") == Decimal("10000")
    # Transfer
    assert sandbox.transfer("did:atlas:sandbox_user_0", "did:atlas:sandbox_user_1", Decimal("100"))
    assert sandbox.get_balance("did:atlas:sandbox_user_0") == Decimal("9900")
    assert sandbox.get_balance("did:atlas:sandbox_user_1") == Decimal("10100")
    # Insufficient funds
    assert not sandbox.transfer("did:atlas:sandbox_user_0", "did:atlas:sandbox_user_1", Decimal("999999"))
    # Mint
    sandbox.mint("did:atlas:sandbox_user_0", Decimal("500"))
    assert sandbox.get_balance("did:atlas:sandbox_user_0") == Decimal("10400")
    # Save/restore state
    state_id = sandbox.save_state()
    sandbox.transfer("did:atlas:sandbox_user_0", "did:atlas:sandbox_user_1", Decimal("1000"))
    assert sandbox.restore_state(state_id)
    assert sandbox.get_balance("did:atlas:sandbox_user_0") == Decimal("10400")  # Restored
    # Mock data
    proofs = sandbox.get_mock_data("proofs", count=5)
    assert len(proofs) == 5
    assert all("proof_id" in p for p in proofs)
    users = sandbox.get_mock_data("users", count=20)
    assert len(users) == 20
    # Reset
    sandbox.reset()
    assert sandbox.get_balance("did:atlas:sandbox_user_0") == Decimal("10000")
    stats = sandbox.stats()
    assert stats["total_accounts"] == 10

def test_mock_data_generator():
    gen = MockDataGenerator()
    proofs = gen.generate_proofs(10)
    assert len(proofs) == 10
    assert all("category" in p for p in proofs)
    txs = gen.generate_transactions(20)
    assert len(txs) == 20
    proposals = gen.generate_proposals(5)
    assert len(proposals) == 5
    users = gen.generate_users(50)
    assert len(users) == 50
    assert all("did" in u for u in users)

def test_transaction_simulator():
    sim = TransactionSimulator()
    scenario_id = sim.create_scenario("Test Flow", "A test scenario", [
        {"action": "create_proof", "params": {"category": "CREATED_KNOWLEDGE"}},
        {"action": "mint", "params": {"amount": 100}},
        {"action": "transfer", "params": {"to": "bob", "amount": 50}},
    ])
    result = sim.run_scenario(scenario_id)
    assert result["steps_executed"] == 3
    assert len(result["results"]) == 3

def test_code_playground():
    playground = CodePlayground()
    # Default examples
    assert len(playground.examples) >= 5
    examples = playground.list_examples()
    assert len(examples) >= 5
    # Get example
    ex = playground.get_example("create_proof")
    assert ex is not None
    assert ex.language == "python"
    assert ex.category == "basic"
    # Execute code
    result = playground.execute("from src.atlas_core.value_recognition import ValueRecognizer", "python")
    assert result.execution_id is not None
    assert result.success is True
    # Execute with known output
    result2 = playground.execute("vr = ValueRecognizer()\nproof = vr.recognize('did:atlas:alice', ValueCategory.CREATED_KNOWLEDGE, 'medium', Decimal('8'))")
    assert "Proof ID" in result2.output or result2.success
    # Share link
    link = playground.share_link("print('hello')")
    assert "playground.atlas" in link
    # List by category
    basic = playground.list_examples(category="basic")
    assert all(e["category"] == "basic" for e in basic)
    stats = playground.stats()
    assert stats["total_examples"] >= 5

def test_tutorial_system():
    ts = TutorialSystem()
    assert len(ts.tutorials) >= 7
    # Get tutorial
    tutorial = ts.get_tutorial("basics")
    assert tutorial is not None
    assert tutorial.level == TutorialLevel.BEGINNER
    assert len(tutorial.steps) >= 3
    assert tutorial.badge is not None
    # List by track
    core_tutorials = ts.list_tutorials(track="core")
    assert len(core_tutorials) >= 2
    # Start tutorial
    assert ts.start_tutorial("did:atlas:student", "basics")
    # Complete steps
    step = ts.complete_step("did:atlas:student", "basics")
    assert step == 1  # Advanced to step 2
    step = ts.complete_step("did:atlas:student", "basics")
    assert step == 2  # Advanced to step 3
    step = ts.complete_step("did:atlas:student", "basics")
    assert step == -1  # Completed
    # Check progress
    progress = ts.get_progress("did:atlas:student")
    assert progress["tutorials_completed"] == 1
    assert len(progress["badges"]) == 1
    assert progress["badges"][0]["name"] == "ATLAS Basics Complete"
    stats = ts.stats()
    assert stats["total_tutorials"] >= 7

def test_doc_generator():
    gen = DocGenerator()
    # Generate from source code
    source = '''\"\"\"Module docstring.\"\"\"\nclass MyClass:\n    \"\"\"A test class.\"\"\"\n    def method_one(self):\n        \"\"\"Does something.\"\"\"\n        pass\n\ndef standalone_func():\n    \"\"\"A standalone function.\"\"\"\n    pass\n'''
    doc = gen.generate_module_doc("test_module", source)
    assert doc.module_name == "test_module"
    assert len(doc.classes) >= 1
    assert doc.classes[0]["name"] == "MyClass"
    # Convert to markdown
    md = gen.to_markdown("test_module")
    assert "# test_module" in md
    assert "MyClass" in md
    # Mermaid diagrams
    mermaid_gen = MermaidDiagramGenerator()
    arch = mermaid_gen.architecture_diagram(["Layer1", "Layer2", "Layer3"])
    assert "graph TD" in arch
    assert "L0[Layer1]" in arch
    flow = mermaid_gen.flow_diagram(["Step1", "Step2", "Step3"])
    assert "graph LR" in flow
    seq = mermaid_gen.sequence_diagram(["Alice", "Bob"], [("Alice", "Bob", "Hello")])
    assert "sequenceDiagram" in seq
    assert "Alice->>Bob: Hello" in seq
    # Architecture doc
    arch_doc = gen.generate_architecture_doc(["Layer1", "Layer2"])
    assert "# ATLAS Architecture" in arch_doc
    assert "```mermaid" in arch_doc
    # Changelog
    changelog = gen.generate_changelog([
        {"date": "2026-07-19", "message": "feat: Phase 16"},
        {"date": "2026-07-19", "message": "fix: badge update"},
    ])
    assert "# Changelog" in changelog
    assert "Phase 16" in changelog
    stats = gen.stats()
    assert stats["total_docs"] >= 1

if __name__ == "__main__":
    test_developer_portal()
    test_sandbox_environment()
    test_mock_data_generator()
    test_transaction_simulator()
    test_code_playground()
    test_tutorial_system()
    test_doc_generator()
    print("✅ All Phase 16 tests passed")
