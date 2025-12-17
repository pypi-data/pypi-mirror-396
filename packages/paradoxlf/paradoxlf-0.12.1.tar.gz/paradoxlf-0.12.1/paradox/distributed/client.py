import requests
import numpy as np

class RemoteShard:
    """
    Client that talks to a remote ShardServer.
    Implements the same interface as LatentShard.
    """
    def __init__(self, host="localhost", port=8000):
        self.base_url = f"http://{host}:{port}"
        self.id = f"remote_{host}_{port}"
        
        # Checking connection
        try:
            resp = requests.get(f"{self.base_url}/")
            if resp.status_code == 200:
                print(f"[RemoteShard] Connected to {self.base_url} | {resp.json()}")
            else:
                print(f"[RemoteShard] Warning: Endpoint returned {resp.status_code}")
        except Exception as e:
            print(f"[RemoteShard] Connection Failed: {e}")

    def add(self, vector, attributes=None):
        payload = {
            "vector": vector.tolist() if isinstance(vector, np.ndarray) else vector,
            "attributes": attributes
        }
        resp = requests.post(f"{self.base_url}/add", json=payload)
        resp.raise_for_status()

    def query(self, target_vector, k=5):
        payload = {
            "vector": target_vector.tolist() if isinstance(target_vector, np.ndarray) else target_vector,
            "k": k
        }
        resp = requests.post(f"{self.base_url}/query", json=payload)
        resp.raise_for_status()
        
        # Convert JSON back to expected tuple format: (id, dist, attributes)
        data = resp.json()
        results = []
        for item in data:
            results.append((item['id'], item['distance'], item['attributes']))
        return results

    def count(self):
        resp = requests.get(f"{self.base_url}/")
        resp.raise_for_status()
        return resp.json().get("count", 0)
