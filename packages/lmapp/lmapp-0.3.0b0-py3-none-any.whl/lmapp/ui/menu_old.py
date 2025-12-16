#!/usr/bin/env python3
"""
Main Menu System
Provides alphabetic multiple-choice menus for user interaction
"""

from typing import List, Callable, Optional

import inquirer
import psutil
from rich.console import Console
from rich.panel import Panel
from lmapp.core.config import get_config_manager
from lmapp import __version__
from lmapp.backend.detector import BackendDetector
from lmapp.core.chat import ChatSession
from lmapp.ui.chat_ui import launch_chat

console = Console()


class MenuItem:
    """Represents a single menu item"""

    def __init__(
        self,
        key: str,
        label: str,
        action: Optional[Callable] = None,
        description: str = "",
    ):
        self.key = key.upper()
        self.label = label
        self.action = action
        self.description = description

    def execute(self):
        """Execute the menu item's action"""
        if self.action:
            return self.action()
        else:
            console.print(f"[yellow]'{self.label}' not yet implemented[/yellow]")


class MainMenu:
    """Main application menu"""

    def __init__(self):
        self.config_manager = get_config_manager()
        self.detector = BackendDetector()
        self.running = True

    def _build_menu_items(self) -> List[MenuItem]:
        """Build the main menu structure based on developer mode"""
        config = self.config_manager.load()
        dev_mode = config.developer_mode

        items = [
            MenuItem(
                "A",
                "Start Chat",
                self.start_chat,
            ),
        ]

        if dev_mode:
            items.extend(
                [
                    MenuItem(
                        "B",
                        "Manage Models",
                        self.manage_models,
                    ),
                    MenuItem(
                        "C",
                        "Configure Settings",
                        self.configure,
                    ),
                    MenuItem(
                        "D",
                        "Shell Customization",
                        self.shell_customize,
                    ),
                    MenuItem(
                        "E",
                        "Help & Documentation",
                        self.show_help,
                    ),
                    MenuItem(
                        "F",
                        "About",
                        self.show_about,
                    ),
                ]
            )
        else:
            items.extend(
                [
                    MenuItem(
                        "B",
                        "Help & Documentation",
                        self.show_help,
                    ),
                    MenuItem(
                        "C",
                        "About",
                        self.show_about,
                    ),
                ]
            )

        items.append(MenuItem("Q", "Quit", self.quit))
        return items

    def display(self):
        """Display the menu"""
        # Rebuild items to reflect current state
        self.items = self._build_menu_items()

        console.print("\n[bold cyan]lmapp - Main Menu[/bold cyan]\n")

    def get_choice(self) -> Optional[str]:
        """Get user's menu choice"""
        # Rebuild items to ensure choices match display
        self.items = self._build_menu_items()
        choices = [(f"{item.key}) {item.label}", item.key) for item in self.items]

        questions = [
            inquirer.List(
                "choice",
                message="Choose an option",
                choices=choices,
            ),
        ]

        try:
            answers = inquirer.prompt(questions)
            if answers:
                return answers["choice"]
            return None
        except KeyboardInterrupt:
            return "Q"

    def run(self):
        """Main menu loop"""
        while self.running:
            self.display()
            choice = self.get_choice()

            if choice:
                # Find and execute the menu item
                for item in self.items:
                    if item.key == choice.upper():
                        console.print()
                        item.execute()
                        break

                if choice.upper() == "Q":
                    break
            else:
                break

        console.print("\n[dim]Thanks for using lmapp![/dim]\n")

    # Menu action methods

    def start_chat(self):
        """Start a new chat session"""
        # Try to find a running backend
        backend = self.detector.get_best_backend()

        if not backend:
            console.print("[red]No backend installed![/red]")
            console.print(
                "You need to install a backend (Ollama or llamafile) to chat."
            )

            questions = [
                inquirer.Confirm(
                    "install",
                    message="Would you like to install a backend now?",
                    default=True,
                )
            ]
            answers = inquirer.prompt(questions)

            if answers and answers["install"]:
                self.install_backend()
                # Try again after install
                backend = self.detector.get_best_backend()
                if not backend:
                    return
            else:
                console.input("[dim]Press Enter to continue...[/dim]")
                return

        if not backend.is_running():
            console.print(
                f"[yellow]Backend {backend.backend_display_name()} is not running.[/yellow]"
            )
            questions = [
                inquirer.Confirm(
                    "start",
                    message=f"Start {backend.backend_display_name()}?",
                    default=True,
                )
            ]
            answers = inquirer.prompt(questions)

            if answers and answers["start"]:
                with console.status("Starting backend..."):
                    if backend.start():
                        console.print("[green]Backend started successfully![/green]")
                    else:
                        console.print("[red]Failed to start backend.[/red]")
                        console.input("[dim]Press Enter to continue...[/dim]")
                        return
            else:
                return

        # Get available models
        with console.status("Fetching models..."):
            models = backend.list_models()

        if not models:
            console.print("[yellow]No models found.[/yellow]")
            # Offer to download default model
            questions = [
                inquirer.Confirm(
                    "download",
                    message="Download default model (tinyllama)?",
                    default=True,
                )
            ]
            answers = inquirer.prompt(questions)

            if answers and answers["download"]:
                # TODO: Implement download logic here or call manage_models
                # For now, just try to use tinyllama and let the backend handle it if it can
                # But backend.list_models() returned empty, so we probably need to explicitly download
                if hasattr(backend, "download_model"):
                    console.print("Downloading model... (this may take a while)")
                    if backend.download_model("tinyllama"):
                        console.print("[green]Model downloaded successfully![/green]")
                        models = ["tinyllama"]
                    else:
                        console.print("[red]Failed to download model.[/red]")
                        console.input("[dim]Press Enter to continue...[/dim]")
                        return
                else:
                    console.print("[red]Backend does not support auto-download.[/red]")
                    console.input("[dim]Press Enter to continue...[/dim]")
                    return
            else:
                console.input("[dim]Press Enter to continue...[/dim]")
                return

        # Ask for model selection if multiple
        config = self.config_manager.load()
        model = models[0]

        # If default model is set and available, use it
        if config.default_model and config.default_model in models:
            model = config.default_model
        elif len(models) > 1:
            questions = [
                inquirer.List(
                    "model",
                    message="Choose a model",
                    choices=models,
                ),
            ]
            answers = inquirer.prompt(questions)
            if answers:
                model = answers["model"]
                # Ask to save as default if not set or different
                if model != config.default_model:
                    q_def = [
                        inquirer.Confirm(
                            "save_default",
                            message=f"Set {model} as default model?",
                            default=True,
                        )
                    ]
                    a_def = inquirer.prompt(q_def)
                    if a_def and a_def["save_default"]:
                        config.default_model = model
                        self.config_manager.save(config)
                        console.print(f"[green]Default model set to {model}[/green]")
            else:
                return

        try:
            session = ChatSession(backend, model=model)
            launch_chat(session)
        except Exception as e:
            console.print(f"[red]Error starting chat: {e}[/red]")
            console.input("[dim]Press Enter to continue...[/dim]")

    def manage_models(self):
        """Model management interface"""
        backend = self.detector.get_best_backend()

        if not backend:
            console.print("[red]No backend installed![/red]")
            questions = [
                inquirer.Confirm(
                    "install",
                    message="Would you like to install a backend now?",
                    default=True,
                )
            ]
            answers = inquirer.prompt(questions)

            if answers and answers["install"]:
                self.install_backend()
                backend = self.detector.get_best_backend()
                if not backend:
                    return
            else:
                console.input("[dim]Press Enter to continue...[/dim]")
                return

        while True:
            console.clear()
            console.print()  # Add blank space for better spacing
            console.print(
                f"[bold cyan]Model Management ({backend.backend_display_name()})[/bold cyan]\n"
            )

            if not backend.is_running():
                console.print(
                    "[yellow]Backend is not running. Starting it to manage models...[/yellow]"
                )
                if not backend.start():
                    console.print("[red]Failed to start backend.[/red]")
                    console.input("[dim]Press Enter to continue...[/dim]")
                    return

            with console.status("Fetching models..."):
                models = backend.list_models()

            console.print("[bold]Installed Models:[/bold]")
            if models:
                for m in models:
                    console.print(f"  • {m}")
            else:
                console.print("  [dim]No models installed[/dim]")

            console.print()

            questions = [
                inquirer.List(
                    "action",
                    message="Choose an action",
                    choices=[
                        ("Download New Model", "download"),
                        ("Back to Main Menu", "back"),
                    ],
                ),
            ]

            answers = inquirer.prompt(questions)
            if not answers or answers["action"] == "back":
                break

            if answers["action"] == "download":
                self.download_model_ui(backend)

    def download_model_ui(self, backend):
        """Show the download model UI"""
        while True:
            # Get system RAM
            ram_gb = psutil.virtual_memory().total / (1024**3)

            # Get currently installed models to filter them out
            installed_models = backend.list_models() or []
            # Normalize installed models to handle tags (simple check)
            installed_base_names = [m.split(":")[0] for m in installed_models]

            # Define recommended models with structured data
            # Format: id, name, version, quality, min_ram
            models_data = [
                {
                    "id": "tinyllama",
                    "name": "TinyLlama",
                    "ver": "1.1B",
                    "qual": "Fast/Low RAM",
                    "min_ram": 2,
                },
                {
                    "id": "qwen2.5:0.5b",
                    "name": "Qwen 2.5",
                    "ver": "0.5B",
                    "qual": "Ultra Fast",
                    "min_ram": 2,
                },
                {
                    "id": "llama3.2:1b",
                    "name": "Llama 3.2",
                    "ver": "1B",
                    "qual": "Modern/Fast",
                    "min_ram": 3,
                },
                {
                    "id": "llama3.2:3b",
                    "name": "Llama 3.2",
                    "ver": "3B",
                    "qual": "Balanced",
                    "min_ram": 4,
                },
                {
                    "id": "phi3",
                    "name": "Phi-3 Mini",
                    "ver": "3.8B",
                    "qual": "High Quality",
                    "min_ram": 4,
                },
                {
                    "id": "mistral",
                    "name": "Mistral",
                    "ver": "7B",
                    "qual": "Standard",
                    "min_ram": 6,
                },
                {
                    "id": "llama3.1",
                    "name": "Llama 3.1",
                    "ver": "8B",
                    "qual": "SOTA",
                    "min_ram": 8,
                },
                {
                    "id": "deepseek-r1:7b",
                    "name": "DeepSeek R1",
                    "ver": "7B",
                    "qual": "Reasoning",
                    "min_ram": 8,
                },
                {
                    "id": "gemma2:9b",
                    "name": "Gemma 2",
                    "ver": "9B",
                    "qual": "Google",
                    "min_ram": 10,
                },
            ]

            # Filter compatible models AND not installed
            compatible_models = []
            for m in models_data:
                # Check RAM
                if m["min_ram"] > ram_gb:
                    continue

                # Check if installed (check both full ID and base name)
                is_installed = False
                if m["id"] in installed_models:
                    is_installed = True
                elif m["id"].split(":")[0] in installed_base_names:
                    is_installed = True

                if not is_installed:
                    compatible_models.append(m)

            # Build choices with aligned columns
            choices = []

            # Add header as pseudo-items (workaround for missing Separator and rendering glitches)
            # We use unique IDs for them and filter them out if selected.
            choices.append((" ", "HEADER_0"))
            choices.append(
                (f"   {'MODEL':^20} {'VERSION':^10} {'QUALITY':^20}", "HEADER_1")
            )
            choices.append((" ", "HEADER_2"))

            for m in compatible_models:
                # Create aligned string for the menu item
                # We use a fixed width font assumption here
                label = f"{m['name']:<20} {m['ver']:<10} {m['qual']:<20}"
                choices.append((label, m["id"]))

            choices.append(("Custom Model Name...", "custom"))
            choices.append(("Back", "back"))

            # Set default to first real model to skip headers
            default_model = compatible_models[0]["id"] if compatible_models else "back"

            questions = [
                inquirer.List(
                    "model_choice",
                    message="Select a model to download",
                    choices=choices,
                    default=default_model,
                ),
            ]

            dl_answers = inquirer.prompt(questions)
            if not dl_answers:
                break

            model_name = dl_answers["model_choice"]

            # Handle header selection (ignore)
            if model_name in ["HEADER_0", "HEADER_1", "HEADER_2"]:
                continue

            if model_name == "back":
                break

            if model_name == "custom":
                model_name = console.input(
                    "Enter model name to download (e.g. llama3, mistral): "
                )

            if model_name:
                console.print(f"[cyan]Downloading {model_name}...[/cyan]")
                # We can't use console.status here easily because download might take a long time and we want output
                if hasattr(backend, "download_model"):
                    # Define a callback to print progress if supported
                    def progress_callback(line):
                        # Try to parse progress if possible, or just print
                        # For now, just print the line if it's meaningful
                        pass  # console.print(line.strip())

                    if backend.download_model(model_name):
                        console.print(
                            f"[green]Successfully downloaded {model_name}![/green]"
                        )
                        console.input("[dim]Press Enter to continue...[/dim]")
                    else:
                        console.print(f"[red]Failed to download {model_name}.[/red]")
                        console.input("[dim]Press Enter to continue...[/dim]")
                else:
                    console.print("[red]Backend does not support auto-download.[/red]")
                    console.input("[dim]Press Enter to continue...[/dim]")

    def install_backend(self):
        """Install a backend"""
        # Filter out MockBackend if present (shouldn't be in production, but good to be safe)
        available_backends = [
            b for b in self.detector.backends if b.backend_name() != "mock"
        ]

        if not available_backends:
            console.print("[red]No installable backends found.[/red]")
            console.input("[dim]Press Enter to continue...[/dim]")
            return

        choices = [(b.backend_display_name(), b) for b in available_backends]

        questions = [
            inquirer.List(
                "backend",
                message="Choose a backend to install",
                choices=choices,
            ),
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        backend = answers["backend"]

        console.print(f"[cyan]Installing {backend.backend_display_name()}...[/cyan]")
        if backend.install():
            console.print(
                f"[green]Successfully installed {backend.backend_display_name()}![/green]"
            )
        else:
            console.print(
                f"[red]Failed to install {backend.backend_display_name()}.[/red]"
            )

        console.input("[dim]Press Enter to continue...[/dim]")

    def configure(self):
        """Configuration interface"""
        while True:
            console.clear()
            console.print("[bold cyan]Configuration[/bold cyan]\n")

            config = self.config_manager.load()

            console.print(
                f"Developer Mode: {'[green]ON[/green]' if config.developer_mode else '[red]OFF[/red]'}"
            )
            console.print(f"Default Model: {config.default_model or '[dim]None[/dim]'}")
            console.print()

            questions = [
                inquirer.List(
                    "setting",
                    message="Choose a setting to change",
                    choices=[
                        ("Set Default Model", "default_model"),
                        ("Back to Main Menu", "back"),
                    ],
                ),
            ]

            answers = inquirer.prompt(questions)
            if not answers or answers["setting"] == "back":
                break

            elif answers["setting"] == "default_model":
                backend = self.detector.get_best_backend()
                if backend:
                    if not backend.is_running():
                        # Try to start it silently or just warn
                        pass

                    # Try to list models if running
                    models = []
                    if backend.is_running():
                        models = backend.list_models()

                    if models:
                        q = [
                            inquirer.List(
                                "model", message="Select default model", choices=models
                            )
                        ]
                        a = inquirer.prompt(q)
                        if a:
                            config.default_model = a["model"]
                            self.config_manager.save(config)
                    else:
                        console.print(
                            "[yellow]No models found or backend not running.[/yellow]"
                        )
                        model_name = console.input(
                            "Enter model name manually (leave empty to cancel): "
                        )
                        if model_name:
                            config.default_model = model_name
                            self.config_manager.save(config)
                else:
                    console.print("[red]No backend found.[/red]")
                    console.input("[dim]Press Enter to continue...[/dim]")

    def shell_customize(self):
        """Shell customization menu"""
        console.print("[bold cyan]Shell Customization[/bold cyan]\n")
        console.print("[yellow]Shell customization coming soon![/yellow]")
        console.print("\n[dim]Options:[/dim]")
        console.print("  • Install bash-it")
        console.print("  • Install Oh My Zsh")
        console.print("  • Configure shell themes")
        console.print("  • Add custom aliases")
        console.print("\n[dim]Press Enter to return to menu[/dim]")
        input()

    def show_help(self):
        """Display help information"""
        help_text = """
[bold]lmapp Help & Documentation[/bold]

[cyan]Menu Options:[/cyan]
• [bold]Start Chat:[/bold] Begin chatting with your local AI
• [bold]Manage Models:[/bold] Download, update, or remove AI models
• [bold]Configure Settings:[/bold] Adjust lmapp configuration
• [bold]Shell Customization:[/bold] Install bash-it or Oh My Zsh
• [bold]About:[/bold] System information and version

[cyan]Quick Start:[/cyan]
1. Run installation: lmapp install
2. Start chatting: lmapp chat
3. Or use this menu to explore features

[yellow]Note:[/yellow] To change the default model, enable Advanced Mode in the About menu.

[cyan]Documentation:[/cyan]
• User Guide: docs/user-guide.md
• Installation: docs/installation.md
• Troubleshooting: docs/troubleshooting.md
• FAQ: docs/faq.md

[cyan]Support:[/cyan]
• GitHub Issues: github.com/yourusername/lmapp/issues
• Documentation: github.com/yourusername/lmapp/docs

[cyan]Version:[/cyan] 0.1.0-dev
        """
        console.print(Panel(help_text, border_style="cyan"))
        console.print("\n[dim]Press Enter to return to menu[/dim]")
        input()

    def show_about(self):
        """Show system information and developer toggle"""
        while True:
            config = self.config_manager.load()
            dev_mode = config.developer_mode

            # Get backend info
            backend_name = config.backend

            if backend_name == "auto":
                rec = self.detector.get_recommended(
                    8
                )  # Default to 8GB assumption for display
                backend_name = f"Auto ({rec.backend_name() if rec else 'None'})"

            # Build About Text
            about_text = f"""
[bold cyan]lmapp[/bold cyan] v{__version__}

[bold]System Information:[/bold]
• Model: [yellow]{config.model}[/yellow]
• Backend: [yellow]{backend_name}[/yellow]
• Advanced Mode: {'[green]ON[/green]' if dev_mode else '[dim]OFF[/dim]'}

[dim]Local LLM Made Simple[/dim]
            """
            console.print(Panel(about_text, title="About", border_style="blue"))

            # Sub-menu options
            options = [
                ("Toggle Advanced Mode", "toggle"),
                ("Back to Main Menu", "back"),
            ]

            questions = [
                inquirer.List(
                    "action",
                    message="Choose an option",
                    choices=options,
                ),
            ]

            try:
                answer = inquirer.prompt(questions)
                if not answer or answer["action"] == "back":
                    break
                elif answer["action"] == "toggle":
                    self.toggle_dev_mode()
            except KeyboardInterrupt:
                break

    def toggle_dev_mode(self):
        """Toggle developer mode"""
        config = self.config_manager.load()
        config.developer_mode = not config.developer_mode
        self.config_manager.save(config)
        state = "ENABLED" if config.developer_mode else "DISABLED"
        color = "green" if config.developer_mode else "yellow"
        console.print(f"[{color}]Advanced Mode {state}[/{color}]")

    def quit(self):
        """Exit the application"""
        self.running = False


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
