import numpy as np
import os
import json
import logging

logger = logging.getLogger("ParadoxPersistence")

class PersistenceManager:
    def __init__(self, storage_dir, dimension):
        self.storage_dir = storage_dir
        self.dimension = dimension
        self.vectors_file = os.path.join(storage_dir, "vectors.dat")
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    def save(self, vectors, objects):
        """
        Save current state to disk.
        """
        logger.info(f"Saving to {self.storage_dir}...")
        
        # Save Metadata
        with open(self.metadata_file, 'w') as f:
            json.dump(objects, f)
            
        # Save Vectors (Binary)
        # If it's a torch tensor, move to CPU numpy first
        if hasattr(vectors, 'cpu'):
            vectors = vectors.cpu().numpy()
            
        fp = np.memmap(self.vectors_file, dtype='float32', mode='w+', shape=vectors.shape)
        fp[:] = vectors[:]
        fp.flush()
        logger.info("Save complete.")

    def load(self, map_mode='r+'):
        """
        Load state from disk. Returns (vectors, objects).
        """
        if not os.path.exists(self.metadata_file) or not os.path.exists(self.vectors_file):
            logger.warning("No existing data found.")
            return None, {}

        logger.info(f"Loading from {self.storage_dir}...")
        
        with open(self.metadata_file, 'r') as f:
            objects = json.load(f)
            
        # Determine shape from metadata count
        count = len(objects)
        shape = (count, self.dimension)
        
        # Memmap the vectors
        vectors = np.memmap(self.vectors_file, dtype='float32', mode=map_mode, shape=shape)
        
        # Convert keys to int (json stores keys as strings)
        objects = {int(k): v for k, v in objects.items()}
        
        return vectors, objects
