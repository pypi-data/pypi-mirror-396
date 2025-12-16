#!/usr/bin/env python3
"""
Base Backend Classes
Defines abstract interface for all LLM backends
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List, Any
from dataclasses import dataclass


class BackendStatus(Enum):
    """Backend operational status"""

    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class BackendInfo:
    """Information about a backend"""

    name: str
    display_name: str
    version: Optional[str] = None
    status: BackendStatus = BackendStatus.NOT_INSTALLED
    executable_path: Optional[str] = None
    api_url: Optional[str] = None

    # 🔖 BOOKMARK - Add capabilities for future projects
    supports_web_access: bool = False  # PROJECT 2
    supports_file_operations: bool = False  # PROJECT 3
    supports_code_execution: bool = False  # PROJECT 3

    # Provide a minimal mapping-like interface so callers can use `in` and
    # index access in tests and templates (e.g., `"name" in info`).
    def __contains__(self, key: str) -> bool:  # pragma: no cover - trivial
        return hasattr(self, key)

    def __getitem__(self, key: str):  # pragma: no cover - trivial
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)


class LLMBackend(ABC):
    """Abstract base class for LLM backends"""

    def __init__(self):
        self.info = BackendInfo(
            name=self.backend_name(), display_name=self.backend_display_name()
        )

    @abstractmethod
    def backend_name(self) -> str:
        """Return backend identifier (e.g., 'ollama')"""
        pass

    @abstractmethod
    def backend_display_name(self) -> str:
        """Return human-readable backend name"""
        pass

    @abstractmethod
    def is_installed(self) -> bool:
        """Check if backend is installed"""
        pass

    @abstractmethod
    def get_version(self) -> Optional[str]:
        """Get backend version if installed"""
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """Check if backend service is running"""
        pass

    @abstractmethod
    def install(self) -> bool:
        """Install the backend (automated)"""
        pass

    @abstractmethod
    def start(self) -> bool:
        """Start the backend service"""
        pass

    @abstractmethod
    def stop(self) -> bool:
        """Stop the backend service"""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models"""
        pass

    @abstractmethod
    def download_model(self, model_name: str, callback=None) -> bool:
        """Download a model with optional progress callback"""
        pass

    @abstractmethod
    def chat(
        self,
        prompt: str,
        model: str = "",
        temperature: float = 0.7,
        *args,
        **kwargs: Any,
    ) -> str:
        """Send a chat prompt and get response.

        Signature uses `prompt` first to match callers across the codebase
        (e.g. `backend.chat(prompt=..., model=..., temperature=...)`).
        Implementations should accept `prompt` as the first argument and
        support `model` as a keyword argument.
        """
        raise NotImplementedError()

    def get_status(self) -> BackendStatus:
        """Get current backend status"""
        if not self.is_installed():
            return BackendStatus.NOT_INSTALLED
        elif self.is_running():
            return BackendStatus.RUNNING
        else:
            return BackendStatus.STOPPED

    def get_info(self) -> BackendInfo:
        """Get backend information"""
        self.info.status = self.get_status()
        self.info.version = self.get_version()
        return self.info
