"""
Test suite for KeviusDB.
Comprehensive tests for all functionality.
"""

import unittest
import tempfile
import os
import sys
import shutil

# Add the parent directory to the path so we can import keviusdb
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keviusdb import KeviusDB, create_memory_database
from keviusdb.comparison import ReverseComparison, NumericComparison
from keviusdb.interfaces import FileSystemInterface, CompressionInterface


class TestKeviusDBBasic(unittest.TestCase):
    """Test basic KeviusDB operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db = create_memory_database()
    
    def tearDown(self):
        """Clean up after tests."""
        self.db.close()
    
    def test_put_get(self):
        """Test basic put and get operations."""
        self.db.put("key1", "value1")
        self.assertEqual(self.db.get("key1"), "value1")
        self.assertIsNone(self.db.get("nonexistent"))
    
    def test_delete(self):
        """Test delete operation."""
        self.db.put("key1", "value1")
        self.assertTrue(self.db.delete("key1"))
        self.assertIsNone(self.db.get("key1"))
        self.assertFalse(self.db.delete("nonexistent"))
    
    def test_contains(self):
        """Test key existence checking."""
        self.db.put("key1", "value1")
        self.assertTrue(self.db.contains("key1"))
        self.assertFalse(self.db.contains("nonexistent"))
    
    def test_size(self):
        """Test database size."""
        self.assertEqual(len(self.db), 0)
        self.db.put("key1", "value1")
        self.assertEqual(len(self.db), 1)
        self.db.put("key2", "value2")
        self.assertEqual(len(self.db), 2)
        self.db.delete("key1")
        self.assertEqual(len(self.db), 1)
    
    def test_clear(self):
        """Test clearing database."""
        self.db.put("key1", "value1")
        self.db.put("key2", "value2")
        self.assertEqual(len(self.db), 2)
        self.db.clear()
        self.assertEqual(len(self.db), 0)
    
    def test_dictionary_interface(self):
        """Test dictionary-like interface."""
        # __setitem__ and __getitem__
        self.db["key1"] = "value1"
        self.assertEqual(self.db["key1"], "value1")
        
        # __contains__
        self.assertTrue("key1" in self.db)
        self.assertFalse("nonexistent" in self.db)
        
        # __delitem__
        del self.db["key1"]
        self.assertFalse("key1" in self.db)
        
        # KeyError for missing keys
        with self.assertRaises(KeyError):
            _ = self.db["nonexistent"]
        
        with self.assertRaises(KeyError):
            del self.db["nonexistent"]


class TestKeviusDBIteration(unittest.TestCase):
    """Test iteration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db = create_memory_database()
        # Add test data in non-sorted order
        data = [("cherry", "red"), ("apple", "green"), ("banana", "yellow"), ("date", "brown")]
        for key, value in data:
            self.db.put(key, value)
    
    def tearDown(self):
        """Clean up after tests."""
        self.db.close()
    
    def test_forward_iteration(self):
        """Test forward iteration (sorted order)."""
        keys = list(self.db.iterate_keys())
        self.assertEqual(keys, ["apple", "banana", "cherry", "date"])
    
    def test_reverse_iteration(self):
        """Test reverse iteration."""
        keys = list(self.db.iterate_keys(reverse=True))
        self.assertEqual(keys, ["date", "cherry", "banana", "apple"])
    
    def test_range_iteration(self):
        """Test range iteration."""
        items = list(self.db.iterate(start_key="banana", end_key="cherry"))
        expected = [("banana", "yellow"), ("cherry", "red")]
        self.assertEqual(items, expected)
    
    def test_prefix_iteration(self):
        """Test prefix iteration."""
        # Add more data with common prefixes
        self.db.put("car", "vehicle")
        self.db.put("cat", "animal")
        self.db.put("care", "concern")
        
        items = list(self.db.iterate_prefix("ca"))
        keys = [item[0] for item in items]
        self.assertIn("car", keys)
        self.assertIn("cat", keys)
        self.assertIn("care", keys)
        self.assertNotIn("apple", keys)
    
    def test_iteration_with_modifications(self):
        """Test iteration behavior when database is modified."""
        keys_before = list(self.db.iterate_keys())
        self.db.put("elderberry", "purple")
        keys_after = list(self.db.iterate_keys())
        
        self.assertEqual(len(keys_after), len(keys_before) + 1)
        self.assertIn("elderberry", keys_after)


