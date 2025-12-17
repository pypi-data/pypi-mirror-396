"""
Retrieval strategies for agent memory.
Different ways to retrieve and rank memories.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta

from .agent_memory import Message
from .types import MemoryType


class RetrievalStrategy(ABC):
    """Base class for memory retrieval strategies."""
    
    @abstractmethod
    def retrieve(self, messages: List[Message], limit: int) -> List[Message]:
        """
        Retrieve messages using this strategy.
        
        Args:
            messages: List of messages to filter
            limit: Maximum number of messages to return
            
        Returns:
            Filtered and ranked list of messages
        """
        pass


class RecencyStrategy(RetrievalStrategy):
    """Retrieve most recent messages."""
    
    def retrieve(self, messages: List[Message], limit: int) -> List[Message]:
        """Get most recent messages."""
        # Sort by sequence number descending (most recent = highest sequence)
        sorted_messages = sorted(messages, key=lambda m: m.sequence, reverse=True)
        return sorted_messages[:limit]


class ImportanceStrategy(RetrievalStrategy):
    """Retrieve most important messages."""
    
    def __init__(self, min_importance: float = 0.0, decay_factor: float = 0.0):
        """
        Initialize importance strategy.
        
        Args:
            min_importance: Minimum importance threshold
            decay_factor: Time decay factor (0 = no decay, higher = more decay)
        """
        self.min_importance = min_importance
        self.decay_factor = decay_factor
    
    def retrieve(self, messages: List[Message], limit: int) -> List[Message]:
        """Get most important messages with optional time decay."""
        
        if self.decay_factor > 0:
            # Apply time decay to importance
            now = datetime.utcnow()
            scored_messages = []
            
            for msg in messages:
                msg_time = datetime.fromisoformat(msg.timestamp.replace('Z', '+00:00').replace('+00:00', ''))
                age_hours = (now - msg_time).total_seconds() / 3600
                decayed_importance = msg.importance * (1.0 / (1.0 + self.decay_factor * age_hours))
                
                if decayed_importance >= self.min_importance:
                    scored_messages.append((decayed_importance, msg))
            
            # Sort by decayed importance
            scored_messages.sort(key=lambda x: x[0], reverse=True)
            return [msg for _, msg in scored_messages[:limit]]
        else:
            # Simple importance filtering and sorting
            filtered = [m for m in messages if m.importance >= self.min_importance]
            sorted_messages = sorted(filtered, key=lambda m: m.importance, reverse=True)
            return sorted_messages[:limit]


class RecentImportantStrategy(RetrievalStrategy):
    """Combine recency and importance."""
    
    def __init__(self, recency_weight: float = 0.5, importance_weight: float = 0.5):
        """
        Initialize combined strategy.
        
        Args:
            recency_weight: Weight for recency (0-1)
            importance_weight: Weight for importance (0-1)
        """
        self.recency_weight = recency_weight
        self.importance_weight = importance_weight
    
    def retrieve(self, messages: List[Message], limit: int) -> List[Message]:
        """Get messages combining recency and importance."""
        if not messages:
            return []
        
        now = datetime.utcnow()
        
        # Calculate max age for normalization
        timestamps = [datetime.fromisoformat(m.timestamp.replace('Z', '+00:00').replace('+00:00', '')) 
                     for m in messages]
        max_age = max((now - t).total_seconds() for t in timestamps) or 1
        
        # Score each message
        scored_messages = []
        for msg in messages:
            msg_time = datetime.fromisoformat(msg.timestamp.replace('Z', '+00:00').replace('+00:00', ''))
            age_seconds = (now - msg_time).total_seconds()
            
            # Normalize recency (0-1, where 1 is most recent)
            recency_score = 1.0 - (age_seconds / max_age)
            
            # Normalize importance (0-1)
            importance_score = msg.importance / 10.0
            
            # Combined score
            combined_score = (self.recency_weight * recency_score + 
                            self.importance_weight * importance_score)
            
            scored_messages.append((combined_score, msg))
        
        # Sort by combined score
        scored_messages.sort(key=lambda x: x[0], reverse=True)
        return [msg for _, msg in scored_messages[:limit]]


class MemoryTypeStrategy(RetrievalStrategy):
    """Retrieve by memory type with fallback."""
    
    def __init__(self, 
                 primary_type: MemoryType = MemoryType.SHORT_TERM,
                 fallback_types: Optional[List[MemoryType]] = None):
        """
        Initialize memory type strategy.
        
        Args:
            primary_type: Primary memory type to retrieve
            fallback_types: Fallback memory types if primary is insufficient
        """
        self.primary_type = primary_type
        self.fallback_types = fallback_types or []
    
    def retrieve(self, messages: List[Message], limit: int) -> List[Message]:
        """Get messages by type priority."""
        result = []
        
        # First, get primary type messages
        primary_messages = [m for m in messages if m.memory_type == self.primary_type]
        result.extend(sorted(primary_messages, key=lambda m: m.timestamp, reverse=True))
        
        # If we need more, try fallback types
        if len(result) < limit and self.fallback_types:
            for fallback_type in self.fallback_types:
                if len(result) >= limit:
                    break
                
                fallback_messages = [m for m in messages 
                                   if m.memory_type == fallback_type 
                                   and m not in result]
                result.extend(sorted(fallback_messages, 
                                   key=lambda m: m.timestamp, reverse=True))
        
        return result[:limit]


class ContextWindowStrategy(RetrievalStrategy):
    """Retrieve messages within a token budget."""
    
    def __init__(self, max_tokens: int = 4000, reserve_tokens: int = 500):
        """
        Initialize context window strategy.
        
        Args:
            max_tokens: Maximum token budget
            reserve_tokens: Tokens to reserve for prompt/response
        """
        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens
        self.available_tokens = max_tokens - reserve_tokens
    
    def retrieve(self, messages: List[Message], limit: int) -> List[Message]:
        """Get messages that fit within token budget."""
        # Sort by recency (most recent first)
        sorted_messages = sorted(messages, key=lambda m: m.timestamp, reverse=True)
        
        result = []
        total_tokens = 0
        
        for msg in sorted_messages:
            if len(result) >= limit:
                break
            
            if total_tokens + msg.tokens <= self.available_tokens:
                result.append(msg)
                total_tokens += msg.tokens
            else:
                # Can't fit more messages
                break
        
        # Return in chronological order (oldest first for context)
        return list(reversed(result))


class SlidingWindowStrategy(RetrievalStrategy):
    """Retrieve messages within a time window."""
    
    def __init__(self, window_hours: float = 24.0):
        """
        Initialize sliding window strategy.
        
        Args:
            window_hours: Size of time window in hours
        """
        self.window_hours = window_hours
    
    def retrieve(self, messages: List[Message], limit: int) -> List[Message]:
        """Get messages within time window."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.window_hours)
        cutoff_iso = cutoff_time.isoformat()
        
        # Filter messages within window
        windowed = [m for m in messages if m.timestamp >= cutoff_iso]
        
        # Sort by recency and limit
        sorted_messages = sorted(windowed, key=lambda m: m.timestamp, reverse=True)
        return sorted_messages[:limit]
