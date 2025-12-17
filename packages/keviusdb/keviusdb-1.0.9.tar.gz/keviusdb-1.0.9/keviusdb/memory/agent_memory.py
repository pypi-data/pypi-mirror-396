"""
Core AgentMemory class for persistent agent memory.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

from ..core import KeviusDB
from .types import MemoryType, MessageRole, Priority
from .session import Session, SessionManager


@dataclass
class Message:
    """Represents a message in agent memory."""
    
    role: Union[MessageRole, str]
    content: str
    timestamp: str
    session_id: str
    memory_type: Union[MemoryType, str] = MemoryType.SHORT_TERM
    importance: float = 5.0
    tokens: int = 0
    metadata: Optional[Dict[str, Any]] = None
    message_id: Optional[str] = None
    sequence: int = 0  # Sequence number for stable sorting
    
    def __post_init__(self):
        # Convert string to enum if needed
        if isinstance(self.role, str):
            self.role = MessageRole(self.role)
        if isinstance(self.memory_type, str):
            self.memory_type = MemoryType(self.memory_type)
        
        if self.metadata is None:
            self.metadata = {}
        
        # Generate message ID if not provided
        if self.message_id is None:
            self.message_id = f"{self.session_id}:{self.timestamp}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['role'] = str(self.role)
        data['memory_type'] = str(self.memory_type)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create from dictionary."""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


