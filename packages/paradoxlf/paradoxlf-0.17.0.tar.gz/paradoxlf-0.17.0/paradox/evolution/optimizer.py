import numpy as np
import random

class GeneticOptimizer:
    """
    Simulates biological evolution in Latent Space.
    """
    def __init__(self, mutation_rate=0.1, mutation_scale=0.05):
        self.mutation_rate = mutation_rate
        self.mutation_scale = mutation_scale

    def mutate(self, vector):
        """Phase 1: Random Mutation"""
        if np.random.random() < self.mutation_rate:
            noise = np.random.normal(0, self.mutation_scale, vector.shape)
            return vector + noise
        return vector

    def crossover(self, parent_a, parent_b):
        """Phase 1: Sexual Reproduction (Vector Combination)"""
        # Interpolate
        alpha = np.random.random()
        child1 = parent_a * alpha + parent_b * (1 - alpha)
        child2 = parent_b * alpha + parent_a * (1 - alpha)
        return child1, child2

class ObjectiveFunction:
    """
    Phase 2: Goal-Driven Functions.
    """
    @staticmethod
    def novelty_score(vector, memory_bank):
        """Goal: Maximize Distance from known memories."""
        if len(memory_bank) == 0:
            return 1.0
        # Average distance to k-nearest neighbors (conceptually)
        # Here we just check avg dist to random sample for speed
        dists = [np.linalg.norm(vector - m) for m in memory_bank[-10:]] 
        return np.mean(dists) if dists else 0.0

    @staticmethod
    def coherence_score(vector):
        """Goal: Keep vector within reasonable magnitude (not exploding)."""
        norm = np.linalg.norm(vector)
        # Gaussian penalty centered at norm=1.0 (assuming normalized space)
        return np.exp(-((norm - 1.0)**2))
