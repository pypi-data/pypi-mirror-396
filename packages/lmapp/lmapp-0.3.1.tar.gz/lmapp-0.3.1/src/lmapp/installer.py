#!/usr/bin/env python3
"""
Installer Module
Manages automated setup of backends and models
"""

import platform
import shutil
from typing import Optional, List, Dict
from rich.console import Console
from rich.prompt import Confirm

from .backend.detector import BackendDetector
from .backend.ollama import OllamaBackend
from .backend.llamafile import LlamafileBackend

console = Console()


class Installer:
    """Automated installer for lmapp"""

    def __init__(self):
        self.detector = BackendDetector()

    def check_requirements(self) -> Dict[str, bool]:
        """Check system requirements"""
        requirements = {
            "os_supported": platform.system().lower() in ["linux", "darwin"],
            "curl_installed": shutil.which("curl") is not None,
            "disk_space": True,  # TODO: Implement disk check
        }
        return requirements

    def run_setup(self) -> bool:
        """Run the interactive setup wizard"""
        console.print("\n[bold cyan]🤖 lmapp Setup Wizard[/bold cyan]")
        console.print("No AI engine detected. Let's set one up for you.\n")

        # 1. Check Requirements
        reqs = self.check_requirements()
        if not reqs["os_supported"]:
            console.print(
                "[red]Error: Currently only Linux and macOS are supported.[/red]"
            )
            return False

        # 2. Choose Backend
        console.print("[bold]Choose an AI Engine:[/bold]")
        console.print(
            "1. [cyan]Ollama[/cyan] (Recommended) - Full-featured, runs as service"
        )
        console.print(
            "2. [cyan]llamafile[/cyan] - Portable, single-file, no installation"
        )

        choice = console.input("\nEnter choice [1/2]: ").strip()

        if choice == "1":
            return self._install_ollama()
        elif choice == "2":
            return self._install_llamafile()
        else:
            console.print("[red]Invalid choice.[/red]")
            return False

    def _install_ollama(self) -> bool:
        """Install Ollama backend"""
        backend = OllamaBackend()
        console.print("\n[bold]Installing Ollama...[/bold]")

        if backend.install():
            console.print("\n[bold]Downloading default model (llama2)...[/bold]")
            if backend.download_model("llama2", callback=lambda x: print(x, end="")):
                console.print(
                    "\n[green]✅ Setup complete! You can now run 'lmapp chat'[/green]"
                )
                return True
            else:
                console.print(
                    "[yellow]⚠ Ollama installed, but model download failed.[/yellow]"
                )
                return True
        return False

    def _install_llamafile(self) -> bool:
        """Install llamafile backend"""
        backend = LlamafileBackend()
        console.print("\n[bold]Setting up llamafile...[/bold]")

        if backend.install():
            console.print(
                "\n[green]✅ Setup complete! You can now run 'lmapp chat'[/green]"
            )
            return True
        return False