class TestKeviusDBBatch(unittest.TestCase):
    """Test batch operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db = create_memory_database()
    
    def tearDown(self):
        """Clean up after tests."""
        self.db.close()
    
    def test_successful_batch(self):
        """Test successful batch commit."""
        with self.db.batch() as batch:
            batch.put("key1", "value1")
            batch.put("key2", "value2")
            batch.delete("nonexistent")  # Should not cause issues
        
        self.assertEqual(self.db.get("key1"), "value1")
        self.assertEqual(self.db.get("key2"), "value2")
    
    def test_batch_rollback_on_exception(self):
        """Test batch rollback when exception occurs."""
        self.db.put("existing", "value")
        
        try:
            with self.db.batch() as batch:
                batch.put("key1", "value1")
                batch.put("key2", "value2")
                raise ValueError("Simulated error")
        except ValueError:
            pass  # Expected
        
        # Changes should be rolled back
        self.assertIsNone(self.db.get("key1"))
        self.assertIsNone(self.db.get("key2"))
        # Existing data should remain
        self.assertEqual(self.db.get("existing"), "value")
    
    def test_empty_batch(self):
        """Test empty batch operations."""
        with self.db.batch() as batch:
            pass  # No operations
        
        self.assertEqual(len(self.db), 0)


class TestKeviusDBSnapshot(unittest.TestCase):
    """Test snapshot functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db = create_memory_database()
        self.db.put("key1", "value1")
        self.db.put("key2", "value2")
    
    def tearDown(self):
        """Clean up after tests."""
        self.db.close()
    
    def test_snapshot_consistency(self):
        """Test snapshot provides consistent view."""
        snapshot = self.db.snapshot()
        
        # Modify original database
        self.db.put("key3", "value3")
        self.db.delete("key1")
        
        # Snapshot should be unchanged
        self.assertEqual(snapshot.get("key1"), "value1")
        self.assertEqual(snapshot.get("key2"), "value2")
        self.assertIsNone(snapshot.get("key3"))
        
        # Original database should be changed
        self.assertIsNone(self.db.get("key1"))
        self.assertEqual(self.db.get("key3"), "value3")
    
    def test_snapshot_immutability(self):
        """Test that snapshots are read-only."""
        snapshot = self.db.snapshot()
        
        with self.assertRaises(RuntimeError):
            snapshot.put("key", "value")
        
        with self.assertRaises(RuntimeError):
            snapshot.delete("key")
        
        with self.assertRaises(RuntimeError):
            with snapshot.batch():
                pass


class TestKeviusDBComparison(unittest.TestCase):
    """Test custom comparison functions."""
    
    def test_default_comparison(self):
        """Test default lexicographic comparison."""
        db = create_memory_database()
        
        keys = ["zebra", "apple", "banana"]
        for key in keys:
            db.put(key, f"value_{key}")
        
        sorted_keys = list(db.iterate_keys())
        self.assertEqual(sorted_keys, ["apple", "banana", "zebra"])
        
        db.close()
    
    def test_reverse_comparison(self):
        """Test reverse comparison."""
        db = KeviusDB(comparison_func=ReverseComparison(), in_memory=True)
        
        keys = ["zebra", "apple", "banana"]
        for key in keys:
            db.put(key, f"value_{key}")
        
        sorted_keys = list(db.iterate_keys())
        self.assertEqual(sorted_keys, ["zebra", "banana", "apple"])
        
        db.close()
    
    def test_numeric_comparison(self):
        """Test numeric comparison."""
        db = KeviusDB(comparison_func=NumericComparison(), in_memory=True)
        
        numbers = ["10", "2", "1", "20"]
        for num in numbers:
            db.put(num, f"value_{num}")
        
        sorted_numbers = list(db.iterate_keys())
        self.assertEqual(sorted_numbers, ["1", "2", "10", "20"])
        
        db.close()


