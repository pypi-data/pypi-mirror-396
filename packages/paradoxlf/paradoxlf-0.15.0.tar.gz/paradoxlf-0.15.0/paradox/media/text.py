from ..encoder import BaseEncoder
import numpy as np

class SimpleTextEncoder(BaseEncoder):
    """
    A basic ASCII/Frequency based encoder for testing.
    Does NOT capture semantic meaning. Use TransformerTextEncoder for that.
    """
    def __init__(self, dimension=64):
        self.dimension = dimension

    def encode(self, text):
        # Naive hashing to vector
        vec = np.zeros(self.dimension, dtype=np.float32)
        for i, char in enumerate(text):
            idx = ord(char) % self.dimension
            vec[idx] += 1.0
        
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

class TransformerTextEncoder(BaseEncoder):
    """
    Uses State-of-the-Art Sentence Transformers (HuggingFace) for semantic embeddings.
    Requires: pip install -U sentence-transformers
    """
    def __init__(self, model_name='all-MiniLM-L6-v2', dimension=None):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            if dimension and self.dimension != dimension:
                print(f"Warning: Model dimension {self.dimension} does not match requested {dimension}.")
        except ImportError:
            raise ImportError("Please install 'sentence-transformers' to use this encoder.")

    def encode(self, text):
        return self.model.encode(text)
