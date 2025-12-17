import numpy as np
from concurrent.futures import ThreadPoolExecutor

class LatentCluster:
    """
    Coordinator for Distributed Latent Memory.
    Manages multiple Shards and performs Map-Reduce on queries.
    """
    def __init__(self, dimension=512, num_shards=4):
        self.dimension = dimension
        self.shards = []
        
        # Initialize Shards
        from .shard import LatentShard
        for i in range(num_shards):
            self.shards.append(LatentShard(shard_id=f"node_{i}", dimension=dimension))
            
        print(f"[Cluster] Online with {num_shards} shards.")
        self.rr_index = 0 # Round-robin pointer

    def add(self, vector, attributes=None):
        """
        Distribute data across shards (Sharding Strategy: Round-Robin).
        """
        # Simple Round-Robin Load Balancing
        target_shard = self.shards[self.rr_index]
        target_shard.add(vector, attributes)
        
        # Update pointer
        self.rr_index = (self.rr_index + 1) % len(self.shards)

    def query(self, target_vector, k=5):
        """
        Distributed Query (Map-Reduce).
        """
        all_candidates = []
        with ThreadPoolExecutor(max_workers=len(self.shards)) as executor:
            futures = {executor.submit(shard.query, target_vector, k): shard for shard in self.shards}
            for future in futures:
                try:
                    results = future.result()
                    all_candidates.extend(results)
                except Exception as e:
                    print(f"[Cluster] Shard query failed: {e}")

        # Reduce
        sorted_candidates = sorted(all_candidates, key=lambda x: x[1])
        return sorted_candidates[:k]

    def retrieve_vector(self, concept_name):
        """
        Finds a concept by name across all shards and returns its vector.
        This is expensive (Broadcast Search) but necessary for reasoning.
        """
        # In a real system, we'd have a global index/lookup table.
        # Here we brute-force search the metadata.
        # Note: Standard Engine doesn't support "get_vector_by_name" easily without iterating.
        # We will iterate all shards' memory.
        
        for shard in self.shards:
            # We assume Shard has a way to peek. For RemoteShard this is hard.
            # We'll use a trick: Semantic Search for the concept name itself (if text encoded)
            # Or assume we have a way to fetch.
            # MVP: We just skip this for now and rely on Vectors being passed in.
            pass
        return None

    def solve_analogy_distributed(self, a_vec, b_vec, c_vec, k=1):
        """
        Solves A - B + C = ?
        """
        # 1. Compute Result Vector locally
        result_vec = a_vec - b_vec + c_vec
        
        # 2. Distributed Search for the result
        return self.query(result_vec, k=k)

    @property
    def total_count(self):
        return sum(s.count() for s in self.shards)
