"""On-chain training — training job orchestration with proof verification."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal
import numpy as np, hashlib, time

@dataclass
class TrainingJob:
    """A training job submitted to the network."""
    job_id: str
    requester: str
    model_type: str
    dataset_cid: str  # IPFS CID of encrypted dataset
    hyperparams: dict
    compute_budget: Decimal  # ATLAS willing to spend
    status: str = "pending"  # pending, running, completed, failed
    assigned_nodes: List[str] = field(default_factory=list)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    final_loss: Optional[float] = None

@dataclass
class TrainingProof:
    """ZK proof that training was executed correctly."""
    proof_id: str
    job_id: str
    node_id: str
    model_hash: str  # Hash of final model weights
    epochs_completed: int
    final_loss: float
    proof_data: bytes
    verified: bool = False
    timestamp: float = field(default_factory=time.time)

class OnChainTrainer:
    """
    Orchestrates on-chain model training.
    
    1. Requester submits training job with compute budget
    2. UBC marketplace allocates compute resources
    3. Nodes train the model and submit proofs
    4. ZK-VM verifies training was done correctly
    5. Final model is registered on the marketplace
    """

    def __init__(self):
        self.jobs: Dict[str, TrainingJob] = {}
        self.proofs: List[TrainingProof] = []

    def submit_job(self, requester: str, model_type: str,
                   dataset_cid: str, hyperparams: dict,
                   compute_budget: Decimal) -> TrainingJob:
        job = TrainingJob(
            job_id=hashlib.sha256(f"{requester}:{model_type}:{time.time()}".encode()).hexdigest()[:16],
            requester=requester, model_type=model_type,
            dataset_cid=dataset_cid, hyperparams=hyperparams,
            compute_budget=compute_budget,
        )
        self.jobs[job.job_id] = job
        return job

    def assign_nodes(self, job_id: str, nodes: List[str]) -> None:
        job = self.jobs.get(job_id)
        if job:
            job.assigned_nodes = nodes
            job.status = "running"
            job.started_at = time.time()

    def submit_proof(self, job_id: str, node_id: str,
                     model_weights: np.ndarray, epochs: int,
                     final_loss: float) -> TrainingProof:
        model_hash = hashlib.sha256(model_weights.tobytes()).hexdigest()
        # Simulate ZK proof generation
        proof_data = hashlib.sha3_256(
            f"{job_id}:{node_id}:{model_hash}:{epochs}".encode()
        ).digest()

        proof = TrainingProof(
            proof_id=hashlib.sha256(f"proof:{job_id}:{node_id}:{time.time()}".encode()).hexdigest()[:16],
            job_id=job_id, node_id=node_id,
            model_hash=model_hash,
            epochs_completed=epochs,
            final_loss=final_loss,
            proof_data=proof_data,
            verified=True,  # In production: ZK-VM verifies
        )
        self.proofs.append(proof)

        # Update job status
        job = self.jobs.get(job_id)
        if job:
            job.status = "completed"
            job.completed_at = time.time()
            job.final_loss = final_loss

        return proof

    def verify_proof(self, proof: TrainingProof) -> bool:
        """Verify a training proof."""
        return proof.proof_data is not None and len(proof.proof_data) >= 32

    def get_job(self, job_id: str) -> Optional[TrainingJob]:
        return self.jobs.get(job_id)

    def pending_jobs(self) -> List[TrainingJob]:
        return [j for j in self.jobs.values() if j.status == "pending"]

    def completed_jobs(self) -> List[TrainingJob]:
        return [j for j in self.jobs.values() if j.status == "completed"]
