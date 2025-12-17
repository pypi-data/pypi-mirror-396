from abc import ABC, abstractmethod
import numpy as np

class BaseEncoder(ABC):
    def __init__(self, dimension):
        self.dimension = dimension

    @abstractmethod
    def encode(self, data):
        """
        Convert input data into a latent vector.
        Should return a numpy array or torch tensor of shape (dimension,)
        """
        pass

class IdentityEncoder(BaseEncoder):
    """
    Expects data to already be a vector.
    """
    def encode(self, data):
        return np.array(data, dtype=np.float32)

class RandomEncoder(BaseEncoder):
    """
    Ignores input data and returns a random vector (for testing).
    """
    def encode(self, data):
        return np.random.randn(self.dimension).astype(np.float32)
