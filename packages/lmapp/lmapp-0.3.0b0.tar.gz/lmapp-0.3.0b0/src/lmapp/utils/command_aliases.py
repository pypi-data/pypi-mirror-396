"""
Command aliases for LMAPP v0.2.3.

Provides convenient shortcuts for common commands.
Users can define custom aliases in ~/.lmapp/aliases.json
"""

import json
from pathlib import Path
from typing import Dict, Optional, List, Tuple


class CommandAliasManager:
    """Manages command aliases for LMAPP CLI."""
    
    # Built-in default aliases (hardcoded shortcuts)
    DEFAULT_ALIASES = {
        # Chat shortcuts
        "c": "chat",
        "ask": "chat",
        "talk": "chat",
        
        # Model management
        "m": "models",
        "ml": "models list",
        "md": "models download",
        "mr": "models remove",
        "mup": "models update",
        
        # Backend management
        "b": "backend",
        "bl": "backend list",
        "bs": "backend switch",
        "bst": "backend status",
        
        # Configuration
        "cfg": "config",
        "conf": "config",
        "settings": "config",
        
        # Session management
        "s": "session",
        "sl": "session list",
        "sn": "session new",
        "sd": "session delete",
        "ss": "session switch",
        "sc": "session clear-history",
        
        # System commands
        "stat": "status",
        "st": "status",
        "info": "status --detailed",
        "h": "help",
        "v": "version",
        "doc": "help",
        
        # Utility shortcuts
        "clean": "cache clear",
        "clear": "cache clear",
        "logs": "logs tail",
        "l": "logs tail",
        "restart": "backend restart",
    }
    
    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """
        Initialize CommandAliasManager.
        
        Args:
            config_dir: Config directory (default: ~/.lmapp/)
        """
        if config_dir is None:
            home = Path.home()
            config_dir = home / ".lmapp"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.aliases_file = self.config_dir / "aliases.json"
        self._custom_aliases: Dict[str, str] = {}
        self._load_custom_aliases()
    
    def _load_custom_aliases(self) -> None:
        """Load custom aliases from file."""
        if self.aliases_file.exists():
            try:
                with open(self.aliases_file, "r") as f:
                    self._custom_aliases = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._custom_aliases = {}
        else:
            self._custom_aliases = {}
    
    def _save_custom_aliases(self) -> None:
        """Save custom aliases to file."""
        with open(self.aliases_file, "w") as f:
            json.dump(self._custom_aliases, f, indent=2)
    
    def get_all_aliases(self) -> Dict[str, str]:
        """Get all aliases (default + custom, custom overrides default)."""
        aliases = self.DEFAULT_ALIASES.copy()
        aliases.update(self._custom_aliases)
        return aliases
    
    def resolve_command(self, input_command: str) -> Tuple[str, bool]:
        """
        Resolve a command (if it's an alias, expand it).
        
        Args:
            input_command: The command to resolve
        
        Returns:
            Tuple of (resolved_command, was_alias)
        """
        all_aliases = self.get_all_aliases()
        
        # Check if input_command matches an alias
        if input_command in all_aliases:
            return all_aliases[input_command], True
        
        return input_command, False
    
    def resolve_with_args(self, args: List[str]) -> Tuple[List[str], bool]:
        """
        Resolve command with arguments.
        
        Args:
            args: List of command arguments (args[0] is command)
        
        Returns:
            Tuple of (resolved_args, was_alias)
        """
        if not args:
            return args, False
        
        first_arg = args[0]
        all_aliases = self.get_all_aliases()
        
        if first_arg in all_aliases:
            expanded = all_aliases[first_arg].split()
            return expanded + args[1:], True
        
        return args, False
    
    def add_alias(self, alias: str, command: str) -> bool:
        """
        Add a custom alias.
        
        Args:
            alias: Short alias
            command: Command to expand to
        
        Returns:
            True if added, False if invalid
        """
        # Validate
        if not alias or not command:
            return False
        
        if not alias.replace("-", "").replace("_", "").isalnum():
            return False
        
        if alias in self.DEFAULT_ALIASES:
            return False  # Can't override built-in aliases
        
        # Add and save
        self._custom_aliases[alias] = command
        self._save_custom_aliases()
        return True
    
    def remove_alias(self, alias: str) -> bool:
        """Remove a custom alias."""
        if alias in self._custom_aliases:
            del self._custom_aliases[alias]
            self._save_custom_aliases()
            return True
        return False
    
    def get_alias(self, alias: str) -> Optional[str]:
        """Get the expansion for an alias."""
        all_aliases = self.get_all_aliases()
        return all_aliases.get(alias)
    
    def list_aliases(self, custom_only: bool = False) -> List[Tuple[str, str]]:
        """
        List all aliases.
        
        Args:
            custom_only: If True, only return custom aliases
        
        Returns:
            List of (alias, command) tuples
        """
        if custom_only:
            aliases = self._custom_aliases
        else:
            aliases = self.get_all_aliases()
        
        return sorted([(alias, cmd) for alias, cmd in aliases.items()])
    
    def has_alias(self, alias: str) -> bool:
        """Check if an alias exists."""
        all_aliases = self.get_all_aliases()
        return alias in all_aliases
    
    def get_alias_info(self, alias: str) -> Optional[Dict]:
        """Get detailed information about an alias."""
        all_aliases = self.get_all_aliases()
        
        if alias not in all_aliases:
            return None
        
        is_custom = alias in self._custom_aliases
        is_builtin = alias in self.DEFAULT_ALIASES
        
        return {
            "alias": alias,
            "command": all_aliases[alias],
            "is_custom": is_custom,
            "is_builtin": is_builtin,
        }
    
    def get_similar_aliases(self, partial: str) -> List[Tuple[str, str]]:
        """Get aliases matching a partial string."""
        all_aliases = self.get_all_aliases()
        matches = [
            (alias, cmd) for alias, cmd in all_aliases.items()
            if partial in alias or partial in cmd
        ]
        return sorted(matches)


# Global instance
_alias_manager: Optional[CommandAliasManager] = None


def get_alias_manager(config_dir: Optional[Path] = None) -> CommandAliasManager:
    """Get or create the global CommandAliasManager instance."""
    global _alias_manager
    if _alias_manager is None:
        _alias_manager = CommandAliasManager(config_dir)
    return _alias_manager