class TestKeviusDBPersistence(unittest.TestCase):
    """Test persistent storage functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.temp_dir, "test.kvdb")
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_persistence(self):
        """Test data persistence across database sessions."""
        # Create and populate database
        db1 = KeviusDB(self.db_file)
        db1.put("key1", "value1")
        db1.put("key2", "value2")
        db1.close()
        
        # Reopen and verify data
        db2 = KeviusDB(self.db_file)
        self.assertEqual(db2.get("key1"), "value1")
        self.assertEqual(db2.get("key2"), "value2")
        db2.close()
    
    def test_file_creation(self):
        """Test database file creation."""
        self.assertFalse(os.path.exists(self.db_file))
        
        db = KeviusDB(self.db_file)
        db.put("key", "value")
        db.close()
        
        self.assertTrue(os.path.exists(self.db_file))
    
    def test_compression(self):
        """Test data compression in storage."""
        db = KeviusDB(self.db_file)
        
        # Add repetitive data that should compress well
        repetitive_data = "A" * 10000
        db.put("large_data", repetitive_data)
        db.close()
        
        # File should be smaller than uncompressed data
        file_size = os.path.getsize(self.db_file)
        self.assertLess(file_size, len(repetitive_data))


class MockFileSystem(FileSystemInterface):
    """Mock filesystem for testing custom interfaces."""
    
    def __init__(self):
        self.files = {}
        self.operations = []
    
    def read_file(self, path: str) -> bytes:
        self.operations.append(f"read:{path}")
        if path not in self.files:
            raise FileNotFoundError(path)
        return self.files[path]
    
    def write_file(self, path: str, data: bytes) -> None:
        self.operations.append(f"write:{path}")
        self.files[path] = data
    
    def file_exists(self, path: str) -> bool:
        self.operations.append(f"exists:{path}")
        return path in self.files
    
    def delete_file(self, path: str) -> None:
        self.operations.append(f"delete:{path}")
        if path in self.files:
            del self.files[path]
    
    def create_directory(self, path: str) -> None:
        self.operations.append(f"mkdir:{path}")


class MockCompression(CompressionInterface):
    """Mock compression for testing."""
    
    def compress(self, data: bytes) -> bytes:
        return b"MOCK:" + data
    
    def decompress(self, compressed_data: bytes) -> bytes:
        if compressed_data.startswith(b"MOCK:"):
            return compressed_data[5:]
        return compressed_data


class TestKeviusDBCustomInterfaces(unittest.TestCase):
    """Test custom interface implementations."""
    
    def test_custom_filesystem(self):
        """Test custom filesystem interface."""
        mock_fs = MockFileSystem()
        db = KeviusDB("test.db", filesystem=mock_fs, in_memory=False)
        
        db.put("key", "value")
        db.flush()
        
        # Verify filesystem operations were called
        self.assertTrue(any("write:" in op for op in mock_fs.operations))
        
        # Verify data persistence through mock filesystem
        value = db.get("key")
        self.assertEqual(value, "value")
        
        db.close()
    
    def test_custom_compression(self):
        """Test custom compression interface."""
        mock_compression = MockCompression()
        mock_fs = MockFileSystem()
        
        db = KeviusDB("test.db", filesystem=mock_fs, 
                     compression=mock_compression, in_memory=False)
        
        db.put("key", "value")
        db.flush()
        
        # Check that data was "compressed" with mock prefix
        file_data = mock_fs.files["test.db"]
        self.assertTrue(file_data.startswith(b"MOCK:"))
        
        db.close()


class TestKeviusDBErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_closed_database_operations(self):
        """Test operations on closed database raise errors."""
        db = create_memory_database()
        db.close()
        
        with self.assertRaises(RuntimeError):
            db.put("key", "value")
        
        with self.assertRaises(RuntimeError):
            db.get("key")
        
        with self.assertRaises(RuntimeError):
            db.delete("key")
        
        with self.assertRaises(RuntimeError):
            with db.batch():
                pass
    
    def test_unicode_handling(self):
        """Test Unicode key and value handling."""
        db = create_memory_database()
        
        # Test Unicode keys and values
        unicode_key = "测试键"
        unicode_value = "测试值"
        
        db.put(unicode_key, unicode_value)
        self.assertEqual(db.get(unicode_key), unicode_value)
        
        # Test emoji
        emoji_key = "🔑"
        emoji_value = "🎯"
        
        db.put(emoji_key, emoji_value)
        self.assertEqual(db.get(emoji_key), emoji_value)
        
        db.close()
    
    def test_large_data(self):
        """Test handling of large data."""
        db = create_memory_database()
        
        # Test large values
        large_value = "x" * 100000
        db.put("large", large_value)
        self.assertEqual(db.get("large"), large_value)
        
        # Test many keys
        for i in range(1000):
            db.put(f"key_{i:04d}", f"value_{i}")
        
        self.assertEqual(len(db), 1001)  # 1000 + 1 large value
        
        db.close()


def main():
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestKeviusDBBasic,
        TestKeviusDBIteration,
        TestKeviusDBBatch,
        TestKeviusDBSnapshot,
        TestKeviusDBComparison,
        TestKeviusDBPersistence,
        TestKeviusDBCustomInterfaces,
        TestKeviusDBErrorHandling,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
