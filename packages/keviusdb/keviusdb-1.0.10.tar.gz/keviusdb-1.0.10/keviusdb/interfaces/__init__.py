"""
Abstract interfaces for KeviusDB components.
Provides virtual interfaces for customizable OS interactions and extensibility.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Tuple, Optional, Protocol
from contextlib import contextmanager


class FileSystemInterface(ABC):
    """Virtual interface for file system operations."""
    
    @abstractmethod
    def read_file(self, path: str) -> bytes:
        """Read entire file content."""
        pass
    
    @abstractmethod
    def write_file(self, path: str, data: bytes) -> None:
        """Write data to file."""
        pass
    
    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        pass
    
    @abstractmethod
    def delete_file(self, path: str) -> None:
        """Delete file."""
        pass
    
    @abstractmethod
    def create_directory(self, path: str) -> None:
        """Create directory if it doesn't exist."""
        pass


class CompressionInterface(ABC):
    """Interface for data compression."""
    
    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        """Compress data."""
        pass
    
    @abstractmethod
    def decompress(self, compressed_data: bytes) -> bytes:
        """Decompress data."""
        pass


class StorageInterface(ABC):
    """Interface for storage operations."""
    
    @abstractmethod
    def put(self, key: bytes, value: bytes) -> None:
        """Store key-value pair."""
        pass
    
    @abstractmethod
    def get(self, key: bytes) -> Optional[bytes]:
        """Retrieve value for key."""
        pass
    
    @abstractmethod
    def delete(self, key: bytes) -> bool:
        """Delete key-value pair. Returns True if key existed."""
        pass
    
    @abstractmethod
    def iterate(self, start_key: Optional[bytes] = None, 
                end_key: Optional[bytes] = None, 
                reverse: bool = False) -> Iterator[Tuple[bytes, bytes]]:
        """Iterate over key-value pairs in sorted order."""
        pass
    
    @abstractmethod
    def snapshot(self) -> 'StorageInterface':
        """Create a snapshot of current state."""
        pass
    
    @abstractmethod
    def flush(self) -> None:
        """Persist changes to storage."""
        pass


class BatchInterface(ABC):
    """Interface for batch operations."""
    
    @abstractmethod
    def put(self, key: bytes, value: bytes) -> None:
        """Add put operation to batch."""
        pass
    
    @abstractmethod
    def delete(self, key: bytes) -> None:
        """Add delete operation to batch."""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """Commit all operations atomically."""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback all operations."""
        pass


class ComparisonFunction(Protocol):
    """Protocol for custom key comparison functions."""
    
    def __call__(self, key1: bytes, key2: bytes) -> int:
        """
        Compare two keys.
        Returns:
            < 0 if key1 < key2
            = 0 if key1 == key2
            > 0 if key1 > key2
        """
        pass


class DatabaseInterface(ABC):
    """Main database interface."""
    
    @abstractmethod
    def put(self, key: str, value: str) -> None:
        """Store key-value pair."""
        pass
    
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Retrieve value for key."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key-value pair."""
        pass
    
    @abstractmethod
    @contextmanager
    def batch(self) -> Iterator[BatchInterface]:
        """Create atomic batch operation context."""
        pass
    
    @abstractmethod
    def snapshot(self) -> 'DatabaseInterface':
        """Create snapshot for consistent reads."""
        pass
    
    @abstractmethod
    def iterate(self, start_key: Optional[str] = None,
                end_key: Optional[str] = None,
                reverse: bool = False) -> Iterator[Tuple[str, str]]:
        """Iterate over key-value pairs."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close database and cleanup resources."""
        pass
