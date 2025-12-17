"""
KeviusDB - A fast key-value storage library with ordered mapping.

Provides:
- Ordered storage by key with custom comparison functions
- Basic operations: Put, Get, Delete
- Atomic batch operations
- Transient snapshots for consistent reads
- Forward and backward iteration
- Automatic data compression
- Virtual interfaces for customization

Example usage:
    from keviusdb import KeviusDB
    
    # Create database
    db = KeviusDB("mydb.kvdb")
    
    # Basic operations
    db.put("key1", "value1")
    value = db.get("key1")
    db.delete("key1")
    
    # Batch operations
    with db.batch() as batch:
        batch.put("key2", "value2")
        batch.put("key3", "value3")
    
    # Snapshots
    snapshot = db.snapshot()
    for key, value in snapshot.iterate():
        print(f"{key}: {value}")
    
    # Iteration
    for key, value in db.iterate():
        print(f"{key}: {value}")
    
    db.close()
"""

from .core import KeviusDB, DatabaseSnapshot, BatchWrapper
from .interfaces import (
    DatabaseInterface, BatchInterface, StorageInterface,
    FileSystemInterface, CompressionInterface, ComparisonFunction
)
from .storage import (
    PersistentStorage, MemoryStorage, 
    DefaultFileSystem, LZ4Compression
)
from .comparison import (
    ComparisonManager, DefaultComparison, 
    ReverseComparison, NumericComparison
)
from .transaction import (
    TransactionManager, Batch, AdvancedBatch,
    Operation, OperationType, SavePoint
)
from .iteration import (
    IteratorFactory, KeyValueIterator, KeyIterator, ValueIterator,
    RangeIterator, PrefixIterator, SnapshotIterator
)

__version__ = "1.0.0"
__author__ = "Ivan APEDO"
__email__ = "ivanapedo@gmail.com"
__description__ = "A fast key-value storage library with ordered mapping"

# Main exports
__all__ = [
    # Main classes
    "KeviusDB",
    "DatabaseSnapshot",
    
    # Interfaces
    "DatabaseInterface",
    "BatchInterface", 
    "StorageInterface",
    "FileSystemInterface",
    "CompressionInterface",
    "ComparisonFunction",
    
    # Storage implementations
    "PersistentStorage",
    "MemoryStorage",
    "DefaultFileSystem",
    "LZ4Compression",
    
    # Comparison functions
    "ComparisonManager",
    "DefaultComparison",
    "ReverseComparison", 
    "NumericComparison",
    
    # Transaction management
    "TransactionManager",
    "Batch",
    "AdvancedBatch",
    "Operation",
    "OperationType",
    "SavePoint",
    
    # Iteration
    "IteratorFactory",
    "KeyValueIterator",
    "KeyIterator",
    "ValueIterator", 
    "RangeIterator",
    "PrefixIterator",
    "SnapshotIterator",
]


def create_database(file_path: str = None, **kwargs) -> KeviusDB:
    """
    Convenience function to create a KeviusDB instance.
    
    Args:
        file_path: Path to database file (None for in-memory)
        **kwargs: Additional arguments for KeviusDB constructor
        
    Returns:
        KeviusDB instance
    """
    return KeviusDB(file_path, **kwargs)


def create_memory_database(**kwargs) -> KeviusDB:
    """
    Convenience function to create an in-memory KeviusDB instance.
    
    Args:
        **kwargs: Additional arguments for KeviusDB constructor
        
    Returns:
        In-memory KeviusDB instance
    """
    return KeviusDB(in_memory=True, **kwargs)
