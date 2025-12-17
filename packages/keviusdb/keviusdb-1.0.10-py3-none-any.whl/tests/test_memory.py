"""
Comprehensive tests for AgentMemory functionality.
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keviusdb.memory import (
    AgentMemory,
    Message,
    MemoryType,
    MessageRole,
    Session,
    RecencyStrategy,
    ImportanceStrategy,
    ContextWindowStrategy,
    TokenCounter,
    ContextWindowManager
)


class TestAgentMemory(unittest.TestCase):
    """Test core AgentMemory functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.memory = AgentMemory()
    
    def tearDown(self):
        """Clean up after tests."""
        self.memory.close()
    
    def test_add_message(self):
        """Test adding messages to memory."""
        msg = self.memory.add_message(
            role=MessageRole.USER,
            content="Hello, world!",
            session_id="test_session"
        )
        
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.role, MessageRole.USER)
        self.assertEqual(msg.content, "Hello, world!")
        self.assertEqual(msg.session_id, "test_session")
        self.assertGreater(msg.tokens, 0)
    
    def test_add_message_with_metadata(self):
        """Test adding messages with custom metadata."""
        msg = self.memory.add_message(
            role="assistant",
            content="I'm here to help!",
            metadata={"model": "gpt-4", "temperature": 0.7}
        )
        
        self.assertEqual(msg.metadata["model"], "gpt-4")
        self.assertEqual(msg.metadata["temperature"], 0.7)
    
    def test_get_recent_messages(self):
        """Test retrieving recent messages."""
        # Add multiple messages
        for i in range(10):
            self.memory.add_message(
                role=MessageRole.USER,
                content=f"Message {i}"
            )
        
        # Get recent 5 messages
        recent = self.memory.get_recent(limit=5)
        
        self.assertEqual(len(recent), 5)
        # Should be in reverse chronological order (most recent first)
        self.assertEqual(recent[0].content, "Message 9")
    
    def test_memory_types(self):
        """Test different memory types."""
        # Add messages of different types
        self.memory.add_message(
            role=MessageRole.USER,
            content="Short term",
            memory_type=MemoryType.SHORT_TERM
        )
        
        self.memory.add_message(
            role=MessageRole.ASSISTANT,
            content="Long term",
            memory_type=MemoryType.LONG_TERM
        )
        
        self.memory.add_message(
            role=MessageRole.SYSTEM,
            content="Semantic fact",
            memory_type=MemoryType.SEMANTIC
        )
        
        # Filter by memory type
        short_term = self.memory.get_all(memory_type=MemoryType.SHORT_TERM)
        long_term = self.memory.get_all(memory_type=MemoryType.LONG_TERM)
        semantic = self.memory.get_all(memory_type=MemoryType.SEMANTIC)
        
        self.assertEqual(len(short_term), 1)
        self.assertEqual(len(long_term), 1)
        self.assertEqual(len(semantic), 1)
        self.assertEqual(short_term[0].content, "Short term")
    
    def test_importance_filtering(self):
        """Test filtering by importance."""
        # Add messages with different importance
        self.memory.add_message(
            role=MessageRole.USER,
            content="Low importance",
            importance=2.0
        )
        
        self.memory.add_message(
            role=MessageRole.USER,
            content="High importance",
            importance=9.0
        )
        
        # Get important messages
        important = self.memory.get_all(min_importance=7.0)
        
        self.assertEqual(len(important), 1)
        self.assertEqual(important[0].content, "High importance")
    
    def test_role_filtering(self):
        """Test filtering by message role."""
        self.memory.add_message(role=MessageRole.USER, content="User message")
        self.memory.add_message(role=MessageRole.ASSISTANT, content="Assistant message")
        self.memory.add_message(role=MessageRole.SYSTEM, content="System message")
        
        user_msgs = self.memory.get_all(role=MessageRole.USER)
        assistant_msgs = self.memory.get_all(role=MessageRole.ASSISTANT)
        
        self.assertEqual(len(user_msgs), 1)
        self.assertEqual(len(assistant_msgs), 1)
        self.assertEqual(user_msgs[0].content, "User message")
    
    def test_count_messages(self):
        """Test counting messages."""
        self.assertEqual(self.memory.count_messages(), 0)
        
        for i in range(5):
            self.memory.add_message(role=MessageRole.USER, content=f"Message {i}")
        
        self.assertEqual(self.memory.count_messages(), 5)
    
    def test_clear_session(self):
        """Test clearing a session."""
        # Add messages
        for i in range(5):
            self.memory.add_message(role=MessageRole.USER, content=f"Message {i}")
        
        self.assertEqual(self.memory.count_messages(), 5)
        
        # Clear session
        deleted = self.memory.clear_session()
        
        self.assertEqual(deleted, 5)
        self.assertEqual(self.memory.count_messages(), 0)
    
    def test_session_isolation(self):
        """Test that sessions are isolated."""
        # Add messages to different sessions
        self.memory.add_message(
            role=MessageRole.USER,
            content="Session 1 message",
            session_id="session1"
        )
        
        self.memory.add_message(
            role=MessageRole.USER,
            content="Session 2 message",
            session_id="session2"
        )
        
        # Get messages for each session
        session1_msgs = self.memory.get_all(session_id="session1")
        session2_msgs = self.memory.get_all(session_id="session2")
        
        self.assertEqual(len(session1_msgs), 1)
        self.assertEqual(len(session2_msgs), 1)
        self.assertEqual(session1_msgs[0].content, "Session 1 message")
        self.assertEqual(session2_msgs[0].content, "Session 2 message")


