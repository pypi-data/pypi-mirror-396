import numpy as np
import uuid
from ..engine import LatentMemoryEngine

class LatentShard:
    """
    Represents a single partition of the distributed memory.
    In v1 (Local), this is a wrapper around an Engine instance.
    In v2 (Network), this will wrap a TCP/HTTP client.
    """
    def __init__(self, shard_id=None, dimension=512):
        self.id = shard_id or str(uuid.uuid4())[:8]
        self.engine = LatentMemoryEngine(dimension=dimension)
        # print(f"[Shard:{self.id}] Initialized.")

    def add(self, vector, attributes=None):
        """Store vector in this local shard."""
        return self.engine.add(vector, attributes)

    def query(self, target_vector, k=5):
        """
        Execute query on this shard.
        Returns list of (id, distance, attributes).
        """
        # Local search
        return self.engine.query(target_vector, k=k)

    def count(self):
        return self.engine.count
