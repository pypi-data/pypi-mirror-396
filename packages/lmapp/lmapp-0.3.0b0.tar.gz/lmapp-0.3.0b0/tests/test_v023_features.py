"""
Tests for LMAPP v0.2.3 new features.

Tests for session management, system prompts, enhanced errors, and command aliases.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Session tests
from lmapp.core.sessions import Message, Session, SessionManager, get_session_manager


class TestMessage:
    """Test Message class."""
    
    def test_message_creation(self):
        """Test basic message creation."""
        msg = Message("user", "Hello world")
        assert msg.role == "user"
        assert msg.content == "Hello world"
        assert msg.timestamp is not None
    
    def test_message_with_metadata(self):
        """Test message with metadata."""
        metadata = {"model": "llama2", "tokens": 42}
        msg = Message("assistant", "Response", metadata=metadata)
        assert msg.metadata == metadata
    
    def test_message_to_dict(self):
        """Test message serialization."""
        msg = Message("user", "Test")
        data = msg.to_dict()
        assert data["role"] == "user"
        assert data["content"] == "Test"
        assert "timestamp" in data
    
    def test_message_from_dict(self):
        """Test message deserialization."""
        original = Message("assistant", "Hello", metadata={"test": True})
        data = original.to_dict()
        restored = Message.from_dict(data)
        assert restored.role == original.role
        assert restored.content == original.content


class TestSession:
    """Test Session class."""
    
    def test_session_creation(self):
        """Test session creation."""
        session = Session()
        assert session.session_id is not None
        assert session.name is not None
        assert len(session.messages) == 0
    
    def test_session_add_message(self):
        """Test adding messages to session."""
        session = Session()
        msg1 = session.add_message("user", "Hello")
        msg2 = session.add_message("assistant", "Hi there")
        
        assert len(session.messages) == 2
        assert session.messages[0].content == "Hello"
        assert session.messages[1].content == "Hi there"
    
    def test_session_get_context(self):
        """Test getting conversation context."""
        session = Session()
        session.add_message("user", "Message 1")
        session.add_message("assistant", "Response 1")
        session.add_message("user", "Message 2")
        
        context = session.get_context(limit=2)
        assert len(context) == 2
        assert context[0]["role"] == "assistant"
        assert context[1]["role"] == "user"
    
    def test_session_get_summary(self):
        """Test getting session summary."""
        session = Session()
        session.add_message("user", "Test message")
        session.add_message("assistant", "Test response")
        
        summary = session.get_summary()
        assert "2 messages" in summary
        assert "1 user" in summary
        assert "1 assistant" in summary
    
    def test_session_serialization(self):
        """Test session serialization and deserialization."""
        session = Session(name="Test Session")
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi")
        
        data = session.to_dict()
        restored = Session.from_dict(data)
        
        assert restored.name == session.name
        assert len(restored.messages) == 2
        assert restored.messages[0].content == "Hello"


class TestSessionManager:
    """Test SessionManager class."""
    
    def test_create_session(self):
        """Test creating a new session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(Path(tmpdir))
            session = manager.create_session(name="Test")
            
            assert session.name == "Test"
            assert manager.get_current_session() == session
            assert (Path(tmpdir) / f"{session.session_id}.json").exists()
    
    def test_load_session(self):
        """Test loading a session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(Path(tmpdir))
            created = manager.create_session()
            created.add_message("user", "Test")
            manager.save_current_session()
            
            manager2 = SessionManager(Path(tmpdir))
            loaded = manager2.load_session(created.session_id)
            
            assert loaded is not None
            assert len(loaded.messages) == 1
            assert loaded.messages[0].content == "Test"
    
    def test_list_sessions(self):
        """Test listing sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(Path(tmpdir))
            manager.create_session(name="Session 1")
            manager.create_session(name="Session 2")
            manager.create_session(name="Session 3")
            
            sessions = manager.list_sessions()
            assert len(sessions) == 3
            assert any(s["name"] == "Session 1" for s in sessions)
    
    def test_delete_session(self):
        """Test deleting a session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(Path(tmpdir))
            session = manager.create_session()
            session_id = session.session_id
            
            assert manager.delete_session(session_id)
            assert manager.load_session(session_id) is None
    
    def test_cleanup_old_sessions(self):
        """Test cleanup of old sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(Path(tmpdir))
            
            # Create old session manually
            old_session = Session()
            old_session.created_at = (datetime.utcnow() - timedelta(days=40)).isoformat() + "Z"
            
            session_file = Path(tmpdir) / f"{old_session.session_id}.json"
            with open(session_file, "w") as f:
                json.dump(old_session.to_dict(), f)
            
            # Create recent session
            manager.create_session(name="Recent")
            
            # Cleanup
            deleted = manager.cleanup_old_sessions(days=30)
            assert deleted == 1
            assert len(manager.list_sessions()) == 1


