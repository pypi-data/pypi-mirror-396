import time
import numpy as np
import concurrent.futures
import multiprocessing

def heavy_physics(vectors):
    # Heavy math that releases GIL
    return np.sin(vectors) * np.cos(vectors) ** 2 + np.tan(vectors * 0.1)

def main():
    N = 1000000 # 1 Million vectors to be sure
    vectors = np.random.rand(N, 128).astype(np.float32)
    
    print(f"Benchmarking with {N} vectors...")
    
    # 1. Single Thread
    start = time.time()
    heavy_physics(vectors)
    print(f"Single CPU: {time.time() - start:.4f}s")
    
    # 2. Processes (What we have now)
    start = time.time()
    chunk_size = N // 4
    chunks = [vectors[i:i+chunk_size] for i in range(0, N, chunk_size)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        list(pool.map(heavy_physics, chunks))
    print(f"Processes (Current): {time.time() - start:.4f}s")

    # 3. Threads (The Optimization)
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(heavy_physics, chunks))
    print(f"Threads (Proposed): {time.time() - start:.4f}s")

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()
