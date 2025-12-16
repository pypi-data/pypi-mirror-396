"""Tests for chat module"""

import pytest
from datetime import datetime
from lmapp.core.chat import ChatSession, ChatMessage
from mock_backend import MockBackend


class TestChatMessage:
    """Test ChatMessage class"""

    def test_message_creation(self):
        """Test creating a chat message"""
        msg = ChatMessage("user", "Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert isinstance(msg.timestamp, datetime)

    def test_message_to_dict(self):
        """Test converting message to dict"""
        msg = ChatMessage("assistant", "Hi there")
        msg_dict = msg.to_dict()

        assert msg_dict["role"] == "assistant"
        assert msg_dict["content"] == "Hi there"
        assert "timestamp" in msg_dict


class TestChatSession:
    """Test ChatSession class"""

    def test_session_creation(self, chat_session):
        """Test creating a chat session"""
        assert chat_session.backend is not None
        assert chat_session.model == "mock-model"
        assert len(chat_session.history) == 0

    def test_session_creation_fails_if_backend_not_running(self):
        """Test session creation fails if backend not running"""
        backend = MockBackend()
        # Don't start the backend

        with pytest.raises(ValueError) as exc_info:
            ChatSession(backend, model="test")

        assert "not running" in str(exc_info.value).lower()

    def test_send_prompt(self, chat_session):
        """Test sending a prompt"""
        response = chat_session.send_prompt("Test prompt")

        assert response is not None
        assert len(response) > 0
        assert len(chat_session.history) == 2  # user + assistant

    def test_send_empty_prompt_fails(self, chat_session):
        """Test sending empty prompt raises error"""
        with pytest.raises(ValueError) as exc_info:
            chat_session.send_prompt("")

        assert "empty" in str(exc_info.value).lower()

    def test_send_whitespace_prompt_fails(self, chat_session):
        """Test sending whitespace-only prompt raises error"""
        with pytest.raises(ValueError):
            chat_session.send_prompt("   ")

    def test_get_history(self, chat_session):
        """Test getting conversation history"""
        chat_session.send_prompt("First message")
        chat_session.send_prompt("Second message")

        history = chat_session.get_history()
        assert len(history) == 4  # 2 user + 2 assistant
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_get_history_with_limit(self, chat_session):
        """Test getting history with limit"""
        chat_session.send_prompt("First")
        chat_session.send_prompt("Second")
        chat_session.send_prompt("Third")

        history = chat_session.get_history(limit=2)
        assert len(history) == 2

    def test_get_history_text(self, chat_session):
        """Test getting history as formatted text"""
        chat_session.send_prompt("Hello")

        history_text = chat_session.get_history_text()
        assert isinstance(history_text, str)
        assert "You:" in history_text or "You" in history_text
        assert "Hello" in history_text

    def test_clear_history(self, chat_session):
        """Test clearing history"""
        chat_session.send_prompt("First")
        chat_session.send_prompt("Second")

        assert len(chat_session.history) > 0

        cleared = chat_session.clear_history()
        assert cleared > 0
        assert len(chat_session.history) == 0

    def test_get_stats(self, chat_session):
        """Test getting session statistics"""
        chat_session.send_prompt("Test message")

        stats = chat_session.get_stats()
        assert stats["backend"] == "mock"
        assert stats["model"] == "mock-model"
        assert stats["messages"] == 2
        assert stats["user_messages"] == 1
        assert stats["assistant_messages"] == 1
        assert "created_at" in stats
        assert "duration_seconds" in stats

    def test_multiple_turns(self, chat_session):
        """Test multi-turn conversation"""
        chat_session.send_prompt("What is Python?")
        chat_session.send_prompt("Is it hard to learn?")
        chat_session.send_prompt("Can I use it for web development?")

        assert len(chat_session.history) == 6  # 3 user + 3 assistant
        stats = chat_session.get_stats()
        assert stats["user_messages"] == 3
        assert stats["assistant_messages"] == 3
