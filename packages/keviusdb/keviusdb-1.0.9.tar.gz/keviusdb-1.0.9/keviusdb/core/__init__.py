"""
Core database engine implementation.
Provides the main KeviusDB class with all key-value operations.
"""

from typing import Optional, Iterator, Tuple
from contextlib import contextmanager

from ..interfaces import (
    DatabaseInterface, BatchInterface, StorageInterface, 
    FileSystemInterface, CompressionInterface, ComparisonFunction
)
from ..storage import PersistentStorage, MemoryStorage, DefaultFileSystem, LZ4Compression
from ..comparison import ComparisonManager
from ..transaction import TransactionManager, Batch
from ..iteration import IteratorFactory

from pycache_handler.handler import py_cache_handler

class KeviusDB(DatabaseInterface):
    """
    Main KeviusDB class - A fast key-value storage library.
    
    Provides ordered mapping from string keys to string values with:
    - Sorted storage by key
    - Custom comparison functions
    - Atomic batch operations
    - Transient snapshots
    - Forward/backward iteration
    - Automatic compression
    - Virtual interfaces for customization
    """
    
    @py_cache_handler
    def __init__(self, 
                 file_path: Optional[str] = None,
                 comparison_func: Optional[ComparisonFunction] = None,
                 filesystem: Optional[FileSystemInterface] = None,
                 compression: Optional[CompressionInterface] = None,
                 in_memory: bool = False):
        """
        Initialize KeviusDB.
        
        Args:
            file_path: Path to database file (None for memory-only)
            comparison_func: Custom key comparison function
            filesystem: Custom filesystem interface
            compression: Custom compression interface
            in_memory: Force in-memory storage
        """
        self._file_path = file_path
        self._comparison_manager = ComparisonManager(comparison_func)
        self._filesystem = filesystem or DefaultFileSystem()
        self._compression = compression or LZ4Compression()
        self._closed = False
        
        # Initialize storage
        if in_memory or file_path is None:
            self._storage = MemoryStorage(self._comparison_manager)
        else:
            self._storage = PersistentStorage(
                file_path, self._comparison_manager, 
                self._filesystem, self._compression
            )
        
        # Initialize transaction manager and iterator factory
        self._transaction_manager = TransactionManager(self._storage)
        self._iterator_factory = IteratorFactory(self._storage)
    
    def put(self, key: str, value: str) -> None:
        """
        Store key-value pair.
        
        Args:
            key: String key
            value: String value
        """
        self._check_not_closed()
        key_bytes = key.encode('utf-8')
        value_bytes = value.encode('utf-8')
        self._storage.put(key_bytes, value_bytes)
    
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve value for key.
        
        Args:
            key: String key
            
        Returns:
            Value string or None if key not found
        """
        self._check_not_closed()
        key_bytes = key.encode('utf-8')
        value_bytes = self._storage.get(key_bytes)
        return value_bytes.decode('utf-8') if value_bytes is not None else None
    
    def delete(self, key: str) -> bool:
        """
        Delete key-value pair.
        
        Args:
            key: String key
            
        Returns:
            True if key existed and was deleted, False otherwise
        """
        self._check_not_closed()
        key_bytes = key.encode('utf-8')
        return self._storage.delete(key_bytes)
    
    @contextmanager
    def batch(self) -> Iterator[BatchInterface]:
        """
        Create atomic batch operation context.
        
        Usage:
            with db.batch() as batch:
                batch.put("key1", "value1")
                batch.put("key2", "value2")
                # Automatically committed on context exit
        """
        self._check_not_closed()
        batch_obj = self._transaction_manager.create_batch()
        
        try:
            yield BatchWrapper(batch_obj)
            batch_obj.commit()
        except Exception:
            batch_obj.rollback()
            raise
    
    def snapshot(self) -> 'DatabaseSnapshot':
        """
        Create snapshot for consistent reads.
        
        Returns:
            DatabaseSnapshot instance
        """
        self._check_not_closed()
        storage_snapshot = self._transaction_manager.create_snapshot()
        return DatabaseSnapshot(storage_snapshot, self._comparison_manager)
    
    def iterate(self, start_key: Optional[str] = None,
                end_key: Optional[str] = None,
                reverse: bool = False) -> Iterator[Tuple[str, str]]:
        """
        Iterate over key-value pairs.
        
        Args:
            start_key: Start key (inclusive), None for beginning
            end_key: End key (inclusive), None for end
            reverse: Iterate in reverse order
            
        Yields:
            Tuple of (key, value) strings
        """
        self._check_not_closed()
        start_bytes = start_key.encode('utf-8') if start_key else None
        end_bytes = end_key.encode('utf-8') if end_key else None
        
        for key_bytes, value_bytes in self._storage.iterate(start_bytes, end_bytes, reverse):
            yield key_bytes.decode('utf-8'), value_bytes.decode('utf-8')
    
    def iterate_keys(self, start_key: Optional[str] = None,
                    end_key: Optional[str] = None,
                    reverse: bool = False) -> Iterator[str]:
        """Iterate over keys only."""
        for key, _ in self.iterate(start_key, end_key, reverse):
            yield key
    
    def iterate_values(self, start_key: Optional[str] = None,
                      end_key: Optional[str] = None,
                      reverse: bool = False) -> Iterator[str]:
        """Iterate over values only."""
        for _, value in self.iterate(start_key, end_key, reverse):
            yield value
    
    def iterate_prefix(self, prefix: str, reverse: bool = False) -> Iterator[Tuple[str, str]]:
        """
        Iterate over keys with specific prefix.
        
        Args:
            prefix: Key prefix to match
            reverse: Iterate in reverse order
            
        Yields:
            Tuple of (key, value) strings
        """
        self._check_not_closed()
        prefix_bytes = prefix.encode('utf-8')
        iterator = self._iterator_factory.prefix_iterator(prefix_bytes, reverse)
        
        for key_bytes, value_bytes in iterator:
            yield key_bytes.decode('utf-8'), value_bytes.decode('utf-8')
    
    def flush(self) -> None:
        """Force persistence of changes to storage."""
        self._check_not_closed()
        self._storage.flush()
    
    def close(self) -> None:
        """Close database and cleanup resources."""
        if not self._closed:
            self._storage.flush()
            if hasattr(self._storage, 'close'):
                self._storage.close()
            self._closed = True
    
    def size(self) -> int:
        """Get number of key-value pairs."""
        self._check_not_closed()
        if hasattr(self._storage, 'size'):
            return self._storage.size()
        # Fallback: count by iteration
        return sum(1 for _ in self.iterate())
    
    def is_empty(self) -> bool:
        """Check if database is empty."""
        return self.size() == 0
    
    def contains(self, key: str) -> bool:
        """Check if key exists."""
        return self.get(key) is not None
    
    def clear(self) -> None:
        """Remove all key-value pairs."""
        self._check_not_closed()
        if hasattr(self._storage, 'clear'):
            self._storage.clear()
        else:
            # Fallback: delete all keys
            keys_to_delete = list(self.iterate_keys())
            for key in keys_to_delete:
                self.delete(key)
    
    def set_comparison_function(self, comparison_func: ComparisonFunction) -> None:
        """
        Set a new comparison function.
        
        Warning: This will affect the ordering of existing data.
        Consider creating a new database instance instead.
        """
        self._comparison_manager.set_comparison_function(comparison_func)
    
    def _check_not_closed(self) -> None:
        """Check if database is not closed."""
        if self._closed:
            raise RuntimeError("Database is closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __len__(self) -> int:
        """Get number of key-value pairs."""
        return self.size()
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists."""
        return self.contains(key)
    
    def __getitem__(self, key: str) -> str:
        """Get value by key (raises KeyError if not found)."""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
    
    def __setitem__(self, key: str, value: str) -> None:
        """Set value by key."""
        self.put(key, value)
    
    def __delitem__(self, key: str) -> None:
        """Delete key (raises KeyError if not found)."""
        if not self.delete(key):
            raise KeyError(key)
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        return self.iterate_keys()


