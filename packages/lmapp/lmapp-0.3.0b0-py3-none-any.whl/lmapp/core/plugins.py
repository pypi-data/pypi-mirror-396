"""
Plugin architecture for LMAPP v0.2.4.

Allows community members to extend LMAPP with custom functionality.
Plugins can add new commands, integrate with external services, or modify behavior.
"""

import importlib.util
import json
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type


class PluginMetadata:
    """Metadata for a plugin."""

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        author: str,
        main_class: str,
        dependencies: Optional[List[str]] = None,
    ):
        """Initialize plugin metadata."""
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.main_class = main_class
        self.dependencies = dependencies or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "main_class": self.main_class,
            "dependencies": self.dependencies,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PluginMetadata":
        """Create from dictionary."""
        return PluginMetadata(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            main_class=data["main_class"],
            dependencies=data.get("dependencies"),
        )


class BasePlugin(ABC):
    """Base class for all LMAPP plugins."""

    def __init__(self, metadata: PluginMetadata):
        """Initialize plugin."""
        self.metadata = metadata
        self.is_enabled = False

    @abstractmethod
    def on_initialize(self) -> bool:
        """Called when plugin is loaded. Return True if successful."""
        pass

    @abstractmethod
    def on_cleanup(self) -> None:
        """Called when plugin is unloaded."""
        pass

    def register_command(self, name: str, handler: callable) -> None:
        """Register a command handler."""
        pass

    def register_hook(self, hook_name: str, handler: callable) -> None:
        """Register a hook handler."""
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "metadata": self.metadata.to_dict(),
            "enabled": self.is_enabled,
        }


class PluginManager:
    """Manages plugin loading, execution, and lifecycle."""

    def __init__(self, plugins_dir: Optional[Path] = None):
        """Initialize plugin manager."""
        if plugins_dir is None:
            home = Path.home()
            plugins_dir = home / ".lmapp" / "plugins"

        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

        self.plugins: Dict[str, BasePlugin] = {}
        self.hooks: Dict[str, List[callable]] = {}
        self.commands: Dict[str, callable] = {}

    def discover_plugins(self) -> List[PluginMetadata]:
        """Discover available plugins in plugins directory."""
        plugins = []

        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue

            manifest_file = plugin_dir / "plugin.json"
            if not manifest_file.exists():
                continue

            try:
                metadata_dict = json.loads(manifest_file.read_text())
                metadata = PluginMetadata.from_dict(metadata_dict)
                plugins.append(metadata)
            except (json.JSONDecodeError, KeyError):
                continue

        return plugins

    def load_plugin(self, plugin_name: str) -> bool:
        """Load and initialize a plugin."""
        plugin_dir = self.plugins_dir / plugin_name

        if not plugin_dir.exists():
            return False

        manifest_file = plugin_dir / "plugin.json"
        if not manifest_file.exists():
            return False

        try:
            metadata_dict = json.loads(manifest_file.read_text())
            metadata = PluginMetadata.from_dict(metadata_dict)

            # Load the main module
            main_file = plugin_dir / "main.py"
            if not main_file.exists():
                return False

            spec = importlib.util.spec_from_file_location(plugin_name, main_file)
            if spec is None or spec.loader is None:
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)

            # Get the plugin class
            if not hasattr(module, metadata.main_class):
                return False

            plugin_class: Type[BasePlugin] = getattr(module, metadata.main_class)
            plugin = plugin_class(metadata)

            # Initialize plugin
            if not plugin.on_initialize():
                return False

            plugin.is_enabled = True
            self.plugins[plugin_name] = plugin

            return True
        except Exception:
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload and cleanup a plugin."""
        if plugin_name not in self.plugins:
            return False

        plugin = self.plugins[plugin_name]
        plugin.on_cleanup()
        del self.plugins[plugin_name]

        if plugin_name in sys.modules:
            del sys.modules[plugin_name]

        return True

    def register_hook(
        self,
        hook_name: str,
        handler: callable,
        plugin_name: Optional[str] = None,
    ) -> None:
        """Register a hook handler."""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []

        self.hooks[hook_name].append(handler)

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger a hook and call all registered handlers."""
        results = []

        if hook_name in self.hooks:
            for handler in self.hooks[hook_name]:
                try:
                    result = handler(*args, **kwargs)
                    results.append(result)
                except Exception:
                    continue

        return results

    def register_command(
        self,
        command_name: str,
        handler: callable,
        plugin_name: Optional[str] = None,
    ) -> None:
        """Register a command handler."""
        key = f"{plugin_name}:{command_name}" if plugin_name else command_name
        self.commands[key] = handler

    def execute_command(self, command_name: str, *args, **kwargs) -> Any:
        """Execute a registered command."""
        if command_name in self.commands:
            try:
                return self.commands[command_name](*args, **kwargs)
            except Exception:
                return None

        return None

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins."""
        return [plugin.get_info() for plugin in self.plugins.values()]

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a loaded plugin."""
        return self.plugins.get(plugin_name)


_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager(plugins_dir: Optional[Path] = None) -> PluginManager:
    """Get or create the global PluginManager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager(plugins_dir)
    return _plugin_manager
