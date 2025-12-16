#!/usr/bin/env python3
"""
Llamafile Backend Integration Tests
Tests llamafile backend when available
"""
import pytest
from pathlib import Path
from src.lmapp.backend.llamafile import LlamafileBackend


@pytest.fixture
def llamafile_backend():
    """Provide a llamafile backend instance"""
    return LlamafileBackend()


class TestLlamafileBackendIntegration:
    """Integration tests for llamafile backend"""

    def test_llamafile_detection(self, llamafile_backend):
        """Test that llamafile can be detected if installed"""
        is_installed = llamafile_backend.is_installed()
        assert isinstance(is_installed, bool)
        
        if is_installed:
            models = llamafile_backend.list_models()
            assert isinstance(models, list)

    def test_llamafile_directory_creation(self, llamafile_backend):
        """Test that llamafile directory is created"""
        llamafile_dir = Path.home() / ".lmapp" / "llamafiles"
        assert llamafile_dir.exists()
        assert llamafile_dir.is_dir()

    @pytest.mark.skipif(
        not LlamafileBackend().is_installed(),
        reason="Llamafile not installed"
    )
    def test_llamafile_service_status(self, llamafile_backend):
        """Test checking llamafile service status"""
        is_running = llamafile_backend.is_running()
        assert isinstance(is_running, bool)

    @pytest.mark.skipif(
        not LlamafileBackend().is_installed(),
        reason="Llamafile not installed"
    )
    def test_llamafile_list_models(self, llamafile_backend):
        """Test listing llamafile models"""
        models = llamafile_backend.list_models()
        assert isinstance(models, list)
        assert len(models) > 0  # Should have at least one if installed

    @pytest.mark.skipif(
        not LlamafileBackend().is_running(),
        reason="Llamafile not running"
    )
    def test_llamafile_chat_response(self, llamafile_backend):
        """Test getting a chat response from llamafile"""
        response = llamafile_backend.chat("Say hello")
        
        assert isinstance(response, str)
        # Note: llamafile might return empty string if not properly configured

    def test_llamafile_backend_info(self, llamafile_backend):
        """Test getting backend info"""
        info = llamafile_backend.get_info()
        
        assert info.name == "llamafile"
        assert info.display_name == "llamafile"
        
        if llamafile_backend.is_installed():
            assert info.version is not None

    @pytest.mark.skipif(
        not LlamafileBackend().is_installed(),
        reason="Llamafile not installed"
    )
    def test_llamafile_start_stop(self, llamafile_backend):
        """Test starting and stopping llamafile"""
        # This test may take some time as llamafile needs to load
        
        initial_status = llamafile_backend.is_running()
        
        # Try to start
        if not initial_status:
            start_result = llamafile_backend.start()
            assert isinstance(start_result, bool)
            
            # If start succeeded, verify it's running
            if start_result:
                assert llamafile_backend.is_running()
                
                # Clean up - stop it
                stop_result = llamafile_backend.stop()
                assert isinstance(stop_result, bool)

    @pytest.mark.slow
    @pytest.mark.skipif(
        LlamafileBackend().is_installed(),
        reason="Llamafile already installed, skip download test"
    )
    def test_llamafile_install(self, llamafile_backend):
        """Test installing llamafile (slow, requires download)"""
        # This test is marked as slow and only runs if not already installed
        # It will download ~60MB
        
        result = llamafile_backend.install()
        assert isinstance(result, bool)
        
        if result:
            assert llamafile_backend.is_installed()
            assert len(llamafile_backend.list_models()) > 0
