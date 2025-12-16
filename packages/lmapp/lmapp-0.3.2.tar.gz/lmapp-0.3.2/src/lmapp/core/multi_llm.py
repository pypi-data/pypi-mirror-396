#!/usr/bin/env python3
"""
Multi-LLM Chat Session
Allows multiple backends to run in conjunction for cross-referenced answers
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from lmapp.backend.base import LLMBackend
from lmapp.utils.logging import logger


@dataclass
class LLMResponse:
    """Response from a single LLM backend"""
    backend_name: str
    model: str
    response: str
    timestamp: datetime


class ChatMessage:
    """Represents a single message in the conversation"""

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }


class MultiLLMSession:
    """
    Manages a chat session with multiple LLM backends.
    Useful for cross-referencing answers and comparing responses.
    """

    def __init__(self, backends: List[Tuple[LLMBackend, str]]):
        """
        Initialize multi-LLM session

        Args:
            backends: List of (LLMBackend, model_name) tuples

        Raises:
            ValueError: If no backends or not all running
        """
        if not backends:
            raise ValueError("At least one backend required")

        # Verify all backends are running
        for backend, model in backends:
            if not backend.is_running():
                raise ValueError(
                    f"Backend '{backend.backend_display_name()}' is not running"
                )

        self.backends = backends
        self.history: List[ChatMessage] = []
        self.responses: List[LLMResponse] = []
        self.created_at = datetime.now()

        logger.debug(
            f"MultiLLMSession initialized with {len(backends)} backends: "
            f"{[b.backend_name() for b, _ in backends]}"
        )

    def send_prompt(
        self, prompt: str, temperature: float = 0.7, consensus_mode: bool = False
    ) -> Dict[str, LLMResponse]:
        """
        Send a prompt to all backends and collect responses

        Args:
            prompt: User prompt
            temperature: LLM temperature (0.0-1.0)
            consensus_mode: If True, combine responses into consensus

        Returns:
            Dictionary mapping backend names to LLMResponse objects

        Raises:
            ValueError: If prompt is empty
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        # Add user message to history
        self.history.append(ChatMessage("user", prompt))

        responses = {}

        # Query each backend
        for backend, model in self.backends:
            try:
                logger.debug(
                    f"Querying {backend.backend_name()} with model {model}"
                )
                response_text = backend.chat(
                    prompt=prompt, model=model, temperature=temperature
                )

                response = LLMResponse(
                    backend_name=backend.backend_name(),
                    model=model,
                    response=response_text,
                    timestamp=datetime.now(),
                )

                responses[backend.backend_name()] = response
                self.responses.append(response)

            except Exception as e:
                logger.error(
                    f"Error querying {backend.backend_name()}: {e}"
                )
                responses[backend.backend_name()] = LLMResponse(
                    backend_name=backend.backend_name(),
                    model=model,
                    response=f"Error: {str(e)}",
                    timestamp=datetime.now(),
                )

        # Add assistant responses to history (synthesized)
        if consensus_mode and len(responses) > 1:
            synthesized = self._synthesize_responses(responses)
            self.history.append(ChatMessage("assistant", synthesized))

        return responses

    def _synthesize_responses(self, responses: Dict[str, LLMResponse]) -> str:
        """
        Synthesize multiple responses into a consensus answer

        Args:
            responses: Dict of backend responses

        Returns:
            Synthesized answer combining insights from all backends
        """
        if not responses:
            return "No responses received"

        synthesis = "**Consensus from Multiple Models:**\n\n"

        for backend_name, response in responses.items():
            synthesis += f"🤖 {backend_name.upper()}:\n{response.response}\n\n"

        return synthesis

    def get_comparative_view(self) -> Dict:
        """
        Get a comparative view of all recent responses

        Returns:
            Dictionary with formatted comparison
        """
        if not self.responses:
            return {"status": "No responses yet"}

        return {
            "total_queries": len(set(r.timestamp for r in self.responses)),
            "backends_used": list(set(r.backend_name for r in self.responses)),
            "latest_responses": [
                {
                    "backend": r.backend_name,
                    "model": r.model,
                    "response": r.response[:100] + "...",
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in self.responses[-len(self.backends) :]
            ],
        }

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get chat history"""
        messages = self.history[-limit:] if limit else self.history
        return [m.to_dict() for m in messages]

    def get_stats(self) -> Dict:
        """Get session statistics"""
        return {
            "created_at": self.created_at.isoformat(),
            "total_messages": len(self.history),
            "total_responses_collected": len(self.responses),
            "backends": len(self.backends),
            "uptime_seconds": (datetime.now() - self.created_at).total_seconds(),
        }
