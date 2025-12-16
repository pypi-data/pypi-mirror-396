#!/usr/bin/env python3
"""
Ollama Backend Integration Tests
Tests real Ollama backend when available
"""
import pytest
from src.lmapp.backend.ollama import OllamaBackend


@pytest.fixture
def ollama_backend():
    """Provide an Ollama backend instance"""
    return OllamaBackend()


class TestOllamaBackendIntegration:
    """Integration tests for Ollama backend (requires Ollama installed)"""

    def test_ollama_detection(self, ollama_backend):
        """Test that Ollama can be detected if installed"""
        # This test will pass even if Ollama is not installed
        is_installed = ollama_backend.is_installed()
        assert isinstance(is_installed, bool)
        
        if is_installed:
            version = ollama_backend.get_version()
            assert version is not None
            assert len(version) > 0

    @pytest.mark.skipif(
        not OllamaBackend().is_installed(),
        reason="Ollama not installed"
    )
    def test_ollama_service_status(self, ollama_backend):
        """Test checking Ollama service status"""
        is_running = ollama_backend.is_running()
        assert isinstance(is_running, bool)

    @pytest.mark.skipif(
        not OllamaBackend().is_running(),
        reason="Ollama not running"
    )
    def test_ollama_list_models(self, ollama_backend):
        """Test listing models from running Ollama"""
        models = ollama_backend.list_models()
        assert isinstance(models, list)
        # If Ollama is running, it should have at least installed models
        # (though it might be empty if no models are pulled)

    @pytest.mark.skipif(
        not OllamaBackend().is_running() or not OllamaBackend().list_models(),
        reason="Ollama not running or no models available"
    )
    def test_ollama_chat_response(self, ollama_backend):
        """Test getting a chat response from Ollama"""
        models = ollama_backend.list_models()
        if not models:
            pytest.skip("No models available")
        
        # Use the first available model
        model = models[0]
        response = ollama_backend.chat("Say hello", model=model)
        
        assert isinstance(response, str)
        assert len(response) > 0

    def test_ollama_backend_info(self, ollama_backend):
        """Test getting backend info"""
        info = ollama_backend.get_info()
        
        assert info.name == "ollama"
        assert info.display_name == "Ollama"
        
        if ollama_backend.is_installed():
            assert info.version is not None

    @pytest.mark.skipif(
        not OllamaBackend().is_installed(),
        reason="Ollama not installed"
    )
    def test_ollama_start_stop(self, ollama_backend):
        """Test starting and stopping Ollama service"""
        # This test only checks that the methods execute without error
        # Actual service management may require system permissions
        
        initial_status = ollama_backend.is_running()
        
        # Try to start (may already be running)
        start_result = ollama_backend.start()
        assert isinstance(start_result, bool)
        
        # Try to stop (may not have permissions)
        stop_result = ollama_backend.stop()
        assert isinstance(stop_result, bool)
