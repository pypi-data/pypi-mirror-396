#!/usr/bin/env python3
"""
Chat Session Management
Handles single conversation session with an LLM backend
"""

from typing import List, Optional, Dict
from datetime import datetime
from lmapp.backend.base import LLMBackend
from lmapp.utils.logging import logger
from lmapp.core.cache import ResponseCache


class ChatMessage:
    """Represents a single message in the conversation"""

    def __init__(self, role: str, content: str):
        """
        Initialize a chat message

        Args:
            role: "user" or "assistant"
            content: Message text
        """
        self.role = role
        self.content = content
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }


class ChatSession:
    """Manages a single conversation session"""

    def __init__(self, backend: LLMBackend, model: str = "tinyllama"):
        """
        Initialize a chat session

        Args:
            backend: LLMBackend instance to use for chat
            model: Model name to use (default: tinyllama)

        Raises:
            ValueError: If backend is not running
        """
        logger.debug(
            f"Creating ChatSession with backend={backend.backend_name()}, model={model}"
        )

        if not backend.is_running():
            logger.error(f"Backend '{backend.backend_display_name()}' is not running")
            raise ValueError(
                f"❌ Backend '{backend.backend_display_name()}' is not running.\n"
                "Please run 'lmapp install' first, or start the backend manually."
            )

        self.backend = backend
        self.model = model
        self.history: List[ChatMessage] = []
        self.created_at = datetime.now()
        self.cache = ResponseCache()
        logger.debug("ChatSession initialized successfully")

    def send_prompt(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Send a prompt and get a response

        Args:
            prompt: User prompt
            temperature: LLM temperature (0.0-1.0)

        Returns:
            Response text

        Raises:
            ValueError: If prompt is empty
            RuntimeError: If backend fails to respond
        """
        logger.debug(
            f"send_prompt: model={self.model}, temp={temperature}, prompt_len={len(prompt)}"
        )

        if not prompt or not prompt.strip():
            logger.warning("Empty prompt attempted")
            raise ValueError("❌ Prompt cannot be empty")
        
        # Check cache for existing response
        cached_response = self.cache.get(
            prompt,
            self.model,
            self.backend.backend_name(),
            temperature
        )
        if cached_response:
            logger.debug(f"Cache hit for prompt (model={self.model}, temperature={temperature})")
            # Add to history for consistency
            self.history.append(ChatMessage("user", prompt))
            self.history.append(ChatMessage("assistant", cached_response))
            return cached_response

        # Add user message to history
        self.history.append(ChatMessage("user", prompt))

        try:
            # Get response from backend
            logger.debug("Requesting response from backend")
            response = self.backend.chat(
                prompt=prompt, model=self.model, temperature=temperature
            )

            if not response:
                logger.error("Backend returned empty response")
                raise RuntimeError("Backend returned empty response")

            # Add assistant message to history
            self.history.append(ChatMessage("assistant", response))
            
            # Cache the response
            self.cache.set(
                prompt,
                response,
                self.model,
                self.backend.backend_name(),
                temperature
            )
            logger.debug(f"Response received: {len(response)} chars, cached for future use")

            return response

        except Exception as e:
            # Remove the user message if we failed to get response
            self.history.pop()
            logger.error(f"Backend error: {str(e)}", exc_info=True)

            # Provide actionable error message
            error_msg = str(e)
            if "connection" in error_msg.lower() or "refused" in error_msg.lower():
                raise RuntimeError(
                    f"❌ Cannot connect to {self.backend.backend_display_name()}.\n"
                    "Try restarting: lmapp install"
                ) from e
            elif "model" in error_msg.lower():
                models = self.backend.list_models()
                raise RuntimeError(
                    f"❌ Model '{self.model}' not found.\n"
                    f"Available models: {', '.join(models)}"
                ) from e
            else:
                raise RuntimeError(f"❌ Backend error: {error_msg}") from e

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history

        Args:
            limit: Maximum number of messages to return (None = all)

        Returns:
            List of messages as dictionaries
        """
        messages = [msg.to_dict() for msg in self.history]

        if limit:
            messages = messages[-limit:]

        return messages

    def get_history_text(self, limit: Optional[int] = None) -> str:
        """
        Get conversation history as formatted text

        Args:
            limit: Maximum number of messages to return (None = all)

        Returns:
            Formatted conversation text
        """
        messages = self.history
        if limit:
            messages = messages[-limit:]

        if not messages:
            return "(No messages yet)"

        text = []
        for msg in messages:
            timestamp = msg.timestamp.strftime("%H:%M:%S")
            role_label = "You" if msg.role == "user" else "AI"
            text.append(f"[{timestamp}] {role_label}: {msg.content}")

        return "\n".join(text)

    def clear_history(self) -> int:
        """
        Clear conversation history

        Returns:
            Number of messages cleared
        """
        count = len(self.history)
        self.history.clear()
        return count

    def get_stats(self) -> Dict:
        """
        Get session statistics

        Returns:
            Dictionary with session stats
        """
        return {
            "backend": self.backend.backend_name(),
            "model": self.model,
            "messages": len(self.history),
            "user_messages": sum(1 for m in self.history if m.role == "user"),
            "assistant_messages": sum(1 for m in self.history if m.role == "assistant"),
            "created_at": self.created_at.isoformat(),
            "duration_seconds": (datetime.now() - self.created_at).total_seconds(),
        }
