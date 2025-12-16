import unittest
import numpy as np
import shutil
import os
from paradox.engine import LatentMemoryEngine

class TestAdvancedFeatures(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./test_adv"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cosine_similarity(self):
        """Test Cosine vs Euclidean metrics."""
        engine = LatentMemoryEngine(dimension=2, backend="numpy")
        
        # Add 3 vectors:
        # A: [1, 0]
        # B: [0, 1] (Orthogonal to A)
        # C: [2, 0] (Same direction as A, magnitude diff)
        
        engine.add([1, 0], {"name": "A"})
        engine.add([0, 1], {"name": "B"})
        engine.add([2, 0], {"name": "C"})
        
        # Euclidean: C is closer to A (dist=1) than B is to A (dist=sqrt(2)=1.41)
        res_euc = engine.query([1, 0], k=3, metric="euclidean")
        # Ordered by dist: A (0), C (1.0), B (1.41)
        self.assertEqual(res_euc[1][2]['name'], "C") # Nearest neighbor (excluding self)

        # Cosine: C is Identical to A (dist=0), B is orthogonal (dist=1)
        res_cos = engine.query([1, 0], k=3, metric="cosine")
        # Ordered by dist: A (0), C (0), B (1)
        # Depending on sort stability, A or C might be first, but B is last.
        
        names = [item[2]['name'] for item in res_cos]
        self.assertIn("A", names[:2])
        self.assertIn("C", names[:2])
        self.assertEqual(names[2], "B")

    def test_visualization_import(self):
        """Ensure visualizer can be initialized."""
        from paradox.visualization import LatentVisualizer
        engine = LatentMemoryEngine(dimension=2)
        viz = LatentVisualizer(engine)
        self.assertIsNotNone(viz)

if __name__ == '__main__':
    unittest.main()
