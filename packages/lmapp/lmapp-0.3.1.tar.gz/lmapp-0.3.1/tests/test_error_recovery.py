#!/usr/bin/env python3
"""
Error Recovery and Handling Tests
Tests for retry logic, fallback strategies, and error messages
"""

import pytest
import time
from unittest.mock import Mock

from lmapp.utils.error_recovery import (
    retry_with_backoff,
    RetryStrategy,
    BackendError,
    ConnectionError,
    ModelNotFoundError,
    TimeoutError,
    BackendFallback,
    ErrorRecovery,
    check_backend_health,
)
from mock_backend import MockBackend


class TestRetryDecorator:
    """Test retry_with_backoff decorator"""

    def test_retry_immediate_success(self):
        """Test that successful calls don't retry"""
        call_count = 0

        @retry_with_backoff(max_retries=3)
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_func()

        assert result == "success"
        assert call_count == 1

    def test_retry_with_eventual_success(self):
        """Test retrying until success"""
        call_count = 0

        @retry_with_backoff(max_retries=3, strategy=RetryStrategy.IMMEDIATE)
        def eventual_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Not ready yet")
            return "success"

        result = eventual_success()

        assert result == "success"
        assert call_count == 3

    def test_retry_exhaustion(self):
        """Test that retries are exhausted"""
        call_count = 0

        @retry_with_backoff(max_retries=2, strategy=RetryStrategy.IMMEDIATE)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError):
            always_fails()

        assert call_count == 3  # Initial attempt + 2 retries

    def test_exponential_backoff(self):
        """Test exponential backoff timing"""
        call_times = []

        @retry_with_backoff(
            max_retries=2, strategy=RetryStrategy.EXPONENTIAL, backoff_base=0.01
        )
        def failing_func():
            call_times.append(time.time())
            raise ConnectionError("Fail")

        with pytest.raises(ConnectionError):
            failing_func()

        # Should have attempted 3 times (initial + 2 retries)
        assert len(call_times) == 3

    def test_linear_backoff(self):
        """Test linear backoff timing"""
        call_times = []

        @retry_with_backoff(
            max_retries=2, strategy=RetryStrategy.LINEAR, backoff_base=0.01
        )
        def failing_func():
            call_times.append(time.time())
            raise ConnectionError("Fail")

        with pytest.raises(ConnectionError):
            failing_func()

        assert len(call_times) == 3


class TestBackendFallback:
    """Test BackendFallback strategy"""

    def test_fallback_initialization(self):
        """Test fallback initialization"""
        primary = MockBackend()
        fallback = BackendFallback(primary)

        assert fallback.primary is primary
        assert fallback.fallback is None
        assert fallback.use_fallback is False

    def test_chat_with_primary_success(self):
        """Test chat succeeds with primary backend"""
        primary = MockBackend()
        fallback = BackendFallback(primary)

        response = fallback.chat(prompt="Hello", model="tinyllama", temperature=0.7)

        assert response is not None
        assert "Hello" in response or response

    def test_chat_with_fallback(self):
        """Test chat fallback when primary fails"""
        primary = Mock()
        primary.chat = Mock(side_effect=ConnectionError("Primary failed"))

        fallback = BackendFallback(primary)
        fallback.fallback = MockBackend()

        response = fallback.chat(prompt="Hello", model="tinyllama", temperature=0.7)

        assert response is not None


class TestErrorRecovery:
    """Test ErrorRecovery helper"""

    def test_connection_error_suggestion(self):
        """Test recovery suggestion for connection errors"""
        error = ConnectionError("Connection refused")
        suggestion = ErrorRecovery.get_recovery_suggestion(error)

        assert suggestion is not None
        assert "lmapp install" in suggestion
        assert "lmapp status" in suggestion

    def test_model_not_found_suggestion(self):
        """Test recovery suggestion for model errors"""
        error = Exception("Model not found")
        suggestion = ErrorRecovery.get_recovery_suggestion(error)

        assert suggestion is not None
        assert "lmapp install" in suggestion

    def test_timeout_suggestion(self):
        """Test recovery suggestion for timeout errors"""
        error = TimeoutError("Request timeout")
        suggestion = ErrorRecovery.get_recovery_suggestion(error)

        assert suggestion is not None
        assert "smaller model" in suggestion

    def test_memory_error_suggestion(self):
        """Test recovery suggestion for memory errors"""
        error = Exception("CUDA out of memory")
        suggestion = ErrorRecovery.get_recovery_suggestion(error)

        assert suggestion is not None
        assert "memory" in suggestion.lower()

    def test_format_error_with_recovery(self):
        """Test formatting error with recovery suggestions"""
        error = ConnectionError("Connection refused")
        formatted = ErrorRecovery.format_error_with_recovery(
            error, context="Starting chat session"
        )

        assert "❌ Error occurred:" in formatted
        assert "Context: Starting chat session" in formatted
        assert "💡 Recovery suggestion:" in formatted
        assert "lmapp install" in formatted


class TestHealthCheck:
    """Test backend health check"""

    def test_health_check_success(self):
        """Test successful health check"""
        backend = MockBackend()
        backend.start()  # Start the backend first

        try:
            result = check_backend_health(backend, timeout=5.0)
            assert result is True
        finally:
            backend.stop()

    def test_health_check_not_running(self):
        """Test health check when backend not running"""
        backend = Mock()
        backend.backend_name = Mock(return_value="TestBackend")
        backend.is_running = Mock(return_value=False)

        with pytest.raises(ConnectionError):
            check_backend_health(backend)

    def test_health_check_empty_response(self):
        """Test health check with empty response"""
        backend = Mock()
        backend.backend_name = Mock(return_value="TestBackend")
        backend.is_running = Mock(return_value=True)
        backend.chat = Mock(return_value="")

        with pytest.raises(ConnectionError):
            check_backend_health(backend)


class TestCustomExceptions:
    """Test custom exception classes"""

    def test_backend_error(self):
        """Test BackendError exception"""
        error = BackendError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_connection_error(self):
        """Test ConnectionError exception"""
        error = ConnectionError("Connection failed")
        assert isinstance(error, BackendError)

    def test_model_not_found_error(self):
        """Test ModelNotFoundError exception"""
        error = ModelNotFoundError("Model not found")
        assert isinstance(error, BackendError)

    def test_timeout_error(self):
        """Test TimeoutError exception"""
        error = TimeoutError("Request timed out")
        assert isinstance(error, BackendError)
