#!/usr/bin/env python3
"""
Backend Installer
Automated installation workflow for LLM backends
"""

from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import inquirer

from .base import LLMBackend
from .detector import BackendDetector
from ..utils.system_check import SystemCheck

console = Console()


class BackendInstaller:
    """
    Automated backend installation
    🤖 AUTOMATION: User picks from 3 options, rest is automatic
    """

    def __init__(self):
        self.detector = BackendDetector()
        self.system_check = SystemCheck()

    def run_installation_wizard(self) -> Optional[LLMBackend]:
        """
        Run interactive installation wizard
        Returns: Installed and running backend, or None
        """
        console.print("\n[bold cyan]Backend Installation Wizard[/bold cyan]\n")

        # Step 1: Check system
        console.print("[bold]Step 1: System Check[/bold]")

        # Step 2: Detect existing backends
        console.print("\n[bold]Step 2: Detecting Backends[/bold]")
        available = self.detector.detect_all()

        if available:
            console.print(f"[green]Found {len(available)} installed backend(s)[/green]")
            for backend in available:
                info = backend.get_info()
                console.print(f"  • {info.display_name} {info.version}")

            # Ask if user wants to use existing
            use_existing = inquirer.confirm(
                message="Use existing backend?", default=True
            )

            if use_existing:
                # Ensure it's running
                backend = available[0]
                if not backend.is_running():
                    console.print("[dim]Starting backend...[/dim]")
                    backend.start()
                return backend

        # Step 3: Recommend backend
        console.print("\n[bold]Step 3: Backend Selection[/bold]")

        # Present options (A/B/C menu)
        choices = [
            ("A) Ollama (Recommended for 8GB+ RAM)", "ollama"),
            ("B) llamafile (Better for limited resources)", "llamafile"),
            ("C) Cancel installation", "cancel"),
        ]

        questions = [
            inquirer.List(
                "backend",
                message="Choose a backend to install",
                choices=choices,
            ),
        ]

        answers = inquirer.prompt(questions)
        if not answers or answers["backend"] == "cancel":
            console.print("[yellow]Installation cancelled[/yellow]")
            return None

        backend_name = answers["backend"]
        backend = self.detector.get_backend_by_name(backend_name)

        if not backend:
            console.print("[red]Invalid backend selection[/red]")
            return None

        # Step 4: Install backend
        console.print(
            f"\n[bold]Step 4: Installing {backend.backend_display_name()}[/bold]"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Installing {backend.backend_display_name()}...", total=None
            )

            success = backend.install()

            if success:
                progress.update(
                    task, description=f"✓ {backend.backend_display_name()} installed"
                )
            else:
                progress.update(task, description="✗ Installation failed")
                console.print("[red]Installation failed. Please check logs.[/red]")
                return None

        # Step 5: Start backend
        console.print(
            f"\n[bold]Step 5: Starting {backend.backend_display_name()}[/bold]"
        )

        if not backend.is_running():
            console.print("[dim]Starting service...[/dim]")
            if not backend.start():
                console.print(
                    "[yellow]⚠ Could not start service automatically[/yellow]"
                )
                console.print("[dim]It may start on first use[/dim]")

        # Verify
        if backend.is_installed():
            console.print(
                f"\n[green]✓ {backend.backend_display_name()} is ready![/green]"
            )
            return backend
        else:
            console.print("\n[red]✗ Installation verification failed[/red]")
            return None

    def install_model(self, backend: LLMBackend, ram_gb: float) -> bool:
        """
        Install appropriate model for the backend
        🤖 AUTOMATION: Auto-selects model based on RAM
        """
        console.print("\n[bold cyan]Model Installation[/bold cyan]\n")

        # Check existing models
        existing = backend.list_models()
        if existing:
            console.print(f"[green]Found {len(existing)} existing model(s):[/green]")
            for model in existing:
                console.print(f"  • {model}")

            use_existing = inquirer.confirm(message="Use existing model?", default=True)

            if use_existing:
                return True

        # Recommend model based on RAM
        recommended_model = self._recommend_model(ram_gb)

        console.print(f"[cyan]Recommended model: {recommended_model}[/cyan]")
        console.print(f"[dim]Based on your system RAM: {ram_gb:.1f}GB[/dim]\n")

        # Offer alternatives
        models = self._get_model_options(ram_gb)

        questions = [
            inquirer.List(
                "model",
                message="Choose a model to download",
                choices=[(f"{m['label']}", m["name"]) for m in models]
                + [("Cancel", "cancel")],
            ),
        ]

        answers = inquirer.prompt(questions)
        if not answers or answers["model"] == "cancel":
            return False

        model_name = answers["model"]

        # Download model
        console.print(f"\n[bold]Downloading {model_name}...[/bold]")
        console.print("[dim]This may take several minutes...[/dim]\n")

        def progress_callback(line: str):
            """Display download progress"""
            if line:
                console.print(f"[dim]{line}[/dim]")

        success = backend.download_model(model_name, callback=progress_callback)

        if success:
            console.print(
                f"\n[green]✓ Model {model_name} downloaded successfully[/green]"
            )
            return True
        else:
            console.print("\n[red]✗ Model download failed[/red]")
            return False

    def _get_system_ram(self) -> float:
        """Get system RAM in GB"""
        import psutil

        ram_bytes = psutil.virtual_memory().total
        return ram_bytes / (1024**3)

    def _recommend_model(self, ram_gb: float) -> str:
        """Recommend model based on RAM"""
        if ram_gb < 6:
            return "tinyllama"
        elif ram_gb < 12:
            return "llama2:7b"
        else:
            return "llama2:13b"

    def _get_model_options(self, ram_gb: float) -> list:
        """Get model options based on RAM"""
        models = []

        # Always offer tiny model
        models.append(
            {
                "name": "tinyllama",
                "label": "A) TinyLlama 1.1B (Fast, ~600MB) - Recommended for 4GB RAM",
                "size_gb": 0.6,
            }
        )

        if ram_gb >= 6:
            models.append(
                {
                    "name": "llama2:7b",
                    "label": "B) Llama 2 7B (Balanced, ~4GB) - Recommended for 8GB RAM",
                    "size_gb": 4,
                }
            )

        if ram_gb >= 12:
            models.append(
                {
                    "name": "llama2:13b",
                    "label": "C) Llama 2 13B (Powerful, ~7GB) - Recommended for 16GB RAM",
                    "size_gb": 7,
                }
            )

        return models
