#!/usr/bin/env python3
"""
Enhanced Error Handling and Recovery (v0.2.2)
Context-aware error messages, intelligent suggestions, and detailed recovery paths
"""

import time
import re
from typing import Optional, TypeVar, Callable, Dict, List, Tuple
from functools import wraps
from enum import Enum
from dataclasses import dataclass

from lmapp.utils.logging import logger
from lmapp.backend.base import LLMBackend

T = TypeVar("T")


# Error Categories for better routing
class ErrorCategory(Enum):
    """Error classification for better handling"""
    CONNECTIVITY = "connectivity"      # Network/connection issues
    MODEL = "model"                      # Model-related issues
    PERFORMANCE = "performance"          # Timeout/speed issues
    RESOURCE = "resource"                # Memory/GPU issues
    AUTHENTICATION = "authentication"    # Auth/permission issues
    CONFIGURATION = "configuration"      # Config/setup issues
    UNKNOWN = "unknown"                  # Unknown errors


class RetryStrategy(Enum):
    """Retry strategy options"""
    EXPONENTIAL = "exponential"  # 1s, 2s, 4s, 8s
    LINEAR = "linear"            # 1s, 2s, 3s, 4s
    IMMEDIATE = "immediate"      # No delay
    ADAPTIVE = "adaptive"         # Adjust based on error type


class BackendError(Exception):
    """Base exception for backend errors"""
    pass


class ConnectionError(BackendError):
    """Connection to backend failed"""
    pass


class ModelNotFoundError(BackendError):
    """Model not found on backend"""
    pass


class TimeoutError(BackendError):
    """Request timeout"""
    pass


class ResourceError(BackendError):
    """Resource exhaustion (memory, GPU, etc.)"""
    pass


class ConfigurationError(BackendError):
    """Configuration error"""
    pass


@dataclass
class ErrorContext:
    """Context information about an error for better handling"""
    operation: str              # What was being attempted
    backend_name: str          # Which backend
    model_name: str            # Which model
    attempt_number: int = 1    # Which attempt
    is_first_attempt: bool = True
    previous_error: Optional[str] = None
    user_environment: Dict = None  # System info
    
    def to_dict(self) -> Dict:
        return {
            "operation": self.operation,
            "backend": self.backend_name,
            "model": self.model_name,
            "attempt": self.attempt_number,
            "first_attempt": self.is_first_attempt,
            "previous_error": self.previous_error,
        }