# System prompts tests
from lmapp.core.system_prompts import SystemPromptManager, get_prompt_manager


class TestSystemPromptManager:
    """Test SystemPromptManager class."""
    
    def test_default_prompts_exist(self):
        """Test that default prompts are available."""
        manager = SystemPromptManager()
        roles = manager.list_available_roles()
        
        assert "default" in roles
        assert "code" in roles
        assert "analysis" in roles
        assert "creative" in roles
    
    def test_get_default_prompt(self):
        """Test getting default prompts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SystemPromptManager(Path(tmpdir))
            prompt = manager.get_prompt("code")
            
            assert "programmer" in prompt.lower() or "code" in prompt.lower()
            assert len(prompt) > 50
    
    def test_set_custom_prompt(self):
        """Test setting a custom prompt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SystemPromptManager(Path(tmpdir))
            custom = "You are a helpful assistant for testing."
            
            manager.set_custom_prompt(custom)
            assert manager.get_custom_prompt() == custom
            assert manager.get_prompt("default") == custom
    
    def test_clear_custom_prompt(self):
        """Test clearing custom prompt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SystemPromptManager(Path(tmpdir))
            manager.set_custom_prompt("Custom")
            manager.clear_custom_prompt()
            
            assert manager.get_custom_prompt() is None
    
    def test_show_prompt_info(self):
        """Test getting prompt information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SystemPromptManager(Path(tmpdir))
            info = manager.show_prompt("code")
            
            assert info["role"] == "code"
            assert "prompt" in info
            assert "length" in info


# Enhanced error tests
from lmapp.utils.enhanced_errors import (
    HelpfulError, ErrorMessageLibrary, ErrorMessageFormatter,
    ErrorContextExtractor, ErrorSeverity
)


class TestHelpfulError:
    """Test HelpfulError class."""
    
    def test_helpful_error_creation(self):
        """Test creating a helpful error."""
        error = HelpfulError(
            title="Test Error",
            message="This is a test error",
            severity=ErrorSeverity.ERROR,
            suggestions=["Try this", "Or that"]
        )
        
        assert error.title == "Test Error"
        assert len(error.suggestions) == 2
    
    def test_format_for_display(self):
        """Test error formatting."""
        error = HelpfulError(
            title="Test",
            message="Test message",
            suggestions=["Suggestion 1"]
        )
        
        display = error.format_for_display(verbose=True)
        assert "Test" in display
        assert "Test message" in display
        assert "Suggestion 1" in display


class TestErrorMessageLibrary:
    """Test ErrorMessageLibrary."""
    
    def test_model_not_found_error(self):
        """Test model not found error."""
        error = ErrorMessageLibrary.model_not_found("llama2", "ollama")
        assert "llama2" in error.message
        assert "Download" in error.suggestions[0]
    
    def test_backend_not_running_error(self):
        """Test backend not running error."""
        error = ErrorMessageLibrary.backend_not_running("ollama")
        assert "ollama" in error.message.lower()
        assert any("start" in s.lower() for s in error.suggestions)
    
    def test_out_of_memory_error(self):
        """Test out of memory error."""
        error = ErrorMessageLibrary.out_of_memory()
        assert "memory" in error.message.lower()
        assert any("model" in s.lower() for s in error.suggestions)


