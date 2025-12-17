"""
Comparison functions for key ordering.
Provides default and custom comparison implementations.
"""

from typing import Optional
from ..interfaces import ComparisonFunction


class DefaultComparison:
    """Default lexicographic comparison for bytes."""
    
    def __call__(self, key1: bytes, key2: bytes) -> int:
        """Standard lexicographic comparison."""
        if key1 < key2:
            return -1
        elif key1 > key2:
            return 1
        else:
            return 0


class ReverseComparison:
    """Reverse lexicographic comparison."""
    
    def __call__(self, key1: bytes, key2: bytes) -> int:
        """Reverse lexicographic comparison."""
        if key1 > key2:
            return -1
        elif key1 < key2:
            return 1
        else:
            return 0


class NumericComparison:
    """Numeric comparison for keys that represent numbers."""
    
    def __call__(self, key1: bytes, key2: bytes) -> int:
        """Compare keys as numeric values."""
        try:
            num1 = float(key1.decode('utf-8'))
            num2 = float(key2.decode('utf-8'))
            if num1 < num2:
                return -1
            elif num1 > num2:
                return 1
            else:
                return 0
        except (ValueError, UnicodeDecodeError):
            # Fallback to lexicographic comparison
            return DefaultComparison()(key1, key2)


class ComparisonManager:
    """Manages comparison functions and provides utilities."""
    
    def __init__(self, comparison_func: Optional[ComparisonFunction] = None):
        self._comparison_func = comparison_func or DefaultComparison()
    
    def compare(self, key1: bytes, key2: bytes) -> int:
        """Compare two keys using the configured comparison function."""
        return self._comparison_func(key1, key2)
    
    def sort_key(self, key: bytes):
        """Create a sort key for Python's sorted() function."""
        from functools import cmp_to_key
        return cmp_to_key(lambda a, b: self.compare(a, b))(key)
    
    def is_less_than(self, key1: bytes, key2: bytes) -> bool:
        """Check if key1 < key2."""
        return self.compare(key1, key2) < 0
    
    def is_equal(self, key1: bytes, key2: bytes) -> bool:
        """Check if key1 == key2."""
        return self.compare(key1, key2) == 0
    
    def is_greater_than(self, key1: bytes, key2: bytes) -> bool:
        """Check if key1 > key2."""
        return self.compare(key1, key2) > 0
    
    def set_comparison_function(self, comparison_func: ComparisonFunction) -> None:
        """Set a new comparison function."""
        self._comparison_func = comparison_func
