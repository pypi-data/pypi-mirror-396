#!/usr/bin/env python3
"""
Shell Customization Module
Manages bash-it, Oh My Zsh, and other shell enhancements
"""

import subprocess
import platform
import os
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from lmapp.utils.logging import logger


console = Console()


class ShellCustomizer:
    """Manages shell customization and environment setup"""

    SHELL_RC_FILES = {
        "bash": Path.home() / ".bashrc",
        "zsh": Path.home() / ".zshrc",
        "fish": Path.home() / ".config/fish/config.fish",
    }

    def __init__(self):
        self.shell = self._detect_shell()
        self.shell_rc = self.SHELL_RC_FILES.get(self.shell)
        logger.debug(f"Detected shell: {self.shell}")

    def _detect_shell(self) -> str:
        """Detect current shell"""
        shell_env = os.environ.get("SHELL", "bash")
        return Path(shell_env).name

    def install_bash_it(self) -> bool:
        """
        Install bash-it for bash shell customization

        Returns:
            True if successful
        """
        if self.shell != "bash":
            console.print(
                "[yellow]⚠ bash-it requires bash shell (currently using "
                f"{self.shell})[/yellow]"
            )
            return False

        bash_it_dir = Path.home() / ".bash_it"

        if bash_it_dir.exists():
            console.print("[green]✓ bash-it already installed[/green]")
            return True

        try:
            console.print("[cyan]Installing bash-it...[/cyan]")

            # Clone bash-it repository
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "https://github.com/Bash-it/bash-it.git",
                    str(bash_it_dir),
                ],
                check=True,
                capture_output=True,
                timeout=60,
            )

            # Run bash-it installer
            subprocess.run(
                ["bash", str(bash_it_dir / "install.sh")],
                check=True,
                capture_output=True,
                timeout=30,
            )

            console.print(
                "[green]✓ bash-it installed successfully[/green]\n"
                "[yellow]💡 Reload your shell: exec bash[/yellow]"
            )
            return True

        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗ Installation failed: {e}[/red]")
            logger.error(f"bash-it installation error: {e}")
            return False

    def install_oh_my_zsh(self) -> bool:
        """
        Install Oh My Zsh for zsh shell customization

        Returns:
            True if successful
        """
        if self.shell != "zsh":
            console.print(
                "[yellow]⚠ Oh My Zsh requires zsh shell (currently using "
                f"{self.shell})[/yellow]"
            )
            return False

        omz_dir = Path.home() / ".oh-my-zsh"

        if omz_dir.exists():
            console.print("[green]✓ Oh My Zsh already installed[/green]")
            return True

        try:
            console.print("[cyan]Installing Oh My Zsh...[/cyan]")

            # Clone Oh My Zsh repository
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "https://github.com/ohmyzsh/ohmyzsh.git",
                    str(omz_dir),
                ],
                check=True,
                capture_output=True,
                timeout=60,
            )

            console.print(
                "[green]✓ Oh My Zsh installed successfully[/green]\n"
                "[yellow]💡 Reload your shell: exec zsh[/yellow]"
            )
            return True

        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗ Installation failed: {e}[/red]")
            logger.error(f"Oh My Zsh installation error: {e}")
            return False

    def add_lmapp_alias(self) -> bool:
        """
        Add lmapp aliases to shell RC file

        Returns:
            True if successful
        """
        if not self.shell_rc:
            console.print(
                f"[red]✗ Shell RC file not found for {self.shell}[/red]"
            )
            return False

        aliases = """
# lmapp aliases
alias lmapp-chat='lmapp chat'
alias lmapp-status='lmapp status'
alias lmapp-config='lmapp config show'
alias lmapp-models='ollama list'  # Ollama models
"""

        try:
            # Check if already added
            if self.shell_rc.exists():
                content = self.shell_rc.read_text()
                if "lmapp-chat" in content:
                    console.print("[yellow]⚠ lmapp aliases already added[/yellow]")
                    return True

            # Append aliases
            with open(self.shell_rc, "a") as f:
                f.write(aliases)

            console.print(
                "[green]✓ lmapp aliases added[/green]\n"
                "[yellow]💡 Reload your shell to use new aliases[/yellow]"
            )
            return True

        except Exception as e:
            console.print(f"[red]✗ Error adding aliases: {e}[/red]")
            logger.error(f"Alias addition error: {e}")
            return False

    def get_shell_info(self) -> dict:
        """Get information about current shell setup"""
        return {
            "current_shell": self.shell,
            "shell_rc_file": str(self.shell_rc),
            "rc_file_exists": self.shell_rc.exists() if self.shell_rc else False,
            "bash_it_installed": (Path.home() / ".bash_it").exists(),
            "oh_my_zsh_installed": (Path.home() / ".oh-my-zsh").exists(),
        }

    def show_shell_menu(self) -> None:
        """Display shell customization menu"""
        console.print(
            "\n[cyan bold]🐚 Shell Customization Menu[/cyan bold]\n"
        )

        options = [
            ("A", "Install bash-it", lambda: self.install_bash_it()),
            ("B", "Install Oh My Zsh", lambda: self.install_oh_my_zsh()),
            ("C", "Add lmapp aliases", lambda: self.add_lmapp_alias()),
            ("D", "Show shell info", lambda: self._show_shell_info()),
            ("Q", "Back to main menu", None),
        ]

        for key, desc, _ in options:
            console.print(f"  {key}) {desc}")

        choice = input("\n[?] Choose an option: ").strip().upper()

        for key, desc, handler in options:
            if choice == key and handler:
                handler()
                break

    def _show_shell_info(self) -> None:
        """Display current shell information"""
        info = self.get_shell_info()
        console.print("\n[cyan]Current Shell Setup:[/cyan]")
        for key, value in info.items():
            console.print(f"  {key}: {value}")
