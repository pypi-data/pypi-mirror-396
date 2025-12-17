import numpy as np
from ..engine import LatentMemoryEngine
from .client import RemoteShard

class EdgeNode:
    """
    A lightweight Paradox instance meant for Edge Devices (IoT, Mobile, Local PC).
    It processes data locally and only syncs 'Novel' patterns to the Cloud.
    """
    def __init__(self, cloud_host="localhost", cloud_port=8000, local_dim=64, capacity=1000):
        # 1. Local 'Short Term Memory' (STM)
        self.local_memory = LatentMemoryEngine(dimension=local_dim)
        
        # 2. Cloud 'Long Term Memory' (LTM) Link
        self.cloud_client = RemoteShard(host=cloud_host, port=cloud_port)
        
        self.novelty_threshold = 0.5 # Distance threshold to consider something "New"
        print(f"[Edge] Online. Linked to Cloud at {cloud_host}:{cloud_port}")

    def perceive(self, vector, attributes=None):
        """
        Ingest a thought.
        1. Check if it's new (Novelty Detection).
        2. If new -> Add to Local Memory AND Sync to Cloud.
        3. If known -> Just ignore or update weight.
        """
        # 1. Query Local Memory to check novelty
        # LatentMemoryEngine.query returns list of (id, dist, attrs)
        if self.local_memory.count > 0:
            results = self.local_memory.query(vector, k=1)
            dist = results[0][1]
        else:
            dist = float('inf')

        is_novel = dist > self.novelty_threshold
        
        status = "Known"
        if is_novel:
            status = "Novel"
            # Add to Local
            self.local_memory.add(vector, attributes)
            
            # Sync to Cloud
            try:
                self.cloud_client.add(vector, attributes)
                status += " (Synced)"
            except Exception as e:
                status += f" (Sync Failed: {e})"
        
        return {"status": status, "novelty_score": dist}

    def query_hybrid(self, vector, k=5):
        """
        Query Local first (Fast), if poor results, query Cloud (Slow but deep).
        """
        local_results = self.local_memory.query(vector, k=k)
        
        # If local results are bad (high distance), ask cloud
        best_local_dist = local_results[0][1] if local_results else float('inf')
        
        if best_local_dist > self.novelty_threshold:
            print("[Edge] Local memory insufficient. Querying Cloud...")
            try:
                cloud_results = self.cloud_client.query(vector, k=k)
                return cloud_results # Return cloud results
            except Exception as e:
                print(f"[Edge] Cloud query failed: {e}")
                return local_results
        
        return local_results

    def sync_all(self):
        """Force upload all local memory to cloud."""
        # Simple iteration not supported by Engine yet (no get_all), 
        # so this is a placeholder or requires Engine update.
        print("[Edge] Batch sync not implemented yet.")
