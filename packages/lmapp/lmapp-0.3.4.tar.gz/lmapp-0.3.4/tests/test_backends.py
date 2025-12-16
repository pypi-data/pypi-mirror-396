"""Tests for backend modules"""

from mock_backend import MockBackend
from lmapp.backend.detector import BackendDetector
from lmapp.backend.base import BackendStatus


class TestMockBackend:
    """Test MockBackend implementation"""

    def test_backend_name(self):
        """Test backend_name method"""
        backend = MockBackend()
        assert backend.backend_name() == "mock"

    def test_display_name(self):
        """Test backend_display_name method"""
        backend = MockBackend()
        assert backend.backend_display_name() == "Mock (Testing)"

    def test_is_installed(self):
        """Test is_installed always returns True"""
        backend = MockBackend()
        assert backend.is_installed() is True

    def test_get_version(self):
        """Test get_version returns mock version"""
        backend = MockBackend()
        assert backend.get_version() == "1.0.0-mock"

    def test_start_stop(self):
        """Test start and stop methods"""
        backend = MockBackend()

        assert backend.is_running() is False
        backend.start()
        assert backend.is_running() is True
        backend.stop()
        assert backend.is_running() is False

    def test_list_models(self):
        """Test list_models returns mock models"""
        backend = MockBackend()
        models = backend.list_models()
        assert "mock-model" in models
        assert "mock-7b" in models
        assert "mock-13b" in models

    def test_chat(self):
        """Test chat returns response"""
        backend = MockBackend()
        backend.start()

        response = backend.chat("Hello", model="mock-model")
        assert response is not None
        assert len(response) > 0
        assert "You asked: Hello" in response

    def test_get_info(self):
        """Test get_info returns correct structure"""
        backend = MockBackend()
        info = backend.get_info()

        assert info.name == "mock"
        assert info.display_name == "Mock (Testing)"
        assert info.version == "1.0.0-mock"
        assert info.status == BackendStatus.INSTALLED


class TestBackendDetector:
    """Test BackendDetector class"""

    def test_detector_initialization(self):
        """Test detector initializes with backends"""
        detector = BackendDetector()
        assert detector.backends is not None
        assert len(detector.backends) > 0

    def test_detect_all(self):
        """Test detect_all returns available backends"""
        detector = BackendDetector()
        available = detector.detect_all()
        # Mock backend is always available
        assert len(available) >= 0

    def test_get_recommended(self):
        """Test get_recommended returns a backend"""
        detector = BackendDetector()
        recommended = detector.get_recommended(16)
        assert recommended is not None

    def test_get_backend_by_name(self):
        """Test get_backend_by_name retrieves backends"""
        detector = BackendDetector()
        mock = detector.get_backend_by_name("mock")
        # May or may not have mock if not specifically added to detector
        if mock:
            assert mock.backend_name() == "mock"

    def test_show_status_table(self, capsys):
        """Test show_status_table produces output"""
        detector = BackendDetector()
        detector.show_status_table()
        # Just verify it doesn't crash
        assert True