class ErrorAnalyzer:
    """Analyze errors and categorize them"""
    
    # Pattern matching for error types
    CONNECTIVITY_PATTERNS = [
        r"connection",
        r"refused",
        r"timeout",
        r"network.*unreachable|unreachable.*network",
        r"no.*route|route.*host",
        r"cannot.*connect|connect.*failed",
        r"dns.*error|name.*resolve",
        r"error.*open|open.*error",
    ]
    
    MODEL_PATTERNS = [
        r"model.*not.*found|not.*found.*model",
        r"unknown.*model|model.*unknown",
        r"model.*does.*not.*exist|exist.*model",
        r"cannot.*load.*model|load.*model",
    ]
    
    RESOURCE_PATTERNS = [
        r"out.*of.*memory|memory.*error|memory.*exhausted",
        r"cuda.*error|gpu.*error",
        r"device.*error|device.*out",
        r"malloc.*error|insufficient.*memory",
        r"no.*space.*left|disk.*full",
    ]
    
    TIMEOUT_PATTERNS = [
        r"timeout|timed.*out",
        r"deadline.*exceeded",
        r"request.*timeout|timeout.*request",
    ]
    
    @classmethod
    def categorize_error(cls, error: Exception) -> ErrorCategory:
        """Categorize an error based on its message"""
        error_msg = str(error).lower()
        
        # Check each pattern type
        for pattern in cls.CONNECTIVITY_PATTERNS:
            if re.search(pattern, error_msg):
                return ErrorCategory.CONNECTIVITY
        
        for pattern in cls.MODEL_PATTERNS:
            if re.search(pattern, error_msg):
                return ErrorCategory.MODEL
        
        for pattern in cls.RESOURCE_PATTERNS:
            if re.search(pattern, error_msg):
                return ErrorCategory.RESOURCE
        
        for pattern in cls.TIMEOUT_PATTERNS:
            if re.search(pattern, error_msg):
                return ErrorCategory.PERFORMANCE
        
        # Check simple keywords
        if any(word in error_msg for word in ["auth", "permission", "unauthorized", "forbidden"]):
            return ErrorCategory.AUTHENTICATION
        
        if any(word in error_msg for word in ["config", "setting", "parameter", "invalid"]):
            return ErrorCategory.CONFIGURATION
        
        return ErrorCategory.UNKNOWN

    @classmethod
    def get_error_suggestion(cls, error: Exception, context: Optional[ErrorContext] = None) -> str:
        """Get context-aware error suggestion"""
        category = cls.categorize_error(error)
        error_msg = str(error)
        
        suggestions = []
        
        # Add operation context
        if context:
            operation = context.operation
            backend = context.backend_name
            model = context.model_name
            
            if context.attempt_number > 1:
                suggestions.append(f"⏱️  Attempt {context.attempt_number} failed on '{operation}' with {backend}/{model}")
            else:
                suggestions.append(f"🔍 First attempt failed on '{operation}' with {backend}/{model}")
        
        # Add category-specific suggestions
        if category == ErrorCategory.CONNECTIVITY:
            suggestions.extend([
                "🔌 Connectivity issue detected:",
                "  1. Check internet connection",
                f"  2. Verify backend is running: lmapp status",
                f"  3. Try restarting backend: lmapp restart",
                "  4. Check firewall/proxy settings",
            ])
        
        elif category == ErrorCategory.MODEL:
            suggestions.extend([
                "📦 Model not found:",
                "  1. List available models: lmapp list",
                "  2. Download a model: lmapp install --model llama2",
                "  3. Check model path: lmapp config",
            ])
        
        elif category == ErrorCategory.PERFORMANCE:
            suggestions.extend([
                "⏱️  Request timeout detected:",
                "  1. Use a faster/smaller model: lmapp list --sizes",
                "  2. Increase timeout: lmapp config --timeout 120",
                "  3. Check backend load: lmapp status",
                "  4. Close other applications using GPU",
            ])
        
        elif category == ErrorCategory.RESOURCE:
            suggestions.extend([
                "💾 Resource exhaustion (memory/GPU):",
                "  1. Use a smaller quantized model: lmapp install --quantized",
                "  2. Close other applications",
                "  3. Check GPU memory: nvidia-smi",
                "  4. Enable offloading: lmapp config --offload",
            ])
        
        elif category == ErrorCategory.CONFIGURATION:
            suggestions.extend([
                "⚙️  Configuration error:",
                "  1. Reset configuration: lmapp config --reset",
                "  2. Verify settings: lmapp config --show",
                "  3. Reconfigure: lmapp setup",
            ])
        
        else:
            suggestions.extend([
                "❓ Unknown error occurred:",
                "  1. Check logs: lmapp logs",
                "  2. Try again (transient error)",
                "  3. Report issue: https://github.com/nabaznyl/lmapp/issues",
            ])
        
        return "\n".join(suggestions)


def retry_with_backoff(
    max_retries: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    backoff_base: float = 1.0,
    context: Optional[ErrorContext] = None,
) -> Callable:
    """
    Decorator for retrying operations with backoff and context-aware error handling
    
    Args:
        max_retries: Maximum number of retry attempts
        strategy: Retry strategy (EXPONENTIAL, LINEAR, IMMEDIATE, ADAPTIVE)
        backoff_base: Base for backoff calculation
        context: Error context for better error messages
    """
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            operation_name = getattr(func, '__name__', 'unknown_operation')
            error_context = context or ErrorContext(
                operation=operation_name,
                backend_name="unknown",
                model_name="unknown"
            )
            
            for attempt in range(max_retries + 1):
                try:
                    error_context.attempt_number = attempt + 1
                    error_context.is_first_attempt = (attempt == 0)
                    
                    logger.debug(
                        f"Executing {operation_name} (attempt {attempt + 1}/{max_retries + 1})"
                    )
                    return func(*args, **kwargs)
                
                except (ConnectionError, TimeoutError) as e:
                    last_exception = e
                    error_context.previous_error = str(e)
                    
                    if attempt < max_retries:
                        # Calculate backoff based on strategy
                        if strategy == RetryStrategy.EXPONENTIAL:
                            wait_time = backoff_base * (2 ** attempt)
                        elif strategy == RetryStrategy.LINEAR:
                            wait_time = backoff_base * (attempt + 1)
                        elif strategy == RetryStrategy.ADAPTIVE:
                            # Shorter waits for transient errors
                            category = ErrorAnalyzer.categorize_error(e)
                            if category == ErrorCategory.CONNECTIVITY:
                                wait_time = backoff_base * (2 ** attempt)  # Exponential for connection
                            elif category == ErrorCategory.PERFORMANCE:
                                wait_time = backoff_base * (attempt + 2)   # Linear for performance
                            else:
                                wait_time = 0
                        else:
                            wait_time = 0
                        
                        logger.warning(
                            f"{func.__name__} failed: {str(e)}. "
                            f"Retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} retries: {str(e)}"
                        )
                
                except Exception as e:
                    logger.error(
                        f"{func.__name__} raised unretryable error: {str(e)}",
                        exc_info=True,
                    )
                    raise
            
            if last_exception:
                raise last_exception
            raise RuntimeError(f"{func.__name__} failed without captured exception")
        
        return wrapper
    
    return decorator


