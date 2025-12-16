# core/exceptions.py
"""
Custom Exceptions - Simplified
==============================

Domain-specific exceptions for clean error handling.
"""

from typing import Dict, Any, Optional


class SecurityAnalysisError(Exception):
    """Base exception for all application errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize exception
        
        Args:
            message: Error message
            details: Optional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """String representation"""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ValidationError(SecurityAnalysisError):
    """Validation error (invalid input)"""
    pass


class ParsingError(SecurityAnalysisError):
    """Parsing error (invalid format)"""
    pass


class LLMError(SecurityAnalysisError):
    """LLM provider error"""
    
    def __init__(
        self,
        message: str,
        raw_response: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize LLM error
        
        Args:
            message: Error message
            raw_response: Optional raw LLM response
            details: Optional error details
        """
        self.raw_response = raw_response
        super().__init__(message, details)


class ChunkingError(SecurityAnalysisError):
    """Chunking process error"""
    pass


class CacheError(SecurityAnalysisError):
    """Cache operation error"""
    pass


class ConfigurationError(SecurityAnalysisError):
    """Configuration error"""
    pass
