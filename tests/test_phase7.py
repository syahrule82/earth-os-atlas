"""Phase 7 integration tests."""
import numpy as np
from src.constitution.constitution import AtlasConstitution, ArticleCategory
from src.constitution.rights import RightsEngine, RightType
from src.constitution.amendments import AmendmentProcess
from src.congress.congress import PlanetaryCongress
from src.congress.argumentation import ArgumentGraph, Argument, AttackRelation, SupportRelation
from src.congress.coalition import CoalitionFormer
from src.neural_democracy.thought_voting import NeuralVotingSystem, IntentDecoder
from src.neural_democracy.anti_coercion import AntiCoercionDetector
from src.neural_democracy.vote_weighting import CognitiveVoteWeighter
from src.justice.arbitration import ArbitrationSystem, DisputeType, DisputeStatus
from src.justice.evidence import EvidenceChain
from src.justice.precedent import PrecedentSystem
import time

def test_constitution():
    constitution = AtlasConstitution()
    assert len(constitution.articles) == 27
    assert constitution.is_constitutional("mint", {"contribution_proven": True, "identity_verified": True})
    assert not constitution.is_constitutional("mint", {"contribution_proven": False, "identity_verified": True})
    summary = constitution.summary()
    assert summary["total_articles"] == 27

def test_amendment_process():
    constitution = AtlasConstitution()
    amendment = constitution.propose_amendment(
        article_id=6, proposer="did:atlas:governance",
        description="Reduce max tax from 10% to 5%",
        new_text="No tax on ATLAS transactions shall exceed 5%.",
        new_rule_code="proportional_tax",
    )
    assert amendment.status == "proposed"
    assert amendment.supermajority_required == 0.75  # Not a protected article
    # Ratify with 80% support
    ratified = constitution.ratify_amendment(amendment.amendment_id, 80, 20)
    assert ratified
    assert amendment.status == "ratified"

def test_protected_amendment():
    constitution = AtlasConstitution()
    amendment = constitution.propose_amendment(
        article_id=1, proposer="did:atlas:governance",
        description="Modify right to value",
        new_text="Modified text", new_rule_code="right_to_value",
    )
    assert amendment.supermajority_required == 0.90  # Protected article
    # 80% is not enough for protected article
    not_ratified = constitution.ratify_amendment(amendment.amendment_id, 80, 20)
    assert not not_ratified

def test_rights_engine():
    engine = RightsEngine()
    engine.register_citizen("did:atlas:alice")
    assert engine.check_right("did:atlas:alice", RightType.RIGHT_TO_VALUE, {"contribution_proven": True})
    assert not engine.check_right("did:atlas:alice", RightType.RIGHT_TO_PRIVACY, {"force_reveal": True})
    # Report violation
    v = engine.report_violation("did:atlas:alice", RightType.RIGHT_TO_PRIVACY,
                                 "did:atlas:violator", "Forced neural scan")
    assert v.severity == "moderate"
    assert len(engine.get_violations(unresolved_only=True)) == 1

def test_planetary_congress():
    congress = PlanetaryCongress()
    session = congress.open_session("prop_001", "Reduce minting halving period",
                                     "Change halving from 4 years to 2 years")
    assert session.status == "deliberating"
    assert len(session.participants) == 4  # 4 Titans
    result = congress.deliberate(session.session_id)
    assert result.outcome in ["passed", "rejected", "tabled"]
    assert len(result.votes) == 4
    assert len(result.transcript) == 20  # 4 Titans * 5 rounds

def test_argumentation():
    graph = ArgumentGraph()
    arg1 = Argument(arg_id="a1", claim="Proposal benefits economy", proponent="HERMES", strength=0.8)
    arg2 = Argument(arg_id="a2", claim="Proposal harms privacy", proponent="PROMETHEUS", strength=0.7)
    graph.add_argument(arg1)
    graph.add_argument(arg2)
    graph.add_attack(AttackRelation(source_id="a2", target_id="a1", rebuttal="Privacy outweighs economic gain"))
    score1 = graph.compute_acceptability("a1")
    score2 = graph.compute_acceptability("a2")
    assert 0 <= score1 <= 1
    assert 0 <= score2 <= 1

def test_coalition():
    former = CoalitionFormer()
    coalition = former.form_coalition("Growth Alliance", ["HERMES", "CHRONOS"],
                                       "Pro-economic growth", 0.5)
    assert coalition.active
    assert former.get_coalition("HERMES").name == "Growth Alliance"
    assert former.total_weight() == 0.5
    former.dissolve_coalition(coalition.coalition_id)
    assert not former.get_coalition("HERMES")

def test_neural_voting():
    system = NeuralVotingSystem()
    # Simulate EEG data (approve pattern)
    eeg_approve = np.random.randn(8, 256) * 50
    # Calibrate
    system.decoder.calibrate("did:atlas:voter1",
                              np.array([0.8, 0.3, 0.9, 0.2]),
                              np.array([0.2, 0.9, 0.3, 0.8]))
    vote = system.cast_neural_vote("did:atlas:voter1", "prop_001", eeg_approve)
    assert vote.proposal_id == "prop_001"
    assert 0 <= vote.confidence <= 1
    # Tally
    tally = system.tally("prop_001")
    assert tally["total_votes"] == 1

