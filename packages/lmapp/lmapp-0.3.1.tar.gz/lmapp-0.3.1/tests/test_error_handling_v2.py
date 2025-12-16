#!/usr/bin/env python3
"""
Tests for enhanced error handling and recovery (v0.2.2)
"""

import pytest
from unittest.mock import Mock, patch

from lmapp.utils.error_recovery_v2 import (
    ErrorCategory,
    ErrorAnalyzer,
    ErrorContext,
    EnhancedErrorRecovery,
    ConnectionError,
    TimeoutError as LMAppTimeoutError,
    BackendError,
    retry_with_backoff,
    RetryStrategy,
)


class TestErrorAnalyzer:
    """Test error categorization and analysis"""
    
    def test_categorize_connectivity_error(self):
        """Test connectivity error detection"""
        error = ConnectionError("Connection refused")
        category = ErrorAnalyzer.categorize_error(error)
        assert category == ErrorCategory.CONNECTIVITY
    
    def test_categorize_model_error(self):
        """Test model not found detection"""
        error = Exception("Model not found on backend")
        category = ErrorAnalyzer.categorize_error(error)
        assert category == ErrorCategory.MODEL
    
    def test_categorize_timeout_error(self):
        """Test timeout detection"""
        error = LMAppTimeoutError("Request timed out after 30s")
        category = ErrorAnalyzer.categorize_error(error)
        assert category == ErrorCategory.PERFORMANCE
    
    def test_categorize_resource_error(self):
        """Test resource error detection"""
        error = Exception("CUDA out of memory")
        category = ErrorAnalyzer.categorize_error(error)
        assert category == ErrorCategory.RESOURCE
    
    def test_categorize_memory_error(self):
        """Test memory error detection"""
        error = Exception("MemoryError: malloc failed")
        category = ErrorAnalyzer.categorize_error(error)
        assert category == ErrorCategory.RESOURCE
    
    def test_categorize_configuration_error(self):
        """Test configuration error detection"""
        error = Exception("Invalid configuration parameter")
        category = ErrorAnalyzer.categorize_error(error)
        assert category == ErrorCategory.CONFIGURATION
    
    def test_get_error_suggestion_connectivity(self):
        """Test suggestion for connectivity errors"""
        error = ConnectionError("Connection refused")
        suggestion = ErrorAnalyzer.get_error_suggestion(error)
        assert "lmapp status" in suggestion
        assert "Connectivity issue" in suggestion
    
    def test_get_error_suggestion_model(self):
        """Test suggestion for model errors"""
        error = Exception("Model not found")
        suggestion = ErrorAnalyzer.get_error_suggestion(error)
        assert "lmapp list" in suggestion
        assert "lmapp install" in suggestion
    
    def test_get_error_suggestion_timeout(self):
        """Test suggestion for timeout errors"""
        error = LMAppTimeoutError("Request timed out")
        suggestion = ErrorAnalyzer.get_error_suggestion(error)
        assert "timeout" in suggestion.lower()
    
    def test_get_error_suggestion_with_context(self):
        """Test suggestion includes context information"""
        context = ErrorContext(
            operation="chat",
            backend_name="ollama",
            model_name="llama2"
        )
        error = ConnectionError("Connection refused")
        suggestion = ErrorAnalyzer.get_error_suggestion(error, context)
        assert "chat" in suggestion
        assert "ollama" in suggestion
        assert "llama2" in suggestion


class TestErrorContext:
    """Test error context creation and tracking"""
    
    def test_create_error_context(self):
        """Test ErrorContext initialization"""
        context = ErrorContext(
            operation="generate_response",
            backend_name="ollama",
            model_name="mistral"
        )
        assert context.operation == "generate_response"
        assert context.backend_name == "ollama"
        assert context.model_name == "mistral"
        assert context.attempt_number == 1
        assert context.is_first_attempt is True
    
    def test_error_context_to_dict(self):
        """Test ErrorContext serialization"""
        context = ErrorContext(
            operation="chat",
            backend_name="ollama",
            model_name="llama2",
            attempt_number=2
        )
        context_dict = context.to_dict()
        assert context_dict["operation"] == "chat"
        assert context_dict["backend"] == "ollama"
        assert context_dict["model"] == "llama2"
        assert context_dict["attempt"] == 2


class TestEnhancedErrorRecovery:
    """Test enhanced error message formatting"""
    
    def test_format_error_message_basic(self):
        """Test basic error message formatting"""
        error = ConnectionError("Backend offline")
        message = EnhancedErrorRecovery.format_error_message(error)
        assert "ConnectionError" in message
        assert "Backend offline" in message
        assert "❌" in message
    
    def test_format_error_message_with_context(self):
        """Test error message with context"""
        context = ErrorContext(
            operation="generate",
            backend_name="ollama",
            model_name="neural"
        )
        error = ConnectionError("Connection failed")
        message = EnhancedErrorRecovery.format_error_message(error, context)
        assert "generate" in message
        assert "ollama" in message
        assert "neural" in message
        assert "📍 Context" in message
    
    def test_format_error_message_multiple_attempts(self):
        """Test error message for retry attempts"""
        context = ErrorContext(
            operation="query",
            backend_name="ollama",
            model_name="llama2",
            attempt_number=3
        )
        error = LMAppTimeoutError("Timeout on attempt 3")
        message = EnhancedErrorRecovery.format_error_message(error, context)
        assert "Attempt: 3" in message
    
    def test_should_retry_connection_error(self):
        """Test that connection errors are retryable"""
        error = ConnectionError("Connection refused")
        assert EnhancedErrorRecovery.should_retry(error, 0, 3) is True
        assert EnhancedErrorRecovery.should_retry(error, 3, 3) is False
    
    def test_should_retry_timeout_error(self):
        """Test that timeout errors are retryable"""
        error = LMAppTimeoutError("Request timed out")
        assert EnhancedErrorRecovery.should_retry(error, 0, 3) is True
    
    def test_should_not_retry_other_errors(self):
        """Test that other errors are not retried"""
        error = ValueError("Invalid parameter")
        assert EnhancedErrorRecovery.should_retry(error, 0, 3) is False


