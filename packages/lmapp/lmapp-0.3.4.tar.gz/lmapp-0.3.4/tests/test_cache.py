"""
Tests for Response Caching Module
"""

import pytest
from lmapp.core.cache import ResponseCache


class TestResponseCache:
    """Test suite for ResponseCache"""

    @pytest.fixture
    def cache(self, tmp_path):
        """Create a temporary cache instance for testing"""
        return ResponseCache(cache_dir=tmp_path, ttl_hours=1)

    def test_cache_initialization(self, cache):
        """Test cache initializes correctly"""
        assert cache.cache_dir.exists()
        assert cache.db_path.exists()

    def test_cache_set_and_get(self, cache):
        """Test storing and retrieving cached responses"""
        query = "How do I optimize Python code?"
        response = "Use list comprehensions and avoid unnecessary loops..."

        # Store in cache
        assert cache.set(query, response, "mistral", "ollama", 0.7) is True

        # Retrieve from cache
        cached = cache.get(query, "mistral", "ollama", 0.7)
        assert cached == response

    def test_cache_miss_returns_none(self, cache):
        """Test getting non-existent cache entry returns None"""
        result = cache.get("Non-existent query", "mistral", "ollama", 0.7)
        assert result is None

    def test_cache_different_models_separate(self, cache):
        """Test that different models have separate cache entries"""
        query = "What is a decorator?"
        response1 = "Response from model A"
        response2 = "Response from model B"

        # Cache for two different models
        cache.set(query, response1, "model-a", "ollama", 0.7)
        cache.set(query, response2, "model-b", "ollama", 0.7)

        # Verify they're separate
        assert cache.get(query, "model-a", "ollama", 0.7) == response1
        assert cache.get(query, "model-b", "ollama", 0.7) == response2

    def test_cache_different_temperatures_separate(self, cache):
        """Test that different temperatures have separate cache entries"""
        query = "Explain recursion"
        response1 = "Conservative response"
        response2 = "Creative response"

        cache.set(query, response1, "mistral", "ollama", 0.3)
        cache.set(query, response2, "mistral", "ollama", 0.9)

        assert cache.get(query, "mistral", "ollama", 0.3) == response1
        assert cache.get(query, "mistral", "ollama", 0.9) == response2

    def test_cache_different_backends_separate(self, cache):
        """Test that different backends have separate cache entries"""
        query = "What is API?"
        response1 = "Ollama response"
        response2 = "Llamafile response"

        cache.set(query, response1, "mistral", "ollama", 0.7)
        cache.set(query, response2, "mistral", "llamafile", 0.7)

        assert cache.get(query, "mistral", "ollama", 0.7) == response1
        assert cache.get(query, "mistral", "llamafile", 0.7) == response2

    def test_cache_query_normalization(self, cache):
        """Test that queries with whitespace variations are treated the same"""
        # These should be treated as the same query
        query1 = "How do I use Python?"
        query2 = "  How do I use Python?  "
        response = "Python is a programming language..."

        cache.set(query1, response, "mistral", "ollama", 0.7)
        # Query with extra whitespace should still hit
        cached = cache.get(query2, "mistral", "ollama", 0.7)
        assert cached == response

    def test_cache_statistics(self, cache):
        """Test cache statistics tracking"""
        # Add some cache entries
        cache.set("Query 1", "Response 1", "mistral", "ollama", 0.7)
        cache.set("Query 2", "Response 2", "mistral", "ollama", 0.7)

        # Access one multiple times
        cache.get("Query 1", "mistral", "ollama", 0.7)
        cache.get("Query 1", "mistral", "ollama", 0.7)

        stats = cache.get_stats()

        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 2
        assert stats["total_accesses"] >= 2  # At least 2 accesses from set

    def test_cache_clear_all(self, cache):
        """Test clearing entire cache"""
        cache.set("Query", "Response", "mistral", "ollama", 0.7)

        stats = cache.get_stats()
        assert stats["total_entries"] > 0

        cleared = cache.clear(expired_only=False)
        assert cleared > 0

        stats = cache.get_stats()
        assert stats["total_entries"] == 0

    def test_cache_by_query_lookup(self, cache):
        """Test looking up all cached variants of a query"""
        query = "What is Python?"

        # Cache different model variations
        cache.set(query, "Response A", "model-a", "ollama", 0.7)
        cache.set(query, "Response B", "model-b", "ollama", 0.7)

        variants = cache.get_by_query(query)
        assert len(variants) == 2
        assert variants[0]["model"] in ["model-a", "model-b"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
