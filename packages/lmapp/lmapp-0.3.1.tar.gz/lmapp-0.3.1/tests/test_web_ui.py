"""
Tests for LMAPP Web UI Server - FastAPI backend.

Tests cover API endpoints, WebSocket connections, document management,
and plugin integration.

Author: LMAPP Community
License: MIT
"""

import json
import pytest
from fastapi.testclient import TestClient
from lmapp.web.server import app, state


@pytest.fixture(autouse=True)
def reset_state():
    """Reset application state before each test."""
    state.active_connections = []
    state.chat_history = []
    state.uploaded_documents = {}
    state.installed_plugins = []
    yield
    state.active_connections = []
    state.chat_history = []
    state.uploaded_documents = {}
    state.installed_plugins = []


@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints."""

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code in [200, 404]  # 200 if static files mounted, 404 if not

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "LMAPP Web UI"
        assert data["version"] == "0.2.6"

    def test_status(self, client):
        """Test status endpoint."""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "version" in data
        assert "stats" in data
        assert "features" in data


class TestModelEndpoints:
    """Test model management endpoints."""

    def test_get_models(self, client):
        """Test getting available models."""
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "models" in data
        assert isinstance(data["models"], list)
        assert "default_model" in data


class TestChatEndpoints:
    """Test chat endpoints."""

    def test_post_chat(self, client):
        """Test sending a chat message."""
        response = client.post("/api/chat", json={"message": "Hello"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Hello"
        assert "response" in data
        assert "model" in data

    def test_post_chat_empty_message(self, client):
        """Test sending empty message raises error."""
        response = client.post("/api/chat", json={"message": ""})
        assert response.status_code == 400

    def test_post_chat_custom_model(self, client):
        """Test sending message with custom model."""
        response = client.post(
            "/api/chat",
            json={"message": "Test", "model": "custom-model"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "custom-model"

    def test_chat_history(self, client):
        """Test that chat history is maintained."""
        client.post("/api/chat", json={"message": "Hello"})
        client.post("/api/chat", json={"message": "How are you?"})

        assert len(state.chat_history) == 4  # 2 messages * 2 (user + assistant)
        assert state.chat_history[0]["role"] == "user"
        assert state.chat_history[1]["role"] == "assistant"


class TestDocumentEndpoints:
    """Test document management endpoints."""

    def test_list_documents_empty(self, client):
        """Test listing documents when none uploaded."""
        response = client.get("/api/documents")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["documents"]) == 0
        assert data["total_documents"] == 0

    def test_upload_document(self, client):
        """Test uploading a document."""
        response = client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", b"test content")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "document_id" in data
        assert data["filename"] == "test.txt"

    def test_list_documents_after_upload(self, client):
        """Test listing documents after upload."""
        # Upload a document
        client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", b"content")}
        )

        # List documents
        response = client.get("/api/documents")
        assert response.status_code == 200
        data = response.json()
        assert data["total_documents"] == 1
        assert data["documents"][0]["name"] == "test.txt"

    def test_delete_document(self, client):
        """Test deleting a document."""
        # Upload a document
        upload_response = client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", b"content")}
        )
        doc_id = upload_response.json()["document_id"]

        # Delete the document
        response = client.delete(f"/api/documents/{doc_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_delete_nonexistent_document(self, client):
        """Test deleting nonexistent document raises error."""
        response = client.delete("/api/documents/nonexistent")
        assert response.status_code == 404

    def test_multiple_documents(self, client):
        """Test uploading and managing multiple documents."""
        # Upload multiple documents
        for i in range(3):
            client.post(
                "/api/documents/upload",
                files={"file": (f"test{i}.txt", b"content")}
            )

        # Verify all documents listed
        response = client.get("/api/documents")
        data = response.json()
        assert data["total_documents"] == 3


class TestPluginEndpoints:
    """Test plugin management endpoints."""

    def test_list_plugins(self, client):
        """Test listing available plugins."""
        response = client.get("/api/plugins")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "plugins" in data
        assert isinstance(data["plugins"], list)
        assert data["total"] == len(data["plugins"])

    def test_install_plugin(self, client):
        """Test installing a plugin."""
        response = client.post("/api/plugins/translator/install")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["plugin"] == "translator"

        # Verify plugin is in installed list
        assert "translator" in state.installed_plugins

    def test_install_plugin_already_installed(self, client):
        """Test installing already installed plugin raises error."""
        # Install once
        client.post("/api/plugins/translator/install")

        # Try to install again
        response = client.post("/api/plugins/translator/install")
        assert response.status_code == 200  # Returns success: False
        data = response.json()
        assert data["success"] is False

    def test_uninstall_plugin(self, client):
        """Test uninstalling a plugin."""
        # Install plugin first
        client.post("/api/plugins/translator/install")

        # Uninstall it
        response = client.post("/api/plugins/translator/uninstall")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify plugin removed
        assert "translator" not in state.installed_plugins

    def test_uninstall_nonexistent_plugin(self, client):
        """Test uninstalling nonexistent plugin raises error."""
        response = client.post("/api/plugins/nonexistent/uninstall")
        assert response.status_code == 404

    def test_plugin_status_tracking(self, client):
        """Test that plugin installation status is tracked."""
        # List plugins before installation
        response = client.get("/api/plugins")
        plugins_before = response.json()["plugins"]
        translator_before = next(
            (p for p in plugins_before if p["name"] == "translator"),
            None
        )
        assert translator_before is not None
        assert translator_before["installed"] is False

        # Install plugin
        client.post("/api/plugins/translator/install")

        # List plugins after installation
        response = client.get("/api/plugins")
        plugins_after = response.json()["plugins"]
        translator_after = next(
            (p for p in plugins_after if p["name"] == "translator"),
            None
        )
        assert translator_after is not None
        assert translator_after["installed"] is True


class TestWebSocketChat:
    """Test WebSocket chat endpoint."""

    def test_websocket_connect(self, client):
        """Test connecting to WebSocket endpoint."""
        with client.websocket_connect("/ws/chat") as websocket:
            # Connection should succeed
            assert websocket is not None

    def test_websocket_send_message(self, client):
        """Test sending message via WebSocket."""
        with client.websocket_connect("/ws/chat") as websocket:
            # Send a message
            websocket.send_json({"message": "Hello", "model": "test-model"})

            # Receive tokens
            response = websocket.receive_json()
            assert response["type"] == "token"

    def test_websocket_streaming_response(self, client):
        """Test streaming response via WebSocket."""
        with client.websocket_connect("/ws/chat") as websocket:
            # Send a message
            websocket.send_json({"message": "Test", "model": "test-model"})

            # Collect all responses
            responses = []
            while True:
                response = websocket.receive_json()
                responses.append(response)
                if response.get("type") == "complete":
                    break

            # Should have multiple tokens and completion marker
            assert len(responses) > 1
            assert responses[-1]["type"] == "complete"

    def test_websocket_empty_message(self, client):
        """Test sending empty message via WebSocket."""
        with client.websocket_connect("/ws/chat") as websocket:
            websocket.send_json({"message": ""})

            response = websocket.receive_json()
            assert "error" in response

    def test_websocket_multiple_messages(self, client):
        """Test multiple messages in same WebSocket connection."""
        with client.websocket_connect("/ws/chat") as websocket:
            # Send first message
            websocket.send_json({"message": "Hello"})
            response1 = websocket.receive_json()
            assert "token" in str(response1).lower() or "error" in str(response1).lower()

            # Send second message
            websocket.send_json({"message": "World"})
            response2 = websocket.receive_json()
            assert "token" in str(response2).lower() or "error" in str(response2).lower()


class TestIntegration:
    """Integration tests across endpoints."""

    def test_complete_workflow(self, client):
        """Test a complete workflow: upload -> chat -> plugins."""
        # Check initial status
        status = client.get("/api/status").json()
        assert status["stats"]["documents"] == 0

        # Upload a document
        client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", b"Test document")}
        )

        # Send a chat message
        chat = client.post("/api/chat", json={"message": "Analyze this"}).json()
        assert chat["success"] is True

        # Install a plugin
        plugin = client.post("/api/plugins/code-analyzer/install").json()
        assert plugin["success"] is True

        # Check final status
        final_status = client.get("/api/status").json()
        assert final_status["stats"]["documents"] == 1
        assert final_status["stats"]["plugins_installed"] == 1

    def test_error_handling(self, client):
        """Test error handling across endpoints."""
        # Test 400 error
        response = client.post("/api/chat", json={"message": ""})
        assert response.status_code == 400

        # Test 404 error
        response = client.delete("/api/documents/nonexistent")
        assert response.status_code == 404

        response = client.post("/api/plugins/nonexistent/uninstall")
        assert response.status_code == 404


class TestDataTypes:
    """Test request/response data types."""

    def test_chat_message_validation(self, client):
        """Test ChatMessage Pydantic model."""
        # Valid message
        response = client.post("/api/chat", json={"message": "Test"})
        assert response.status_code == 200

        # Invalid (no message key)
        response = client.post("/api/chat", json={"content": "Test"})
        assert response.status_code == 422

    def test_response_formats(self, client):
        """Test that all responses follow expected format."""
        # Chat response
        chat = client.post("/api/chat", json={"message": "Test"}).json()
        assert "success" in chat
        assert "message" in chat or "error" in chat

        # Status response
        status = client.get("/api/status").json()
        assert "stats" in status
        assert "features" in status

        # Documents response
        docs = client.get("/api/documents").json()
        assert "documents" in docs
        assert "total_documents" in docs
