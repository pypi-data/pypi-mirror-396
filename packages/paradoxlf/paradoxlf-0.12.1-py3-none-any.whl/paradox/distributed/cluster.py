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
        1. Broadcast query to all shards (Map).
        2. Gather k results from each.
        3. Merge and Sort globally (Reduce).
        4. Return top k.
        """
        all_candidates = []
        
        # 1. & 2. Parallel Query Broadcast
        # We use ThreadPool to simulate network parallelism
        with ThreadPoolExecutor(max_workers=len(self.shards)) as executor:
            # Lambda to call query on a shard
            futures = {executor.submit(shard.query, target_vector, k): shard for shard in self.shards}
            
            for future in futures:
                try:
                    results = future.result()
                    all_candidates.extend(results)
                except Exception as e:
                    print(f"[Cluster] Shard query failed: {e}")

        # 3. Reduce (Merge & Sort)
        # Results are (id, dist, attrs). We sort by dist (ascending).
        # We assume Euclidean/Cosine distance where lower is better (usually).
        # Wait, LatentMemoryEngine.query returns distances.
        
        # If strict cosine sim was used, higher is better? 
        # engine.py query retuns 'dists' which are 1-sim for cosine. So LOWER is always BETTER.
        
        sorted_candidates = sorted(all_candidates, key=lambda x: x[1])
        
        # 4. Return Top K
        return sorted_candidates[:k]

    @property
    def total_count(self):
        return sum(s.count() for s in self.shards)
