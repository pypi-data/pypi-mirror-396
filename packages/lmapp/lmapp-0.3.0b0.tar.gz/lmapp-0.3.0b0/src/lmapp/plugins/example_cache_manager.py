#!/usr/bin/env python3
"""
Cache Manager Plugin
Optimizes LLM response caching and RAG document cache management
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta

from .plugin_manager import BasePlugin, PluginMetadata


@dataclass
class CacheEntry:
    """Single cache entry"""
    key: str
    value: Any
    created_at: float
    accessed_at: float
    ttl_seconds: int
    hit_count: int = 0
    size_bytes: int = 0


@dataclass
class CacheStats:
    """Cache statistics"""
    total_entries: int
    total_size_mb: float
    hit_rate: float  # hits / (hits + misses)
    miss_rate: float
    avg_entry_size_kb: float
    oldest_entry_age_hours: float
    newest_entry_age_hours: float


class SimpleLRUCache:
    """Simple LRU (Least Recently Used) cache with TTL support"""

    def __init__(self, max_size_mb: int = 100):
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.entries: Dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Set cache entry with TTL"""
        value_str = json.dumps(value) if not isinstance(value, str) else value
        size_bytes = len(value_str.encode())

        # Check if adding this would exceed size limit
        current_size = sum(e.size_bytes for e in self.entries.values())
        if current_size + size_bytes > self.max_size_bytes:
            # Evict LRU entry
            self._evict_lru()

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            accessed_at=time.time(),
            ttl_seconds=ttl_seconds,
            size_bytes=size_bytes,
        )

        self.entries[key] = entry
        return True

    def get(self, key: str) -> Tuple[Optional[Any], bool]:
        """Get cache entry, returns (value, is_hit)"""
        if key not in self.entries:
            self.misses += 1
            return None, False

        entry = self.entries[key]

        # Check if expired
        age_seconds = time.time() - entry.created_at
        if age_seconds > entry.ttl_seconds:
            del self.entries[key]
            self.misses += 1
            return None, False

        # Update access time and hit count
        entry.accessed_at = time.time()
        entry.hit_count += 1
        self.hits += 1

        return entry.value, True

    def clear_expired(self) -> int:
        """Remove all expired entries, return count removed"""
        current_time = time.time()
        expired_keys = [
            k for k, e in self.entries.items()
            if (current_time - e.created_at) > e.ttl_seconds
        ]

        for key in expired_keys:
            del self.entries[key]

        return len(expired_keys)

    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        total_size = sum(e.size_bytes for e in self.entries.values())
        total_size_mb = total_size / (1024 * 1024)

        total_accesses = self.hits + self.misses
        hit_rate = self.hits / total_accesses if total_accesses > 0 else 0.0
        miss_rate = self.misses / total_accesses if total_accesses > 0 else 0.0

        if not self.entries:
            avg_size_kb = 0.0
            oldest_age = 0.0
            newest_age = 0.0
        else:
            avg_size_kb = (total_size / len(self.entries)) / 1024
            current_time = time.time()
            ages = [current_time - e.created_at for e in self.entries.values()]
            oldest_age = max(ages) / 3600  # Convert to hours
            newest_age = min(ages) / 3600

        return CacheStats(
            total_entries=len(self.entries),
            total_size_mb=total_size_mb,
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            avg_entry_size_kb=avg_size_kb,
            oldest_entry_age_hours=oldest_age,
            newest_entry_age_hours=newest_age,
        )

    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self.entries:
            return

        lru_key = min(self.entries.keys(), key=lambda k: self.entries[k].accessed_at)
        del self.entries[lru_key]


