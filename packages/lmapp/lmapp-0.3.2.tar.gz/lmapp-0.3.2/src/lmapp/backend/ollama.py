#!/usr/bin/env python3
"""
Ollama Backend Implementation
Manages Ollama installation and interaction
"""
import shutil
import subprocess
import requests
import time
from typing import Optional, List

from .base import LLMBackend


class OllamaBackend(LLMBackend):
    """Ollama backend integration"""

    DEFAULT_API_URL = "http://localhost:11434"

    def __init__(self):
        super().__init__()
        self.api_url = self.DEFAULT_API_URL

    def backend_name(self) -> str:
        return "ollama"

    def backend_display_name(self) -> str:
        return "Ollama"

    def is_installed(self) -> bool:
        """Check if Ollama is installed"""
        return shutil.which("ollama") is not None

    def get_version(self) -> Optional[str]:
        """Get Ollama version"""
        if not self.is_installed():
            return None
        try:
            result = subprocess.run(
                ["ollama", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Parse version from output (e.g., "ollama version 0.1.14")
                return result.stdout.strip().split()[-1]
        except Exception:
            pass
        return None

    def is_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def install(self) -> bool:
        """
        Install Ollama automatically on Debian-based systems
        🤖 AUTOMATION: Fully automated installation
        """
        if self.is_installed():
            return True
        from rich.console import Console

        console = Console()
        console.print("[cyan]Installing Ollama...[/cyan]")
        try:
            # Use official Ollama install script
            console.print("[dim]Downloading Ollama installer...[/dim]")
            result = subprocess.run(
                ["curl", "-fsSL", "https://ollama.com/install.sh"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                console.print("[red]Failed to download installer[/red]")
                return False
            # Run installer
            console.print("[dim]Running installer...[/dim]")
            install_result = subprocess.run(
                ["sh"], input=result.stdout, capture_output=True, text=True, timeout=120
            )
            if install_result.returncode == 0:
                console.print("[green]✓ Ollama installed successfully[/green]")
                # Wait for service to start
                console.print("[dim]Waiting for service to start...[/dim]")
                time.sleep(5)
                return True
            else:
                console.print(
                    f"[red]Installation failed: {install_result.stderr}[/red]"
                )
                return False
        except Exception as e:
            console.print(f"[red]Installation error: {e}[/red]")
            return False

    def start(self) -> bool:
        """Start Ollama service"""
        if not self.is_installed():
            return False

        if self.is_running():
            return True

        try:
            # Try starting via systemctl first (standard Linux service)
            subprocess.run(
                ["systemctl", "--user", "start", "ollama"],
                capture_output=True,
                timeout=10,
            )
            time.sleep(2)
            if self.is_running():
                return True

            # Fallback: Start as background process
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            # Wait for startup
            for _ in range(10):
                if self.is_running():
                    return True
                time.sleep(1)
            return False
        except Exception:
            return False

    def stop(self) -> bool:
        """Stop Ollama service"""
        try:
            subprocess.run(
                ["systemctl", "--user", "stop", "ollama"],
                capture_output=True,
                timeout=10,
            )
            return True
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """List installed models"""
        if not self.is_running():
            return []

        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception:
            pass

        return []

    def download_model(self, model_name: str, callback=None) -> bool:
        """
        Download a model
        🤖 AUTOMATION: Automated with progress callback
        """
        if not self.is_running():
            self.start()
            time.sleep(3)

        try:
            # Use ollama pull command
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            # Stream output
            if callback:
                if process.stdout is not None:
                    for line in process.stdout:
                        callback(line.strip())
                else:
                    process.wait()
            else:
                process.wait()
            return process.returncode == 0
        except Exception:
            return False

    def chat(
        self, prompt: str, model: str = "", temperature: float = 0.7, *args, **kwargs
    ) -> str:
        """Send a chat prompt to Ollama"""
        if not self.is_running():
            return ""

        try:
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False, **kwargs},
                timeout=60,
            )

            if response.status_code == 200:
                return response.json().get("response", "")
        except Exception:
            pass

        return ""
