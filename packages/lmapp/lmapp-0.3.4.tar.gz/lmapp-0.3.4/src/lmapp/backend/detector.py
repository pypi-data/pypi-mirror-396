#!/usr/bin/env python3
"""
Backend Detector
Automatically detects available and suitable LLM backends
"""

from typing import List, Optional
from rich.console import Console
from rich.table import Table

from .base import LLMBackend, BackendStatus
from .ollama import OllamaBackend
from .llamafile import LlamafileBackend

console = Console()


class BackendDetector:
    """Detect and recommend LLM backends"""

    def __init__(self):
        self.backends: List[LLMBackend] = [
            OllamaBackend(),
            LlamafileBackend(),
        ]

    def get_best_backend(self) -> Optional[LLMBackend]:
        """Return the best available backend.

        Preference order:
        1. Any running backend
        2. First detected installed backend
        3. None if nothing is available
        """
        available = self.detect_all()
        if not available:
            return None

        # Prefer a running backend
        for b in available:
            if b.is_running():
                return b

        # Otherwise return the first available
        return available[0]

    def detect_all(self) -> List[LLMBackend]:
        """Detect all available backends"""
        available = []

        for backend in self.backends:
            if backend.is_installed():
                available.append(backend)

        return available

    def get_recommended(self, ram_gb: float) -> Optional[LLMBackend]:
        """Get recommended backend based on system specs"""
        # Check if Ollama is already installed
        for backend in self.backends:
            if isinstance(backend, OllamaBackend) and backend.is_installed():
                console.print("[green]✓ Ollama already installed (recommended)[/green]")
                return backend

        # If nothing installed, recommend based on RAM
        if ram_gb >= 8:
            console.print("[cyan]Recommending Ollama (best for 8GB+ RAM)[/cyan]")
            return OllamaBackend()
        else:
            console.print(
                "[cyan]Recommending llamafile (better for limited RAM)[/cyan]"
            )
            return LlamafileBackend()

    def show_status_table(self):
        """Display status of all backends"""
        table = Table(title="Backend Status")

        table.add_column("Backend", style="cyan")
        table.add_column("Status", style="yellow")
        table.add_column("Version", style="green")
        table.add_column("Running", style="blue")

        for backend in self.backends:
            info = backend.get_info()
            status_icon = "✓" if info.status != BackendStatus.NOT_INSTALLED else "✗"
            running_icon = "✓" if backend.is_running() else "✗"

            table.add_row(
                info.display_name,
                f"{status_icon} {info.status.value}",
                info.version or "N/A",
                running_icon,
            )

        console.print(table)

    def get_backend_by_name(self, name: str) -> Optional[LLMBackend]:
        """Get backend instance by name"""
        for backend in self.backends:
            if backend.backend_name() == name.lower():
                return backend
        return None
