#!/usr/bin/env python3
"""
lmapp CLI - Main entry point
Provides the primary command-line interface for lmapp
"""
import os
import signal
from pathlib import Path
from typing import Optional

import sys
import click
from rich.console import Console
from rich.panel import Panel

from lmapp import __version__
from lmapp.ui.menu import MainMenu
from lmapp.ui.chat_ui import launch_chat
from lmapp.utils.system_check import SystemCheck
from lmapp.utils.logging import logger, LOG_FILE
from lmapp.backend.installer import BackendInstaller
from lmapp.backend.detector import BackendDetector
from lmapp.core.chat import ChatSession
from lmapp.core.nux import check_first_run, run_user_mode_setup
from lmapp.core.config import get_config_manager

console = Console()


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--dev", is_flag=True, help="Enable Developer Mode")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompts (assume yes)")
@click.pass_context
def main(ctx, version, debug, dev, yes):
    """lmapp - Local LLM Made Simple

    Your personal AI assistant, running locally on your machine.
    """
    # Set global assume_yes flag
    if yes:
        get_config_manager().update(assume_yes=True)

    if debug:

        os.environ["LMAPP_DEBUG"] = "1"
        logger.enable_debug()

    logger.debug(f"lmapp CLI started, version={__version__}, debug={debug}")

    # Setup global exception handler
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Ignore Click exceptions which are handled by Click
        if issubclass(exc_type, click.exceptions.ClickException):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Log to ErrorDB
        try:
            from lmapp.core.error_db import ErrorDB

            db = ErrorDB()
            solution = db.log_error(exc_value)

            console.print(
                f"\n[bold red]An unexpected error occurred:[/bold red] {exc_value}"
            )
            if solution:
                console.print(
                    f"\n[bold green]Suggested Solution:[/bold green] {solution}"
                )

            # Silent logging as requested
            # console.print(f"\n[dim]Error has been logged to the database. Run 'lmapp errors' to view history.[/dim]")
        except Exception:
            # Fallback if ErrorDB fails
            console.print(f"\n[bold red]Critical Error:[/bold red] {exc_value}")
            # console.print(f"[dim]Failed to log error: {e}[/dim]")

        # Call original hook if debug

        if os.environ.get("LMAPP_DEBUG"):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            sys.exit(1)

    sys.excepthook = handle_exception

    if version:
        console.print(
            f"[bold cyan]lmapp[/bold cyan] version [yellow]{__version__}[/yellow]"
        )
        sys.exit(0)

    # NUX Check
    if check_first_run():
        run_user_mode_setup()

    # Workflow Calibration Check
    # Only run if interactive, not running help, and not in test mode
    is_interactive = sys.stdin.isatty()
    is_help = "--help" in sys.argv
    is_test = "pytest" in sys.modules

    # Only prompt for workflow on main menu or chat command
    # Prevents annoying prompts on utility commands like 'server', 'status', etc.
    allowed_commands = [None, "chat"]
    should_check_workflow = (
        is_interactive 
        and not is_help 
        and not is_test 
        and ctx.invoked_subcommand in allowed_commands
    )

    if should_check_workflow:
        from lmapp.core.workflow import WorkflowManager
        from lmapp.ui.prompt import confirm

        workflow_mgr = WorkflowManager()
        if workflow_mgr.should_prompt():
            console.print("\n[bold cyan]Roles & Workflows Setup[/bold cyan]")
            console.print("Would you like to configure your AI assistant's behavior?")
            console.print("[dim](Operating rules, tool awareness, etc.)[/dim]")

            if confirm("Run setup wizard?", default=True):
                workflow_mgr.run_setup_wizard()
            else:
                # Suppress future prompts?
                if confirm("Suppress this prompt in the future?", default=True):
                    get_config_manager().update(suppress_workflow_prompt=True)

    # Handle Developer Mode flag
    if dev:
        config_manager = get_config_manager()
        config = config_manager.load()
        if not config.developer_mode:
            config.developer_mode = True
            config_manager.save(config)
            console.print("[green]Developer Mode Enabled[/green]")

    if ctx.invoked_subcommand is None:
        # No subcommand, show main menu
        show_welcome()
        menu = MainMenu()
        menu.run()


