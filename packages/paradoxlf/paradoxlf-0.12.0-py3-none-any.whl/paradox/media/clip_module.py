from ..encoder import BaseEncoder
import numpy as np
from PIL import Image

class CLIPEncoder(BaseEncoder):
    """
    Unified Encoder for Images and Text using OpenAI's CLIP model.
    Maps both modalities to the SAME latent space.
    Requires: pip install transformers torch
    """
    def __init__(self, model_name="openai/clip-vit-base-patch32", device="cpu"):
        try:
            from transformers import CLIPProcessor, CLIPModel
            import torch
            self.torch = torch
            self.device = device
            # print(f"Loading CLIP Model: {model_name}...")
            self.model = CLIPModel.from_pretrained(model_name).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.dimension = self.model.config.projection_dim
            # print(f"CLIP Loaded. Dimension: {self.dimension}")
        except ImportError:
            raise ImportError("Please install 'transformers' and 'torch' to use CLIPEncoder.")

    def encode(self, data):
        """
        Auto-detects data type (str or Image) and encodes accordingly.
        """
        if isinstance(data, str):
            return self.encode_text(data)
        elif isinstance(data, Image.Image):
            return self.encode_image(data)
        else:
            raise ValueError("CLIPEncoder only supports text (str) or PIL Images.")

    def encode_text(self, text):
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        with self.torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        # Normalize
        text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
        return text_features.cpu().numpy()[0]

    def encode_image(self, image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        # Normalize
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        return image_features.cpu().numpy()[0]
