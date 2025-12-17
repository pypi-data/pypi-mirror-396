"""
Memory types and message roles for agent memory system.
"""

from enum import Enum
from typing import Optional


class MemoryType(Enum):
    """Types of memory storage."""
    
    SHORT_TERM = "short_term"    # Working memory, recent context
    LONG_TERM = "long_term"       # Episodic memory, historical context
    SEMANTIC = "semantic"         # Facts, knowledge, summaries
    SYSTEM = "system"             # System-level metadata and instructions
    
    def __str__(self) -> str:
        return self.value


class MessageRole(Enum):
    """Roles for conversation messages."""
    
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"
    
    def __str__(self) -> str:
        return self.value


class Priority(Enum):
    """Priority levels for memories."""
    
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10
    
    def __int__(self) -> int:
        return self.value
