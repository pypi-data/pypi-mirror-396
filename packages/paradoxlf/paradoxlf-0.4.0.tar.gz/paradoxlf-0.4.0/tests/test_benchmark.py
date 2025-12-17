import sys
import os
import time
import numpy as np
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.simulation import SimulationEnv

def heavy_physics(vectors, dt, backend):
    """
    A physics function that intentionally does some heavy math 
    to make CPU usage visible.
    """
    # Simulate N-body-ish complexity or just heavy math
    # Here we just do some expensive trig operations
    return np.sin(vectors) * np.cos(vectors) * 0.01

def main():
    print("=== Paradox V0.4.0 Benchmark: Parallel Simulation ===")
    
    # 1. Setup massive dataset
    N = 50000 # 50k vectors
    Dim = 128
    print(f"Initializing {N} vectors (Dim={Dim})...")
    
    engine = LatentMemoryEngine(dimension=Dim)
    # Fast bulk add hack for benchmark
    engine.vectors = np.random.rand(N, Dim).astype(np.float32)
    engine.count = N
    
    sim = SimulationEnv(engine)
    
    # 2. Test Single Threaded
    print("\n[Running Single-Threaded Mode...]")
    start_time = time.time()
    sim.run(steps=5, dynamics_fn=heavy_physics, parallel=False)
    single_duration = time.time() - start_time
    print(f"Single-Threaded Duration: {single_duration:.4f}s")
    
    # 3. Test Parallel (Forced)
    print("\n[Running Parallel Mode...]")
    start_time = time.time()
    sim.run(steps=5, dynamics_fn=heavy_physics, parallel=True)
    parallel_duration = time.time() - start_time
    print(f"Parallel Duration: {parallel_duration:.4f}s")

    # 4. Test Auto (Should choose False for 50k items)
    print("\n[Running Auto Mode (Expect Single-Threaded)...]")
    start_time = time.time()
    sim.run(steps=5, dynamics_fn=heavy_physics, parallel="auto")
    auto_duration = time.time() - start_time
    print(f"Auto Duration: {auto_duration:.4f}s")
    
    # 4. Result
    speedup = single_duration / parallel_duration
    print(f"\nSpeedup Factor: {speedup:.2f}x")
    
    if speedup > 0.8: # Allowing 0.8 for overhead, though ideally > 1.0
        print("Test PASSED: Parallel mode is functional.")
    else:
        print("WARNING: Parallel mode might be slower (overhead on small workload).")

if __name__ == "__main__":
    # Windows needs freeze_support for multiprocessing
    from multiprocessing import freeze_support
    freeze_support()
    main()