def show_welcome():
    """Display welcome message"""
    welcome_text = """
[bold cyan]Welcome to lmapp[/bold cyan] - Your Local AI Assistant

[dim]Privacy-first • Fully local • Easy to use[/dim]
    """
    console.print(Panel(welcome_text, border_style="cyan"))


@main.command()
@click.option("--model", default=None, help="Model to use for chat")
def chat(model):
    """Start a new chat session"""
    logger.debug(f"chat command started with model={model}")

    # Get detector to find best backend
    detector = BackendDetector()
    backend = None

    # Try to find a running backend
    for b in detector.detect_all():
        logger.debug(f"Checking backend: {b.backend_name()}")
        if b.is_running():
            logger.debug(f"Found running backend: {b.backend_name()}")
            backend = b
            break

    if not backend:
        # No running backend found
        available = detector.detect_all()
        logger.warning(
            f"No running backend found. Available: {[b.backend_name() for b in available]}"
        )

        if not available:
            console.print("[red]✗ No LLM backends installed[/red]")
            console.print("\nTo install a backend, run:")
            console.print("  [bold]lmapp install[/bold]")
            sys.exit(1)

        # Backend installed but not running
        console.print(
            f"[yellow]⚠️  Backend '{available[0].backend_display_name()}' is not running[/yellow]"
        )
        console.print("\nTo start it, run:")
        console.print("  [bold]lmapp install[/bold]")
        sys.exit(1)

    # Determine model to use
    chat_model = model or "tinyllama"

    # Check if model exists
    logger.debug(f"Checking for model: {chat_model}")
    models = backend.list_models()
    if chat_model not in models:
        logger.warning(f"Model '{chat_model}' not found. Available: {models}")
        console.print("[yellow]⚠️  Model not found[/yellow]")
        console.print("\nAvailable models:")
        for m in models:
            console.print(f"  - {m}")
        console.print("\nDownload a model with:")
        console.print("  [bold]lmapp install[/bold]")
        sys.exit(1)

    try:
        # Create and launch chat session
        logger.debug(
            f"Creating ChatSession with backend={backend.backend_name()}, model={chat_model}"
        )
        session = ChatSession(backend, model=chat_model)
        logger.debug("ChatSession created, launching chat UI")
        launch_chat(session)
    except ValueError as e:
        logger.error(f"ValueError in chat: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.debug("Chat interrupted by user")
        console.print("\n[yellow]Chat interrupted[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}", exc_info=True)
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        sys.exit(1)


@main.command()
def errors():
    """View error history and solutions"""
    from lmapp.core.error_db import ErrorDB
    from rich.table import Table
    from rich import box
    import time

    db = ErrorDB()
    history = db.get_history()

    if not history:
        console.print("[green]No errors recorded in the database.[/green]")
        return

    table = Table(title="Error History", box=box.ROUNDED)
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Error", style="red")
    table.add_column("Solution", style="green")

    for entry in history[-10:]:  # Show last 10
        ts = entry.get("timestamp", 0)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
        error_msg = entry.get("message", "") or entry.get(
            "error", ""
        )  # Handle both keys if schema changed
        solution = entry.get("solution", "") or "-"

        # Truncate long error messages
        if len(error_msg) > 80:
            error_msg = error_msg[:77] + "..."

        table.add_row(timestamp, error_msg, solution)

    console.print(table)
    console.print(
        f"\n[dim]Showing last {min(len(history), 10)} of {len(history)} errors. Log file: {db.db_file}[/dim]"
    )


@main.command()
def install():
    """Run the automated installation wizard"""
    logger.debug("install command started")
    console.print("[bold cyan]lmapp Installation Wizard[/bold cyan]\n")

    # Step 1: System check
    logger.debug("Running system checks")
    checker = SystemCheck()
    if checker.run_all_checks():
        console.print("\n[green]✓ System checks passed![/green]")
        logger.debug("System checks passed")
    else:
        logger.error("System checks failed")
        console.print(
            "\n[red]✗ System checks failed. Please address issues above.[/red]"
        )
        sys.exit(1)

    # Step 2: Backend installation (automated)
    logger.debug("Starting backend installation")
    installer = BackendInstaller()
    backend = installer.run_installation_wizard()

    if not backend:
        logger.warning("Backend installation cancelled or failed")
        console.print("\n[yellow]Installation cancelled or failed[/yellow]")
        sys.exit(1)

    # Step 3: Model installation (automated)
    logger.debug(f"Backend installed: {backend.backend_name()}")
    ram_gb = checker.results.get("ram_gb", 4)
    if installer.install_model(backend, ram_gb):
        logger.info("Installation complete and successful")
        console.print("\n[bold green]🎉 Installation complete![/bold green]")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("  1. Run: [bold]lmapp chat[/bold]")
        console.print("  2. Or run: [bold]lmapp[/bold] to see the menu")
    else:
        logger.warning("Model installation skipped")
        console.print("\n[yellow]Backend installed but model download skipped[/yellow]")
        console.print("[dim]You can download models later with: lmapp config[/dim]")


@main.group(invoke_without_command=True)
@click.pass_context
def model(ctx):
    """List of installed LLM's"""
    if ctx.invoked_subcommand is None:
        detector = BackendDetector()
        backend = detector.get_best_backend()

        if not backend:
            console.print("[red]No backend installed![/red]")
            return

        if not backend.is_running():
            console.print(
                f"[yellow]Backend {backend.backend_display_name()} is not running.[/yellow]"
            )
            return

        models = backend.list_models()
        console.print("[bold]Installed Models:[/bold]")
        if models:
            for m in models:
                console.print(f"  • {m}")
        else:
            console.print("  [dim]No models installed[/dim]")


@model.command()
def download():
    """Download New Model"""
    detector = BackendDetector()
    backend = detector.get_best_backend()

    if not backend:
        console.print("[red]No backend installed![/red]")
        return

    if not backend.is_running():
        console.print(
            f"[yellow]Backend {backend.backend_display_name()} is not running. Starting it...[/yellow]"
        )
        if not backend.start():
            console.print("[red]Failed to start backend.[/red]")
            return

    menu = MainMenu()
    menu.download_model_ui(backend)


# --- Server Management ---

PID_FILE = Path.home() / ".local" / "share" / "lmapp" / "server.pid"


def _get_server_pid() -> Optional[int]:
    """Get PID of running server if exists"""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            # Check if process actually exists
            try:
                os.kill(pid, 0)
                return pid
            except OSError:
                # Stale PID file
                PID_FILE.unlink()
                return None
        except ValueError:
            PID_FILE.unlink()
            return None
    return None


@main.group(name="server", invoke_without_command=True)
@click.pass_context
def server(ctx):
    """Manage the API server (start, stop, list)"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(server_start)


@server.command(name="start")
def server_start():
    """Start the API server (default)"""
    import uvicorn
    from lmapp.server.app import app

    # Check if already running
    pid = _get_server_pid()
    if pid:
        console.print(f"[yellow]Server is already running (PID: {pid})[/yellow]")
        console.print("Run [bold]lmapp server stop[/bold] to stop it.")
        return

    # Check port 8000
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", 8000))
    sock.close()
    if result == 0:
        console.print("[red]Port 8000 is already in use by another process.[/red]")
        console.print("Run [bold]lsof -i :8000[/bold] to identify it.")
        return

    console.print("[bold cyan]Starting lmapp API Server...[/bold cyan]")
    console.print("[dim]Listening on http://localhost:8000[/dim]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    # Write PID
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))

    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Server error: {e}[/red]")
    finally:
        if PID_FILE.exists():
            PID_FILE.unlink()


@server.command(name="stop")
def server_stop():
    """Stop the running server"""
    pid = _get_server_pid()
    if not pid:
        console.print("[yellow]No running server found.[/yellow]")
        return

    try:
        os.kill(pid, signal.SIGINT)
        console.print(f"[green]Stopped server (PID: {pid})[/green]")
        if PID_FILE.exists():
            PID_FILE.unlink()
    except ProcessLookupError:
        console.print("[yellow]Server process not found (stale PID file removed)[/yellow]")
        if PID_FILE.exists():
            PID_FILE.unlink()
    except Exception as e:
        console.print(f"[red]Failed to stop server: {e}[/red]")


@server.command(name="list")
def server_list():
    """List active server"""
    pid = _get_server_pid()
    if pid:
        console.print(f"[green]●[/green] Server running on port 8000 (PID: {pid})")
        console.print(f"  URL: http://localhost:8000")
    else:
        console.print("[dim]No server running[/dim]")


@server.command(name="kill")
@click.option("-a", "--all", "kill_all", is_flag=True, help="Kill all instances")
def server_kill(kill_all):
    """Force kill server processes"""
    if kill_all:
        import subprocess
        try:
            subprocess.run(["pkill", "-f", "lmapp server"], check=False)
            console.print("[green]Killed all lmapp server instances[/green]")
            if PID_FILE.exists():
                PID_FILE.unlink()
        except Exception as e:
            console.print(f"[red]Failed to kill processes: {e}[/red]")
    else:
        server_stop()


@main.command(name="serve", hidden=True)
def serve():
    """Alias for server"""
    ctx = click.get_current_context()
    ctx.invoke(server_start)


@main.command()
def status():
    """Show system status and configuration"""
    logger.debug("status command started")
    console.print("[bold]LMAPP Status Report[/bold]\n")

    # Show version and config
    from lmapp.core.config import get_config_manager

    _ = get_config_manager().get()

    console.print("[bold]Version[/bold]\n")
    console.print(f"  Version: {__version__}")
    console.print("  Status: [green]Production Ready[/green]")
    console.print("  License: [cyan]MIT (Free)[/cyan]")

    checker = SystemCheck()
    checker.run_all_checks()

    # Show backend status
    console.print("\n[bold]Backend Status[/bold]\n")
    detector = BackendDetector()
    detector.show_status_table()
    logger.debug("Status command completed")


@main.group()
def workflow():
    """Manage AI Roles & Workflows"""


@workflow.command(name="setup")
def workflow_setup():
    """Run the interactive Roles & Workflows wizard"""
    from lmapp.core.workflow import WorkflowManager

    WorkflowManager().run_setup_wizard()


@main.group()
def config():
    """Manage lmapp configuration settings"""
    logger.debug("config command group started")


@config.command(name="show")
def config_show():
    """Display current configuration"""
    logger.debug("config show command started")

    from lmapp.core.config import get_config_manager

    manager = get_config_manager()
    config = manager.load()

    content = f"[bold]Current Configuration:[/bold]\n"
    content += f"backend: {config.backend}\n"
    content += f"model: {config.model}\n"
    content += f"temperature: {config.temperature}\n"
    content += f"debug: {config.debug}\n"
    content += f"developer_mode: {config.developer_mode}"

    console.print(Panel.fit(content))
    
    # Format paths for display (replace home with ~)
    config_path = str(manager.config_file).replace(str(Path.home()), "~")
    log_path = str(LOG_FILE).replace(str(Path.home()), "~")
    
    console.print(f"[dim]Configuration file: {config_path}[/dim]")
    console.print(f"[dim]Log file: {log_path}[/dim]")


@main.group()
def plugin():
    """Manage plugins and marketplace"""
    logger.debug("plugin command group started")


@plugin.command(name="update")
def plugin_update():
    """Update plugin registries"""
    from lmapp.plugins.plugin_marketplace import get_plugin_marketplace

    marketplace = get_plugin_marketplace()
    console.print("Updating plugin registries...")
    marketplace.refresh_registries()
    console.print("[green]Registries updated successfully.[/green]")


@plugin.command(name="list")
@click.option("--registry", help="Filter by registry name")
@click.option("--certified", is_flag=True, help="Show only certified plugins")
def plugin_list(registry, certified):
    """List available plugins"""
    from lmapp.plugins.plugin_marketplace import get_plugin_marketplace
    from rich.table import Table

    marketplace = get_plugin_marketplace()
    plugins = marketplace.list_plugins(registry=registry, certified_only=certified)

    if not plugins:
        console.print("[yellow]No plugins found.[/yellow]")
        return

    table = Table(title="Available Plugins")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Description")
    table.add_column("Rating", style="yellow")
    table.add_column("Verified", style="blue")

    for p in plugins:
        verified_mark = "✓" if p.verified else ""
        table.add_row(
            p.name,
            p.version,
            p.description[:50] + "..." if len(p.description) > 50 else p.description,
            f"{p.rating} ({p.reviews})",
            verified_mark,
        )

    console.print(table)


@plugin.command(name="search")
@click.argument("query")
def plugin_search(query):
    """Search for plugins"""
    from lmapp.plugins.plugin_marketplace import get_plugin_marketplace
    from rich.table import Table

    marketplace = get_plugin_marketplace()
    results = marketplace.search_all(query)

    if not results:
        console.print(f"[yellow]No plugins found matching '{query}'.[/yellow]")
        return

    table = Table(title=f"Search Results: {query}")
    table.add_column("Registry", style="magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Verified", style="blue")

    for registry_name, p in results:
        verified_mark = "✓" if p.verified else ""
        table.add_row(
            registry_name,
            p.name,
            p.description[:50] + "..." if len(p.description) > 50 else p.description,
            verified_mark,
        )

    console.print(table)


@plugin.command(name="install")
@click.argument("plugin_name")
@click.option("--registry", default="official", help="Registry to install from")
def plugin_install(plugin_name, registry):
    """Install a plugin"""
    from lmapp.plugins.plugin_marketplace import get_plugin_marketplace

    marketplace = get_plugin_marketplace()
    console.print(
        f"Installing [cyan]{plugin_name}[/cyan] from [magenta]{registry}[/magenta]..."
    )

    if marketplace.install_plugin(plugin_name, registry):
        console.print(f"[green]Successfully installed {plugin_name}![/green]")
    else:
        console.print(
            f"[red]Failed to install {plugin_name}. Check logs for details.[/red]"
        )

    console.print(manager.show())
    console.print()
    console.print("[dim]Configuration location: ~/.config/lmapp/config.json[/dim]")
    console.print("[dim]Log location: ~/.local/share/lmapp/logs/lmapp.log[/dim]")


@config.command(name="set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a configuration value

    Examples:
        lmapp config set model mistral
        lmapp config set temperature 0.5
        lmapp config set debug true
        lmapp config set backend ollama
    """
    logger.debug(f"config set command: {key}={value}")

    from lmapp.core.config import get_config_manager, LMAppConfig
    from pydantic import ValidationError

    manager = get_config_manager()

    # Parse value based on type
    parsed_value = value
    if value.lower() in ("true", "false"):
        parsed_value = value.lower() == "true"
    elif value.replace(".", "", 1).isdigit():
        # Try to parse as float or int
        try:
            if "." in value:
                parsed_value = float(value)
            else:
                parsed_value = int(value)
        except ValueError:
            parsed_value = value

    # Validate key exists
    cfg = manager.get()
    if not hasattr(cfg, key):
        console.print(f"[red]✗ Unknown configuration key: {key}[/red]")
        console.print("\n[cyan]Valid keys:[/cyan]")
        for field_name in cfg.model_dump().keys():
            field_value = getattr(cfg, field_name)
            console.print(
                f"  [yellow]{field_name:15}[/yellow] (current: {field_value})"
            )
        logger.warning(f"Invalid config key: {key}")
        return

    # Validate the value by creating a temporary config
    try:
        test_data = cfg.model_dump()
        test_data[key] = parsed_value
        LMAppConfig(**test_data)  # This will raise ValidationError if invalid
    except ValidationError as e:
        console.print(f"[red]✗ Failed to set {key}: Invalid value[/red]")
        # Extract the error message from validation error
        for error in e.errors():
            console.print(f"  [yellow]{error['msg']}[/yellow]")
        logger.warning(f"Validation failed for {key}={parsed_value}: {e}")
        # Validation errors are non-fatal for interactive CLI usage; return
        # so the command prints a helpful message but does not exit the process.
        return
    except Exception as e:
        console.print(f"[red]✗ Failed to set {key}: {str(e)}[/red]")
        logger.error(f"Unexpected error setting {key}: {str(e)}")
        return

    # Update config
    try:
        if manager.update(**{key: parsed_value}):
            console.print(f"[green]✓ Updated {key} = {parsed_value}[/green]")
            logger.info(f"Config updated: {key}={parsed_value}")
        else:
            console.print("[red]✗ Failed to save configuration[/red]")
            logger.error(f"Failed to save config after updating {key}")
    except Exception as e:
        console.print(f"[red]✗ Failed to set {key}: {str(e)}[/red]")
        logger.error(f"Exception while setting {key}: {str(e)}")


@config.command(name="reset")
@click.confirmation_option(prompt="This will reset all settings to defaults. Continue?")
def config_reset():
    """Reset all settings to defaults"""
    logger.debug("config reset command started")

    from lmapp.core.config import ConfigManager, LMAppConfig

    manager = ConfigManager()
    default_config = LMAppConfig()

    try:
        manager.save(default_config)
        console.print("[green]✓ Configuration reset to defaults[/green]")
        console.print(manager.show())
        logger.info("Config reset to defaults")
    except Exception as e:
        console.print(f"[red]✗ Failed to reset config: {str(e)}[/red]")
        logger.error(f"Failed to reset config: {str(e)}")


@config.command(name="validate")
def config_validate():
    """Validate current configuration"""
    logger.debug("config validate command started")

    from lmapp.core.config import get_config

    try:
        cfg = get_config()
        console.print("[green]✓ Configuration is valid[/green]")
        console.print(cfg.model_dump())
        logger.debug("Config validation passed")
    except Exception as e:
        console.print(f"[red]✗ Configuration is invalid: {str(e)}[/red]")
        logger.error(f"Config validation failed: {str(e)}")


@main.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def tests(args):
    """Run the test suite (pytest wrapper)"""
    import subprocess

    cmd = ["pytest"] + list(args)
    console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
    sys.exit(subprocess.call(cmd))


@main.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def src(args):
    """Run code linting (flake8 wrapper)"""
    import subprocess

    # Default to src/ if no args provided, otherwise pass args to flake8
    target = list(args) if args else ["src/"]
    cmd = ["flake8"] + target
    console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
    sys.exit(subprocess.call(cmd))


@main.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def format(args):
    """Run code formatting (black wrapper)"""
    import subprocess

    target = list(args) if args else ["src/", "tests/"]
    cmd = ["black"] + target
    console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
    sys.exit(subprocess.call(cmd))


@main.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def lint(args):
    """Run code linting (flake8 wrapper)"""
    import subprocess

    target = list(args) if args else ["src/", "tests/"]
    cmd = ["flake8"] + target
    console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
    sys.exit(subprocess.call(cmd))


@main.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def types(args):
    """Run type checking (mypy wrapper)"""
    import subprocess

    target = list(args) if args else ["src/"]
    cmd = ["mypy"] + target
    console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()

# Backwards-compatible alias: some tests and external code import `cli`.
# Provide `cli` as an alias to the main click entrypoint.
cli = main
