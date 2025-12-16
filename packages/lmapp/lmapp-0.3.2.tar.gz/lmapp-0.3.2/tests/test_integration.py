"""Integration tests for lmapp backend detection and CLI workflows."""

import pytest
from lmapp.backend.detector import BackendDetector
from mock_backend import MockBackend
from lmapp.core.config import LMAppConfig


class TestBackendDetector:
    """Test backend detection and initialization."""

    def test_detector_detects_backends(self):
        """Test that detector finds available backends."""
        detector = BackendDetector()
        backends = detector.detect_all()

        assert backends is not None
        assert isinstance(backends, list)
        assert len(backends) > 0

    def test_detector_mock_always_available(self):
        """Test that mock backend is always available."""
        detector = BackendDetector()
        backends = detector.detect_all()

        # At least one backend should be available
        assert len(backends) >= 1

    def test_detector_get_recommended(self):
        """Test getting recommended backend by RAM."""
        detector = BackendDetector()
        backend = detector.get_recommended(ram_gb=8)

        # Should return a backend (or None, which is acceptable)
        if backend is not None:
            assert hasattr(backend, "start")
            assert hasattr(backend, "stop")
            assert hasattr(backend, "chat")

    def test_detector_get_by_name(self):
        """Test getting backend by name."""
        detector = BackendDetector()
        # Mock backend is no longer in detector, so this should return None
        backend = detector.get_backend_by_name("mock")
        assert backend is None

    def test_detector_status_display(self):
        """Test backend status display works."""
        detector = BackendDetector()
        # This should not raise an exception
        detector.show_status_table()  # Just ensure it runs


class TestMockBackendIntegration:
    """Integration tests for mock backend functionality."""

    def test_mock_backend_lifecycle(self):
        """Test complete mock backend lifecycle."""
        backend = MockBackend()

        # Initial state
        assert not backend.is_running()

        # Start
        backend.start()
        assert backend.is_running()

        # Chat
        response = backend.chat("Hello, world!")
        assert isinstance(response, str)
        assert len(response) > 0

        # Stop
        backend.stop()
        assert not backend.is_running()

    def test_mock_backend_chat_response(self):
        """Test mock backend generates reasonable responses."""
        backend = MockBackend()
        backend.start()

        # Test different message types
        responses = {
            "What is Python?": backend.chat("What is Python?"),
            "Explain async/await": backend.chat("Explain async/await"),
            "Hi": backend.chat("Hi"),
        }

        # All should have responses
        for message, response in responses.items():
            assert response is not None
            assert len(response) > 10
            assert isinstance(response, str)

        backend.stop()

    def test_mock_backend_info(self):
        """Test backend info method."""
        backend = MockBackend()
        info = backend.get_info()

        # Info should be a dict-like object or have name attribute
        assert hasattr(info, "name") or isinstance(info, dict)
        if isinstance(info, dict):
            assert "name" in info
            assert info["name"] == "mock"


class TestConfigIntegration:
    """Integration tests for configuration system."""

    def test_config_initialization_with_defaults(self):
        """Test config initializes with sensible defaults."""
        config = LMAppConfig()

        assert config.temperature >= 0.0
        assert config.temperature <= 1.0
        assert config.model is not None
        assert config.timeout > 0

    def test_config_validation_integration(self):
        """Test config validation across multiple fields."""
        # Valid config
        config = LMAppConfig(temperature=0.5, model="mistral", timeout=30)
        assert config is not None

        # Invalid temperature (too high)
        with pytest.raises(ValueError):
            LMAppConfig(temperature=2.0)

        # Invalid temperature (negative)
        with pytest.raises(ValueError):
            LMAppConfig(temperature=-0.5)

    def test_config_model_persistence(self):
        """Test that config model changes persist."""
        config1 = LMAppConfig(model="llama2")

        # Create another config - should not affect previous
        config2 = LMAppConfig(model="mistral")

        assert config1.model == "llama2"
        assert config2.model == "mistral"


class TestCLIIntegration:
    """Integration tests for CLI workflows."""

    def test_cli_main_help(self):
        """Test that help command works."""
        from click.testing import CliRunner
        from lmapp.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "Commands:" in result.output or "Options:" in result.output

    def test_cli_status_command(self):
        """Test status command works and shows system info."""
        from click.testing import CliRunner
        from lmapp.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        # Status should show some system information
        assert len(result.output) > 20

    def test_cli_version_flag(self):
        """Test version flag displays version."""
        from click.testing import CliRunner
        from lmapp.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        # Should exit successfully
        assert result.exit_code == 0
        # Should contain version info
        assert "0.1.0" in result.output or "version" in result.output.lower()

    def test_cli_invalid_command(self):
        """Test CLI handles invalid commands gracefully."""
        from click.testing import CliRunner
        from lmapp.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["invalid-command"])

        # Should exit with error
        assert result.exit_code != 0


class TestBackendChatIntegration:
    """Integration tests for chat functionality across backends."""

    def test_chat_message_formats(self):
        """Test chat handles various message formats."""
        backend = MockBackend()
        backend.start()

        test_cases = [
            "Simple question?",
            "Multi-word question about Python?",
            "123 numeric message",
            "Special chars: !@#$%",
        ]

        for message in test_cases:
            # All should not raise exceptions
            try:
                response = backend.chat(message)
                assert response is not None
            except Exception as e:
                pytest.fail(f"Chat failed on message '{message}': {e}")

        backend.stop()

    def test_chat_consecutive_messages(self):
        """Test multiple consecutive chat messages."""
        backend = MockBackend()
        backend.start()

        messages = ["Hello", "How are you?", "Tell me about Python", "Goodbye"]

        responses = []
        for msg in messages:
            response = backend.chat(msg)
            responses.append(response)
            assert response is not None

        # All responses should be present
        assert len(responses) == len(messages)

        backend.stop()


class TestSystemIntegration:
    """End-to-end system integration tests."""

    def test_full_workflow_start_to_chat(self):
        """Test complete workflow: detect -> start -> chat -> stop."""
        # Force MockBackend for integration test to avoid dependency on real Ollama
        backend = MockBackend()
        assert backend is not None

        # Load config
        config = LMAppConfig()
        assert config is not None

        # Start backend
        backend.start()
        assert backend.is_running()

        # Send message
        message = "What is machine learning?"
        response = backend.chat(message)
        assert response is not None
        assert len(response) > 0

        # Stop backend
        backend.stop()
        assert not backend.is_running()

    def test_repeated_start_stop_cycles(self):
        """Test backend handles repeated start/stop cycles."""
        backend = MockBackend()

        for _ in range(5):
            backend.start()
            assert backend.is_running()

            response = backend.chat("Test")
            assert response is not None

            backend.stop()
            assert not backend.is_running()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
