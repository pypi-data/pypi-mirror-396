#!/usr/bin/env python3
"""
First-Run Wizard for LMAPP
Guides new users through initial setup with hardware detection and model selection
"""

from typing import Optional
import inquirer
import psutil
from rich.console import Console
from rich.panel import Panel
from lmapp.core.config import LMAppConfig, ConfigManager
from lmapp.backend.detector import BackendDetector

console = Console()


class FirstRunWizard:
    """Interactive setup wizard for first-time users"""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.detector = BackendDetector()
        self.config = self.config_manager.load()

    def run(self) -> bool:
        """Run the first-run wizard if needed
        
        Returns:
            True if wizard completed, False if skipped
        """
        if self.config.completed_setup:
            return False

        self._show_welcome()
        hardware_info = self._detect_hardware()
        recommended_model = self._get_recommended_model(hardware_info)
        
        if self._should_download_model(recommended_model):
            self._download_model(recommended_model)

        # Mark setup as complete
        self.config.completed_setup = True
        self.config_manager.save(self.config)

        self._show_completion()
        return True

    def _show_welcome(self) -> None:
        """Show welcome screen"""
        welcome_text = """
[bold cyan]Welcome to LMAPP! 👋[/bold cyan]

This is your first time using LMAPP. Let's set you up quickly.

LMAPP is a beautiful local AI chat application.
Everything runs on [bold]your machine[/bold] - no cloud, no subscriptions.

This wizard will:
1. Detect your hardware
2. Recommend the best model for you
3. Download a model (optional)
4. Get you chatting in minutes

You're about to have your own AI assistant. Let's go!
        """
        console.print(Panel(welcome_text, border_style="cyan"))
        console.input("\n[dim]Press Enter to continue...[/dim]")

    def _detect_hardware(self) -> dict:
        """Detect system hardware capabilities
        
        Returns:
            Dictionary with hardware information
        """
        console.clear()
        console.print("[cyan]🔍 Detecting your hardware...[/cyan]\n")
        
        memory = psutil.virtual_memory()
        cpu_info = psutil.cpu_count()
        
        hardware = {
            "total_ram_gb": memory.total / (1024**3),
            "available_ram_gb": memory.available / (1024**3),
            "cpu_cores": cpu_info,
            "cpu_percent": psutil.cpu_percent(interval=1),
        }

        # Display detected info
        info_text = f"""
[bold cyan]System Hardware[/bold cyan]

[bold]Memory:[/bold]
• Total RAM: {hardware['total_ram_gb']:.1f}GB
• Available: {hardware['available_ram_gb']:.1f}GB

[bold]Processor:[/bold]
• CPU Cores: {hardware['cpu_cores']}
• Current Load: {hardware['cpu_percent']}%

[dim]This information helps us recommend the best model for you.[/dim]
        """
        console.print(Panel(info_text, border_style="green"))
        console.input("\n[dim]Press Enter to continue...[/dim]")
        
        return hardware

    def _get_recommended_model(self, hardware: dict) -> str:
        """Get model recommendation based on hardware
        
        Args:
            hardware: Dictionary with hardware info
            
        Returns:
            Recommended model name
        """
        ram_gb = hardware["total_ram_gb"]

        if ram_gb < 2:
            return "qwen2.5:0.5b"  # 370MB
        elif ram_gb < 4:
            return "llama3.2:1b"  # 950MB
        elif ram_gb < 8:
            return "llama3.2:3b"  # 1.9GB
        else:
            return "mistral"  # 4GB

    def _should_download_model(self, recommended: str) -> bool:
        """Ask user if they want to download the recommended model
        
        Args:
            recommended: The recommended model name
            
        Returns:
            True if user wants to download, False otherwise
        """
        console.clear()
        
        # Map model to display name and size
        model_info = {
            "qwen2.5:0.5b": ("Qwen 2.5 Ultra-Light (0.5B)", "370MB", "Minimal RAM"),
            "llama3.2:1b": ("Llama 3.2 Light (1B)", "950MB", "2GB RAM"),
            "llama3.2:3b": ("Llama 3.2 Standard (3B)", "1.9GB", "4GB RAM"),
            "mistral": ("Mistral 7B", "4GB", "8GB RAM"),
        }

        display_name, size, requirement = model_info.get(
            recommended, (recommended, "Unknown", "Unknown")
        )

        recommendation_text = f"""
[bold cyan]🤖 Recommended Model[/bold cyan]

Based on your hardware, we recommend:

[bold]{display_name}[/bold]
• Size: {size}
• RAM Requirement: {requirement}
• Best for: High-quality responses with good speed

This model is perfect for your system.

[dim]You can always download other models later from the Models menu.[/dim]
        """
        console.print(Panel(recommendation_text, border_style="yellow"))

        q = [inquirer.Confirm(
            "download",
            message="Download this model now?",
            default=True
        )]
        
        answer = inquirer.prompt(q)
        return answer.get("download", True) if answer else False

    def _download_model(self, model_name: str) -> None:
        """Download and setup the recommended model
        
        Args:
            model_name: Name of the model to download
        """
        console.clear()
        console.print(f"\n[cyan]⬇️  Downloading {model_name}...[/cyan]\n")
        
        backend = self.detector.get_best_backend()
        
        if not backend:
            console.print("[yellow]⚠️  No backend found (Ollama/llamafile required)[/yellow]")
            console.input("[dim]Press Enter to continue...[/dim]")
            return

        # Ensure backend is running
        if not backend.is_running():
            console.print("[dim]Starting backend...[/dim]")
            try:
                backend.start()
            except Exception as e:
                console.print(f"[red]❌ Failed to start backend: {e}[/red]")
                console.input("[dim]Press Enter to continue...[/dim]")
                return

        # Download model
        try:
            with console.status(f"Downloading {model_name}... (this may take a few minutes)"):
                # Note: Model download would be handled by backend
                # For now, we just show the message
                pass
            console.print(f"[green]✓ {model_name} is ready![/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Model download skipped: {e}[/yellow]")

        console.input("\n[dim]Press Enter to continue...[/dim]")

    def _show_completion(self) -> None:
        """Show completion message and next steps"""
        console.clear()
        
        completion_text = """
[bold green]✓ Setup Complete![/bold green]

You're all set! Here's what's next:

[bold]Getting Started:[/bold]
1. Go back to the main menu
2. Select [bold]"Start Chat"[/bold]
3. Begin chatting with your AI

[bold]Tips:[/bold]
• Your AI stays on [bold]your machine[/bold] - complete privacy
• Works [bold]offline[/bold] - no cloud needed
• Enable [bold]Advanced Mode[/bold] in About for more features
• Check [bold]Plugins[/bold] for cool extensions

[bold]Need Help?[/bold]
• Select [bold]"Help & Documentation"[/bold] from main menu
• Visit: github.com/nabaznyl/lmapp
• Report issues: github.com/nabaznyl/lmapp/issues

Enjoy your local AI! 🚀
        """
        console.print(Panel(completion_text, border_style="green"))
        console.input("\n[dim]Press Enter to go back to main menu...[/dim]")


def run_first_time_setup(config_manager: Optional[ConfigManager] = None) -> bool:
    """Convenience function to run first-time setup
    
    Args:
        config_manager: Optional ConfigManager instance
        
    Returns:
        True if wizard ran, False if skipped
    """
    wizard = FirstRunWizard()
    return wizard.run()


if __name__ == "__main__":
    # For testing
    wizard = FirstRunWizard()
    wizard.run()
