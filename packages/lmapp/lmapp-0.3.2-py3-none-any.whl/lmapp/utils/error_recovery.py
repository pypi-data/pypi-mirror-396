#!/usr/bin/env python3
"""
Error Handling and Recovery
Retry logic, fallback strategies, and enhanced error messages
"""

import time
from typing import Optional, TypeVar, Callable
from functools import wraps
from enum import Enum

from lmapp.utils.logging import logger
from lmapp.backend.base import LLMBackend

T = TypeVar("T")


class RetryStrategy(Enum):
    """Retry strategy options"""

    EXPONENTIAL = "exponential"  # 1s, 2s, 4s, 8s
    LINEAR = "linear"  # 1s, 2s, 3s, 4s
    IMMEDIATE = "immediate"  # No delay


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


def retry_with_backoff(
    max_retries: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    backoff_base: float = 1.0,
) -> Callable:
    """
    Decorator for retrying operations with backoff

    Args:
        max_retries: Maximum number of retry attempts
        strategy: Retry strategy (EXPONENTIAL, LINEAR, IMMEDIATE)
        backoff_base: Base for backoff calculation
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    logger.debug(
                        f"Executing {func.__name__} (attempt {attempt + 1}/{max_retries + 1})"
                    )
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_exception = e

                    if attempt < max_retries:
                        # Calculate backoff
                        if strategy == RetryStrategy.EXPONENTIAL:
                            wait_time = backoff_base * (2**attempt)
                        elif strategy == RetryStrategy.LINEAR:
                            wait_time = backoff_base * (attempt + 1)
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

            # Always raise a meaningful exception if retries failed
            if last_exception:
                raise last_exception
            raise RuntimeError(f"{func.__name__} failed without captured exception")

        return wrapper

    return decorator


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


class ErrorRecovery:
    """Enhanced error messages with recovery suggestions"""

    @staticmethod
    def get_recovery_suggestion(error: Exception) -> Optional[str]:
        """
        Get recovery suggestion for an error

        Args:
            error: The exception that occurred

        Returns:
            Recovery suggestion message, or None
        """
        error_msg = str(error).lower()

        # Connection errors
        if "connection" in error_msg or "refused" in error_msg:
            return (
                "Backend is not running.\n"
                "Try:\n"
                "  1. lmapp install    # Install and start backend\n"
                "  2. lmapp status     # Check backend status"
            )

        # Model not found
        if "model" in error_msg or "not found" in error_msg:
            return (
                "Model not found on backend.\n"
                "Try:\n"
                "  1. lmapp status     # See available models\n"
                "  2. lmapp install    # Download a model"
            )

        # Timeout
        if "timeout" in error_msg:
            return (
                "Request timed out (backend too slow).\n"
                "Try:\n"
                "  1. Use a smaller model\n"
                "  2. lmapp status     # Check backend health"
            )

        # Memory issues
        if "memory" in error_msg or "cuda" in error_msg:
            return (
                "Memory error (model too large for device).\n"
                "Try:\n"
                "  1. Use a smaller model\n"
                "  2. Close other applications to free RAM"
            )

        return None

    @staticmethod
    def format_error_with_recovery(
        error: Exception, context: Optional[str] = None
    ) -> str:
        """
        Format error message with recovery suggestions

        Args:
            error: The exception that occurred
            context: Additional context about what was being attempted

        Returns:
            Formatted error message with recovery suggestions
        """
        lines = ["❌ Error occurred:"]

        if context:
            lines.append(f"  Context: {context}")

        lines.append(f"  Message: {str(error)}")

        suggestion = ErrorRecovery.get_recovery_suggestion(error)
        if suggestion:
            lines.append("\n💡 Recovery suggestion:")
            for line in suggestion.split("\n"):
                lines.append(f"  {line}")

        lines.append("\n📖 For more help: lmapp --help")

        return "\n".join(lines)


# Health check function for backend
@retry_with_backoff(max_retries=3, strategy=RetryStrategy.LINEAR)
def check_backend_health(backend: LLMBackend, timeout: float = 5.0) -> bool:
    """
    Check if backend is healthy and responsive

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
        response = backend.chat(prompt="Test", model="tinyllama", temperature=0.5)

        if not response:
            raise ConnectionError(f"{backend.backend_name()} returned empty response")

        logger.debug(f"{backend.backend_name()} health check passed")
        return True
    except Exception as e:
        logger.warning(f"Backend health check failed: {str(e)}")
        raise ConnectionError(f"Backend health check failed: {str(e)}") from e
