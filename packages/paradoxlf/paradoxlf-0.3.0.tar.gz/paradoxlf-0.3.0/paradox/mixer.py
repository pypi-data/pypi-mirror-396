import numpy as np

class ParadoxMixer:
    """
    Advanced Latent Space Operations (Blending, Arithmetic, Superposition).
    """
    
    @staticmethod
    def interpolate(vec_a, vec_b, ratio=0.5):
        """
        Returns a weighted blend of two vectors.
        ratio 0.0 = vec_a
        ratio 1.0 = vec_b
        """
        return vec_a * (1 - ratio) + vec_b * ratio

    @staticmethod
    def add(vec_a, vec_b):
        """Add two concepts together."""
        return vec_a + vec_b

    @staticmethod
    def subtract(vec_a, vec_b):
        """Remove concept B from concept A."""
        return vec_a - vec_b
    
    @staticmethod
    def analogy(a, b, c):
        """
        Solves 'A is to B as C is to ???'
        Result = B - A + C
        Example: King - Man + Woman = Queen
        """
        return b - a + c

    @staticmethod
    def noise(vec, magnitude=0.1):
        """Adds random noise to create a variation."""
        noise = np.random.normal(0, magnitude, vec.shape)
        return vec + noise
