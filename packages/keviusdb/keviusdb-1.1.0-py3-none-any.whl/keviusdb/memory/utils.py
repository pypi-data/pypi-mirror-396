"""
Token counting utilities for agent memory.
Provides token estimation and counting for different models.
"""

from typing import Optional
import re


class TokenCounter:
    """Utility for counting and estimating tokens."""
    
    # Average characters per token for different models
    CHARS_PER_TOKEN = {
        'gpt-4': 4.0,
        'gpt-3.5-turbo': 4.0,
        'claude': 4.5,
        'llama': 4.0,
        'default': 4.0
    }
    
    @staticmethod
    def estimate_tokens(text: str, model: str = 'default') -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to estimate
            model: Model name for model-specific estimation
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        chars_per_token = TokenCounter.CHARS_PER_TOKEN.get(
            model, 
            TokenCounter.CHARS_PER_TOKEN['default']
        )
        
        # Basic estimation: characters / chars_per_token
        char_count = len(text)
        base_estimate = max(1, int(char_count / chars_per_token))
        
        # Adjust for spaces and punctuation (typically counted as tokens)
        word_count = len(text.split())
        punctuation_count = len(re.findall(r'[.,!?;:\-\(\)\[\]{}]', text))
        
        # Refined estimate
        adjusted_estimate = max(base_estimate, word_count, punctuation_count)
        
        return adjusted_estimate
    
    @staticmethod
    def count_conversation_tokens(messages: list, model: str = 'default') -> int:
        """
        Count total tokens in a conversation.
        
        Args:
            messages: List of message dictionaries with 'content' key
            model: Model name for estimation
            
        Returns:
            Total token count
        """
        total = 0
        
        for msg in messages:
            # Add tokens for content
            content = msg.get('content', '')
            total += TokenCounter.estimate_tokens(content, model)
            
            # Add overhead tokens (role, structure, etc.)
            total += 4  # Approximate overhead per message
        
        return total
    
    @staticmethod
    def fits_in_context(messages: list, 
                       max_tokens: int = 4000,
                       reserve_tokens: int = 500,
                       model: str = 'default') -> bool:
        """
        Check if messages fit in context window.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum context window size
            reserve_tokens: Tokens to reserve for response
            model: Model name
            
        Returns:
            True if messages fit in available context
        """
        total_tokens = TokenCounter.count_conversation_tokens(messages, model)
        available_tokens = max_tokens - reserve_tokens
        return total_tokens <= available_tokens
    
    @staticmethod
    def truncate_to_fit(messages: list,
                       max_tokens: int = 4000,
                       reserve_tokens: int = 500,
                       model: str = 'default',
                       keep_system: bool = True) -> list:
        """
        Truncate messages to fit in context window.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum context window size
            reserve_tokens: Tokens to reserve for response
            model: Model name
            keep_system: Keep system messages even when truncating
            
        Returns:
            Truncated list of messages
        """
        available_tokens = max_tokens - reserve_tokens
        
        # Separate system messages if needed
        system_messages = []
        other_messages = []
        
        if keep_system:
            for msg in messages:
                if msg.get('role') == 'system':
                    system_messages.append(msg)
                else:
                    other_messages.append(msg)
        else:
            other_messages = messages
        
        # Calculate system message tokens
        system_tokens = TokenCounter.count_conversation_tokens(system_messages, model)
        available_for_others = available_tokens - system_tokens
        
        # Add messages from most recent until we run out of tokens
        result = []
        current_tokens = 0
        
        # Process in reverse to keep most recent
        for msg in reversed(other_messages):
            msg_tokens = TokenCounter.estimate_tokens(msg.get('content', ''), model) + 4
            
            if current_tokens + msg_tokens <= available_for_others:
                result.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        # Combine system messages + truncated messages
        return system_messages + result


class ContextWindowManager:
    """Manages context window for conversations."""
    
    def __init__(self, 
                 max_tokens: int = 4000,
                 reserve_tokens: int = 500,
                 model: str = 'default'):
        """
        Initialize context window manager.
        
        Args:
            max_tokens: Maximum context window size
            reserve_tokens: Tokens to reserve for response
            model: Model name for token counting
        """
        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens
        self.model = model
        self.available_tokens = max_tokens - reserve_tokens
    
    def get_available_tokens(self) -> int:
        """Get number of available tokens for messages."""
        return self.available_tokens
    
    def estimate_message_tokens(self, content: str) -> int:
        """Estimate tokens for a message."""
        return TokenCounter.estimate_tokens(content, self.model) + 4
    
    def can_fit(self, messages: list) -> bool:
        """Check if messages fit in context."""
        return TokenCounter.fits_in_context(
            messages,
            self.max_tokens,
            self.reserve_tokens,
            self.model
        )
    
    def truncate(self, messages: list, keep_system: bool = True) -> list:
        """Truncate messages to fit in context."""
        return TokenCounter.truncate_to_fit(
            messages,
            self.max_tokens,
            self.reserve_tokens,
            self.model,
            keep_system
        )
    
    def get_usage_stats(self, messages: list) -> dict:
        """
        Get context window usage statistics.
        
        Args:
            messages: List of messages
            
        Returns:
            Dictionary with usage statistics
        """
        total_tokens = TokenCounter.count_conversation_tokens(messages, self.model)
        
        return {
            'total_tokens': total_tokens,
            'max_tokens': self.max_tokens,
            'reserve_tokens': self.reserve_tokens,
            'available_tokens': self.available_tokens,
            'used_tokens': total_tokens,
            'remaining_tokens': max(0, self.available_tokens - total_tokens),
            'utilization_percent': (total_tokens / self.available_tokens * 100) if self.available_tokens > 0 else 0,
            'fits_in_context': total_tokens <= self.available_tokens
        }