class AgentMemory:
    """
    Persistent memory system for AI agents.
    
    Provides:
    - Timestamped message storage
    - Session management
    - Memory types (short-term, long-term, semantic)
    - Context window retrieval
    - Token counting
    """
    
    MESSAGE_PREFIX = "_msg:"
    
    def __init__(self, 
                 db_path: Optional[str] = None,
                 db: Optional[KeviusDB] = None,
                 default_session_id: str = "default"):
        """
        Initialize agent memory.
        
        Args:
            db_path: Path to database file (creates new KeviusDB if provided)
            db: Existing KeviusDB instance (overrides db_path)
            default_session_id: Default session ID for operations
        """
        if db is not None:
            self._db = db
        elif db_path is not None:
            self._db = KeviusDB(db_path)
        else:
            self._db = KeviusDB(in_memory=True)
        
        self._session_manager = SessionManager(self._db)
        self._default_session_id = default_session_id
        self._message_counter = 0  # Counter for ensuring unique keys
    
    def add_message(self,
                   role: Union[MessageRole, str],
                   content: str,
                   session_id: Optional[str] = None,
                   memory_type: Union[MemoryType, str] = MemoryType.SHORT_TERM,
                   importance: float = 5.0,
                   tokens: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   timestamp: Optional[str] = None) -> Message:
        """
        Add a message to memory.
        
        Args:
            role: Message role (user, assistant, system, etc.)
            content: Message content
            session_id: Session identifier (uses default if not provided)
            memory_type: Type of memory (short_term, long_term, semantic)
            importance: Importance score (0-10)
            tokens: Token count (auto-estimated if not provided)
            metadata: Additional metadata
            timestamp: Custom timestamp (auto-generated if not provided)
            
        Returns:
            Created Message instance
        """
        session_id = session_id or self._default_session_id
        timestamp = timestamp or datetime.utcnow().isoformat()
        
        # Ensure unique timestamp by adding counter if needed
        self._message_counter += 1
        unique_timestamp = f"{timestamp}:{self._message_counter:010d}"
        
        # Auto-estimate tokens if not provided
        if tokens is None:
            tokens = self._estimate_tokens(content)
        
        # Create message (use original timestamp for display, unique for storage)
        message = Message(
            role=role,
            content=content,
            timestamp=timestamp,
            session_id=session_id,
            memory_type=memory_type,
            importance=importance,
            tokens=tokens,
            metadata=metadata or {},
            sequence=self._message_counter  # Add sequence for sorting
        )
        
        # Store message with unique key
        key = self._get_message_key(session_id, unique_timestamp)
        self._db.put(key, message.to_json())
        
        # Update session
        session = self._session_manager.get_or_create_session(session_id)
        session.increment_message_count()
        session.add_tokens(tokens)
        self._session_manager.update_session(session)
        
        return message
    
    def get_message(self, session_id: str, timestamp: str) -> Optional[Message]:
        """
        Get a specific message.
        
        Args:
            session_id: Session identifier
            timestamp: Message timestamp
            
        Returns:
            Message instance or None
        """
        key = self._get_message_key(session_id, timestamp)
        data = self._db.get(key)
        
        if data is None:
            return None
        
        return Message.from_json(data)
    
    def get_recent(self,
                   session_id: Optional[str] = None,
                   limit: int = 10,
                   memory_type: Optional[MemoryType] = None,
                   role: Optional[MessageRole] = None) -> List[Message]:
        """
        Get recent messages.
        
        Args:
            session_id: Session identifier (uses default if not provided)
            limit: Maximum number of messages to return
            memory_type: Filter by memory type
            role: Filter by message role
            
        Returns:
            List of Message instances (most recent first)
        """
        session_id = session_id or self._default_session_id
        messages = []
        
        # Get all messages for this session
        prefix = self._get_message_prefix(session_id)
        
        for key, value in self._db.iterate_prefix(prefix):
            try:
                message = Message.from_json(value)
                
                # Apply filters
                if memory_type and message.memory_type != memory_type:
                    continue
                if role and message.role != role:
                    continue
                
                messages.append(message)
                    
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Return most recent messages (reverse chronological order)
        messages.reverse()
        return messages[:limit]
    
    def get_all(self,
                session_id: Optional[str] = None,
                memory_type: Optional[MemoryType] = None,
                role: Optional[MessageRole] = None,
                min_importance: Optional[float] = None) -> List[Message]:
        """
        Get all messages matching filters.
        
        Args:
            session_id: Session identifier (uses default if not provided)
            memory_type: Filter by memory type
            role: Filter by message role
            min_importance: Minimum importance score
            
        Returns:
            List of Message instances
        """
        session_id = session_id or self._default_session_id
        messages = []
        
        prefix = self._get_message_prefix(session_id)
        
        for key, value in self._db.iterate_prefix(prefix):
            try:
                message = Message.from_json(value)
                
                # Apply filters
                if memory_type and message.memory_type != memory_type:
                    continue
                if role and message.role != role:
                    continue
                if min_importance and message.importance < min_importance:
                    continue
                
                messages.append(message)
                
            except (json.JSONDecodeError, KeyError):
                continue
        
        return messages
    
    def get_range(self,
                  session_id: Optional[str] = None,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  memory_type: Optional[MemoryType] = None) -> List[Message]:
        """
        Get messages within a time range.
        
        Args:
            session_id: Session identifier (uses default if not provided)
            start_time: Start of time range
            end_time: End of time range
            memory_type: Filter by memory type
            
        Returns:
            List of Message instances
        """
        session_id = session_id or self._default_session_id
        messages = []
        
        # Convert datetime to ISO format for comparison
        start_iso = start_time.isoformat() if start_time else None
        end_iso = end_time.isoformat() if end_time else None
        
        prefix = self._get_message_prefix(session_id)
        
        for key, value in self._db.iterate_prefix(prefix):
            try:
                message = Message.from_json(value)
                
                # Apply time range filter
                if start_iso and message.timestamp < start_iso:
                    continue
                if end_iso and message.timestamp > end_iso:
                    continue
                
                # Apply memory type filter
                if memory_type and message.memory_type != memory_type:
                    continue
                
                messages.append(message)
                
            except (json.JSONDecodeError, KeyError):
                continue
        
        return messages
    
    def delete_message(self, session_id: str, timestamp: str) -> bool:
        """
        Delete a specific message.
        
        Args:
            session_id: Session identifier
            timestamp: Message timestamp
            
        Returns:
            True if message existed and was deleted
        """
        key = self._get_message_key(session_id, timestamp)
        return self._db.delete(key)
    
    def clear_session(self, session_id: Optional[str] = None) -> int:
        """
        Clear all messages in a session.
        
        Args:
            session_id: Session identifier (uses default if not provided)
            
        Returns:
            Number of messages deleted
        """
        session_id = session_id or self._default_session_id
        count = 0
        
        prefix = self._get_message_prefix(session_id)
        
        # Collect keys to delete
        keys_to_delete = []
        for key, _ in self._db.iterate_prefix(prefix):
            keys_to_delete.append(key)
        
        # Delete messages
        for key in keys_to_delete:
            if self._db.delete(key):
                count += 1
        
        # Reset session metadata
        session = self._session_manager.get_session(session_id)
        if session:
            session.update(message_count=0, total_tokens=0)
            self._session_manager.update_session(session)
        
        return count
    
    def count_messages(self, session_id: Optional[str] = None) -> int:
        """
        Count messages in a session.
        
        Args:
            session_id: Session identifier (uses default if not provided)
            
        Returns:
            Number of messages
        """
        session_id = session_id or self._default_session_id
        count = 0
        
        prefix = self._get_message_prefix(session_id)
        for _ in self._db.iterate_prefix(prefix):
            count += 1
        
        return count
    
    def get_session(self, session_id: Optional[str] = None) -> Optional[Session]:
        """
        Get session metadata.
        
        Args:
            session_id: Session identifier (uses default if not provided)
            
        Returns:
            Session instance or None
        """
        session_id = session_id or self._default_session_id
        return self._session_manager.get_session(session_id)
    
    def list_sessions(self) -> List[Session]:
        """
        List all sessions.
        
        Returns:
            List of Session instances
        """
        return self._session_manager.list_sessions()
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its messages.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session existed and was deleted
        """
        # Delete all messages
        self.clear_session(session_id)
        
        # Delete session metadata
        return self._session_manager.delete_session(session_id)
    
    def close(self):
        """Close the underlying database."""
        self._db.close()
    
    def flush(self):
        """Flush changes to disk."""
        self._db.flush()
    
    def _get_message_key(self, session_id: str, timestamp: str) -> str:
        """Generate database key for a message."""
        return f"{self.MESSAGE_PREFIX}{session_id}:{timestamp}"
    
    def _get_message_prefix(self, session_id: str) -> str:
        """Generate prefix for session messages."""
        return f"{self.MESSAGE_PREFIX}{session_id}:"
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        Simple approximation: ~4 characters per token.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Simple heuristic: 4 characters ≈ 1 token
        return max(1, len(text) // 4)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
