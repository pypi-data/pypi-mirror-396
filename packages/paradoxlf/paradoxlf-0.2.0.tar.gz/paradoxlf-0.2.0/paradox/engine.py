import numpy as np
from .utils import get_optimal_backend, get_system_resources
from .persistence import PersistenceManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ParadoxEngine")

class LatentMemoryEngine:
    def __init__(self, dimension=128, backend=None, storage_dir=None):
        """
        Initialize the Latent Memory Engine.
        
        Args:
            dimension (int): The dimensionality of the latent vectors.
            backend (str, optional): Force 'numpy' or 'torch'. Defaults to auto-detect.
            storage_dir (str, optional): Path to directory for persistence.
        """
        self.dimension = dimension
        self.backend_type = backend if backend else get_optimal_backend()
        self.storage_dir = storage_dir
        self.persistence = PersistenceManager(storage_dir, dimension) if storage_dir else None
        
        self.objects = {}
        self.vectors = None
        self.count = 0
        
        self.encoder = None # Optional component
        self.decoder = None # Optional component

        loaded = False
        if self.persistence:
            # Try loading existing data
            vecs, objs = self.persistence.load()
            if vecs is not None:
                logger.info(f"Restored {len(objs)} objects from disk.")
                self.objects = objs
                self.count = len(objs)
                
                # If we want to use Torch, we load into RAM (Memmap is numpy only essentially)
                # For hybrid approach, we would keep it as memmap if backend='numpy'
                if self.backend_type == "torch":
                    import torch
                    self.torch = torch
                    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                    self.vectors = torch.tensor(vecs, device=self.device, dtype=torch.float32)
                else:
                    self.vectors = vecs # Keep as memmap or array
                    # Note: if it's a memmap, it's not resizeable easily via vstack.
                    # For this MVP, if we load from disk, we might convert to in-memory array for addition support
                    # unless we implement sophisticated chunking.
                    self.vectors = np.array(vecs) # Load fully into RAM for now to allow adding
                
                loaded = True

        if not loaded:
            logger.info(f"Initializing Paradox Engine | Backend: {self.backend_type} | Dim: {dimension}")
            
            if self.backend_type == "torch":
                try:
                    import torch
                    self.torch = torch
                    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                    self.vectors = torch.empty((0, self.dimension), device=self.device)
                except ImportError:
                    logger.warning("PyTorch not found, falling back to NumPy.")
                    self.backend_type = "numpy"
            
            if self.backend_type == "numpy":
                self.vectors = np.empty((0, self.dimension), dtype=np.float32)

    def set_encoder(self, encoder):
        """Attach an encoder."""
        self.encoder = encoder

    def set_decoder(self, decoder):
        """Attach a decoder."""
        self.decoder = decoder

    def save(self):
        """Persist current state to disk."""
        if self.persistence:
            self.persistence.save(self.vectors, self.objects)
        else:
            logger.warning("No storage_dir configured. Cannot save.")

    def _resize_storage(self, new_count):
        """
        Internal method to resize vector storage efficiently.
        """
        pass # To be implemented for optimization

    def add(self, data, attributes=None):
        """
        Add a single object to the memory.
        
        Args:
            data: Latent vector OR raw data (if encoder is set).
            attributes (dict): Arbitrary metadata.
        """
        if self.encoder:
            vector = self.encoder.encode(data)
        else:
            vector = data

        # Ensure vector shape matches
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension mismatch. Expected {self.dimension}, got {len(vector)}")

        obj_id = self.count
        self.count += 1
        
        # Store metadata
        if attributes is None:
            attributes = {}
        attributes['_id'] = obj_id
        self.objects[obj_id] = attributes

        # Update Vector Store
        if self.backend_type == "numpy":
            # Check if we are appending to a memmap, which forces a copy to RAM behavior
            if isinstance(self.vectors, np.memmap):
                logger.warning("Appending to Memmap in MVP mode: entire dataset is being loaded into RAM.")
                
            vector = np.array([vector], dtype=np.float32)
            self.vectors = np.vstack([self.vectors, vector])
        elif self.backend_type == "torch":
            tensor = self.torch.tensor([vector], device=self.device, dtype=self.torch.float32)
            self.vectors = self.torch.cat([self.vectors, tensor], dim=0)
            
        return obj_id

    def retrieve(self, obj_id):
        """
        Retrieve attributes for a specific object ID.
        """
        return self.objects.get(obj_id)

    def query(self, target_vector, k=5, metric="euclidean"):
        """
        Find the k neareast neighbors to the target vector.
        
        Args:
            target_vector: Query vector.
            k (int): Number of results.
            metric (str): 'euclidean' or 'cosine'.
            
        Returns a list of (id, distance, attributes) tuples.
        """
        if self.count == 0:
            return []

        # Ensure target is correct format
        if self.backend_type == "numpy":
            target = np.array(target_vector, dtype=np.float32)
            
            if metric == "euclidean":
                dists = np.linalg.norm(self.vectors - target, axis=1)
            elif metric == "cosine":
                # Cosine Dist = 1 - Cosine Sim
                # Sim = (A . B) / (|A|*|B|)
                norm_v = np.linalg.norm(self.vectors, axis=1)
                norm_t = np.linalg.norm(target)
                # Avoid divide by zero
                norm_v[norm_v == 0] = 1e-9
                if norm_t == 0: norm_t = 1e-9
                
                sim = np.dot(self.vectors, target) / (norm_v * norm_t)
                dists = 1 - sim
            else:
                raise ValueError(f"Unknown metric: {metric}")
            # Euclidean distance: sqrt(sum((a - b)^2))
            # Or Cosine: dot(a, b) / (norm(a) * norm(b))
            
            # Simple Euclidean for MVP
            dists = np.linalg.norm(self.vectors - target, axis=1)
            # Get top k indices
            nearest_indices = dists.argsort()[:k]
            results = []
            for idx in nearest_indices:
                dist = float(dists[idx])
                results.append((int(idx), dist, self.objects[idx]))
            return results

        elif self.backend_type == "torch":
            target = self.torch.tensor(target_vector, device=self.device, dtype=self.torch.float32)
            
            if metric == "euclidean":
                dists = self.torch.norm(self.vectors - target, dim=1)
            elif metric == "cosine":
                 dists = 1 - self.torch.nn.functional.cosine_similarity(self.vectors, target.unsqueeze(0))
            else:
                 raise ValueError(f"Unknown metric: {metric}")
            # Get top k
            values, indices = self.torch.topk(dists, k, largest=False)
            
            results = []
            # Move to CPU for result construction
            indices_cpu = indices.cpu().numpy()
            values_cpu = values.cpu().numpy()
            
            for i in range(len(indices_cpu)):
                idx = int(indices_cpu[i])
                dist = float(values_cpu[i])
                results.append((idx, dist, self.objects[idx]))
            return results

    def get_info(self):
        """Returns engine status."""
        return {
            "backend": self.backend_type,
            "object_count": self.count,
            "dimension": self.dimension,
            "resources": get_system_resources()
        }
