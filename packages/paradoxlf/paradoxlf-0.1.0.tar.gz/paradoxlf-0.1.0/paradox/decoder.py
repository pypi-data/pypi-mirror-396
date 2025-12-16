from abc import ABC, abstractmethod

class BaseDecoder(ABC):
    def __init__(self, dimension):
        self.dimension = dimension

    @abstractmethod
    def decode(self, vector):
        """
        Reconstruct data from latent vector.
        """
        pass

class IdentityDecoder(BaseDecoder):
    def decode(self, vector):
        return vector
