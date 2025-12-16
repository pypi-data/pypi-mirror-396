#!/usr/bin/env python3
"""
Terminal Mode for Advanced CLI Operations
Allows users to run lmapp commands and shell commands interactively
"""

import subprocess
import sys
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.syntax import Syntax

console = Console()


class CLITerminalMode:
    """Interactive CLI terminal for advanced commands"""

    def __init__(self):
        self.history = []
        self.running = False

    def start(self) -> None:
        """Start the interactive terminal"""
        self.running = True

        console.print(
            "\n[cyan bold]🖥️  lmapp Advanced CLI Terminal[/cyan bold]\n"
        )
        console.print(
            "[dim]Type 'help' for available commands or shell commands directly[/dim]"
        )
        console.print("[dim]Type 'exit' or 'quit' to return to main menu[/dim]\n")

        while self.running:
            try:
                command = Prompt.ask("[lmapp]").strip()

                if not command:
                    continue

                self.handle_command(command)

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted[/yellow]")
                break
            except EOFError:
                break

        self.running = False

    def handle_command(self, command: str) -> None:
        """
        Handle a command - either lmapp or shell

        Args:
            command: The command to execute
        """
        if command.lower() in ["exit", "quit"]:
            self.running = False
            return

        if command.lower() == "help":
            self.show_help()
            return

        if command.lower() == "history":
            self.show_history()
            return

        if command.lower() == "clear":
            console.clear()
            return

        # Check if it's an lmapp command
        if command.startswith("lmapp "):
            self.run_lmapp_command(command)
        else:
            self.run_shell_command(command)

    def run_lmapp_command(self, command: str) -> None:
        """Run an lmapp command"""
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.history.append(command)

            if result.stdout:
                console.print(result.stdout)
            if result.stderr:
                console.print(f"[red]{result.stderr}[/red]")

        except subprocess.TimeoutExpired:
            console.print("[red]✗ Command timed out[/red]")
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")

    def run_shell_command(self, command: str) -> None:
        """Run a shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.history.append(command)

            if result.stdout:
                console.print(result.stdout)
            if result.stderr:
                console.print(f"[yellow]{result.stderr}[/yellow]")

        except subprocess.TimeoutExpired:
            console.print("[red]✗ Command timed out[/red]")
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")

    def show_help(self) -> None:
        """Display help information"""
        help_text = """
[cyan bold]Available Commands:[/cyan bold]

[yellow]lmapp Commands:[/yellow]
  lmapp chat              Start a chat session
  lmapp status            Show backend status
  lmapp config show       Display current configuration
  lmapp config set <k> <v>  Set a configuration value
  lmapp install           Install/setup a backend
  lmapp start             Start the backend service
  lmapp stop              Stop the backend service
  lmapp models list       List available models

[yellow]Shell Commands:[/yellow]
  Any shell command (bash, zsh, etc.)
  Examples: ls, pwd, git status, python script.py

[yellow]Terminal Commands:[/yellow]
  help                    Show this help message
  history                 Show command history
  clear                   Clear the terminal
  exit / quit             Exit the terminal

[cyan bold]Examples:[/cyan bold]
  > lmapp chat
  > lmapp config set temperature 0.5
  > ls -la
  > git log --oneline
  > python3 -c "import lmapp; print(lmapp.__version__)"
"""
        console.print(help_text)

    def show_history(self) -> None:
        """Display command history"""
        if not self.history:
            console.print("[yellow]No commands in history[/yellow]")
            return

        console.print("\n[cyan bold]Command History:[/cyan bold]")
        for i, cmd in enumerate(self.history, 1):
            console.print(f"  {i:3d}  {cmd}")
        console.print()