class TestRetryDecorator:
    """Test retry decorator with backoff strategies"""
    
    def test_retry_success_first_attempt(self):
        """Test successful operation on first attempt"""
        def test_func():
            return "success"
        
        decorated = retry_with_backoff(max_retries=3)(test_func)
        result = decorated()
        assert result == "success"
    
    def test_retry_success_after_failure(self):
        """Test successful operation after failures"""
        call_count = {'count': 0}
        
        def test_func():
            call_count['count'] += 1
            if call_count['count'] < 3:
                raise ConnectionError("Failed")
            return "success"
        
        decorated = retry_with_backoff(max_retries=3, strategy=RetryStrategy.IMMEDIATE)(test_func)
        result = decorated()
        assert result == "success"
        assert call_count['count'] == 3
    
    def test_retry_max_retries_exceeded(self):
        """Test failure when max retries exceeded"""
        def test_func():
            raise ConnectionError("Always fails")
        
        decorated = retry_with_backoff(max_retries=2, strategy=RetryStrategy.IMMEDIATE)(test_func)
        
        with pytest.raises(ConnectionError):
            decorated()
    
    def test_retry_non_retryable_error(self):
        """Test non-retryable errors propagate immediately"""
        def test_func():
            raise ValueError("Invalid param")
        
        decorated = retry_with_backoff(max_retries=3)(test_func)
        
        with pytest.raises(ValueError):
            decorated()
    
    def test_retry_exponential_strategy(self):
        """Test exponential backoff strategy"""
        def test_func():
            return "success"
        
        decorated = retry_with_backoff(
            max_retries=3,
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_base=0.01
        )(test_func)
        result = decorated()
        assert result == "success"
    
    def test_retry_adaptive_strategy(self):
        """Test adaptive backoff strategy"""
        def test_func():
            return "success"
        
        decorated = retry_with_backoff(
            max_retries=3,
            strategy=RetryStrategy.ADAPTIVE,
            backoff_base=0.01
        )(test_func)
        result = decorated()
        assert result == "success"
    
    def test_retry_with_context(self):
        """Test retry with error context"""
        context = ErrorContext(
            operation="test_op",
            backend_name="test_backend",
            model_name="test_model"
        )
        def test_func():
            return "success"
        
        decorated = retry_with_backoff(
            max_retries=2,
            context=context
        )(test_func)
        result = decorated()
        assert result == "success"


class TestErrorCategoryEnum:
    """Test ErrorCategory enum values"""
    
    def test_error_categories_defined(self):
        """Test all error categories are defined"""
        assert hasattr(ErrorCategory, 'CONNECTIVITY')
        assert hasattr(ErrorCategory, 'MODEL')
        assert hasattr(ErrorCategory, 'PERFORMANCE')
        assert hasattr(ErrorCategory, 'RESOURCE')
        assert hasattr(ErrorCategory, 'AUTHENTICATION')
        assert hasattr(ErrorCategory, 'CONFIGURATION')
        assert hasattr(ErrorCategory, 'UNKNOWN')
    
    def test_error_category_values(self):
        """Test error category enum values"""
        assert ErrorCategory.CONNECTIVITY.value == "connectivity"
        assert ErrorCategory.MODEL.value == "model"
        assert ErrorCategory.PERFORMANCE.value == "performance"


# Integration tests
class TestErrorHandlingIntegration:
    """Integration tests for error handling"""
    
    def test_full_error_handling_flow(self):
        """Test complete error handling flow"""
        error = ConnectionError("Backend connection failed")
        context = ErrorContext(
            operation="chat",
            backend_name="ollama",
            model_name="mistral"
        )
        
        # Categorize
        category = ErrorAnalyzer.categorize_error(error)
        assert category == ErrorCategory.CONNECTIVITY
        
        # Get suggestion
        suggestion = ErrorAnalyzer.get_error_suggestion(error, context)
        assert "lmapp status" in suggestion
        
        # Format message
        message = EnhancedErrorRecovery.format_error_message(error, context)
        assert "ConnectionError" in message
        assert "chat" in message
    
    def test_multiple_error_scenarios(self):
        """Test various error scenarios"""
        scenarios = [
            (ConnectionError("Connection refused"), ErrorCategory.CONNECTIVITY),
            (Exception("out of memory"), ErrorCategory.RESOURCE),
            (Exception("Model not found"), ErrorCategory.MODEL),
            (LMAppTimeoutError("Request timed out after 30s"), ErrorCategory.PERFORMANCE),
        ]
        
        for error, expected_category in scenarios:
            category = ErrorAnalyzer.categorize_error(error)
            assert category == expected_category

