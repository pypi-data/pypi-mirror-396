"""
Plugin system for LMAPP v0.2.4.

Enables community contributions and extensibility through a modular plugin architecture.
Plugins can extend functionality like git integration, code analysis, summarization, etc.

Features:
- Plugin discovery and loading
- Plugin lifecycle management
- Plugin metadata and versioning
- Plugin configuration support
- Safe plugin execution with error isolation
"""

import importlib
import json
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import inspect


class PluginStatus(Enum):
    """Plugin status states."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class PluginMetadata:
    """Metadata about a plugin."""
    
    name: str
    version: str
    description: str
    author: str
    license: str = "MIT"
    dependencies: List[str] = field(default_factory=list)
    entry_point: str = ""  # e.g., "my_plugin:MyPlugin"
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "dependencies": self.dependencies,
            "entry_point": self.entry_point,
            "tags": self.tags,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PluginMetadata":
        """Create from dictionary."""
        return PluginMetadata(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            license=data.get("license", "MIT"),
            dependencies=data.get("dependencies", []),
            entry_point=data.get("entry_point", ""),
            tags=data.get("tags", []),
        )


class BasePlugin(ABC):
    """Base class for all LMAPP plugins."""
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the plugin.
        
        Args:
            config: Plugin configuration dictionary
        """
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the plugin's main functionality.
        
        Returns:
            Plugin execution result
        """
        pass
    
    def cleanup(self) -> None:
        """Cleanup when plugin is unloaded (optional)."""
        pass
    
    def get_commands(self) -> Dict[str, Callable]:
        """
        Get CLI commands provided by this plugin.
        
        Returns:
            Dict of {command_name: handler_function}
        """
        return {}


@dataclass
class PluginInfo:
    """Information about a loaded plugin."""
    
    metadata: PluginMetadata
    plugin: BasePlugin
    status: PluginStatus = PluginStatus.UNLOADED
    error_message: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)


class PluginManager:
    """Manages plugin discovery, loading, and execution."""
    
    def __init__(self, plugins_dir: Optional[Path] = None):
        """
        Initialize PluginManager.
        
        Args:
            plugins_dir: Directory containing plugins (default: ~/.lmapp/plugins/)
        """
        if plugins_dir is None:
            home = Path.home()
            plugins_dir = home / ".lmapp" / "plugins"
        
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_plugins: Dict[str, PluginInfo] = {}
        self.registry_file = self.plugins_dir / "registry.json"
    
    def discover_plugins(self) -> List[Path]:
        """
        Discover available plugins.
        
        Returns:
            List of paths to plugin directories
        """
        plugins = []
        
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                # Look for plugin.json or __init__.py
                if (item / "plugin.json").exists() or (item / "__init__.py").exists():
                    plugins.append(item)
        
        return sorted(plugins)
    
    def load_plugin(self, plugin_path: Path, config: Optional[Dict[str, Any]] = None) -> Optional[PluginInfo]:
        """
        Load a single plugin.
        
        Args:
            plugin_path: Path to plugin directory
            config: Plugin configuration
        
        Returns:
            PluginInfo if successful, None otherwise
        """
        try:
            # Load metadata
            metadata_file = plugin_path / "plugin.json"
            if not metadata_file.exists():
                return None
            
            with open(metadata_file, "r") as f:
                metadata_dict = json.load(f)
            
            metadata = PluginMetadata.from_dict(metadata_dict)
            
            # Load plugin class
            plugin = self._load_plugin_class(plugin_path, metadata)
            
            if plugin is None:
                return None
            
            # Create PluginInfo
            info = PluginInfo(metadata=metadata, plugin=plugin, config=config or {})
            
            # Initialize
            try:
                plugin.initialize(info.config)
                info.status = PluginStatus.LOADED
            except Exception as e:
                info.status = PluginStatus.ERROR
                info.error_message = str(e)
                return info
            
            self.loaded_plugins[metadata.name] = info
            return info
        
        except Exception as e:
            return None
    
    def load_all_plugins(self) -> int:
        """
        Load all available plugins.
        
        Returns:
            Number of successfully loaded plugins
        """
        plugins = self.discover_plugins()
        loaded_count = 0
        
        for plugin_path in plugins:
            config = self._load_plugin_config(plugin_path)
            info = self.load_plugin(plugin_path, config)
            
            if info and info.status != PluginStatus.ERROR:
                loaded_count += 1
        
        return loaded_count
    
    def get_plugin(self, name: str) -> Optional[PluginInfo]:
        """Get a loaded plugin by name."""
        return self.loaded_plugins.get(name)
    
    def execute_plugin(self, name: str, *args, **kwargs) -> Optional[Any]:
        """
        Execute a plugin's main functionality.
        
        Args:
            name: Plugin name
            *args: Arguments to pass to plugin
            **kwargs: Keyword arguments to pass to plugin
        
        Returns:
            Plugin execution result
        """
        info = self.get_plugin(name)
        
        if not info:
            return None
        
        if info.status == PluginStatus.ERROR:
            return None
        
        try:
            return info.plugin.execute(*args, **kwargs)
        except Exception as e:
            info.status = PluginStatus.ERROR
            info.error_message = str(e)
            return None
    
    def get_plugin_commands(self) -> Dict[str, Callable]:
        """
        Get all CLI commands from all plugins.
        
        Returns:
            Dict of {command_name: handler_function}
        """
        commands = {}
        
        for plugin_info in self.loaded_plugins.values():
            if plugin_info.status != PluginStatus.ERROR:
                try:
                    plugin_commands = plugin_info.plugin.get_commands()
                    commands.update(plugin_commands)
                except Exception:
                    pass
        
        return commands
    
    def unload_plugin(self, name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            name: Plugin name
        
        Returns:
            True if successful
        """
        info = self.get_plugin(name)
        
        if not info:
            return False
        
        try:
            info.plugin.cleanup()
            del self.loaded_plugins[name]
            return True
        except Exception:
            return False
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all loaded plugins.
        
        Returns:
            List of plugin information dictionaries
        """
        plugins_info = []
        
        for name, info in self.loaded_plugins.items():
            plugins_info.append({
                "name": name,
                "version": info.metadata.version,
                "description": info.metadata.description,
                "author": info.metadata.author,
                "status": info.status.value,
                "error": info.error_message,
            })
        
        return sorted(plugins_info, key=lambda x: x["name"])
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded plugins."""
        statuses = {}
        for info in self.loaded_plugins.values():
            status = info.status.value
            statuses[status] = statuses.get(status, 0) + 1
        
        return {
            "total_plugins": len(self.loaded_plugins),
            "by_status": statuses,
            "with_errors": len([p for p in self.loaded_plugins.values() if p.status == PluginStatus.ERROR]),
        }
    
    def _load_plugin_class(self, plugin_path: Path, metadata: PluginMetadata) -> Optional[BasePlugin]:
        """Load the plugin class from module."""
        try:
            # Add plugin path to sys.path temporarily
            plugin_path_str = str(plugin_path)
            if plugin_path_str not in sys.path:
                sys.path.insert(0, plugin_path_str)
            
            # Import module and get class
            entry_point = metadata.entry_point
            if not entry_point:
                return None
            
            module_name, class_name = entry_point.split(":")
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)
            
            # Verify it's a BasePlugin
            if not issubclass(plugin_class, BasePlugin):
                return None
            
            return plugin_class()
        
        except Exception:
            return None
    
    def _load_plugin_config(self, plugin_path: Path) -> Dict[str, Any]:
        """Load plugin configuration."""
        config_file = plugin_path / "config.json"
        
        if not config_file.exists():
            return {}
        
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager(plugins_dir: Optional[Path] = None) -> PluginManager:
    """Get or create the global PluginManager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager(plugins_dir)
    return _plugin_manager
