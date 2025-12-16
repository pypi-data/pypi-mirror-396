#!/usr/bin/env python3
"""
Enhanced Menu System with Advanced Mode
Provides intuitive beginner experience with power-user features
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
    """Main application menu with Advanced Mode support"""

    def __init__(self):
        self.config_manager = get_config_manager()
        self.detector = BackendDetector()
        self.running = True

    def _build_menu_items(self) -> List[MenuItem]:
        """Build menu structure based on Advanced Mode setting"""
        config = self.config_manager.load()
        advanced = config.advanced_mode

        items = [
            MenuItem("A", "Start Chat", self.start_chat),
        ]

        if advanced:
            # Advanced Mode: Full feature access
            items.extend([
                MenuItem("B", "Plugins", self.manage_plugins),
                MenuItem("C", "Models", self.manage_models),
                MenuItem("D", "API & Integration", self.show_api),
                MenuItem("E", "Settings", self.configure),
                MenuItem("F", "Developer Tools", self.show_dev_tools),
                MenuItem("G", "Help & Documentation", self.show_help),
                MenuItem("H", "About", self.show_about),
            ])
        else:
            # Beginner Mode: Simplified menus
            items.extend([
                MenuItem("B", "Plugins", self.manage_plugins),
                MenuItem("C", "Settings", self.configure),
                MenuItem("D", "Help & Documentation", self.show_help),
                MenuItem("E", "About", self.show_about),
            ])

        items.append(MenuItem("Q", "Quit", self.quit))
        return items

    def display(self):
        """Display the menu with enhanced visual hierarchy"""
        config = self.config_manager.load()
        mode_indicator = "[bold green]📊 Advanced Mode[/bold green]" if config.advanced_mode else "[dim]Beginner Mode[/dim]"
        
        # Clear console for fresh start
        console.clear()
        
        # Show header with branding
        console.print("\n" + "=" * 60)
        console.print("[bold cyan]LMAPP - Local LLM Chat[/bold cyan]", justify="center")
        console.print(f"Version {__version__}", justify="center", style="dim")
        
        # Show mode indicator
        console.print(f"\nMode: {mode_indicator}", justify="center")
        console.print("=" * 60 + "\n")

    def get_choice(self) -> Optional[str]:
        """Get user's menu choice with visual separators"""
        self.items = self._build_menu_items()
        
        # Organize items into categories
        chat_items = [i for i in self.items if i.key == "A"]
        management_items = [i for i in self.items if i.key in ["B", "C", "D"]]
        advanced_items = [i for i in self.items if i.key in ["E", "F"]]
        control_items = [i for i in self.items if i.key in ["G", "H"]]
        quit_items = [i for i in self.items if i.key == "Q"]
        
        # Display categorized menu with separators
        if chat_items:
            console.print("[cyan]─── Chat ───[/cyan]")
            for item in chat_items:
                console.print(f"  [bold]{item.key}[/bold])  {item.label}")
        
        if management_items:
            console.print("\n[cyan]─── Explore & Manage ───[/cyan]")
            for item in management_items:
                console.print(f"  [bold]{item.key}[/bold])  {item.label}")
        
        if advanced_items:
            console.print("\n[cyan]─── Configure ───[/cyan]")
            for item in advanced_items:
                console.print(f"  [bold]{item.key}[/bold])  {item.label}")
        
        if control_items:
            console.print("\n[cyan]─── Help & Info ───[/cyan]")
            for item in control_items:
                console.print(f"  [bold]{item.key}[/bold])  {item.label}")
        
        if quit_items:
            console.print("\n[cyan]─── Exit ───[/cyan]")
            for item in quit_items:
                console.print(f"  [bold]{item.key}[/bold])  {item.label}")
        
        console.print()
        
        # Get user input
        try:
            choice = console.input("[bold]Enter your choice [/bold](Q to quit): ").upper().strip()
            return choice if choice else None
        except KeyboardInterrupt:
            return "Q"

    def run(self):
        """Main menu loop with first-run wizard"""
        from lmapp.ui.first_run import FirstRunWizard
        
        # Run first-time setup wizard if needed
        config = self.config_manager.load()
        if not config.completed_setup:
            wizard = FirstRunWizard()
            wizard.run()
        
        # Main menu loop
        while self.running:
            self.display()
            choice = self.get_choice()

            if choice:
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

    # ============================================================================
    # MENU ACTIONS
    # ============================================================================

    def start_chat(self):
        """Start chat - with auto-setup for beginners"""
        backend = self.detector.get_best_backend()

        if not backend:
            console.print("[red]No backend found![/red]")
            console.print("\n[dim]A backend like Ollama is required to use LMAPP.[/dim]")
            
            q = [inquirer.Confirm("install", message="Install a backend now?", default=True)]
            if inquirer.prompt(q).get("install"):
                self.manage_models()
            return

        # Ensure backend is running
        if not backend.is_running():
            with console.status("Starting backend..."):
                if not backend.start():
                    console.print("[red]Failed to start backend.[/red]")
                    console.input("[dim]Press Enter to continue...[/dim]")
                    return

        # Get available models
        with console.status("Fetching models..."):
            models = backend.list_models() or []

        if not models:
            console.print("[yellow]No models found.[/yellow]")
            q = [inquirer.Confirm("download", message="Download a model?", default=True)]
            if inquirer.prompt(q).get("download"):
                self.manage_models()
                return
            else:
                return

        # Select or auto-use model
        config = self.config_manager.load()
        model = config.default_model if config.default_model in models else models[0]

        if len(models) > 1 and model not in models:
            q = [inquirer.List("model", message="Choose a model", choices=models)]
            model = inquirer.prompt(q).get("model")

        if not model:
            return

        try:
            session = ChatSession(backend, model=model)
            launch_chat(session)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.input("[dim]Press Enter to continue...[/dim]")

    def manage_plugins(self):
        """Browse and execute plugins"""
        from lmapp.plugins.plugin_manager import PluginManager
        
        config = self.config_manager.load()
        self.plugin_manager = PluginManager()
        
        if config.advanced_mode:
            self._manage_plugins_advanced()
        else:
            self._manage_plugins_beginner()

    def _manage_plugins_beginner(self):
        """Simplified plugin interface for beginners - load real plugins"""
        while True:
            console.clear()
            console.print("[bold cyan]🔌 Plugins[/bold cyan]\n")
            
            # Discover actual plugins
            plugin_paths = self.plugin_manager.discover_plugins()
            
            if not plugin_paths:
                console.print("[dim]No plugins found[/dim]")
                console.print("[yellow]Visit github.com/nabaznyl/lmapp for plugins[/yellow]")
                console.input("\n[dim]Press Enter to go back...[/dim]")
                break
            
            # Load plugins and group by category/tags
            plugins_by_category = {}
            choices = []
            
            for plugin_path in plugin_paths:
                plugin_info = self.plugin_manager.load_plugin(plugin_path)
                if plugin_info and plugin_info.metadata:
                    name = plugin_info.metadata.name
                    desc = plugin_info.metadata.description or "No description"
                    tags = plugin_info.metadata.tags or ["General"]
                    
                    category = tags[0] if tags else "General"
                    if category not in plugins_by_category:
                        plugins_by_category[category] = []
                        choices.append((f"[bold cyan]{category}[/bold cyan]", f"HEADER_{category}"))
                    
                    plugins_by_category[category].append((name, plugin_info))
                    choices.append((f"  {name:<25} - {desc[:40]}", name))
                    choices.append(("", "SPACER"))
            
            if not choices:
                console.print("[dim]No plugins available[/dim]")
                console.input("[dim]Press Enter to go back...[/dim]")
                break
            
            choices.append(("Back to Menu", "back"))
            
            q = [inquirer.List("plugin", message="Select a plugin", choices=choices)]
            answer = inquirer.prompt(q)
            
            if not answer:
                break
            
            selected = answer.get("plugin")
            if selected in ["back"] or selected.startswith("HEADER_") or selected == "SPACER":
                if selected == "back":
                    break
                continue
            
            # Find and execute selected plugin
            for category, plugins in plugins_by_category.items():
                for name, plugin_info in plugins:
                    if name == selected:
                        self._execute_plugin(plugin_info)
                        break

    def _manage_plugins_advanced(self):
        """Full plugin management for advanced users - load real plugins"""
        while True:
            console.clear()
            console.print("[bold cyan]🔌 Plugins (Advanced Mode)[/bold cyan]\n")
            
            # Discover actual plugins
            plugin_paths = self.plugin_manager.discover_plugins()
            
            if not plugin_paths:
                console.print("[dim]No plugins found[/dim]")
                console.print("[yellow]To add plugins, place them in ~/.lmapp/plugins/[/yellow]")
                console.input("\n[dim]Press Enter to go back...[/dim]")
                break
            
            # Load and display all plugins
            choices = []
            loaded_plugins = {}
            
            for plugin_path in plugin_paths:
                plugin_info = self.plugin_manager.load_plugin(plugin_path)
                if plugin_info and plugin_info.metadata:
                    name = plugin_info.metadata.name
                    version = plugin_info.metadata.version or "unknown"
                    desc = plugin_info.metadata.description or "No description"
                    loaded_plugins[name] = plugin_info
                    
                    status = "✓" if plugin_info.is_loaded else "✗"
                    choices.append((f"{status} {name:<20} v{version:<10} - {desc[:35]}", name))
            
            choices.extend([
                ("", "SPACER"),
                ("Browse Plugin Repository", "repo"),
                ("Back to Menu", "back"),
            ])
            
            q = [inquirer.List("plugin", message="Choose plugin", choices=choices)]
            answer = inquirer.prompt(q)
            
            if not answer:
                break
            
            selected = answer.get("plugin")
            if selected == "back":
                break
            elif selected == "repo":
                console.print("[yellow]Plugin repository: github.com/nabaznyl/lmapp/plugins[/yellow]")
                console.input("[dim]Press Enter to continue...[/dim]")
            elif selected in loaded_plugins:
                self._execute_plugin(loaded_plugins[selected])

    def _execute_plugin(self, plugin_info):
        """Execute a plugin and display output
        
        Args:
            plugin_info: PluginInfo object with loaded plugin
        """
        try:
            console.clear()
            console.print(f"[bold cyan]{plugin_info.metadata.name}[/bold cyan]\n")
            console.print(f"[dim]{plugin_info.metadata.description}[/dim]\n")
            
            # Try to execute the plugin
            if plugin_info.plugin and hasattr(plugin_info.plugin, 'execute'):
                with console.status(f"Running {plugin_info.metadata.name}..."):
                    result = plugin_info.plugin.execute()
                
                if result:
                    console.print("[green]✓ Completed successfully[/green]")
                    console.print(f"\n[dim]Output:[/dim]\n{result}")
                else:
                    console.print("[yellow]Plugin executed but no output[/yellow]")
            else:
                console.print("[yellow]Plugin interface not yet available[/yellow]")
                console.print("[dim]Plugin loading UI coming soon[/dim]")
        
        except Exception as e:
            console.print(f"[red]✗ Error executing plugin: {e}[/red]")
            console.print("[dim]Check plugin compatibility and configuration[/dim]")
        
        console.input("\n[dim]Press Enter to go back...[/dim]")

    def manage_models(self):
        """Download and manage models - auto-detects hardware"""
        backend = self.detector.get_best_backend()

        if not backend:
            console.print("[red]No backend installed![/red]")
            q = [inquirer.Confirm("install", message="Install Ollama?", default=True)]
            if inquirer.prompt(q).get("install"):
                self._install_backend_auto()
            return

        while True:
            console.clear()
            console.print(f"[bold cyan]Models ({backend.backend_display_name()})[/bold cyan]\n")

            if not backend.is_running():
                console.print("[yellow]Starting backend...[/yellow]\n")
                if not backend.start():
                    console.print("[red]Failed to start backend[/red]")
                    console.input("[dim]Press Enter to continue...[/dim]")
                    return

            with console.status("Fetching models..."):
                models = backend.list_models() or []

            if models:
                console.print("[bold]Installed Models:[/bold]")
                for m in models:
                    console.print(f"  ✓ {m}")
            else:
                console.print("[dim]No models installed[/dim]")

            console.print()

            q = [inquirer.List(
                "action",
                message="Choose an action",
                choices=[
                    ("Download New Model", "download"),
                    ("Back to Menu", "back"),
                ],
            )]

            answer = inquirer.prompt(q)
            if not answer or answer.get("action") == "back":
                break

            if answer.get("action") == "download":
                self._download_model_ui(backend)

    def _download_model_ui(self, backend):
        """Model download interface with hardware detection"""
        ram_gb = psutil.virtual_memory().total / (1024**3)
        installed = [m.split(":")[0] for m in (backend.list_models() or [])]

        # Hardware-optimized model recommendations
        models = [
            {"id": "qwen2.5:0.5b", "name": "Qwen 2.5", "size": "0.5B", "speed": "⚡ Ultra-Fast", "ram": 2},
            {"id": "tinyllama", "name": "TinyLlama", "size": "1.1B", "speed": "⚡ Fast", "ram": 2},
            {"id": "llama3.2:1b", "name": "Llama 3.2", "size": "1B", "speed": "⚡ Fast", "ram": 3},
            {"id": "llama3.2:3b", "name": "Llama 3.2", "size": "3B", "speed": "🔥 Balanced", "ram": 4},
            {"id": "phi3", "name": "Phi-3 Mini", "size": "3.8B", "speed": "🔥 Good", "ram": 4},
            {"id": "mistral", "name": "Mistral", "size": "7B", "speed": "💪 Standard", "ram": 6},
            {"id": "llama3.1", "name": "Llama 3.1", "size": "8B", "speed": "💪 Excellent", "ram": 8},
            {"id": "neural-chat", "name": "Neural Chat", "size": "7B", "speed": "💪 Optimized", "ram": 6},
        ]

        # Filter: compatible RAM + not installed
        compatible = [m for m in models if m["ram"] <= ram_gb and m["id"].split(":")[0] not in installed]

        if not compatible:
            console.print("[yellow]All compatible models already installed[/yellow]")
            console.input("[dim]Press Enter to continue...[/dim]")
            return

        choices = [
            (f"{m['name']:<15} {m['size']:<6} {m['speed']:<15}", m['id'])
            for m in compatible
        ]
        choices.append(("Custom model name...", "custom"))
        choices.append(("Back", "back"))

        q = [inquirer.List("model", message="Select a model to download", choices=choices)]
        answer = inquirer.prompt(q)
        model = answer.get("model") if answer else None

        if model == "back" or not model:
            return

        if model == "custom":
            model = console.input("Enter model name (e.g., mistral, llama3): ").strip()
            if not model:
                return

        console.print(f"\n[cyan]Downloading {model}...[/cyan]")
        if hasattr(backend, "download_model") and backend.download_model(model):
            console.print(f"[green]✓ Model '{model}' downloaded![/green]")
        else:
            console.print(f"[red]✗ Failed to download '{model}'[/red]")

        console.input("[dim]Press Enter to continue...[/dim]")

    def _install_backend_auto(self):
        """Auto-install best backend for system"""
        console.print("[cyan]Detecting system...[/cyan]\n")

        available = [b for b in self.detector.backends if b.backend_name() != "mock"]
        if not available:
            console.print("[red]No installable backends found[/red]")
            return

        # Recommend Ollama by default (most compatible)
        recommended = next((b for b in available if b.backend_name() == "ollama"), available[0])

        console.print(f"[dim]Recommended: {recommended.backend_display_name()}[/dim]\n")

        with console.status(f"Installing {recommended.backend_display_name()}..."):
            if recommended.install():
                console.print(f"[green]✓ {recommended.backend_display_name()} installed![/green]")
            else:
                console.print(f"[red]✗ Installation failed[/red]")

        console.input("[dim]Press Enter to continue...[/dim]")

    def show_api(self):
        """REST API documentation (Advanced only)"""
        api_text = """
[bold cyan]REST API Endpoints[/bold cyan]

[bold]Chat:[/bold]
  POST /chat - Send message
  POST /chat/stream - Stream response
  GET /chat/history - Get conversation

[bold]Plugins:[/bold]
  GET /plugins - List all
  POST /plugins/{id} - Execute
  GET /plugins/{id}/status

[bold]Models:[/bold]
  GET /models - List available
  POST /models/{id}/select

[bold]System:[/bold]
  GET /health - Health check
  GET /metrics - Performance stats

[dim]Run: lmapp server --help[/dim]
        """
        console.print(Panel(api_text, border_style="cyan"))
        console.input("\n[dim]Press Enter to continue...[/dim]")

    def show_dev_tools(self):
        """Developer tools (Advanced only)"""
        console.print("[bold cyan]Developer Tools[/bold cyan]\n")
        console.print("[yellow]Coming soon:[/yellow]")
        console.print("  • Debug logging viewer")
        console.print("  • Performance profiler")
        console.print("  • Error history")
        console.print("  • Plugin tester")
        console.input("\n[dim]Press Enter to continue...[/dim]")

    def configure(self):
        """Settings interface - simplified for beginners"""
        config = self.config_manager.load()

        while True:
            console.clear()
            console.print("[bold cyan]Settings[/bold cyan]\n")

            choices = []

            if not config.advanced_mode:
                choices.extend([
                    ("Dark Mode (Coming)", "dark-mode"),
                    ("Default Model", "default-model"),
                    ("Enable Advanced Mode", "advanced-mode"),
                ])
            else:
                choices.extend([
                    ("Dark Mode (Coming)", "dark-mode"),
                    ("Default Model", "default-model"),
                    ("Backend", "backend"),
                    ("Temperature", "temperature"),
                    ("Disable Advanced Mode", "advanced-mode"),
                ])

            choices.append(("Back to Menu", "back"))

            q = [inquirer.List("setting", message="Choose a setting", choices=choices)]
            answer = inquirer.prompt(q)
            setting = answer.get("setting") if answer else "back"

            if setting == "back":
                break

            elif setting == "default-model":
                backend = self.detector.get_best_backend()
                if backend and backend.is_running():
                    models = backend.list_models() or []
                    if models:
                        q = [inquirer.List("model", message="Select default model", choices=models)]
                        ans = inquirer.prompt(q)
                        if ans:
                            config.default_model = ans.get("model")
                            self.config_manager.save(config)
                            console.print("[green]✓ Default model updated[/green]")
                    else:
                        console.print("[yellow]No models found[/yellow]")
                else:
                    console.print("[yellow]Backend not running[/yellow]")
                console.input("[dim]Press Enter to continue...[/dim]")

            elif setting == "advanced-mode":
                config.advanced_mode = not config.advanced_mode
                self.config_manager.save(config)
                state = "[green]ENABLED[/green]" if config.advanced_mode else "[dim]DISABLED[/dim]"
                console.print(f"\nAdvanced Mode {state}")
                console.input("[dim]Press Enter to continue...[/dim]")

            elif setting in ["dark-mode", "backend", "temperature"]:
                console.print("[yellow]Coming soon[/yellow]")
                console.input("[dim]Press Enter to continue...[/dim]")

    def show_help(self):
        """Help & Documentation"""
        help_text = """
[bold cyan]Help & Documentation[/bold cyan]

[bold]Getting Started:[/bold]
1. Select "Start Chat" from main menu
2. LMAPP auto-downloads a model for your hardware
3. Start chatting with your local AI!

[bold]Using Plugins:[/bold]
From chat, press [bold]Ctrl+P[/bold] to access plugins:
• [bold]Auditor:[/bold] Review your code
• [bold]Translator:[/bold] Translate text
• [bold]Knowledge Base:[/bold] Search documents
• [bold]...and 5 more[/bold]

[bold]Keyboard Shortcuts:[/bold]
• [bold]Ctrl+C:[/bold] Exit chat
• [bold]Ctrl+L:[/bold] Clear screen
• [bold]/help:[/bold] In-chat help

[bold]Resources:[/bold]
• GitHub: github.com/nabaznyl/lmapp
• Docs: github.com/nabaznyl/lmapp/wiki
• Issues: github.com/nabaznyl/lmapp/issues

[bold]Tips:[/bold]
• Models stay on your machine (privacy first)
• No cloud calls, works offline
• Enable Advanced Mode for more control
        """
        console.print(Panel(help_text, border_style="cyan"))
        console.input("\n[dim]Press Enter to continue...[/dim]")

    def show_about(self):
        """About screen with hardware info and mode toggle"""
        while True:
            config = self.config_manager.load()
            mode_text = "[green]ENABLED ✓[/green]" if config.advanced_mode else "[yellow]DISABLED[/yellow]"

            # Get hardware info
            memory = psutil.virtual_memory()
            cpu_count = psutil.cpu_count()
            memory_gb = memory.total / (1024**3)
            
            # Get recommended model
            if memory_gb < 2:
                recommended = "qwen2.5:0.5b (370MB) - Minimal"
            elif memory_gb < 4:
                recommended = "llama3.2:1b (950MB) - Light"
            elif memory_gb < 8:
                recommended = "llama3.2:3b (1.9GB) - Balanced"
            else:
                recommended = "llama3.1 (8GB) - Powerful"

            about_text = f"""
[bold cyan]LMAPP[/bold cyan] v{__version__}

Beautiful AI. Complete control. Your data, always.

[bold]System Information:[/bold]
• RAM: {memory_gb:.1f}GB
• CPU Cores: {cpu_count}
• Recommended Model: {recommended}

[bold]Current Configuration:[/bold]
• Default Model: {config.model}
• Backend: {config.backend}
• Advanced Mode: {mode_text}

[dim]MIT Licensed • Privacy-First • Fully Local[/dim]
            """
            console.print(Panel(about_text, title="About LMAPP", border_style="blue"))

            q = [inquirer.List(
                "action",
                message="Choose an option",
                choices=[
                    ("Toggle Advanced Mode", "toggle"),
                    ("View All System Info", "info"),
                    ("Back to Menu", "back"),
                ],
            )]

            answer = inquirer.prompt(q)
            action = answer.get("action") if answer else "back"

            if action == "back":
                break
            elif action == "toggle":
                config.advanced_mode = not config.advanced_mode
                self.config_manager.save(config)
                state = "[green]ENABLED ✓[/green]" if config.advanced_mode else "[yellow]DISABLED[/yellow]"
                console.clear()
                console.print(f"\n[bold]Advanced Mode {state}[/bold]")
                console.print("\n[dim]Menu will update on next screen...[/dim]")
                console.input("[dim]Press Enter to return to main menu[/dim]")
                # Return to main menu - it will rebuild items automatically
                break
            elif action == "info":
                # Get detailed system info
                backend = self.detector.get_best_backend()
                backend_name = backend.backend_display_name() if backend else "None"
                
                info = f"""
[bold cyan]System Information[/bold cyan]

[bold]Hardware:[/bold]
• RAM: {memory_gb:.1f}GB (Total)
• CPU: {cpu_count} cores
• Available Memory: {memory.available / (1024**3):.1f}GB

[bold]Software:[/bold]
• LMAPP Version: {__version__}
• Detected Backend: {backend_name}
• Backend Status: {'Running ✓' if backend and backend.is_running() else 'Not Running'}

[bold]Recommended Model:[/bold]
{recommended}

[bold]Advanced Mode:[/bold]
{mode_text}
                """
                console.print(Panel(info, border_style="green", title="System Details"))
                console.input("\n[dim]Press Enter to continue...[/dim]")


    def quit(self):
        """Exit application"""
        self.running = False


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
