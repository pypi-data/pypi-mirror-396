import unittest
import shutil
import numpy as np
import os
from paradox.engine import LatentMemoryEngine

class TestParadox(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./test_storage"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_add_and_query(self):
        """Test basic addition and querying functionality."""
        engine = LatentMemoryEngine(dimension=4, backend="numpy")
        
        vec1 = [1, 0, 0, 0]
        vec2 = [0, 1, 0, 0]
        
        engine.add(vec1, {"name": "one"})
        engine.add(vec2, {"name": "two"})
        
        self.assertEqual(engine.count, 2)
        
        # Query near vec1
        results = engine.query([0.9, 0.1, 0, 0], k=1)
        self.assertEqual(results[0][0], 0) # Index 0
        self.assertEqual(results[0][2]['name'], "one")

    def test_persistence(self):
        """Test saving and loading from disk."""
        engine = LatentMemoryEngine(dimension=2, storage_dir=self.test_dir, backend="numpy")
        engine.add([1, 1], {"val": "A"})
        engine.add([2, 2], {"val": "B"})
        engine.save()
        
        # New engine instance
        engine2 = LatentMemoryEngine(dimension=2, storage_dir=self.test_dir, backend="numpy")
        self.assertEqual(engine2.count, 2)
        self.assertEqual(engine2.retrieve(1)['val'], "B")

    def test_encoder(self):
        """Test adding data via an encoder."""
        from paradox.encoder import IdentityEncoder
        engine = LatentMemoryEngine(dimension=3, backend="numpy")
        engine.set_encoder(IdentityEncoder(3))
        
        # Identity encoder expects vector matching dim
        engine.add([1, 2, 3], {"test": "yes"})
        self.assertEqual(engine.count, 1)
        self.assertTrue(np.array_equal(engine.vectors[0], [1, 2, 3]))

if __name__ == '__main__':
    unittest.main()
