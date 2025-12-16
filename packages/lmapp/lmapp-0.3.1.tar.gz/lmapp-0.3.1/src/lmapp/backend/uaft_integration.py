#!/usr/bin/env python3
"""
UAFT (Universal Automation Framework Tool) Integration

Provides optional download and installation of uaft as a companion tool.
UAFT enhances lmapp with automation capabilities:
  - Project initialization
  - Automated testing and cleanup
  - Code fixing workflows
  - Git integration
"""

import subprocess
import sys
from typing import Optional
from pathlib import Path
import json

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import inquirer

console = Console()


class UAFTIntegration:
    """
    Manages UAFT installation and integration with lmapp
    """

    def __init__(self):
        self.uaft_installed = self._check_uaft_installed()
        self.uaft_config = self._load_uaft_config()

    def _check_uaft_installed(self) -> bool:
        """Check if UAFT is installed and available"""
        try:
            result = subprocess.run(
                ["uaft", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def _load_uaft_config(self) -> dict:
        """Load uaft configuration if available"""
        config_path = Path.home() / ".lmapp" / "uaft_config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"enabled": False, "version": None}

    def prompt_installation(self) -> bool:
        """
        Prompt user to install UAFT as optional companion tool.
        Returns True if user wants to install, False otherwise.
        """
        console.print("\n[bold cyan]Optional: Universal Automation Framework Tool[/bold cyan]")
        console.print("""
UAFT is a recommended companion tool that enhances lmapp with:
  ✨ Project automation and initialization
  🧪 Automated testing workflows
  🔧 Code fixing and cleanup
  📝 Git and GitHub integration
  🔌 Plugin system for extensibility

UAFT makes it easy to automate repetitive tasks in your projects.
        """)

        if self.uaft_installed:
            console.print("[green]✓ UAFT is already installed![/green]")
            enable = inquirer.confirm(
                message="Enable UAFT integration with lmapp?",
                default=True
            )
            return enable

        questions = [
            inquirer.Confirm(
                "install_uaft",
                message="Would you like to install UAFT now?",
                default=True
            )
        ]

        answers = inquirer.prompt(questions)
        return answers.get("install_uaft", False)

    def install_uaft(self) -> bool:
        """
        Install UAFT from PyPI.
        Returns True if successful, False otherwise.
        """
        console.print("\n[bold]Installing UAFT...[/bold]")

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                task = progress.add_task("Downloading and installing UAFT...", total=None)

                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "uaft", "-q"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                progress.stop()

                if result.returncode == 0:
                    console.print("[green]✓ UAFT installed successfully![/green]")
                    self._save_uaft_config(enabled=True)
                    self._show_uaft_quickstart()
                    return True
                else:
                    console.print(f"[red]✗ Installation failed: {result.stderr}[/red]")
                    return False

        except subprocess.TimeoutExpired:
            console.print("[red]✗ Installation timed out[/red]")
            return False
        except Exception as e:
            console.print(f"[red]✗ Installation error: {e}[/red]")
            return False

    def _save_uaft_config(self, enabled: bool) -> None:
        """Save UAFT configuration"""
        config_dir = Path.home() / ".lmapp"
        config_dir.mkdir(parents=True, exist_ok=True)

        config = {
            "enabled": enabled,
            "version": "0.2.1"  # Current UAFT version
        }

        config_path = config_dir / "uaft_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    def _show_uaft_quickstart(self) -> None:
        """Show UAFT quickstart information"""
        console.print("\n[bold cyan]UAFT Quickstart[/bold cyan]")
        console.print("""
Get started with UAFT:

  1. Initialize a project:
     $ uaft init

  2. View automation configuration:
     $ cat uaft.json

  3. Run available automations:
     $ uaft --help

Learn more: https://github.com/nabaznyl/uaft
        """)

    def get_integration_status(self) -> dict:
        """Get current UAFT integration status"""
        return {
            "installed": self.uaft_installed,
            "enabled": self.uaft_config.get("enabled", False),
            "version": self.uaft_config.get("version")
        }