class EnhancedErrorRecovery:
    """Enhanced error messages with context-aware recovery suggestions"""
    
    @staticmethod
    def format_error_message(
        error: Exception,
        context: Optional[ErrorContext] = None,
        include_traceback: bool = False
    ) -> str:
        """
        Format error message with rich context and suggestions
        
        Args:
            error: The exception that occurred
            context: Error context with operation details
            include_traceback: Include full traceback in output
        
        Returns:
            Formatted error message
        """
        lines = []
        
        # Header with error type
        error_type = type(error).__name__
        error_msg = str(error)
        lines.append(f"❌ {error_type}: {error_msg}")
        
        # Context information
        if context:
            lines.append("\n📍 Context:")
            lines.append(f"  Operation: {context.operation}")
            lines.append(f"  Backend: {context.backend_name}")
            lines.append(f"  Model: {context.model_name}")
            lines.append(f"  Attempt: {context.attempt_number}")
            
            if context.previous_error:
                lines.append(f"  Previous error: {context.previous_error}")
        
        # Recovery suggestions
        suggestion = ErrorAnalyzer.get_error_suggestion(error, context)
        lines.append("\n💡 Suggestions:")
        lines.append(suggestion)
        
        # Help footer
        lines.append("\n📖 For more help:")
        lines.append("  • lmapp --help")
        lines.append("  • lmapp status")
        lines.append("  • https://github.com/nabaznyl/lmapp#troubleshooting")
        
        return "\n".join(lines)
    
    @staticmethod
    def should_retry(error: Exception, attempt: int, max_retries: int) -> bool:
        """
        Determine if an error is retryable
        
        Args:
            error: The exception
            attempt: Current attempt number
            max_retries: Maximum retries allowed
        
        Returns:
            True if should retry
        """
        if attempt >= max_retries:
            return False
        
        # Retryable error types
        retryable = (ConnectionError, TimeoutError)
        return isinstance(error, retryable)


@retry_with_backoff(max_retries=3, strategy=RetryStrategy.ADAPTIVE)
def check_backend_health(backend: LLMBackend, timeout: float = 5.0) -> bool:
    """
    Check if backend is healthy and responsive with detailed error reporting
    
    Args:
        backend: Backend to check
        timeout: Timeout in seconds
    
    Returns:
        True if backend is healthy
    
    Raises:
        ConnectionError: If backend is not responding
    """
    logger.debug(f"Checking health of {backend.backend_name()}")
    
    try:
        if not backend.is_running():
            raise ConnectionError(f"{backend.backend_name()} is not running")
        
        # Quick chat to test responsiveness
        response = backend.chat(
            prompt="Test",
            model="tinyllama",
            temperature=0.5
        )
        
        if not response:
            raise ConnectionError(
                f"{backend.backend_name()} returned empty response"
            )
        
        logger.debug(f"{backend.backend_name()} health check passed")
        return True
    
    except Exception as e:
        logger.warning(f"Backend health check failed: {str(e)}")
        raise ConnectionError(
            f"Backend health check failed: {str(e)}"
        ) from e


# Maintain backward compatibility
class BackendFallback:
    """Fallback strategy for backend failures"""
    
    def __init__(self, primary_backend: LLMBackend):
        """Initialize with primary backend"""
        self.primary = primary_backend
        self.fallback: Optional[LLMBackend] = None
        self.use_fallback = False
    
    @retry_with_backoff(max_retries=2, strategy=RetryStrategy.EXPONENTIAL)
    def chat(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
    ) -> str:
        """
        Send chat with automatic fallback on failure
        
        Args:
            prompt: User prompt
            model: Model name
            temperature: Temperature setting
        
        Returns:
            Response text
        
        Raises:
            BackendError: If both primary and fallback fail
        """
        try:
            if self.use_fallback and self.fallback:
                logger.debug("Using fallback backend for chat")
                return self.fallback.chat(prompt, model, temperature)
            else:
                logger.debug("Using primary backend for chat")
                return self.primary.chat(prompt, model, temperature)
        except Exception as e:
            # Try fallback
            if not self.use_fallback and self.fallback:
                logger.warning(f"Primary backend failed: {str(e)}. Trying fallback...")
                self.use_fallback = True
                try:
                    response = self.fallback.chat(prompt, model, temperature)
                    logger.info("Fallback backend succeeded")
                    return response
                except Exception as fallback_error:
                    logger.error(f"Fallback backend also failed: {str(fallback_error)}")
                    raise BackendError(
                        f"Both primary and fallback backends failed.\n"
                        f"Primary error: {str(e)}\n"
                        f"Fallback error: {str(fallback_error)}"
                    ) from e
            else:
                raise

