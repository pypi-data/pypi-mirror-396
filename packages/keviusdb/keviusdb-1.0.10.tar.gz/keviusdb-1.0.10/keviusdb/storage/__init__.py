"""
Storage layer implementations.
Handles data persistence, compression, and file system operations.
"""

import os
import json
import lz4.frame
from typing import Optional, Iterator, Tuple
from ..interfaces import FileSystemInterface, CompressionInterface, StorageInterface


class DefaultFileSystem(FileSystemInterface):
    """Default file system implementation using standard Python I/O."""
    
    def read_file(self, path: str) -> bytes:
        """Read entire file content."""
        try:
            with open(path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path}")
    
    def write_file(self, path: str, data: bytes) -> None:
        """Write data to file."""
        # Ensure directory exists
        directory = os.path.dirname(path)
        if directory:
            self.create_directory(directory)
        
        with open(path, 'wb') as f:
            f.write(data)
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        return os.path.exists(path)
    
    def delete_file(self, path: str) -> None:
        """Delete file."""
        if self.file_exists(path):
            os.remove(path)
    
    def create_directory(self, path: str) -> None:
        """Create directory if it doesn't exist."""
        if path and not os.path.exists(path):
            os.makedirs(path, exist_ok=True)


class LZ4Compression(CompressionInterface):
    """LZ4 compression implementation for fast compression/decompression."""
    
    def compress(self, data: bytes) -> bytes:
        """Compress data using LZ4."""
        if not data:
            return b''
        return lz4.frame.compress(data)
    
    def decompress(self, compressed_data: bytes) -> bytes:
        """Decompress LZ4 compressed data."""
        if not compressed_data:
            return b''
        return lz4.frame.decompress(compressed_data)


class MemoryStorage(StorageInterface):
    """In-memory storage implementation using sorted containers."""
    
    def __init__(self, comparison_manager):
        from sortedcontainers import SortedDict
        from functools import cmp_to_key
        
        self._comparison_manager = comparison_manager
        self._data = SortedDict(cmp_to_key(self._comparison_manager.compare))
    
    def put(self, key: bytes, value: bytes) -> None:
        """Store key-value pair in memory."""
        self._data[key] = value
    
    def get(self, key: bytes) -> Optional[bytes]:
        """Retrieve value for key from memory."""
        return self._data.get(key)
    
    def delete(self, key: bytes) -> bool:
        """Delete key-value pair from memory."""
        if key in self._data:
            del self._data[key]
            return True
        return False
    
    def iterate(self, start_key: Optional[bytes] = None,
                end_key: Optional[bytes] = None,
                reverse: bool = False) -> Iterator[Tuple[bytes, bytes]]:
        """Iterate over key-value pairs in sorted order."""
        items = self._data.items()
        
        if start_key is not None or end_key is not None:
            filtered_items = []
            for key, value in items:
                if start_key is not None and self._comparison_manager.is_less_than(key, start_key):
                    continue
                if end_key is not None and self._comparison_manager.is_greater_than(key, end_key):
                    continue
                filtered_items.append((key, value))
            items = filtered_items
        
        if reverse:
            items = reversed(list(items))
        
        yield from items
    
    def snapshot(self) -> 'MemoryStorage':
        """Create a snapshot of current state."""
        snapshot = MemoryStorage(self._comparison_manager)
        snapshot._data = self._data.copy()
        return snapshot
    
    def flush(self) -> None:
        """No-op for memory storage."""
        pass
    
    def clear(self) -> None:
        """Clear all data."""
        self._data.clear()
    
    def size(self) -> int:
        """Get number of key-value pairs."""
        return len(self._data)


class PersistentStorage(StorageInterface):
    """Persistent storage implementation with compression."""
    
    def __init__(self, file_path: str, comparison_manager,
                 filesystem: Optional[FileSystemInterface] = None,
                 compression: Optional[CompressionInterface] = None):
        self._file_path = file_path
        self._comparison_manager = comparison_manager
        self._filesystem = filesystem or DefaultFileSystem()
        self._compression = compression or LZ4Compression()
        self._memory_storage = MemoryStorage(comparison_manager)
        self._dirty = False
        
        # Load existing data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load data from file."""
        if not self._filesystem.file_exists(self._file_path):
            return
        
        try:
            compressed_data = self._filesystem.read_file(self._file_path)
            if compressed_data:
                data = self._compression.decompress(compressed_data)
                entries = json.loads(data.decode('utf-8'))
                
                for key_str, value_str in entries:
                    key = key_str.encode('utf-8')
                    value = value_str.encode('utf-8')
                    self._memory_storage.put(key, value)
        except Exception as e:
            raise RuntimeError(f"Failed to load data from {self._file_path}: {e}")
    
    def _save_data(self) -> None:
        """Save data to file."""
        if not self._dirty:
            return
        
        try:
            entries = []
            for key, value in self._memory_storage.iterate():
                entries.append([key.decode('utf-8'), value.decode('utf-8')])
            
            data = json.dumps(entries).encode('utf-8')
            compressed_data = self._compression.compress(data)
            self._filesystem.write_file(self._file_path, compressed_data)
            self._dirty = False
        except Exception as e:
            raise RuntimeError(f"Failed to save data to {self._file_path}: {e}")
    
    def put(self, key: bytes, value: bytes) -> None:
        """Store key-value pair."""
        self._memory_storage.put(key, value)
        self._dirty = True
    
    def get(self, key: bytes) -> Optional[bytes]:
        """Retrieve value for key."""
        return self._memory_storage.get(key)
    
    def delete(self, key: bytes) -> bool:
        """Delete key-value pair."""
        result = self._memory_storage.delete(key)
        if result:
            self._dirty = True
        return result
    
    def iterate(self, start_key: Optional[bytes] = None,
                end_key: Optional[bytes] = None,
                reverse: bool = False) -> Iterator[Tuple[bytes, bytes]]:
        """Iterate over key-value pairs."""
        return self._memory_storage.iterate(start_key, end_key, reverse)
    
    def snapshot(self) -> StorageInterface:
        """Create a snapshot of current state."""
        return self._memory_storage.snapshot()
    
    def flush(self) -> None:
        """Persist changes to storage."""
        self._save_data()
    
    def close(self) -> None:
        """Close storage and save changes."""
        self.flush()
    
    def size(self) -> int:
        """Get number of key-value pairs."""
        return self._memory_storage.size()
