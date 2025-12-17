import numpy as np

try:
    import torch
except ImportError:
    torch = None

class ParadoxMixer:
    """
    Advanced Latent Space Operations (Blending, Arithmetic, Superposition).
    Supports both NumPy and PyTorch backends automatically.
    """
    
    @staticmethod
    def _is_torch(vec):
        return torch is not None and isinstance(vec, torch.Tensor)

    @classmethod
    def interpolate(cls, vec_a, vec_b, ratio=0.5):
        """
        Returns a weighted blend of two vectors.
        """
        # Logic remains same for both backends due to operator overloading
        return vec_a * (1 - ratio) + vec_b * ratio

    @classmethod
    def add(cls, vec_a, vec_b):
        return vec_a + vec_b

    @classmethod
    def subtract(cls, vec_a, vec_b):
        return vec_a - vec_b
    
    @classmethod
    def analogy(cls, a, b, c):
        return b - a + c

    @classmethod
    def noise(cls, vec, magnitude=0.1):
        if cls._is_torch(vec):
            return vec + torch.randn_like(vec) * magnitude
        else:
            return vec + np.random.normal(0, magnitude, vec.shape)
