import time
import logging

logger = logging.getLogger("ParadoxSimulation")

import concurrent.futures
import multiprocessing
import numpy as np

# Top-level helper for multiprocessing
def _parallel_worker(args):
    """
    Worker function for parallel step execution.
    args: (chunk, dynamics_fn, dt)
    """
    chunk, dynamics_fn, dt = args
    return dynamics_fn(chunk, dt, "numpy")

class SimulationEnv:
    def __init__(self, engine):
        """
        Initialize the simulation environment with a Paradox Engine.
        """
        self.engine = engine
        self.running = False
        self.num_workers = multiprocessing.cpu_count()
        
    def step(self, dynamics_fn, dt=0.1, parallel="auto", executor=None):
        """
        Apply a dynamics function to evolve the latent state.
        ...
        executor: Optional ProcessPoolExecutor instance for reuse.
        """
        if self.engine.count == 0:
            return

        # Auto-Tune Parallelism
        # Based on Threading benchmarks, overhead is negligible.
        PARALLEL_THRESHOLD = 10000 
        
        if parallel == "auto":
            if self.engine.count > PARALLEL_THRESHOLD:
                parallel = True
            else:
                parallel = False

        # If Torch backend (GPU), parallel CPU doesn't make sense, so ignore it.
        # Torch handles parallelism internally on the GPU.
        if self.engine.backend_type == "torch":
            parallel = False

        if not parallel:
            # Single-threaded (Standard)
            delta = dynamics_fn(self.engine.vectors, dt, self.engine.backend_type)
            if delta is not None:
                self.engine.vectors += delta
        else:
            # Multi-processing (CPU only)
            vectors = self.engine.vectors
            chunk_size = len(vectors) // self.num_workers
            if chunk_size < 1: chunk_size = 1
            
            tasks = []
            for i in range(0, len(vectors), chunk_size):
                chunk = vectors[i:i + chunk_size]
                tasks.append((chunk, dynamics_fn, dt))

            # Execute in parallel
            if executor:
                results = list(executor.map(_parallel_worker, tasks))
            else:
                # Fallback if no executor provided (slower)
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as pool:
                    results = list(pool.map(_parallel_worker, tasks))
            
            # Reassemble results
            if results and results[0] is not None:
                delta = np.vstack(results)
                self.engine.vectors += delta
            
    def run(self, steps, dynamics_fn, dt=0.1, callback=None, parallel="auto"):
        """
        Run the simulation for a fixed number of steps.
        """
        self.running = True
        logger.info(f"Starting simulation for {steps} steps (Parallel={parallel})...")
        
        # Resolve Auto
        if parallel == "auto":
             if self.engine.count > 100000 and self.engine.backend_type == "numpy":
                 parallel = True
             else:
                 parallel = False

        executor = None
        if parallel and self.engine.backend_type == "numpy":
             # Use ThreadPoolExecutor instead of ProcessPool for NumPy workloads
             # NumPy releases the GIL, so threads are far more efficient (Shared Memory, No Pickling)
             executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers)

        try:
            for i in range(steps):
                if not self.running: break
                self.step(dynamics_fn, dt, parallel=parallel, executor=executor)
                if callback:
                    callback(i, self.engine)
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user.")
        finally:
            if executor:
                executor.shutdown()
        
        self.running = False
        logger.info("Simulation complete.")

# --- Example Dynamics Functions ---

def simple_gravity_well(vectors, dt, backend):
    """
    Pulls all objects slightly towards the origin (0,0,...).
    Delta = -0.01 * vector * dt
    """
    if backend == "numpy":
        return -0.1 * vectors * dt
    elif backend == "torch":
        return -0.1 * vectors * dt
