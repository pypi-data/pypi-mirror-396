"""
Session management for LMAPP - enables conversation context and history.

Stores conversation history for multi-turn interactions with context preservation.
Sessions are stored in ~/.lmapp/sessions/ with automatic management.

Features:
- Session creation and loading
- Message history with timestamps
- Context preservation across calls
- Automatic cleanup of old sessions
- Session metadata tracking
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
import uuid


class Message:
    """Represents a single message in a conversation."""
    
    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a Message.
        
        Args:
            role: "user", "assistant", or "system"
            content: Message text content
            timestamp: ISO format timestamp (auto-generated if None)
            metadata: Additional message metadata
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.utcnow().isoformat() + "Z"
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Message":
        """Create Message from dictionary."""
        return Message(
            role=data["role"],
            content=data["content"],
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {}),
        )


class Session:
    """Manages a single conversation session."""
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        name: Optional[str] = None,
        created_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a Session.
        
        Args:
            session_id: Unique session identifier (auto-generated if None)
            name: Human-readable session name
            created_at: Creation timestamp (auto-generated if None)
            metadata: Additional session metadata
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.name = name or f"Session {self.session_id[:8]}"
        self.created_at = created_at or datetime.utcnow().isoformat() + "Z"
        self.metadata = metadata or {}
        self.messages: List[Message] = []
        self.last_accessed = datetime.utcnow().isoformat() + "Z"
    
    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Add a message to the session."""
        message = Message(role, content, metadata=metadata)
        self.messages.append(message)
        self.last_accessed = datetime.utcnow().isoformat() + "Z"
        return message
    
    def get_context(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get conversation context for model.
        
        Returns last N messages in format suitable for LLM API.
        
        Args:
            limit: Maximum number of messages to return
        
        Returns:
            List of {role, content} dicts for LLM API
        """
        messages = self.messages[-limit:] if limit else self.messages
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    def get_summary(self) -> str:
        """Generate a summary of the conversation."""
        if not self.messages:
            return "Empty session"
        
        user_msgs = len([m for m in self.messages if m.role == "user"])
        assistant_msgs = len([m for m in self.messages if m.role == "assistant"])
        total = len(self.messages)
        
        first_msg = self.messages[0].content[:50] + "..." if self.messages else ""
        return f"{total} messages ({user_msgs} user, {assistant_msgs} assistant) - starts: '{first_msg}'"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for storage."""
        return {
            "session_id": self.session_id,
            "name": self.name,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "metadata": self.metadata,
            "messages": [msg.to_dict() for msg in self.messages],
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Session":
        """Create Session from dictionary."""
        session = Session(
            session_id=data["session_id"],
            name=data.get("name"),
            created_at=data.get("created_at"),
            metadata=data.get("metadata", {}),
        )
        session.messages = [Message.from_dict(msg) for msg in data.get("messages", [])]
        session.last_accessed = data.get("last_accessed", session.last_accessed)
        return session


class SessionManager:
    """Manages all LMAPP sessions."""
    
    def __init__(self, sessions_dir: Optional[Path] = None):
        """
        Initialize SessionManager.
        
        Args:
            sessions_dir: Directory to store sessions (default: ~/.lmapp/sessions/)
        """
        if sessions_dir is None:
            home = Path.home()
            sessions_dir = home / ".lmapp" / "sessions"
        
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._current_session: Optional[Session] = None
    
    def create_session(
        self,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """Create a new session."""
        session = Session(name=name, metadata=metadata)
        self._save_session(session)
        self._current_session = session
        return session
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session from disk."""
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, "r") as f:
                data = json.load(f)
            session = Session.from_dict(data)
            self._current_session = session
            return session
        except (json.JSONDecodeError, IOError):
            return None
    
    def get_current_session(self) -> Optional[Session]:
        """Get the current active session."""
        return self._current_session
    
    def set_current_session(self, session: Session) -> None:
        """Set the current active session."""
        self._current_session = session
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions."""
        sessions_info = []
        
        for session_file in sorted(self.sessions_dir.glob("*.json")):
            try:
                with open(session_file, "r") as f:
                    data = json.load(f)
                    session = Session.from_dict(data)
                    sessions_info.append({
                        "session_id": session.session_id,
                        "name": session.name,
                        "created_at": session.created_at,
                        "last_accessed": session.last_accessed,
                        "message_count": len(session.messages),
                        "summary": session.get_summary(),
                    })
            except (json.JSONDecodeError, IOError):
                continue
        
        return sorted(sessions_info, key=lambda x: x["last_accessed"], reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        session_file = self.sessions_dir / f"{session_id}.json"
        try:
            session_file.unlink()
            if self._current_session and self._current_session.session_id == session_id:
                self._current_session = None
            return True
        except FileNotFoundError:
            return False
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Delete sessions older than specified days. Returns count deleted."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = 0
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, "r") as f:
                    data = json.load(f)
                    created_at_str = data["created_at"].replace("Z", "")
                    created_at = datetime.fromisoformat(created_at_str)
                    
                    if created_at < cutoff:
                        self.delete_session(data["session_id"])
                        deleted += 1
            except (json.JSONDecodeError, IOError, ValueError):
                continue
        
        return deleted
    
    def _save_session(self, session: Session) -> None:
        """Save a session to disk."""
        session_file = self.sessions_dir / f"{session.session_id}.json"
        with open(session_file, "w") as f:
            json.dump(session.to_dict(), f, indent=2)
    
    def save_current_session(self) -> None:
        """Save the current session to disk."""
        if self._current_session:
            self._save_session(self._current_session)


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager(sessions_dir: Optional[Path] = None) -> SessionManager:
    """Get or create the global SessionManager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(sessions_dir)
    return _session_manager