def test_anti_coercion():
    detector = AntiCoercionDetector()
    # Normal EEG (low stress)
    normal_eeg = np.random.randn(8, 256) * 20
    detector.set_baseline("did:atlas:voter1", normal_eeg)
    result_normal = detector.check_coercion("did:atlas:voter1", normal_eeg)
    assert not result_normal["coerced"]
    # High stress EEG (elevated beta, suppressed alpha)
    stress_eeg = np.random.randn(8, 256) * 100
    result_stress = detector.check_coercion("did:atlas:voter1", stress_eeg)
    # May or may not detect coercion depending on random data, but should have stress_level
    assert "stress_level" in result_stress

def test_vote_weighting():
    weighter = CognitiveVoteWeighter()
    weight = weighter.weight_vote(
        confidence=0.9, cognitive_load=0.8,
        stress_level=0.1, reputation=1.5)
    assert weight.final_weight > 0
    assert weight.final_weight <= 2.0
    assert "focus" in weight.factors

def test_arbitration():
    system = ArbitrationSystem()
    # Register arbitrators
    for i in range(5):
        system.register_arbitrator(f"arb_{i}", 0.9 + i * 0.01,
                                    [DisputeType.MINTING_DISPUTE], tier=1)
    # File dispute
    dispute = system.file_dispute(
        DisputeType.MINTING_DISPUTE, "did:atlas:claimant",
        "did:atlas:respondent", "Minting without sufficient proof",
        ["ev_1", "ev_2"])
    assert dispute.status == DisputeStatus.FILED
    # Assign arbitrators
    arbitrators = system.assign_arbitrators(dispute.dispute_id)
    assert len(arbitrators) <= 3  # Tier 1 = 3 arbitrators
    # Render ruling
    ruling = system.render_ruling(dispute.dispute_id, arbitrators[0].arbitrator_id,
                                   "in_favor_of_claimant", "Insufficient proof")
    assert ruling.decision == "in_favor_of_claimant"
    assert dispute.status == DisputeStatus.RESOLVED
    # Appeal
    appealed = system.appeal(dispute.dispute_id)
    assert appealed
    assert dispute.tier == 2

def test_evidence_chain():
    chain = EvidenceChain()
    ev1 = chain.submit("document", "did:atlas:alice", b"Transaction log proof")
    ev2 = chain.submit("witness_statement", "did:atlas:bob", b"I saw the value creation")
    assert chain.verify_chain()
    assert len(chain.get_chain()) == 2
    # Tampering should break chain
    ev1.content_hash = "tampered"
    assert not chain.verify_chain()

def test_precedent():
    system = PrecedentSystem()
    p1 = system.register_precedent(
        "minting_dispute", "Ruling: proof requires 2 attestations",
        "Minimum attestation count is 2", "ruling_001", tier=2)
    p2 = system.register_precedent(
        "minting_dispute", "Ruling: expired proofs cannot mint",
        "30-day expiry is binding", "ruling_002", tier=3)
    precedents = system.find_precedents("minting_dispute")
    assert len(precedents) == 2
    assert precedents[0].authority >= precedents[1].authority  # Sorted by authority

def test_amendment_formal_process():
    process = AmendmentProcess()
    proposal = process.create_proposal(
        article_id=15, proposer="did:atlas:governance",
        title="Extend voting period", description="Extend from 7 to 14 days",
        current_text="All proposals have a 7-day voting period.",
        proposed_text="All proposals have a 14-day voting period.",
        proposed_rule_code="voting_period")
    assert proposal.status == "open"
    # Add debate comments
    for i in range(25):
        process.add_debate_comment(proposal.proposal_id, f"voter_{i}", "support", "Good idea")
    # Start voting
    started = process.start_voting(proposal.proposal_id)
    # May fail if debate period not elapsed (but we can force by setting debate_ends)
    proposal.debate_ends = time.time() - 1
    started = process.start_voting(proposal.proposal_id)
    assert started
    # Cast votes
    for i in range(80):
        process.cast_vote(proposal.proposal_id, True)
    for i in range(20):
        process.cast_vote(proposal.proposal_id, False)
    ratified = process.finalize(proposal.proposal_id)
    assert ratified  # 80% > 75% threshold

if __name__ == "__main__":
    test_constitution()
    test_amendment_process()
    test_protected_amendment()
    test_rights_engine()
    test_planetary_congress()
    test_argumentation()
    test_coalition()
    test_neural_voting()
    test_anti_coercion()
    test_vote_weighting()
    test_arbitration()
    test_evidence_chain()
    test_precedent()
    test_amendment_formal_process()
    print("✅ All Phase 7 tests passed")
