import numpy as np

class GuardRail:
    """
    Phase 6: Safety Constraints.
    """
    def __init__(self, max_norm=5.0, forbidden_regions=None):
        self.max_norm = max_norm
        self.forbidden_regions = forbidden_regions or []

    def check(self, vector):
        """Returns True if safe, False if dangerous."""
        norm = np.linalg.norm(vector)
        if norm > self.max_norm:
            return False, f"Magnitude Violation ({norm:.2f} > {self.max_norm})"
        
        # Check forbidden logical zones (Phase 6 placeholder)
        for region in self.forbidden_regions:
            if np.linalg.norm(vector - region) < 0.5:
                return False, "Forbidden Concept Proximity"
                
        return True, "Safe"

    def sanitize(self, vector):
        """Clamps vector to safety limits."""
        norm = np.linalg.norm(vector)
        if norm > self.max_norm:
            return vector * (self.max_norm / norm)
        return vector
