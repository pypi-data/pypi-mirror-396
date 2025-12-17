"""
Session management for agent memory.
Provides isolation and organization of conversation sessions.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class SessionMetadata:
    """Metadata for a conversation session."""
    
    session_id: str
    created_at: str
    updated_at: str
    message_count: int = 0
    total_tokens: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionMetadata':
        """Create from dictionary."""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SessionMetadata':
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


class Session:
    """Represents a conversation session."""
    
    def __init__(self, session_id: str, metadata: Optional[SessionMetadata] = None):
        self.session_id = session_id
        
        if metadata is None:
            now = datetime.utcnow().isoformat()
            self.metadata = SessionMetadata(
                session_id=session_id,
                created_at=now,
                updated_at=now
            )
        else:
            self.metadata = metadata
    
    def update(self, message_count: Optional[int] = None, 
               total_tokens: Optional[int] = None,
               custom_metadata: Optional[Dict[str, Any]] = None):
        """Update session metadata."""
        self.metadata.updated_at = datetime.utcnow().isoformat()
        
        if message_count is not None:
            self.metadata.message_count = message_count
        
        if total_tokens is not None:
            self.metadata.total_tokens = total_tokens
        
        if custom_metadata:
            self.metadata.metadata.update(custom_metadata)
    
    def increment_message_count(self, count: int = 1):
        """Increment the message count."""
        self.metadata.message_count += count
        self.metadata.updated_at = datetime.utcnow().isoformat()
    
    def add_tokens(self, tokens: int):
        """Add to the total token count."""
        self.metadata.total_tokens += tokens
        self.metadata.updated_at = datetime.utcnow().isoformat()
    
    def to_json(self) -> str:
        """Serialize session to JSON."""
        return self.metadata.to_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Session':
        """Deserialize session from JSON."""
        metadata = SessionMetadata.from_json(json_str)
        return cls(metadata.session_id, metadata)


class SessionManager:
    """Manages multiple conversation sessions."""
    
    SESSION_PREFIX = "_session_meta:"
    
    def __init__(self, db):
        """
        Initialize session manager.
        
        Args:
            db: KeviusDB instance for storage
        """
        self._db = db
    
    def create_session(self, session_id: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> Session:
        """
        Create a new session.
        
        Args:
            session_id: Unique session identifier
            metadata: Optional custom metadata
            
        Returns:
            Session instance
        """
        session = Session(session_id)
        
        if metadata:
            session.metadata.metadata = metadata
        
        self._save_session(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session instance or None if not found
        """
        key = self._get_session_key(session_id)
        data = self._db.get(key)
        
        if data is None:
            return None
        
        return Session.from_json(data)
    
    def get_or_create_session(self, session_id: str,
                             metadata: Optional[Dict[str, Any]] = None) -> Session:
        """
        Get existing session or create new one.
        
        Args:
            session_id: Session identifier
            metadata: Optional custom metadata for new sessions
            
        Returns:
            Session instance
        """
        session = self.get_session(session_id)
        if session is None:
            session = self.create_session(session_id, metadata)
        return session
    
    def update_session(self, session: Session):
        """
        Update session metadata.
        
        Args:
            session: Session to update
        """
        session.metadata.updated_at = datetime.utcnow().isoformat()
        self._save_session(session)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session existed and was deleted
        """
        key = self._get_session_key(session_id)
        return self._db.delete(key)
    
    def list_sessions(self) -> List[Session]:
        """
        List all sessions.
        
        Returns:
            List of Session instances
        """
        sessions = []
        
        # Iterate over session metadata entries
        for key, value in self._db.iterate_prefix(self.SESSION_PREFIX):
            try:
                session = Session.from_json(value)
                sessions.append(session)
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Sort by updated_at (most recent first)
        sessions.sort(key=lambda s: s.metadata.updated_at, reverse=True)
        return sessions
    
    def count_sessions(self) -> int:
        """
        Count total number of sessions.
        
        Returns:
            Number of sessions
        """
        count = 0
        for _ in self._db.iterate_prefix(self.SESSION_PREFIX):
            count += 1
        return count
    
    def _save_session(self, session: Session):
        """Save session to database."""
        key = self._get_session_key(session.session_id)
        self._db.put(key, session.to_json())
    
    def _get_session_key(self, session_id: str) -> str:
        """Generate database key for session."""
        return f"{self.SESSION_PREFIX}{session_id}"
