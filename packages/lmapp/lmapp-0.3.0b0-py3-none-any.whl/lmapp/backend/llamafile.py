#!/usr/bin/env python3
"""
llamafile Backend Implementation
Manages llamafile download and execution
"""

import subprocess
import requests
from typing import Optional, List
from pathlib import Path

from .base import LLMBackend


class LlamafileBackend(LLMBackend):
    """llamafile backend integration"""

    LLAMAFILE_DIR = Path.home() / ".lmapp" / "llamafiles"

    def __init__(self):
        super().__init__()
        self.LLAMAFILE_DIR.mkdir(parents=True, exist_ok=True)
        self.current_process = None

    def backend_name(self) -> str:
        return "llamafile"

    def backend_display_name(self) -> str:
        return "llamafile"

    def is_installed(self) -> bool:
        """Check if any llamafile exists"""
        if not self.LLAMAFILE_DIR.exists():
            return False

        # Check for any .llamafile files
        llamafiles = list(self.LLAMAFILE_DIR.glob("*.llamafile"))
        return len(llamafiles) > 0

    def get_version(self) -> Optional[str]:
        """Get llamafile version (if available)"""
        # llamafile doesn't have a traditional version command
        if self.is_installed():
            return "latest"
        return None

    def is_running(self) -> bool:
        """Check if llamafile is running"""
        if self.current_process:
            return self.current_process.poll() is None

        # Check if port 8080 is in use (default llamafile port)
        try:
            response = requests.get("http://localhost:8080/health", timeout=1)
            return response.status_code == 200
        except Exception:
            return False

    def download_model(self, model_name: str, callback=None) -> bool:
        """
        Download a model
        For llamafile, this currently only supports the default model (TinyLlama)
        or models we have URLs for.
        """
        # TODO: Implement a proper model registry for llamafile
        if "tinyllama" in model_name.lower():
            return self.install()

        # If it's a URL, try to download it
        if model_name.startswith("http"):
            # TODO: Implement URL download
            pass

        return False

    def install(self) -> bool:
        """
        Download a llamafile model
        🤖 AUTOMATION: Downloads appropriate model for system
        """
        from rich.console import Console

        console = Console()

        # For now, we'll download TinyLlama as a small, fast model
        # 🔖 BOOKMARK - In future, select model based on RAM
        model_url = (
            "https://huggingface.co/Mozilla/TinyLlama-1.1B-Chat-v1.0-llamafile/"
            "resolve/main/TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile"
        )
        model_name = "tinyllama.llamafile"
        model_path = self.LLAMAFILE_DIR / model_name

        if model_path.exists():
            console.print("[green]✓ llamafile already downloaded[/green]")
            return True

        console.print(f"[cyan]Downloading {model_name}...[/cyan]")
        console.print("[dim]This may take a few minutes...[/dim]")

        # Check for GPU support
        try:
            # Simple check for nvidia-smi
            subprocess.run(
                ["nvidia-smi"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            console.print(
                "[green]✓ GPU detected (llamafile will use it automatically)[/green]"
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print("[yellow]⚠ No GPU detected (running on CPU)[/yellow]")

        try:
            # Download with progress
            response = requests.get(model_url, stream=True, timeout=300)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(model_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Simple progress indicator
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            if int(percent) % 10 == 0:  # Show every 10%
                                console.print(f"[dim]Downloaded: {percent:.0f}%[/dim]")

            # Make executable
            model_path.chmod(0o755)

            console.print("[green]✓ llamafile downloaded successfully[/green]")
            return True

        except Exception as e:
            console.print(f"[red]Download failed: {e}[/red]")
            if model_path.exists():
                model_path.unlink()
            return False

    def start(self) -> bool:
        """Start llamafile server"""
        if self.is_running():
            return True

        # Find first llamafile
        llamafiles = list(self.LLAMAFILE_DIR.glob("*.llamafile"))
        if not llamafiles:
            return False

        llamafile_path = llamafiles[0]

        try:
            # Start llamafile in server mode
            # Use --nobrowser to prevent opening a browser tab
            self.current_process = subprocess.Popen(
                [str(llamafile_path), "--server", "--port", "8080", "--nobrowser"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

            # Wait a bit for startup
            import time

            for _ in range(10):
                if self.is_running():
                    return True
                time.sleep(1)

            return False
        except Exception:
            return False

    def stop(self) -> bool:
        """Stop llamafile server"""
        if self.current_process:
            self.current_process.terminate()
            self.current_process.wait(timeout=5)
            self.current_process = None
            return True
        return False

    def list_models(self) -> List[str]:
        """List available llamafiles"""
        llamafiles = list(self.LLAMAFILE_DIR.glob("*.llamafile"))
        return [f.stem for f in llamafiles]

    def download_model(self, model_name: str, callback=None) -> bool:
        """Download a specific model"""
        # 🔖 BOOKMARK - Implement model-specific downloads
        # For now, just use install() which downloads TinyLlama
        return self.install()

    def chat(
        self, prompt: str, model: str = "", temperature: float = 0.7, *args, **kwargs
    ) -> str:
        """Send a chat prompt to llamafile"""
        if not self.is_running():
            return ""

        try:
            response = requests.post(
                "http://localhost:8080/completion",
                json={"prompt": prompt, "stream": False, **kwargs},
                timeout=60,
            )

            if response.status_code == 200:
                return response.json().get("content", "")
        except Exception:
            pass

        return ""