class TestErrorContextExtractor:
    """Test ErrorContextExtractor."""
    
    def test_extract_model_name(self):
        """Test extracting model name from error."""
        error_text = "Model 'mistral' not found"
        model = ErrorContextExtractor.extract_model_name_from_error(error_text)
        assert model == "mistral"
    
    def test_extract_backend_name(self):
        """Test extracting backend name from error."""
        error_text = "Ollama connection refused"
        backend = ErrorContextExtractor.extract_backend_name_from_error(error_text)
        assert backend == "ollama"
    
    def test_suggest_common_fixes(self):
        """Test suggesting common fixes."""
        error_text = "Connection refused"
        fixes = ErrorContextExtractor.suggest_common_fixes(error_text)
        assert len(fixes) > 0
        assert any("backend" in fix.lower() for fix in fixes)


# Command aliases tests
from lmapp.utils.command_aliases import CommandAliasManager, get_alias_manager


class TestCommandAliasManager:
    """Test CommandAliasManager class."""
    
    def test_default_aliases_exist(self):
        """Test that default aliases are available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CommandAliasManager(Path(tmpdir))
            aliases = manager.get_all_aliases()
            
            assert "c" in aliases
            assert aliases["c"] == "chat"
            assert "m" in aliases
            assert aliases["m"] == "models"
    
    def test_resolve_command(self):
        """Test resolving a command alias."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CommandAliasManager(Path(tmpdir))
            resolved, was_alias = manager.resolve_command("c")
            
            assert resolved == "chat"
            assert was_alias is True
    
    def test_resolve_with_args(self):
        """Test resolving with arguments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CommandAliasManager(Path(tmpdir))
            resolved, was_alias = manager.resolve_with_args(["m", "list"])
            
            assert resolved[0] == "models"
            assert resolved[1] == "list"
            assert was_alias is True
    
    def test_add_custom_alias(self):
        """Test adding custom alias."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CommandAliasManager(Path(tmpdir))
            success = manager.add_alias("ch", "chat hello")
            
            assert success
            assert manager.get_alias("ch") == "chat hello"
    
    def test_remove_alias(self):
        """Test removing custom alias."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CommandAliasManager(Path(tmpdir))
            manager.add_alias("test", "testing")
            
            success = manager.remove_alias("test")
            assert success
            assert manager.get_alias("test") is None
    
    def test_list_aliases(self):
        """Test listing aliases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CommandAliasManager(Path(tmpdir))
            aliases = manager.list_aliases()
            
            assert len(aliases) > 0
            assert any(alias == "c" for alias, _ in aliases)
    
    def test_has_alias(self):
        """Test checking if alias exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CommandAliasManager(Path(tmpdir))
            
            assert manager.has_alias("c")
            assert not manager.has_alias("nonexistent")
    
    def test_get_similar_aliases(self):
        """Test finding similar aliases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CommandAliasManager(Path(tmpdir))
            similar = manager.get_similar_aliases("chat")
            
            assert len(similar) > 0


# Integration tests
class TestV023Integration:
    """Integration tests for v0.2.3 features."""
    
    def test_session_with_prompts(self):
        """Test session management with custom prompts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir) / "sessions"
            prompts_dir = Path(tmpdir) / "prompts"
            
            session_mgr = SessionManager(sessions_dir)
            prompt_mgr = SystemPromptManager(prompts_dir)
            
            # Create session
            session = session_mgr.create_session(name="Coding Session")
            
            # Get system prompt
            system_prompt = prompt_mgr.get_prompt("code")
            
            # Add context
            session.add_message("system", system_prompt)
            session.add_message("user", "How do I write a loop in Python?")
            
            assert len(session.messages) == 2
            session_mgr.save_current_session()
            
            # Reload
            loaded = session_mgr.load_session(session.session_id)
            assert len(loaded.messages) == 2
    
    def test_aliases_with_error_messages(self):
        """Test that aliases work with error handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            alias_mgr = CommandAliasManager(Path(tmpdir))
            
            # Alias for error handling
            error_cmd, was_alias = alias_mgr.resolve_command("doc")
            assert was_alias
            
            # Error message should work
            error = ErrorMessageLibrary.model_not_found("test", "ollama")
            assert error.title is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
