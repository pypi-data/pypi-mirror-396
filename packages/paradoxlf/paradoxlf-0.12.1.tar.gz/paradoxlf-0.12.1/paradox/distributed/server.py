import uvicorn
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
    def __init__(self, dimension=128, shard_id="shard_0"):
        self.app = FastAPI(title=f"Paradox Latent Shard: {shard_id}")
        self.shard = LatentShard(shard_id=shard_id, dimension=dimension)
        self._setup_routes()
        
    def _setup_routes(self):
        @self.app.get("/")
        def read_root():
            return {"status": "online", "id": self.shard.id, "count": self.shard.count()}
            
        @self.app.post("/add")
        def add_item(item: AddItemRequest):
            try:
                self.shard.add(np.array(item.vector, dtype=np.float32), item.attributes)
                return {"status": "ok"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.post("/query")
        def query(item: QueryRequest):
            try:
                results = self.shard.query(np.array(item.vector, dtype=np.float32), k=item.k)
                # Convert numpy types to native Python for JSON serialization
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

# Entry point for CLI
def start_server(dim=128, port=8000, id="shard_X"):
    server = ShardServer(dimension=dim, shard_id=id)
    server.run(port=port)
