#!/usr/bin/env python3
"""
Tests for Cache Manager Plugin
"""

import time

from lmapp.plugins.example_cache_manager import (
    CacheManagerPlugin,
    SimpleLRUCache,
    CacheEntry,
)


class TestCacheEntry:
    """Test cache entry data class"""

    def test_entry_creation(self):
        """Test cache entry can be created"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=time.time(),
            accessed_at=time.time(),
            ttl_seconds=3600,
        )
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.hit_count == 0

    def test_entry_with_size(self):
        """Test entry with size tracking"""
        entry = CacheEntry(
            key="test",
            value="data",
            created_at=time.time(),
            accessed_at=time.time(),
            ttl_seconds=3600,
            size_bytes=1024,
        )
        assert entry.size_bytes == 1024


class TestSimpleLRUCache:
    """Test LRU cache implementation"""

    def test_cache_creation(self):
        """Test cache can be created"""
        cache = SimpleLRUCache(max_size_mb=10)
        assert cache.max_size_mb == 10
        assert len(cache.entries) == 0

    def test_cache_set_and_get(self):
        """Test setting and getting cache entries"""
        cache = SimpleLRUCache()

        cache.set("key1", "value1")
        value, hit = cache.get("key1")

        assert value == "value1"
        assert hit is True
        assert cache.hits == 1

    def test_cache_miss(self):
        """Test cache miss"""
        cache = SimpleLRUCache()

        value, hit = cache.get("nonexistent")

        assert value is None
        assert hit is False
        assert cache.misses == 1

    def test_cache_ttl_expiration(self):
        """Test TTL-based expiration"""
        cache = SimpleLRUCache()

        # Set entry with 1-second TTL
        cache.set("key1", "value1", ttl_seconds=1)

        # Should be available immediately
        value, hit = cache.get("key1")
        assert hit is True

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        value, hit = cache.get("key1")
        assert hit is False

    def test_cache_hit_rate_calculation(self):
        """Test hit rate calculation"""
        cache = SimpleLRUCache()

        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key1")  # Hit
        cache.get("missing")  # Miss

        assert cache.hits == 2
        assert cache.misses == 1

    def test_cache_lru_eviction(self):
        """Test LRU eviction when size limit exceeded"""
        cache = SimpleLRUCache(max_size_mb=0.0001)  # Very small

        cache.set("key1", "x" * 100)  # ~100 bytes
        assert len(cache.entries) == 1  # Should have first entry

        cache.set("key2", "x" * 100)  # Should evict key1

        # One of the entries should be gone
        assert len(cache.entries) <= 1

    def test_clear_expired_entries(self):
        """Test clearing expired entries"""
        cache = SimpleLRUCache()

        cache.set("key1", "value1", ttl_seconds=1)
        cache.set("key2", "value2", ttl_seconds=10000)

        assert len(cache.entries) == 2

        time.sleep(1.1)
        removed = cache.clear_expired()

        assert removed == 1
        assert len(cache.entries) == 1

    def test_cache_stats(self):
        """Test cache statistics"""
        cache = SimpleLRUCache()

        cache.set("key1", "value1" * 10)
        cache.get("key1")
        cache.get("key1")

        stats = cache.get_stats()

        assert stats.total_entries == 1
        assert stats.hit_rate > 0
        assert stats.avg_entry_size_kb > 0

    def test_stats_with_no_entries(self):
        """Test stats for empty cache"""
        cache = SimpleLRUCache()

        stats = cache.get_stats()

        assert stats.total_entries == 0
        assert stats.total_size_mb == 0
        assert stats.hit_rate == 0

    def test_stats_with_only_misses(self):
        """Test stats with only cache misses"""
        cache = SimpleLRUCache()

        cache.get("key1")
        cache.get("key2")
        cache.get("key3")

        stats = cache.get_stats()

        assert stats.hit_rate == 0
        assert stats.miss_rate == 1.0


class TestCacheManagerPlugin:
    """Test cache manager plugin"""

    def test_plugin_initialization(self):
        """Test plugin can be instantiated"""
        plugin = CacheManagerPlugin()
        assert plugin.metadata.name == "cache_manager"
        assert plugin.metadata.license == "MIT"

    def test_plugin_has_three_caches(self):
        """Test plugin has response, RAG, and search caches"""
        plugin = CacheManagerPlugin()

        assert hasattr(plugin, "response_cache")
        assert hasattr(plugin, "rag_cache")
        assert hasattr(plugin, "search_cache")
        assert isinstance(plugin.response_cache, SimpleLRUCache)

    def test_cache_response(self):
        """Test caching LLM response"""
        plugin = CacheManagerPlugin()

        prompt = "What is AI?"
        response = "AI is artificial intelligence"

        key = plugin.cache_response(prompt, response)

        assert key is not None
        cached = plugin.get_cached_response(prompt)
        assert cached == response

    def test_get_uncached_response(self):
        """Test getting uncached response returns None"""
        plugin = CacheManagerPlugin()

        result = plugin.get_cached_response("nonexistent prompt")
        assert result is None

    def test_cache_document(self):
        """Test caching RAG document"""
        plugin = CacheManagerPlugin()

        doc_path = "/path/to/doc.txt"
        content = "Document content here"

        key = plugin.cache_document(doc_path, content)

        assert key is not None
        cached = plugin.get_cached_document(doc_path)
        assert cached == content

    def test_cache_search_result(self):
        """Test caching search results"""
        plugin = CacheManagerPlugin()

        query = "python programming"
        results = [
            {"title": "Python Basics", "score": 0.95},
            {"title": "Advanced Python", "score": 0.87},
        ]

        key = plugin.cache_search_result(query, results)

        assert key is not None
        cached = plugin.get_cached_search(query)
        assert cached == results

    def test_execute_stats_action(self):
        """Test execute with stats action"""
        plugin = CacheManagerPlugin()

        plugin.cache_response("test", "response")

        result = plugin.execute(action="stats")

        assert result["status"] == "success"
        assert "caches" in result
        assert "response" in result["caches"]

    def test_execute_clear_action(self):
        """Test execute with clear action"""
        plugin = CacheManagerPlugin()

        plugin.cache_response("test", "response")
        plugin.cache_document("doc", "content")

        result = plugin.execute(action="clear", cache_type="response")

        assert result["status"] == "success"
        assert result["entries_removed"] == 1

    def test_execute_cleanup_action(self):
        """Test execute with cleanup action"""
        plugin = CacheManagerPlugin()

        # Add entry with short TTL
        plugin.response_cache.set("test", "value", ttl_seconds=1)

        time.sleep(1.1)

        result = plugin.execute(action="cleanup")

        assert result["status"] == "success"
        assert result["entries_removed"] >= 1

    def test_execute_optimize_action(self):
        """Test execute with optimize action"""
        plugin = CacheManagerPlugin()

        plugin.cache_response("test", "response")

        result = plugin.execute(action="optimize")

        assert result["status"] == "success"
        assert "recommendations" in result

    def test_execute_invalid_action(self):
        """Test execute with invalid action"""
        plugin = CacheManagerPlugin()

        result = plugin.execute(action="invalid")

        assert result["status"] == "error"

    def test_cache_type_filtering(self):
        """Test cache type filtering in execute"""
        plugin = CacheManagerPlugin()

        plugin.cache_response("test", "response")
        plugin.cache_document("doc", "content")
        plugin.cache_search_result("query", [])

        # Clear only response cache
        plugin.execute(action="clear", cache_type="response")
        assert plugin.response_cache.entries == {}
        assert len(plugin.rag_cache.entries) > 0

    def test_generate_recommendations(self):
        """Test generating cache recommendations"""
        plugin = CacheManagerPlugin()

        # Set cache to high usage
        for i in range(100):
            plugin.cache_response(f"prompt_{i}", f"response_{i}")

        stats_result = plugin.execute(action="stats")
        stats = stats_result["caches"]

        recommendations = plugin._generate_recommendations(stats)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_generate_key_consistency(self):
        """Test that same input generates same key"""
        plugin = CacheManagerPlugin()

        key1 = plugin._generate_key("test data")
        key2 = plugin._generate_key("test data")

        assert key1 == key2

    def test_generate_different_keys(self):
        """Test that different inputs generate different keys"""
        plugin = CacheManagerPlugin()

        key1 = plugin._generate_key("data1")
        key2 = plugin._generate_key("data2")

        assert key1 != key2

    def test_plugin_has_execute_method(self):
        """Test plugin implements execute method"""
        plugin = CacheManagerPlugin()
        assert hasattr(plugin, "execute")
        assert callable(plugin.execute)

    def test_cache_with_json_serializable_value(self):
        """Test caching JSON-serializable objects"""
        plugin = CacheManagerPlugin()

        data = {"key": "value", "number": 42}

        plugin.cache_search_result("test", [data])
        cached = plugin.get_cached_search("test")

        assert cached[0]["key"] == "value"
        assert cached[0]["number"] == 42

    def test_total_cached_size(self):
        """Test total cached size calculation"""
        plugin = CacheManagerPlugin()

        plugin.cache_response("p1", "response1" * 100)
        plugin.cache_document("d1", "document1" * 100)

        result = plugin.execute(action="stats")

        assert "total_cached_mb" in result
        assert result["total_cached_mb"] > 0
