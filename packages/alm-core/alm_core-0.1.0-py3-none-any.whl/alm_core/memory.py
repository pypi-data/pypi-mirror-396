"""
Data Airlock and Dual-Store Memory System
Implements PII sanitization and memory management.
"""

import re
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime


class DataAirlock:
    """
    The Data Airlock sanitizes sensitive information before LLM inference
    and rehydrates it afterwards.
    
    This is a core novelty of ALM: The LLM provider never sees raw PII.
    """
    
    def __init__(self, custom_patterns: Dict[str, str] = None):
        """
        Initialize with PII detection patterns.
        
        Args:
            custom_patterns: Additional regex patterns for PII detection
        """
        self._secure_store: Dict[str, str] = {}
        
        # Default PII patterns
        self.pii_patterns = {
            "email": r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b",
            "phone": r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        }
        
        # Add custom patterns
        if custom_patterns:
            self.pii_patterns.update(custom_patterns)
    
    def sanitize(self, text: str) -> str:
        """
        Replaces sensitive data with tokens (e.g., <EMAIL_abc123>) before LLM inference.
        
        Args:
            text: Raw text containing potential PII
            
        Returns:
            Sanitized text with PII replaced by tokens
        """
        sanitized_text = text
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                # Handle tuple matches (from groups in regex)
                if isinstance(match, tuple):
                    match = ''.join(match)
                
                # Create unique token
                token = f"<{pii_type.upper()}_{uuid.uuid4().hex[:8]}>"
                
                # Store mapping for later rehydration
                self._secure_store[token] = match
                
                # Replace in text
                sanitized_text = sanitized_text.replace(match, token)
        
        return sanitized_text
    
    def rehydrate(self, text: str) -> str:
        """
        Restores sensitive data from tokens after LLM inference.
        
        Args:
            text: Text containing tokens
            
        Returns:
            Text with tokens replaced by original values
        """
        rehydrated_text = text
        
        for token, original_value in self._secure_store.items():
            if token in rehydrated_text:
                rehydrated_text = rehydrated_text.replace(token, original_value)
        
        return rehydrated_text
    
    def clear_store(self):
        """Clear the secure store (for privacy)."""
        self._secure_store.clear()
    
    def get_token_count(self) -> int:
        """Get number of PII items currently stored."""
        return len(self._secure_store)


class DualMemory:
    """
    Implements the dual-store memory system:
    - Working Memory: Episodic (current session)
    - Long-term Memory: Semantic (persistent knowledge)
    
    All data served to the LLM is sanitized via the Data Airlock.
    """
    
    def __init__(self, airlock: Optional[DataAirlock] = None):
        """
        Initialize dual memory system.
        
        Args:
            airlock: DataAirlock instance for PII protection
        """
        self.working_memory: List[Dict[str, Any]] = []  # Episodic (Session)
        self.long_term_memory: Dict[str, Any] = {}  # Semantic (Database)
        self.airlock = airlock or DataAirlock()
        self.max_working_memory_size = 50  # Prevent context overflow
    
    def add_episode(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """
        Add an entry to working memory (episodic).
        
        Args:
            role: Speaker role (e.g., 'user', 'assistant', 'system')
            content: Message content
            metadata: Additional metadata (timestamp, etc.)
        """
        episode = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.working_memory.append(episode)
        
        # Implement sliding window to prevent memory overflow
        if len(self.working_memory) > self.max_working_memory_size:
            # Keep first message (often system prompt) and recent messages
            self.working_memory = [self.working_memory[0]] + self.working_memory[-self.max_working_memory_size+1:]
    
    def get_context_window(self, sanitize: bool = True) -> List[Dict[str, str]]:
        """
        Returns context for the LLM.
        
        Args:
            sanitize: Whether to sanitize PII (default True)
            
        Returns:
            List of message dictionaries suitable for LLM input
        """
        if not sanitize:
            # Return raw content (for internal use only)
            return [{"role": msg["role"], "content": msg["content"]} 
                    for msg in self.working_memory]
        
        # CRITICAL: Sanitize before sending to LLM
        sanitized_context = []
        for msg in self.working_memory:
            sanitized_msg = {
                "role": msg["role"],
                "content": self.airlock.sanitize(msg["content"])
            }
            sanitized_context.append(sanitized_msg)
        
        return sanitized_context
    
    def add_to_long_term(self, key: str, value: Any):
        """
        Store information in long-term memory (semantic).
        
        Args:
            key: Identifier for the information
            value: The information to store
        """
        self.long_term_memory[key] = {
            "value": value,
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }
    
    def recall_from_long_term(self, key: str) -> Optional[Any]:
        """
        Retrieve information from long-term memory.
        
        Args:
            key: Identifier to retrieve
            
        Returns:
            Stored value or None if not found
        """
        if key in self.long_term_memory:
            self.long_term_memory[key]["access_count"] += 1
            return self.long_term_memory[key]["value"]
        return None
    
    def clear_working_memory(self):
        """Clear episodic memory (new session)."""
        self.working_memory.clear()
        self.airlock.clear_store()
    
    def export_session(self) -> Dict[str, Any]:
        """
        Export current session for persistence.
        
        Returns:
            Dictionary containing working memory and metadata
        """
        return {
            "working_memory": self.working_memory,
            "session_start": self.working_memory[0]["timestamp"] if self.working_memory else None,
            "session_end": datetime.now().isoformat(),
            "message_count": len(self.working_memory)
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage."""
        return {
            "working_memory_size": len(self.working_memory),
            "long_term_memory_size": len(self.long_term_memory),
            "pii_tokens_stored": self.airlock.get_token_count(),
            "memory_usage_percent": (len(self.working_memory) / self.max_working_memory_size) * 100
        }
