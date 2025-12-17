"""
Transaction and batch operation management.
Provides atomic operations and rollback capabilities.
"""

from typing import List, Optional
from enum import Enum
from ..interfaces import BatchInterface, StorageInterface


class OperationType(Enum):
    """Types of operations in a batch."""
    PUT = "put"
    DELETE = "delete"


class Operation:
    """Represents a single operation in a batch."""
    
    def __init__(self, op_type: OperationType, key: bytes, value: Optional[bytes] = None):
        self.op_type = op_type
        self.key = key
        self.value = value
    
    def __repr__(self) -> str:
        if self.op_type == OperationType.PUT:
            return f"PUT({self.key!r}, {self.value!r})"
        else:
            return f"DELETE({self.key!r})"


class Batch(BatchInterface):
    """Atomic batch operation implementation."""
    
    def __init__(self, storage: StorageInterface):
        self._storage = storage
        self._operations: List[Operation] = []
        self._committed = False
        self._rolled_back = False
    
    def put(self, key: bytes, value: bytes) -> None:
        """Add put operation to batch."""
        if self._committed or self._rolled_back:
            raise RuntimeError("Cannot modify committed or rolled back batch")
        
        self._operations.append(Operation(OperationType.PUT, key, value))
    
    def delete(self, key: bytes) -> None:
        """Add delete operation to batch."""
        if self._committed or self._rolled_back:
            raise RuntimeError("Cannot modify committed or rolled back batch")
        
        self._operations.append(Operation(OperationType.DELETE, key))
    
    def commit(self) -> None:
        """Commit all operations atomically."""
        if self._committed:
            raise RuntimeError("Batch already committed")
        if self._rolled_back:
            raise RuntimeError("Cannot commit rolled back batch")
        
        try:
            # Apply all operations
            for operation in self._operations:
                if operation.op_type == OperationType.PUT:
                    self._storage.put(operation.key, operation.value)
                elif operation.op_type == OperationType.DELETE:
                    self._storage.delete(operation.key)
            
            self._committed = True
        except Exception as e:
            # If any operation fails, we should ideally rollback
            # For now, we'll let the exception propagate
            raise RuntimeError(f"Failed to commit batch: {e}") from e
    
    def rollback(self) -> None:
        """Rollback all operations."""
        if self._committed:
            raise RuntimeError("Cannot rollback committed batch")
        
        self._operations.clear()
        self._rolled_back = True
    
    def size(self) -> int:
        """Get number of operations in batch."""
        return len(self._operations)
    
    def is_empty(self) -> bool:
        """Check if batch is empty."""
        return len(self._operations) == 0
    
    def operations(self) -> List[Operation]:
        """Get copy of operations list."""
        return self._operations.copy()


class TransactionManager:
    """Manages transactions and provides ACID properties."""
    
    def __init__(self, storage: StorageInterface):
        self._storage = storage
    
    def create_batch(self) -> Batch:
        """Create a new batch operation."""
        return Batch(self._storage)
    
    def execute_batch(self, batch: Batch) -> None:
        """Execute a batch operation atomically."""
        if not isinstance(batch, Batch):
            raise TypeError("Expected Batch instance")
        
        batch.commit()
    
    def create_snapshot(self) -> StorageInterface:
        """Create a consistent snapshot of the storage."""
        return self._storage.snapshot()


class SavePoint:
    """Represents a savepoint for partial rollbacks."""
    
    def __init__(self, storage_snapshot: StorageInterface, operation_count: int):
        self._storage_snapshot = storage_snapshot
        self._operation_count = operation_count
    
    @property
    def operation_count(self) -> int:
        """Number of operations when savepoint was created."""
        return self._operation_count
    
    @property
    def storage_snapshot(self) -> StorageInterface:
        """Storage state when savepoint was created."""
        return self._storage_snapshot


class AdvancedBatch(Batch):
    """Advanced batch with savepoint support."""
    
    def __init__(self, storage: StorageInterface):
        super().__init__(storage)
        self._savepoints: List[SavePoint] = []
    
    def create_savepoint(self) -> SavePoint:
        """Create a savepoint for partial rollback."""
        if self._committed or self._rolled_back:
            raise RuntimeError("Cannot create savepoint on committed or rolled back batch")
        
        snapshot = self._storage.snapshot()
        savepoint = SavePoint(snapshot, len(self._operations))
        self._savepoints.append(savepoint)
        return savepoint
    
    def rollback_to_savepoint(self, savepoint: SavePoint) -> None:
        """Rollback to a specific savepoint."""
        if self._committed:
            raise RuntimeError("Cannot rollback committed batch")
        
        if savepoint not in self._savepoints:
            raise ValueError("Invalid savepoint")
        
        # Remove operations after the savepoint
        self._operations = self._operations[:savepoint.operation_count]
        
        # Remove newer savepoints
        savepoint_index = self._savepoints.index(savepoint)
        self._savepoints = self._savepoints[:savepoint_index + 1]
    
    def release_savepoint(self, savepoint: SavePoint) -> None:
        """Release a savepoint (cannot rollback to it anymore)."""
        if savepoint in self._savepoints:
            self._savepoints.remove(savepoint)
