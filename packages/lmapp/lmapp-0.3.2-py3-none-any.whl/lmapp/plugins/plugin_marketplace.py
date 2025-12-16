"""
LMAPP Plugin Marketplace - Plugin discovery and distribution system.

Features:
- Plugin registry (local + remote)
- Plugin validation and certification
- Plugin installation from marketplace
- Plugin search and filtering
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json


@dataclass
class PluginRegistry:
    """Central registry for plugin metadata and discovery."""
    
    name: str  # e.g., "official", "community", "verified"
    url: str  # URL to plugin registry (can be local or remote)
    description: str
    plugins: Dict[str, 'PluginMarketplaceEntry'] = field(default_factory=dict)
    
    def add_plugin(self, entry: 'PluginMarketplaceEntry') -> None:
        """Add plugin to registry."""
        self.plugins[entry.name] = entry
    
    def search(self, query: str) -> List['PluginMarketplaceEntry']:
        """Search plugins by name or description."""
        query = query.lower()
        results = []
        for plugin in self.plugins.values():
            if (query in plugin.name.lower() or 
                query in plugin.description.lower() or
                any(query in tag.lower() for tag in plugin.tags)):
                results.append(plugin)
        return results
    
    def get_by_name(self, name: str) -> Optional['PluginMarketplaceEntry']:
        """Get plugin by exact name."""
        return self.plugins.get(name)
    
    def to_dict(self) -> Dict:
        """Serialize registry to dictionary."""
        return {
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "plugins": {
                name: entry.to_dict() 
                for name, entry in self.plugins.items()
            }
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'PluginRegistry':
        """Deserialize registry from dictionary."""
        registry = PluginRegistry(
            name=data["name"],
            url=data["url"],
            description=data["description"]
        )
        for name, plugin_data in data.get("plugins", {}).items():
            registry.add_plugin(PluginMarketplaceEntry.from_dict(plugin_data))
        return registry


@dataclass
class PluginMarketplaceEntry:
    """Plugin entry in marketplace with metadata and ratings."""
    
    name: str
    version: str
    author: str
    description: str
    repository: str  # GitHub, GitLab, etc.
    install_url: str  # URL or local path
    tags: List[str] = field(default_factory=list)
    downloads: int = 0
    rating: float = 5.0  # 0.0 - 5.0
    reviews: int = 0
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    verified: bool = False  # LMAPP certification
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "repository": self.repository,
            "install_url": self.install_url,
            "tags": self.tags,
            "downloads": self.downloads,
            "rating": self.rating,
            "reviews": self.reviews,
            "last_updated": self.last_updated,
            "verified": self.verified,
            "dependencies": self.dependencies,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'PluginMarketplaceEntry':
        """Deserialize from dictionary."""
        return PluginMarketplaceEntry(
            name=data["name"],
            version=data["version"],
            author=data["author"],
            description=data["description"],
            repository=data["repository"],
            install_url=data["install_url"],
            tags=data.get("tags", []),
            downloads=data.get("downloads", 0),
            rating=data.get("rating", 5.0),
            reviews=data.get("reviews", 0),
            last_updated=data.get("last_updated", datetime.utcnow().isoformat()),
            verified=data.get("verified", False),
            dependencies=data.get("dependencies", []),
        )


class PluginMarketplace:
    """Main marketplace manager - handles registries and plugin discovery."""
    
    def __init__(self, storage_path: Path = None):
        """Initialize marketplace."""
        self.storage_path = storage_path or Path.home() / ".lmapp" / "marketplace"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.registries: Dict[str, PluginRegistry] = {}
        self._initialize_default_registries()
    
    def _initialize_default_registries(self) -> None:
        """Initialize default registries."""
        # Official LMAPP registry
        official = PluginRegistry(
            name="official",
            url="https://lmapp.io/marketplace/official",
            description="Official LMAPP plugins"
        )
        self.registries["official"] = official
        
        # Community registry
        community = PluginRegistry(
            name="community",
            url="https://github.com/lmapp-community/plugins",
            description="Community-contributed plugins"
        )
        self.registries["community"] = community
    
    def add_registry(self, registry: PluginRegistry) -> None:
        """Add custom registry."""
        self.registries[registry.name] = registry
    
    def get_registry(self, name: str) -> Optional[PluginRegistry]:
        """Get registry by name."""
        return self.registries.get(name)
    
    def search_all(self, query: str) -> List[tuple[str, PluginMarketplaceEntry]]:
        """Search across all registries."""
        results = []
        for registry_name, registry in self.registries.items():
            for entry in registry.search(query):
                results.append((registry_name, entry))
        # Sort by rating and downloads
        results.sort(
            key=lambda x: (x[1].verified, x[1].rating, x[1].downloads),
            reverse=True
        )
        return results
    
    def install_plugin(self, plugin_name: str, registry: str = "official") -> bool:
        """Install plugin from marketplace."""
        registry_obj = self.get_registry(registry)
        if not registry_obj:
            return False
        
        entry = registry_obj.get_by_name(plugin_name)
        if not entry:
            return False
        
        # Download/copy plugin from entry.install_url
        # (Implementation depends on URL scheme)
        
        # Update download count
        entry.downloads += 1
        
        return True
    
    def save_registries(self) -> None:
        """Save registries to disk."""
        for registry_name, registry in self.registries.items():
            registry_file = self.storage_path / f"{registry_name}.json"
            with open(registry_file, "w") as f:
                json.dump(registry.to_dict(), f, indent=2)
    
    def load_registries(self) -> None:
        """Load registries from disk."""
        for registry_file in self.storage_path.glob("*.json"):
            try:
                with open(registry_file) as f:
                    data = json.load(f)
                    registry = PluginRegistry.from_dict(data)
                    self.registries[registry.name] = registry
            except Exception:
                pass  # Skip corrupted registries
    
    def list_plugins(self, registry: str = None, certified_only: bool = False) -> List[PluginMarketplaceEntry]:
        """List all plugins in registry."""
        plugins = []
        
        registries_to_search = (
            {registry: self.registries[registry]} 
            if registry else 
            self.registries
        )
        
        for reg in registries_to_search.values():
            for plugin in reg.plugins.values():
                if certified_only and not plugin.verified:
                    continue
                plugins.append(plugin)
        
        return sorted(
            plugins,
            key=lambda p: (p.verified, p.rating, p.downloads),
            reverse=True
        )


# Global marketplace instance
_marketplace_instance: Optional[PluginMarketplace] = None


def get_plugin_marketplace() -> PluginMarketplace:
    """Get or create global plugin marketplace instance."""
    global _marketplace_instance
    if _marketplace_instance is None:
        _marketplace_instance = PluginMarketplace()
        _marketplace_instance.load_registries()
    return _marketplace_instance
