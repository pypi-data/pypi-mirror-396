#!/usr/bin/env python3
"""
Chat UI - Interactive Terminal Interface
Provides interactive chat interface with command parsing
"""

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from lmapp.core.chat import ChatSession

console = Console()


class ChatUI:
    """Interactive chat interface"""

    # Commands that can be used in chat
    COMMANDS = {
        "/help": "Show this help message",
        "/history": "Show conversation history",
        "/clear": "Clear conversation history",
        "/stats": "Show session statistics",
        "/exit": "Exit chat",
        "/quit": "Exit chat",
    }

    def __init__(self, session: ChatSession):
        """
        Initialize chat UI

        Args:
            session: ChatSession instance
        """
        self.session = session
        self.temperature = 0.7

    def print_welcome(self):
        """Print welcome message"""
        console.print(
            Panel(
                f"[bold cyan]Chat Session Started[/bold cyan]\n"
                f"Model: [yellow]{self.session.model}[/yellow]\n"
                f"Backend: [green]{self.session.backend.backend_display_name()}[/green]\n\n"
                f"Type [cyan]/help[/cyan] for commands, [cyan]/exit[/cyan] to quit",
                title="lmapp",
                border_style="cyan",
            )
        )

    def print_help(self):
        """Print help message"""
        help_text = "Available Commands:\n"
        for cmd, desc in self.COMMANDS.items():
            help_text += f"\n  [cyan]{cmd:<12}[/cyan] {desc}"

        console.print(Panel(help_text, title="Help", border_style="blue"))

    def print_history(self):
        """Print conversation history"""
        history_text = self.session.get_history_text()
        console.print(
            Panel(history_text, title="Conversation History", border_style="green")
        )

    def print_stats(self):
        """Print session statistics"""
        stats = self.session.get_stats()
        stats_text = ""
        for key, value in stats.items():
            if key == "duration_seconds":
                value = f"{value:.1f}s"
            stats_text += f"\n  {key}: {value}"

        console.print(Panel(stats_text, title="Session Stats", border_style="magenta"))

    def parse_command(self, user_input: str) -> Optional[str]:
        """
        Parse and execute user commands

        Args:
            user_input: Raw user input

        Returns:
            "exit" to exit, None to continue
        """
        cmd = user_input.strip().lower()

        if cmd == "/help":
            self.print_help()
            return None

        elif cmd == "/history":
            self.print_history()
            return None

        elif cmd == "/clear":
            cleared = self.session.clear_history()
            console.print(f"[yellow]✓ Cleared {cleared} messages[/yellow]")
            return None

        elif cmd == "/stats":
            self.print_stats()
            return None

        elif cmd in ("/exit", "/quit"):
            return "exit"

        elif cmd.startswith("/"):
            # Unknown command
            console.print(f"[red]✗ Unknown command: {cmd}[/red]")
            console.print("[cyan]Type /help for available commands[/cyan]")
            return None

        # Not a command, return input for processing
        return user_input

    def run(self):
        """Run interactive chat loop"""
        self.print_welcome()

        try:
            while True:
                try:
                    # Get user input
                    user_input = console.input("\n[cyan]You:[/cyan] ").strip()

                    if not user_input:
                        continue

                    # Try to parse as command
                    result = self.parse_command(user_input)

                    if result == "exit":
                        console.print("\n[yellow]👋 Goodbye![/yellow]")
                        break

                    if result is None:
                        # Command was handled, continue
                        continue

                    # Send prompt to backend
                    console.print("[cyan]AI:[/cyan]", end=" ")
                    response = self.session.send_prompt(
                        result, temperature=self.temperature
                    )
                    console.print(response)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Chat interrupted[/yellow]")
                    break

                except ValueError as e:
                    console.print(f"[red]{str(e)}[/red]")

                except RuntimeError as e:
                    console.print(f"[red]{str(e)}[/red]")
                    console.print(
                        "[yellow]Try running 'lmapp install' or restart the backend[/yellow]"
                    )
                    break

                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")

        except EOFError:
            # Ctrl+D pressed
            console.print("\n[yellow]👋 Goodbye![/yellow]")


def launch_chat(session: ChatSession):
    """
    Launch interactive chat UI

    Args:
        session: ChatSession instance
    """
    ui = ChatUI(session)
    ui.run()
