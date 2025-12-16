import time
import logging

logger = logging.getLogger("ParadoxSimulation")

class SimulationEnv:
    def __init__(self, engine):
        """
        Initialize the simulation environment with a Paradox Engine.
        """
        self.engine = engine
        self.running = False
        
    def step(self, dynamics_fn, dt=0.1):
        """
        Apply a dynamics function to evolve the latent state.
        
        Args:
            dynamics_fn (callable): Function that takes (vectors, dt) and returns delta_vectors
            dt (float): Time step delta
        """
        if self.engine.count == 0:
            return

        # Access vectors directly based on backend
        vectors = self.engine.vectors
        
        # Calculate update
        delta = dynamics_fn(vectors, dt, self.engine.backend_type)
        
        # Apply update
        if self.engine.backend_type == "numpy":
            self.engine.vectors += delta
        elif self.engine.backend_type == "torch":
            self.engine.vectors += delta
            
    def run(self, steps, dynamics_fn, dt=0.1, callback=None):
        """
        Run the simulation for a fixed number of steps.
        """
        self.running = True
        logger.info(f"Starting simulation for {steps} steps...")
        
        for i in range(steps):
             self.step(dynamics_fn, dt)
             if callback:
                 callback(i, self.engine)
        
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
