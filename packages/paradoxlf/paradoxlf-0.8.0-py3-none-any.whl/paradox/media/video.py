from ..encoder import BaseEncoder
from ..decoder import BaseDecoder
from .image import SimpleImageEncoder, SimpleImageDecoder
import numpy as np

class SimpleVideoEncoder(BaseEncoder):
    """
    Encodes a sequence of frames data into a sequence of vectors.
    """
    def __init__(self, width=64, height=64):
        self.image_encoder = SimpleImageEncoder(width, height)
        # Dimension is same as single image, but output will be (T, Dim)
        super().__init__(dimension=self.image_encoder.dimension)

    def encode(self, frames_list):
        """
        frames_list: List of PIL Images or file paths.
        Returns: Numpy array of shape (NumFrames, Dimension)
        """
        vectors = []
        for frame in frames_list:
            vec = self.image_encoder.encode(frame)
            vectors.append(vec)
        
        return np.array(vectors)

class SimpleVideoDecoder(BaseDecoder):
    """
    Reconstructs video frames from latent vectors.
    """
    def __init__(self, width=64, height=64):
        self.image_decoder = SimpleImageDecoder(width, height)
        super().__init__(dimension=self.image_decoder.dimension)

    def decode(self, latent_sequence):
        """
        latent_sequence: (T, Dim) array
        Returns: List of PIL Images
        """
        frames = []
        for vec in latent_sequence:
            img = self.image_decoder.decode(vec)
            frames.append(img)
        return frames

def latent_interpolate(vec_a, vec_b, steps=10):
    """
    Dreams new frames between two latent points.
    """
    vectors = []
    for i in range(steps):
        alpha = i / (steps - 1)
        # Linear Interpolation (LERP)
        vec = vec_a * (1 - alpha) + vec_b * alpha
        vectors.append(vec)
    return np.array(vectors)