class TestSessionManagement(unittest.TestCase):
    """Test session management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.memory = AgentMemory()
    
    def tearDown(self):
        """Clean up after tests."""
        self.memory.close()
    
    def test_session_creation(self):
        """Test creating sessions."""
        session = self.memory.get_session("test_session")
        self.assertIsNone(session)
        
        # Add a message to create session
        self.memory.add_message(
            role=MessageRole.USER,
            content="Test",
            session_id="test_session"
        )
        
        session = self.memory.get_session("test_session")
        self.assertIsNotNone(session)
        self.assertEqual(session.session_id, "test_session")
        self.assertEqual(session.metadata.message_count, 1)
    
    def test_session_metadata_updates(self):
        """Test that session metadata updates correctly."""
        # Add messages
        for i in range(3):
            self.memory.add_message(
                role=MessageRole.USER,
                content=f"Message {i}",
                session_id="test_session"
            )
        
        session = self.memory.get_session("test_session")
        self.assertEqual(session.metadata.message_count, 3)
        self.assertGreater(session.metadata.total_tokens, 0)
    
    def test_list_sessions(self):
        """Test listing all sessions."""
        # Create multiple sessions
        self.memory.add_message(role=MessageRole.USER, content="Test", session_id="session1")
        self.memory.add_message(role=MessageRole.USER, content="Test", session_id="session2")
        self.memory.add_message(role=MessageRole.USER, content="Test", session_id="session3")
        
        sessions = self.memory.list_sessions()
        self.assertEqual(len(sessions), 3)
        
        session_ids = [s.session_id for s in sessions]
        self.assertIn("session1", session_ids)
        self.assertIn("session2", session_ids)
        self.assertIn("session3", session_ids)
    
    def test_delete_session(self):
        """Test deleting a session."""
        # Create session with messages
        for i in range(5):
            self.memory.add_message(
                role=MessageRole.USER,
                content=f"Message {i}",
                session_id="temp_session"
            )
        
        # Verify it exists
        self.assertEqual(self.memory.count_messages("temp_session"), 5)
        self.assertIsNotNone(self.memory.get_session("temp_session"))
        
        # Delete session
        self.memory.delete_session("temp_session")
        
        # Verify it's gone
        self.assertEqual(self.memory.count_messages("temp_session"), 0)
        self.assertIsNone(self.memory.get_session("temp_session"))


class TestTokenCounting(unittest.TestCase):
    """Test token counting utilities."""
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        text = "Hello, world!"
        tokens = TokenCounter.estimate_tokens(text)
        
        self.assertGreater(tokens, 0)
        self.assertLess(tokens, len(text))  # Should be less than character count
    
    def test_different_models(self):
        """Test token estimation for different models."""
        text = "This is a test message for token counting."
        
        gpt4_tokens = TokenCounter.estimate_tokens(text, model='gpt-4')
        claude_tokens = TokenCounter.estimate_tokens(text, model='claude')
        
        # Both should give reasonable estimates
        self.assertGreater(gpt4_tokens, 0)
        self.assertGreater(claude_tokens, 0)
    
    def test_conversation_token_count(self):
        """Test counting tokens in a conversation."""
        messages = [
            {'role': 'user', 'content': 'Hello!'},
            {'role': 'assistant', 'content': 'Hi there! How can I help?'},
            {'role': 'user', 'content': 'What is the weather?'}
        ]
        
        total_tokens = TokenCounter.count_conversation_tokens(messages)
        self.assertGreater(total_tokens, 0)
    
    def test_context_window_manager(self):
        """Test context window management."""
        manager = ContextWindowManager(max_tokens=100, reserve_tokens=20)
        
        self.assertEqual(manager.get_available_tokens(), 80)
        
        # Create messages that fit
        messages = [
            {'role': 'user', 'content': 'Short message'}
        ]
        
        self.assertTrue(manager.can_fit(messages))
        
        # Create messages that don't fit
        large_messages = [
            {'role': 'user', 'content': 'x' * 1000}
        ]
        
        self.assertFalse(manager.can_fit(large_messages))
    
    def test_truncate_to_fit(self):
        """Test truncating messages to fit context."""
        messages = [
            {'role': 'system', 'content': 'System prompt'},
            {'role': 'user', 'content': 'Message 1 with some content that takes up tokens'},
            {'role': 'assistant', 'content': 'Response 1 with detailed explanation that uses many tokens'},
            {'role': 'user', 'content': 'Message 2 with more content to increase token count'},
            {'role': 'assistant', 'content': 'Response 2 with another detailed explanation using tokens'},
            {'role': 'user', 'content': 'Message 3 with additional content for token budget'}
        ]
        
        truncated = TokenCounter.truncate_to_fit(
            messages,
            max_tokens=50,
            reserve_tokens=10,
            keep_system=True
        )
        
        # System message should be kept
        self.assertEqual(truncated[0]['role'], 'system')
        
        # Should have fewer messages
        self.assertLess(len(truncated), len(messages))


class TestRetrievalStrategies(unittest.TestCase):
    """Test memory retrieval strategies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.memory = AgentMemory()
        
        # Add test messages with varying properties
        for i in range(10):
            self.memory.add_message(
                role=MessageRole.USER,
                content=f"Message {i}",
                importance=float(i),
                memory_type=MemoryType.SHORT_TERM if i < 5 else MemoryType.LONG_TERM
            )
    
    def tearDown(self):
        """Clean up after tests."""
        self.memory.close()
    
    def test_recency_strategy(self):
        """Test recency-based retrieval."""
        messages = self.memory.get_all()
        strategy = RecencyStrategy()
        
        recent = strategy.retrieve(messages, limit=3)
        
        self.assertEqual(len(recent), 3)
        # Most recent should be Message 9
        self.assertEqual(recent[0].content, "Message 9")
    
    def test_importance_strategy(self):
        """Test importance-based retrieval."""
        messages = self.memory.get_all()
        strategy = ImportanceStrategy(min_importance=7.0)
        
        important = strategy.retrieve(messages, limit=5)
        
        # Should only get messages with importance >= 7
        self.assertLessEqual(len(important), 3)
        for msg in important:
            self.assertGreaterEqual(msg.importance, 7.0)
    
    def test_context_window_strategy(self):
        """Test context window retrieval."""
        messages = self.memory.get_all()
        strategy = ContextWindowStrategy(max_tokens=50, reserve_tokens=10)
        
        windowed = strategy.retrieve(messages, limit=10)
        
        # Should fit within token budget
        total_tokens = sum(msg.tokens for msg in windowed)
        self.assertLessEqual(total_tokens, 40)  # max_tokens - reserve_tokens


class TestPersistence(unittest.TestCase):
    """Test persistence functionality."""
    
    def test_persistent_storage(self):
        """Test that memory persists across instances."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        try:
            # Create memory and add messages
            memory1 = AgentMemory(db_path=db_path)
            memory1.add_message(role=MessageRole.USER, content="Persistent message")
            memory1.flush()
            memory1.close()
            
            # Open new memory instance
            memory2 = AgentMemory(db_path=db_path)
            messages = memory2.get_all()
            
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0].content, "Persistent message")
            
            memory2.close()
        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.remove(db_path)


def main():
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestAgentMemory,
        TestSessionManagement,
        TestTokenCounting,
        TestRetrievalStrategies,
        TestPersistence
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