class CacheManagerPlugin(BasePlugin):
    """
    Manages LLM response cache and RAG document cache.
    
    Features:
    - LRU cache with TTL support
    - Cache statistics and health monitoring
    - Automatic expiration and cleanup
    - Multi-tier caching strategy
    """

    _METADATA = PluginMetadata(
        name="cache_manager",
        version="1.0.0",
        author="lmapp-dev",
        description="Optimize LLM response caching and RAG document caching",
        license="MIT",
        dependencies=[],
        tags=["caching", "performance", "optimization"],
    )

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return self._METADATA
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the plugin."""
        pass

    def __init__(self):
        """Initialize cache manager"""
        super().__init__()
        self.response_cache = SimpleLRUCache(max_size_mb=50)  # LLM responses
        self.rag_cache = SimpleLRUCache(max_size_mb=100)  # RAG documents
        self.search_cache = SimpleLRUCache(max_size_mb=25)  # Search results

    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Manage caches.
        
        Args:
            action: 'stats', 'clear', 'cleanup', 'optimize'
            cache_type: 'all', 'response', 'rag', 'search'
            
        Returns:
            Dictionary with cache management results
        """
        action = kwargs.get("action", "stats")
        cache_type = kwargs.get("cache_type", "all")

        if action == "stats":
            return self._get_all_stats(cache_type)
        elif action == "clear":
            return self._clear_cache(cache_type)
        elif action == "cleanup":
            return self._cleanup_expired(cache_type)
        elif action == "optimize":
            return self._optimize_caches(cache_type)
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def cache_response(self, prompt: str, response: str, ttl_seconds: int = 3600) -> str:
        """
        Cache LLM response.
        
        Args:
            prompt: The prompt that generated this response
            response: The LLM response
            ttl_seconds: Time to live for this cache entry
            
        Returns:
            Cache key
        """
        key = self._generate_key(prompt)
        self.response_cache.set(key, response, ttl_seconds=ttl_seconds)
        return key

    def get_cached_response(self, prompt: str) -> Optional[str]:
        """
        Get cached response for prompt.
        
        Args:
            prompt: The prompt to look up
            
        Returns:
            Cached response or None
        """
        key = self._generate_key(prompt)
        value, hit = self.response_cache.get(key)
        return value if hit else None

    def cache_document(self, doc_path: str, content: str, ttl_seconds: int = 86400) -> str:
        """
        Cache RAG document.
        
        Args:
            doc_path: Path to document
            content: Document content
            ttl_seconds: Time to live (default 24h)
            
        Returns:
            Cache key
        """
        key = self._generate_key(doc_path)
        self.rag_cache.set(key, content, ttl_seconds=ttl_seconds)
        return key

    def get_cached_document(self, doc_path: str) -> Optional[str]:
        """Get cached document content"""
        key = self._generate_key(doc_path)
        value, hit = self.rag_cache.get(key)
        return value if hit else None

    def cache_search_result(self, query: str, results: List[Dict], ttl_seconds: int = 1800) -> str:
        """
        Cache search results.
        
        Args:
            query: Search query
            results: Search results
            ttl_seconds: Time to live (default 30min)
            
        Returns:
            Cache key
        """
        key = self._generate_key(query)
        self.search_cache.set(key, results, ttl_seconds=ttl_seconds)
        return key

    def get_cached_search(self, query: str) -> Optional[List[Dict]]:
        """Get cached search results"""
        key = self._generate_key(query)
        value, hit = self.search_cache.get(key)
        return value if hit else None

    def _get_all_stats(self, cache_type: str) -> Dict[str, Any]:
        """Get statistics for selected caches"""
        if cache_type in ["all", "response"]:
            resp_stats = self.response_cache.get_stats()
        else:
            resp_stats = None

        if cache_type in ["all", "rag"]:
            rag_stats = self.rag_cache.get_stats()
        else:
            rag_stats = None

        if cache_type in ["all", "search"]:
            search_stats = self.search_cache.get_stats()
        else:
            search_stats = None

        return {
            "status": "success",
            "caches": {
                "response": asdict(resp_stats) if resp_stats else None,
                "rag": asdict(rag_stats) if rag_stats else None,
                "search": asdict(search_stats) if search_stats else None,
            },
            "total_cached_mb": sum(
                s.total_size_mb for s in [resp_stats, rag_stats, search_stats]
                if s is not None
            ),
        }

    def _clear_cache(self, cache_type: str) -> Dict[str, Any]:
        """Clear selected caches"""
        cleared = 0

        if cache_type in ["all", "response"]:
            cleared += len(self.response_cache.entries)
            self.response_cache.entries = {}

        if cache_type in ["all", "rag"]:
            cleared += len(self.rag_cache.entries)
            self.rag_cache.entries = {}

        if cache_type in ["all", "search"]:
            cleared += len(self.search_cache.entries)
            self.search_cache.entries = {}

        return {
            "status": "success",
            "message": f"Cleared {cleared} cache entries",
            "entries_removed": cleared,
        }

    def _cleanup_expired(self, cache_type: str) -> Dict[str, Any]:
        """Remove expired entries"""
        removed = 0

        if cache_type in ["all", "response"]:
            removed += self.response_cache.clear_expired()

        if cache_type in ["all", "rag"]:
            removed += self.rag_cache.clear_expired()

        if cache_type in ["all", "search"]:
            removed += self.search_cache.clear_expired()

        return {
            "status": "success",
            "message": f"Removed {removed} expired entries",
            "entries_removed": removed,
        }

    def _optimize_caches(self, cache_type: str) -> Dict[str, Any]:
        """Optimize caches (cleanup + analysis)"""
        # First cleanup
        cleanup_result = self._cleanup_expired(cache_type)
        removed = cleanup_result["entries_removed"]

        # Then get stats
        stats_result = self._get_all_stats(cache_type)

        return {
            "status": "success",
            "expired_removed": removed,
            "cache_stats": stats_result["caches"],
            "recommendations": self._generate_recommendations(stats_result["caches"]),
        }

    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        for cache_name, cache_stats in stats.items():
            if cache_stats is None:
                continue

            if cache_stats["hit_rate"] < 0.3:
                recommendations.append(
                    f"{cache_name}: Low hit rate ({cache_stats['hit_rate']:.1%}), "
                    "consider increasing TTL"
                )

            if cache_stats["total_size_mb"] > 80:
                recommendations.append(
                    f"{cache_name}: Near size limit "
                    f"({cache_stats['total_size_mb']:.1f}MB), "
                    "consider reducing TTL"
                )

            if cache_stats["oldest_entry_age_hours"] > 24:
                recommendations.append(
                    f"{cache_name}: Contains very old entries "
                    f"({cache_stats['oldest_entry_age_hours']:.0f}h old), "
                    "consider shorter TTL"
                )

        if not recommendations:
            recommendations.append("Cache performance is optimal")

        return recommendations

    def _generate_key(self, data: str) -> str:
        """Generate cache key from data (hash)"""
        return hashlib.md5(data.encode()).hexdigest()
