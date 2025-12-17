import numpy as np
from ..engine import LatentMemoryEngine

class LatentConsensus:
    """
    Algorithms for resolving disagreements between multiple latent memory shards.
    """
    
    @staticmethod
    def average_consensus(vectors):
        """
        Simple Consensus: The 'Truth' is the average of all opinions.
        """
        if not vectors:
            return None
        return np.mean(vectors, axis=0)

    @staticmethod
    def weighted_consensus(vectors, weights):
        """
        Weighted Consensus: Some nodes are more trusted than others.
        """
        if len(vectors) != len(weights):
            raise ValueError("Vectors and weights must match")
        
        return np.average(vectors, axis=0, weights=weights)

    @staticmethod
    def detect_outliers(vectors, threshold=0.2):
        """
        Identifies nodes that deviate significantly from the group consensus.
        Returns: strict_consensus_vector, list_of_outlier_indices
        """
        # 1. Calculate rough center
        center = np.mean(vectors, axis=0)
        
        # 2. Measure distances
        dists = np.linalg.norm(vectors - center, axis=1)
        
        # 3. Filter outliers
        valid_vectors = []
        outlier_indices = []
        
        for i, d in enumerate(dists):
            if d < threshold:
                valid_vectors.append(vectors[i])
            else:
                outlier_indices.append(i)
                
        if valid_vectors:
            refined_center = np.mean(valid_vectors, axis=0)
        else:
            refined_center = center # Fallback if everyone disagrees
            
        return refined_center, outlier_indices
