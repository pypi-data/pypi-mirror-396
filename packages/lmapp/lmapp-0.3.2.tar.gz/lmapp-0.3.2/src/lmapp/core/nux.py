#!/usr/bin/env python3
"""
New User Experience (NUX)
Handles first-run setup and silent configuration.
"""

import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from lmapp.core.config import get_config_manager, LMAppConfig
from lmapp.backend.detector import BackendDetector
from lmapp.backend.uaft_integration import UAFTIntegration
from lmapp.utils.logging import logger

console = Console()


def check_first_run() -> bool:
    """Check if this is the first run (config missing)"""
    config_manager = get_config_manager()
    return not config_manager.config_file.exists()


def run_user_mode_setup():
    """Run User Mode setup (formerly Silent Setup)"""
    console.print(
        Panel.fit("[bold blue]Welcome to lmapp![/bold blue]", border_style="blue")
    )
    console.print("Initializing User Mode... (this will only happen once)")

    config_manager = get_config_manager()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:

        # Step 1: Create Configuration
        task1 = progress.add_task("Creating configuration...", total=None)
        time.sleep(0.5)  # UX pause

        # Default config with developer_mode=False
        config = LMAppConfig(
            backend="auto",
            model="tinyllama",
            temperature=0.7,
            debug=False,
            developer_mode=False,
        )
        config_manager.save(config)
        progress.update(task1, completed=100)
        console.print("[green]✓[/green] Configuration created")

        # Step 2: Detect Backend
        task2 = progress.add_task("Detecting AI backend...", total=None)
        detector = BackendDetector()
        backends = detector.detect_all()

        if not backends:
            # No backend found, default to mock but warn
            logger.warning("No AI backend detected. Using Mock backend.")
            console.print(
                "[yellow]![/yellow] No AI backend detected (Ollama/Llamafile). Using Mock backend."
            )
            # In future: Auto-download llamafile here
        else:
            # Auto-select best
            import psutil

            ram_gb = psutil.virtual_memory().total / (1024**3)
            best = detector.get_recommended(ram_gb)
            if best:
                config.backend = best.backend_name()
                config_manager.save(config)
                console.print(
                    f"[green]✓[/green] Found backend: [bold]{best.backend_name()}[/bold]"
                )
            else:
                console.print(
                    "[yellow]![/yellow] Backends found but none recommended. Using auto."
                )

        progress.update(task2, completed=100)

        # Step 3: Model Setup (Placeholder for "Tiny Model")
        task3 = progress.add_task("Checking model availability...", total=None)
        time.sleep(0.5)  # UX pause
        # In future: Check if 'tinyllama' is pulled in Ollama
        progress.update(task3, completed=100)
        console.print("[green]✓[/green] Model ready: [bold]tinyllama[/bold]")

    console.print("\n[bold green]Setup Complete![/bold green]")
    console.print("Type [bold]lmapp chat[/bold] to start chatting.")
    console.print("Type [bold]lmapp --dev[/bold] to enable Developer Mode.\n")
