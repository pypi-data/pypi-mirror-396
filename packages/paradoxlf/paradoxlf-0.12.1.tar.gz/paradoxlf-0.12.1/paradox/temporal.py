import numpy as np

class LatentTrajectory:
    """
    Analyzes sequences of latent vectors to understand temporal dynamics.
    Useful for Video Analysis, Thought Streams, and Prediction.
    """
    def __init__(self, vectors):
        """
        Args:
            vectors: List or Array of shape (T, D) where T=Time, D=Dimension.
        """
        self.vectors = np.array(vectors, dtype=np.float32)
        if len(self.vectors) < 2:
            raise ValueError("Trajectory requires at least 2 points.")
            
    def velocity(self):
        """
        Calculate rate of change between steps.
        Returns array of shape (T-1, D).
        """
        return np.diff(self.vectors, axis=0)
        
    def speed(self):
        """
        Magnitude of velocity (Scalar speed per step).
        Returns array of shape (T-1,).
        """
        vel = self.velocity()
        return np.linalg.norm(vel, axis=1)
        
    def predict_next(self, steps=1, method="linear"):
        """
        Predict future states based on current trajectory.
        Args:
            steps: How many steps to look ahead.
            method: 'linear' (momentum based) or 'average' (avg velocity).
        """
        current_pos = self.vectors[-1]
        
        if method == "linear":
            # Use last known velocity (Momentum)
            vel = self.vectors[-1] - self.vectors[-2]
            future = []
            for i in range(1, steps + 1):
                future.append(current_pos + vel * i)
            return np.array(future)
            
        elif method == "average":
            # Use average velocity of entire path
            avg_vel = np.mean(self.velocity(), axis=0)
            future = []
            for i in range(1, steps + 1):
                future.append(current_pos + avg_vel * i)
            return np.array(future)
        else:
            raise ValueError(f"Unknown method: {method}")

    def curvature(self):
        """
        Measure how 'curved' the thought path is.
        High curvature = changing topics/direction rapidly.
        Low curvature = straight logical path.
        """
        if len(self.vectors) < 3:
            return 0.0
            
        vel = self.velocity()
        # Cosine sim between v_t and v_{t+1}
        # Angle change
        curves = []
        for i in range(len(vel) - 1):
            v1 = vel[i]
            v2 = vel[i+1]
            if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
                curves.append(0.0)
                continue
            
            cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            # Clamp for safety
            cosine = np.clip(cosine, -1.0, 1.0)
            angle = np.arccos(cosine)
            curves.append(angle)
            
        return np.mean(curves)
