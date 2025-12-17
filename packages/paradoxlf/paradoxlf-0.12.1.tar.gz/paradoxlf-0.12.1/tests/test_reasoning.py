
import unittest
import numpy as np
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.mixer import ParadoxMixer

class TestLatentReasoning(unittest.TestCase):
    def setUp(self):
        # 1-Dimensional engine for easy math verification
        self.engine = LatentMemoryEngine(dimension=1, backend="numpy")
        
    def test_basic_arithmetic(self):
        """Verify Mixer arithmetic operations."""
        v1 = np.array([10.0])
        v2 = np.array([5.0])
        
        # Test Add
        res_add = ParadoxMixer.add(v1, v2)
        self.assertTrue(np.allclose(res_add, [15.0]))
        
        # Test Subtract
        res_sub = ParadoxMixer.subtract(v1, v2)
        self.assertTrue(np.allclose(res_sub, [5.0]))
        
        # Test Interpolate (Blending)
        res_mix = ParadoxMixer.interpolate(v1, v2, ratio=0.5)
        self.assertTrue(np.allclose(res_mix, [7.5]))

    def test_analogy_logic(self):
        """
        Verify Analogy: A is to B as C is to ?
        Formula: Result = B - A + C
        Example: 2 is to 4 as 10 is to ? (4 - 2 + 10 = 12)
        """
        a = np.array([2.0])
        b = np.array([4.0])
        c = np.array([10.0])
        
        expected = np.array([12.0])
        result = ParadoxMixer.analogy(a, b, c)
        
        self.assertTrue(np.allclose(result, expected), f"Expected 12.0, got {result}")

    def test_reasoning_flow_in_engine(self):
        """
        Full integration test: Add concepts, perform reasoning, search for result.
        """
        # Add "Concepts" as simple numbers
        # King=10, Man=5, Woman=3 -> Queen should be King(10) - Man(5) + Woman(3) = 8
        
        self.engine.add(np.array([10.0]), {"name": "King"})
        self.engine.add(np.array([5.0]), {"name": "Man"})
        self.engine.add(np.array([3.0]), {"name": "Woman"})
        self.engine.add(np.array([8.0]), {"name": "Queen"}) # The target
        self.engine.add(np.array([50.0]), {"name": "Castle"}) # Distractor
        
        # Perform Reasoning
        # We manually retrieve vectors for simulation
        # In real app, we would use encoder.encode("King")
        v_king = self.engine.query(np.array([10.0]), k=1)[0][2]["vector"] if "vector" in self.engine.query(np.array([10.0]), k=1)[0][2] else np.array([10.0]) 
        # Actually easier to just use raw values since we know them
        
        v_res = ParadoxMixer.analogy(np.array([5.0]), np.array([10.0]), np.array([3.0])) 
        # Check math: 10 - 5 + 3 = 8
        
        # Search for result
        results = self.engine.query(v_res, k=1)
        
        # Verify
        best_match_name = results[0][2]["name"]
        dist = results[0][1]
        
        self.assertEqual(best_match_name, "Queen")
        self.assertLess(dist, 0.001)

if __name__ == '__main__':
    unittest.main()
