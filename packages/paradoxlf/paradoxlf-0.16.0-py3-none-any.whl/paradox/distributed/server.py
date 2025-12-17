import uvicorn
import argparse
import os
import pickle
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from typing import List, Optional, Dict, Any
from .shard import LatentShard

# Data Models
class AddItemRequest(BaseModel):
    vector: List[float]
    attributes: Optional[Dict[str, Any]] = None

class QueryRequest(BaseModel):
    vector: List[float]
    k: int = 5

class ShardServer:
    """
    Exposes a LatentShard over HTTP using FastAPI.
    """
    def __init__(self, dimension=128, shard_id="shard_0", persistence_path=None):
        self.app = FastAPI(title=f"Paradox Latent Shard: {shard_id}")
        self.shard = LatentShard(shard_id=shard_id, dimension=dimension)
        self.persistence_path = persistence_path
        
        # Load state if exists
        if persistence_path and os.path.exists(persistence_path):
             self.load_state()
             
        self._setup_routes()
        
    def save_state(self):
        if not self.persistence_path: return
        print(f"[ShardServer] Saving snapshot to {self.persistence_path}...")
        try:
             # Very naive persistence: dump the whole engine object
             # In production, use Engine's internal serialization
             os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
             with open(self.persistence_path, 'wb') as f:
                 pickle.dump(self.shard, f)
        except Exception as e:
            print(f"[Error] Save failed: {e}")

    def load_state(self):
        print(f"[ShardServer] Loading snapshot from {self.persistence_path}...")
        try:
            with open(self.persistence_path, 'rb') as f:
                loaded_shard = pickle.load(f)
                self.shard = loaded_shard # Swap instance
                print(f"[ShardServer] Restored {self.shard.count()} memories.")
        except Exception as e:
            print(f"[Error] Load failed: {e}")

    def _setup_routes(self):
        @self.app.get("/")
        def read_root():
            return {"status": "online", "id": self.shard.id, "count": self.shard.count()}
            
        @self.app.post("/add")
        def add_item(item: AddItemRequest):
            try:
                self.shard.add(np.array(item.vector, dtype=np.float32), item.attributes)
                # Auto-save on write (Inefficient but robust for prototype)
                # In prod, use a background thread or explicit /save endpoint
                if self.shard.count() % 10 == 0: # Save every 10 items
                    self.save_state()
                return {"status": "ok"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.post("/query")
        def query(item: QueryRequest):
            try:
                results = self.shard.query(np.array(item.vector, dtype=np.float32), k=item.k)
                json_results = []
                for idx, dist, attrs in results:
                    json_results.append({
                        "id": int(idx),
                        "distance": float(dist),
                        "attributes": attrs
                    })
                return json_results
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def run(self, host="0.0.0.0", port=8000):
        print(f"[ShardServer] Listening on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

def main():
    parser = argparse.ArgumentParser(description="Paradox Shard Node")
    parser.add_argument("--id", type=str, default="node_x", help="Unique Node ID")
    parser.add_argument("--port", type=int, default=8000, help="Listen Port")
    parser.add_argument("--dimension", type=int, default=128, help="Latent Vector Dimension")
    parser.add_argument("--persistence", type=str, default="/app/persistence/shard.pkl", help="Path to save state")
    
    args = parser.parse_args()
    
    print(f"=== Paradox Node: {args.id} ===")
    server = ShardServer(dimension=args.dimension, shard_id=args.id, persistence_path=args.persistence)
    server.run(port=args.port)

if __name__ == "__main__":
    main()
