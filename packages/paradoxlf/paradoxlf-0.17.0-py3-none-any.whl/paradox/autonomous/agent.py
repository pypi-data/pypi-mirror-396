import time
import numpy as np
from ..evolution import GeneticOptimizer, ObjectiveFunction
from ..safety import GuardRail
from ..engine import LatentMemoryEngine

class AutoAgent:
    """
    Phase 3, 4, 5: The Autonomous Entity.
    It has a loop: Dream -> Evolve -> Filter -> Act.
    """
    def __init__(self, name="AutoMind_v1", dim=64):
        self.name = name
        self.memory = LatentMemoryEngine(dimension=dim)
        self.optimizer = GeneticOptimizer(mutation_rate=0.3)
        self.safety = GuardRail(max_norm=3.0)
        self.population = [] # Active thoughts

    def seed_thought(self):
        """Generate random initial thought."""
        return np.random.normal(0, 1, self.memory.dimension).astype(np.float32)

    def evolution_step(self):
        """
        Run one cycle of self-improvement.
        """
        # 1. Selection: Pick memories to evolve
        if self.memory.count == 0:
            parents = [self.seed_thought(), self.seed_thought()]
        else:
            # Random sample from memory
            parents = [self.memory.vectors[np.random.randint(self.memory.count)] for _ in range(2)]

        # 2. Reproduction & Mutation (Phase 1, 4)
        child1, child2 = self.optimizer.crossover(parents[0], parents[1])
        child1 = self.optimizer.mutate(child1)
        child2 = self.optimizer.mutate(child2)

        # 3. Evaluation (Phase 2)
        candidates = [child1, child2]
        approved_thoughts = []

        memory_sample = self.memory.vectors[:10] if self.memory.count > 0 else []
        
        for cand in candidates:
            # Optimize: Check Safety FIRST (Phase 6)
            is_safe, msg = self.safety.check(cand)
            if not is_safe:
                print(f"[Safety] Blocked dangerous thought: {msg}")
                cand = self.safety.sanitize(cand)
            
            # Check Quality
            nov = ObjectiveFunction.novelty_score(cand, memory_sample)
            coh = ObjectiveFunction.coherence_score(cand)
            
            score = nov + coh
            if score > 1.2: # Arbitrary "Good Idea" threshold
                approved_thoughts.append((cand, score))

        # 4. Integration (Phase 3)
        for thought, score in approved_thoughts:
            self.memory.add(thought, {"origin": "evolution", "score": float(score)})
            print(f"[{self.name}] Evolved new idea! Score: {score:.2f}")

    def run_autonomous(self, cycles=5):
        print(f"[{self.name}] Starting Autonomous Loop...")
        for i in range(cycles):
            print(f"--- Cycle {i+1} ---")
            self.evolution_step()
            time.sleep(0.1)
