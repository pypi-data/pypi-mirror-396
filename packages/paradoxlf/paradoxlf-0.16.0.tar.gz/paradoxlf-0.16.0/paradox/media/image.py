from ..encoder import BaseEncoder
from ..decoder import BaseDecoder
import numpy as np
import io

try:
    from PIL import Image
except ImportError:
    Image = None

class SimpleImageEncoder(BaseEncoder):
    """
    Encodes images by resizing them to a small fixed size and flattening pixel values.
    This creates a 'visual signature' vector.
    """
    def __init__(self, width=64, height=64):
        self.width = width
        self.height = height
        # Output dimension: Width * Height * 3 (RGB)
        super().__init__(dimension=width * height * 3)

    def encode(self, image_path_or_obj):
        if Image is None:
            raise ImportError("Pillow is required. pip install Pillow")

        # Load image
        if isinstance(image_path_or_obj, str):
            img = Image.open(image_path_or_obj)
        else:
            img = image_path_or_obj

        # Convert to RGB and resize
        img = img.convert('RGB')
        img = img.resize((self.width, self.height))
        
        # Convert to numpy array and normalize to 0-1 range
        arr = np.array(img, dtype=np.float32) / 255.0
        
        # Flatten to 1D vector
        return arr.flatten()

class SimpleImageDecoder(BaseDecoder):
    """
    Reconstructs the image from the flattened vector.
    """
    def __init__(self, width=64, height=64):
        self.width = width
        self.height = height
        super().__init__(dimension=width * height * 3)

    def decode(self, vector):
        if Image is None:
            raise ImportError("Pillow is required. pip install Pillow")
            
        # Reshape back to (H, W, 3)
        # Denormalize (0-1 -> 0-255)
        # IMPORTANT: Clamp values to avoid integer overflow artifacts when predicting outside bounds
        vector = np.clip(vector, 0.0, 1.0)
        
        arr = (vector.reshape(self.height, self.width, 3) * 255).astype(np.uint8)
        
        return Image.fromarray(arr)
