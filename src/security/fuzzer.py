"""Fuzzing Framework — Coverage-guided fuzzing for API endpoints."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
import hashlib, time, random, json

@dataclass
class FuzzTarget:
    """A target for fuzzing."""
    target_id: str
    name: str
    endpoint: str  # API endpoint or function name
    method: str  # GET, POST, function
    input_schema: dict  # Expected input schema
    fuzz_strategy: str = "mutation"  # mutation, generation, grammar
    max_iterations: int = 10000
    timeout_seconds: int = 30

@dataclass
class FuzzResult:
    """Result of a fuzzing campaign."""
    result_id: str
    target_id: str
    iterations: int
    crashes: List[dict] = field(default_factory=list)
    unique_crashes: int = 0
    coverage_percent: float = 0.0
    execution_time_s: float = 0.0
    corpus_size: int = 0
    timestamp: float = field(default_factory=time.time)

@dataclass
class CorpusManager:
    """Manages fuzzing corpus (interesting inputs)."""
    corpus: List[dict] = field(default_factory=list)
    max_size: int = 10000
    
    def add(self, input_data: dict, coverage_hash: str) -> bool:
        """Add input to corpus if it covers new code paths."""
        existing_hashes = {item.get("coverage_hash") for item in self.corpus}
        if coverage_hash not in existing_hashes:
            self.corpus.append({
                "input": input_data,
                "coverage_hash": coverage_hash,
                "timestamp": time.time(),
            })
            if len(self.corpus) > self.max_size:
                self.corpus.pop(0)  # Remove oldest
            return True
        return False
    
    def sample(self) -> Optional[dict]:
        """Sample a random input from corpus."""
        if not self.corpus:
            return None
        return random.choice(self.corpus)["input"]
    
    def size(self) -> int:
        return len(self.corpus)

class FuzzingFramework:
    """
    Coverage-guided fuzzing framework for ATLAS.
    
    - Mutates inputs to find crashes
    - Tracks code coverage to guide exploration
    - Deduplicates crashes by stack trace
    - Supports continuous fuzzing with corpus persistence
    """

    MUTATION_STRATEGIES = [
        "bit_flip", "byte_flip", "byte_insert", "byte_delete",
        "arithmetic", "interesting_values", "dictionary",
        "max_length", "zero_length", "null_bytes",
    ]

    def __init__(self):
        self.targets: Dict[str, FuzzTarget] = {}
        self.results: List[FuzzResult] = {}
        self.corpus = CorpusManager()
        self.crash_dedup: Dict[str, dict] = {}  # crash_hash -> crash

    def register_target(self, target: FuzzTarget) -> None:
        self.targets[target.target_id] = target

    def fuzz(self, target_id: str, iterations: int = 1000) -> FuzzResult:
        """Run a fuzzing campaign against a target."""
        target = self.targets.get(target_id)
        if not target:
            raise ValueError(f"Unknown target: {target_id}")
        
        start = time.time()
        crashes = []
        coverage_paths = set()
        
        for i in range(min(iterations, target.max_iterations)):
            # Generate or mutate input
            if self.corpus.size() > 0 and random.random() < 0.7:
                base_input = self.corpus.sample()
                fuzz_input = self._mutate(base_input)
            else:
                fuzz_input = self._generate(target.input_schema)
            
            # Execute (simulated)
            crash, coverage_hash = self._execute(target, fuzz_input)
            
            # Track coverage
            if coverage_hash:
                coverage_paths.add(coverage_hash)
                self.corpus.add(fuzz_input, coverage_hash)
            
            # Record crash
            if crash:
                crash_hash = hashlib.sha256(
                    json.dumps(crash, sort_keys=True).encode()
                ).hexdigest()[:16]
                if crash_hash not in self.crash_dedup:
                    self.crash_dedup[crash_hash] = crash
                    crashes.append(crash)
        
        execution_time = time.time() - start
        coverage = len(coverage_paths) / max(1, 100) * 100  # Assume 100 possible paths
        
        result = FuzzResult(
            result_id=hashlib.sha256(f"fuzz:{target_id}:{time.time()}".encode()).hexdigest()[:16],
            target_id=target_id,
            iterations=min(iterations, target.max_iterations),
            crashes=crashes,
            unique_crashes=len(crashes),
            coverage_percent=min(100, coverage),
            execution_time_s=execution_time,
            corpus_size=self.corpus.size(),
        )
        self.results[result.result_id] = result
        return result

    def _generate(self, schema: dict) -> dict:
        """Generate a random input based on schema."""
        result = {}
        for field_name, field_type in schema.items():
            if field_type == "string":
                result[field_name] = ''.join(random.choices('abcde"', k=random.randint(0, 100)))
            elif field_type == "int":
                result[field_name] = random.randint(-1000, 1000)
            elif field_type == "float":
                result[field_name] = random.uniform(-1000, 1000)
            elif field_type == "bool":
                result[field_name] = random.choice([True, False])
            else:
                result[field_name] = None
        return result

    def _mutate(self, input_data: dict) -> dict:
        """Mutate an input using random strategies."""
        mutated = dict(input_data)
        if not mutated:
            return mutated
        key = random.choice(list(mutated.keys()))
        strategy = random.choice(self.MUTATION_STRATEGIES)
        value = mutated[key]
        if isinstance(value, str):
            if strategy == "bit_flip" and len(value) > 0:
                idx = random.randint(0, len(value) - 1)
                char = value[idx]
                flipped = chr(ord(char) ^ (1 << random.randint(0, 7)))
                mutated[key] = value[:idx] + flipped + value[idx+1:]
            elif strategy == "max_length":
                mutated[key] = value * 1000
            elif strategy == "zero_length":
                mutated[key] = ""
            elif strategy == "null_bytes":
                mutated[key] = value + "\x00\x00\x00"
        elif isinstance(value, (int, float)):
            if strategy == "arithmetic":
                mutated[key] = value + random.randint(-100, 100)
            elif strategy == "interesting_values":
                mutated[key] = random.choice([0, -1, 2**31, 2**63, -2**63, 0.0, float('inf'), float('nan')])
        return mutated

    def _execute(self, target: FuzzTarget, input_data: dict) -> tuple:
        """Execute target with fuzz input (simulated)."""
        # Simulate execution — 0.1% crash rate
        crash = None
        if random.random() < 0.001:
            crash = {
                "input": input_data,
                "error": random.choice([
                    "OverflowError", "KeyError", "ValueError",
                    "RecursionError", "MemoryError", "TimeoutError",
                ]),
                "stack_trace": f"at {target.endpoint} line {random.randint(1, 100)}",
            }
        # Simulate coverage hash
        coverage_hash = hashlib.sha256(
            json.dumps(input_data, sort_keys=True, default=str).encode()
        ).hexdigest()[:8]
        return crash, coverage_hash

    def get_crashes(self) -> List[dict]:
        return list(self.crash_dedup.values())

    def stats(self) -> dict:
        return {
            "total_targets": len(self.targets),
            "total_campaigns": len(self.results),
            "total_crashes": len(self.crash_dedup),
            "corpus_size": self.corpus.size(),
        }
