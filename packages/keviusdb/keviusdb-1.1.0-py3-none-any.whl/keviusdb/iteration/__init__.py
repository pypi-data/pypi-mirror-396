"""
Iteration support for forward and backward traversal.
Provides efficient iterators with range support.
"""

from typing import Iterator, Tuple, Optional
from ..interfaces import StorageInterface


class KeyValueIterator:
    """Base iterator for key-value pairs."""
    
    def __init__(self, storage: StorageInterface, 
                 start_key: Optional[bytes] = None,
                 end_key: Optional[bytes] = None,
                 reverse: bool = False):
        self._storage = storage
        self._start_key = start_key
        self._end_key = end_key
        self._reverse = reverse
        self._iterator = None
        self._started = False
    
    def __iter__(self) -> Iterator[Tuple[bytes, bytes]]:
        """Return iterator."""
        if not self._started:
            self._iterator = self._storage.iterate(
                self._start_key, self._end_key, self._reverse
            )
            self._started = True
        return self
    
    def __next__(self) -> Tuple[bytes, bytes]:
        """Get next key-value pair."""
        if self._iterator is None:
            self.__iter__()
        return next(self._iterator)


class KeyIterator:
    """Iterator for keys only."""
    
    def __init__(self, storage: StorageInterface,
                 start_key: Optional[bytes] = None,
                 end_key: Optional[bytes] = None,
                 reverse: bool = False):
        self._kv_iterator = KeyValueIterator(storage, start_key, end_key, reverse)
    
    def __iter__(self) -> Iterator[bytes]:
        """Return iterator."""
        return self
    
    def __next__(self) -> bytes:
        """Get next key."""
        key, _ = next(self._kv_iterator)
        return key


class ValueIterator:
    """Iterator for values only."""
    
    def __init__(self, storage: StorageInterface,
                 start_key: Optional[bytes] = None,
                 end_key: Optional[bytes] = None,
                 reverse: bool = False):
        self._kv_iterator = KeyValueIterator(storage, start_key, end_key, reverse)
    
    def __iter__(self) -> Iterator[bytes]:
        """Return iterator."""
        return self
    
    def __next__(self) -> bytes:
        """Get next value."""
        _, value = next(self._kv_iterator)
        return value


class RangeIterator:
    """Iterator with advanced range support."""
    
    def __init__(self, storage: StorageInterface,
                 start_key: Optional[bytes] = None,
                 end_key: Optional[bytes] = None,
                 reverse: bool = False,
                 limit: Optional[int] = None,
                 skip: int = 0):
        self._storage = storage
        self._start_key = start_key
        self._end_key = end_key
        self._reverse = reverse
        self._limit = limit
        self._skip = skip
        self._count = 0
        self._skipped = 0
    
    def __iter__(self) -> Iterator[Tuple[bytes, bytes]]:
        """Return iterator."""
        iterator = self._storage.iterate(self._start_key, self._end_key, self._reverse)
        
        for key, value in iterator:
            # Handle skip
            if self._skipped < self._skip:
                self._skipped += 1
                continue
            
            # Handle limit
            if self._limit is not None and self._count >= self._limit:
                break
            
            self._count += 1
            yield key, value


class PrefixIterator:
    """Iterator for keys with a specific prefix."""
    
    def __init__(self, storage: StorageInterface, prefix: bytes, reverse: bool = False):
        self._storage = storage
        self._prefix = prefix
        self._reverse = reverse
    
    def __iter__(self) -> Iterator[Tuple[bytes, bytes]]:
        """Return iterator."""
        # Calculate start and end keys for prefix
        start_key = self._prefix
        end_key = self._get_prefix_end(self._prefix)
        
        iterator = self._storage.iterate(start_key, end_key, self._reverse)
        
        for key, value in iterator:
            if key.startswith(self._prefix):
                yield key, value
            elif not self._reverse:
                # If we've moved past the prefix in forward iteration, stop
                break
    
    def _get_prefix_end(self, prefix: bytes) -> Optional[bytes]:
        """Calculate the end key for prefix iteration."""
        if not prefix:
            return None
        
        # Increment the last byte to get the exclusive end
        prefix_list = list(prefix)
        for i in range(len(prefix_list) - 1, -1, -1):
            if prefix_list[i] < 255:
                prefix_list[i] += 1
                return bytes(prefix_list[:i + 1])
            prefix_list[i] = 0
        
        # If we can't increment (all bytes are 255), return None
        return None


class SnapshotIterator:
    """Iterator that works on a consistent snapshot."""
    
    def __init__(self, snapshot: StorageInterface,
                 start_key: Optional[bytes] = None,
                 end_key: Optional[bytes] = None,
                 reverse: bool = False):
        self._snapshot = snapshot
        self._start_key = start_key
        self._end_key = end_key
        self._reverse = reverse
    
    def __iter__(self) -> Iterator[Tuple[bytes, bytes]]:
        """Return iterator."""
        return self._snapshot.iterate(self._start_key, self._end_key, self._reverse)


class IteratorFactory:
    """Factory for creating different types of iterators."""
    
    def __init__(self, storage: StorageInterface):
        self._storage = storage
    
    def key_value_iterator(self, start_key: Optional[bytes] = None,
                          end_key: Optional[bytes] = None,
                          reverse: bool = False) -> KeyValueIterator:
        """Create key-value iterator."""
        return KeyValueIterator(self._storage, start_key, end_key, reverse)
    
    def key_iterator(self, start_key: Optional[bytes] = None,
                    end_key: Optional[bytes] = None,
                    reverse: bool = False) -> KeyIterator:
        """Create key-only iterator."""
        return KeyIterator(self._storage, start_key, end_key, reverse)
    
    def value_iterator(self, start_key: Optional[bytes] = None,
                      end_key: Optional[bytes] = None,
                      reverse: bool = False) -> ValueIterator:
        """Create value-only iterator."""
        return ValueIterator(self._storage, start_key, end_key, reverse)
    
    def range_iterator(self, start_key: Optional[bytes] = None,
                      end_key: Optional[bytes] = None,
                      reverse: bool = False,
                      limit: Optional[int] = None,
                      skip: int = 0) -> RangeIterator:
        """Create range iterator with limit and skip."""
        return RangeIterator(self._storage, start_key, end_key, reverse, limit, skip)
    
    def prefix_iterator(self, prefix: bytes, reverse: bool = False) -> PrefixIterator:
        """Create prefix iterator."""
        return PrefixIterator(self._storage, prefix, reverse)
    
    def snapshot_iterator(self, snapshot: StorageInterface,
                         start_key: Optional[bytes] = None,
                         end_key: Optional[bytes] = None,
                         reverse: bool = False) -> SnapshotIterator:
        """Create snapshot iterator."""
        return SnapshotIterator(snapshot, start_key, end_key, reverse)