class BatchWrapper(BatchInterface):
    """Wrapper for batch operations to handle string conversion."""
    
    def __init__(self, batch: Batch):
        self._batch = batch
    
    def put(self, key: str, value: str) -> None:
        """Add put operation to batch."""
        key_bytes = key.encode('utf-8')
        value_bytes = value.encode('utf-8')
        self._batch.put(key_bytes, value_bytes)
    
    def delete(self, key: str) -> None:
        """Add delete operation to batch."""
        key_bytes = key.encode('utf-8')
        self._batch.delete(key_bytes)
    
    def commit(self) -> None:
        """Commit all operations atomically."""
        self._batch.commit()
    
    def rollback(self) -> None:
        """Rollback all operations."""
        self._batch.rollback()


class DatabaseSnapshot(DatabaseInterface):
    """Snapshot of database for consistent reads."""
    
    def __init__(self, storage_snapshot: StorageInterface, comparison_manager):
        self._storage = storage_snapshot
        self._comparison_manager = comparison_manager
        self._iterator_factory = IteratorFactory(self._storage)
    
    def put(self, key: str, value: str) -> None:
        """Not supported on snapshots."""
        raise RuntimeError("Cannot modify snapshot")
    
    def delete(self, key: str) -> bool:
        """Not supported on snapshots."""
        raise RuntimeError("Cannot modify snapshot")
    
    def get(self, key: str) -> Optional[str]:
        """Retrieve value for key from snapshot."""
        key_bytes = key.encode('utf-8')
        value_bytes = self._storage.get(key_bytes)
        return value_bytes.decode('utf-8') if value_bytes is not None else None
    
    @contextmanager
    def batch(self) -> Iterator[BatchInterface]:
        """Not supported on snapshots."""
        raise RuntimeError("Cannot create batch on snapshot")
    
    def snapshot(self) -> 'DatabaseSnapshot':
        """Create another snapshot."""
        storage_snapshot = self._storage.snapshot()
        return DatabaseSnapshot(storage_snapshot, self._comparison_manager)
    
    def iterate(self, start_key: Optional[str] = None,
                end_key: Optional[str] = None,
                reverse: bool = False) -> Iterator[Tuple[str, str]]:
        """Iterate over key-value pairs in snapshot."""
        start_bytes = start_key.encode('utf-8') if start_key else None
        end_bytes = end_key.encode('utf-8') if end_key else None
        
        for key_bytes, value_bytes in self._storage.iterate(start_bytes, end_bytes, reverse):
            yield key_bytes.decode('utf-8'), value_bytes.decode('utf-8')
    
    def close(self) -> None:
        """Close snapshot."""
        pass  # Snapshots don't need explicit cleanup
