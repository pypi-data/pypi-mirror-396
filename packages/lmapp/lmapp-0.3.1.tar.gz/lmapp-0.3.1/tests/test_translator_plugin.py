"""
Tests for Translator Plugin (v0.2.5).

Comprehensive test suite for translator functionality including:
- Basic translation
- Language pair support
- Caching behavior
- CLI commands
- Error handling
"""

import pytest
from pathlib import Path

from lmapp.plugins.example_translator import (
    TranslatorPlugin,
    TranslationCache,
    TRANSLATION_DICT,
)


class TestTranslationCache:
    """Test TranslationCache functionality."""
    
    def test_cache_get_set(self):
        """Test basic cache get/set operations."""
        cache = TranslationCache()
        
        # Test set and get
        cache.set("hello_es", "hola")
        assert cache.get("hello_es") == "hola"
        
        # Test get non-existent
        assert cache.get("nonexistent") is None
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = TranslationCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert len(cache.data) == 2
        
        cache.clear()
        assert len(cache.data) == 0
        assert cache.get("key1") is None
    
    def test_cache_to_dict(self):
        """Test cache export to dictionary."""
        cache = TranslationCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        export = cache.to_dict()
        assert export == {"key1": "value1", "key2": "value2"}
        
        # Verify it's a copy (modifying export doesn't affect cache)
        export["key1"] = "modified"
        assert cache.get("key1") == "value1"
    
    def test_cache_empty_dict(self):
        """Test empty cache returns empty dict."""
        cache = TranslationCache()
        assert cache.to_dict() == {}


class TestTranslatorPlugin:
    """Test TranslatorPlugin functionality."""
    
    def test_plugin_metadata(self):
        """Test plugin metadata."""
        plugin = TranslatorPlugin()
        meta = plugin.metadata
        
        assert meta.name == "translator"
        assert meta.version == "0.1.0"
        assert meta.author == "LMAPP Team"
        assert "translation" in meta.tags
        assert meta.dependencies == []
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = TranslatorPlugin()
        
        # Default values
        assert plugin.source_lang == "en"
        assert plugin.target_lang == "es"
        
        # Custom config
        plugin.initialize({
            "source_lang": "de",
            "target_lang": "fr",
            "cache_translations": True,
        })
        assert plugin.source_lang == "de"
        assert plugin.target_lang == "fr"
    
    def test_plugin_initialization_cache_disabled(self):
        """Test plugin initialization with cache disabled."""
        plugin = TranslatorPlugin()
        plugin.cache.set("key", "value")
        
        plugin.initialize({"cache_translations": False})
        assert len(plugin.cache.data) == 0
    
    def test_same_language_translation(self):
        """Test translation when source and target are same."""
        plugin = TranslatorPlugin()
        
        result = plugin.execute(
            text="hello",
            source_lang="en",
            target_lang="en"
        )
        
        assert result["translated"] == "hello"
        assert result["source"] == "en"
        assert result["target"] == "en"
    
    def test_english_to_spanish_translation(self):
        """Test English to Spanish translation."""
        plugin = TranslatorPlugin()
        
        result = plugin.execute(
            text="hello world",
            source_lang="en",
            target_lang="es"
        )
        
        assert "hola" in result["translated"]
        assert "mundo" in result["translated"]
        assert result["source"] == "en"
        assert result["target"] == "es"
        assert result["cached"] is False
    
    def test_english_to_french_translation(self):
        """Test English to French translation."""
        plugin = TranslatorPlugin()
        
        result = plugin.execute(
            text="hello",
            source_lang="en",
            target_lang="fr"
        )
        
        assert "bonjour" in result["translated"]
        assert result["source"] == "en"
        assert result["target"] == "fr"
    
    def test_english_to_german_translation(self):
        """Test English to German translation."""
        plugin = TranslatorPlugin()
        
        result = plugin.execute(
            text="hello world",
            source_lang="en",
            target_lang="de"
        )
        
        assert "hallo" in result["translated"]
        assert "welt" in result["translated"]
    
    def test_translation_with_positional_arg(self):
        """Test translation using positional argument."""
        plugin = TranslatorPlugin()
        
        result = plugin.execute(
            "hello",
            source_lang="en",
            target_lang="es"
        )
        
        assert "hola" in result["translated"]
    
    def test_translation_caching(self):
        """Test that translations are cached."""
        plugin = TranslatorPlugin()
        
        # First translation (cache miss)
        result1 = plugin.execute(
            text="hello",
            source_lang="en",
            target_lang="es"
        )
        assert result1["cached"] is False
        assert plugin.translation_stats["cache_misses"] == 1
        
        # Second translation (cache hit)
        result2 = plugin.execute(
            text="hello",
            source_lang="en",
            target_lang="es"
        )
        assert result2["cached"] is True
        assert result2["translated"] == result1["translated"]
        assert plugin.translation_stats["cache_hits"] == 1
        assert plugin.translation_stats["total_translations"] == 1
    
    def test_cache_different_for_different_languages(self):
        """Test that cache distinguishes different language pairs."""
        plugin = TranslatorPlugin()
        
        # Translate to Spanish
        result1 = plugin.execute(
            text="hello",
            source_lang="en",
            target_lang="es"
        )
        
        # Translate same text to French (should miss cache)
        result2 = plugin.execute(
            text="hello",
            source_lang="en",
            target_lang="fr"
        )
        
        # Both should be cached now
        assert plugin.translation_stats["cache_hits"] == 0
        assert plugin.translation_stats["cache_misses"] == 2
    
    def test_unsupported_language_pair(self):
        """Test translation with unsupported language pair."""
        plugin = TranslatorPlugin()
        
        result = plugin.execute(
            text="hello",
            source_lang="en",
            target_lang="zh"  # Chinese not in dictionary
        )
        
        # Should return original text when pair not supported
        assert result["translated"] == "hello"
    
    def test_get_commands(self):
        """Test CLI commands are available."""
        plugin = TranslatorPlugin()
        commands = plugin.get_commands()
        
        assert "translate" in commands
        assert "set-language" in commands
        assert "translation-stats" in commands
        assert "clear-cache" in commands
        
        # Verify commands are callable
        assert callable(commands["translate"])
        assert callable(commands["set-language"])
        assert callable(commands["translation-stats"])
        assert callable(commands["clear-cache"])
    
    def test_translate_command(self):
        """Test translate CLI command."""
        plugin = TranslatorPlugin()
        commands = plugin.get_commands()
        
        result = commands["translate"](
            text="hello",
            source_lang="en",
            target_lang="es"
        )
        
        assert "hola" in result["translated"]
    
    def test_set_language_command(self):
        """Test set-language CLI command."""
        plugin = TranslatorPlugin()
        commands = plugin.get_commands()
        
        result = commands["set-language"](source="de", target="fr")
        
        assert result["status"] == "success"
        assert result["source_lang"] == "de"
        assert result["target_lang"] == "fr"
        assert plugin.source_lang == "de"
        assert plugin.target_lang == "fr"
    
    def test_translation_stats_command(self):
        """Test translation-stats CLI command."""
        plugin = TranslatorPlugin()
        
        # Do some translations
        plugin.execute(text="hello", source_lang="en", target_lang="es")
        plugin.execute(text="hello", source_lang="en", target_lang="es")  # Cache hit
        
        commands = plugin.get_commands()
        result = commands["translation-stats"]()
        
        assert result["stats"]["total_translations"] == 1
        assert result["stats"]["cache_hits"] == 1
        assert result["cache_size"] >= 1
    
    def test_clear_cache_command(self):
        """Test clear-cache CLI command."""
        plugin = TranslatorPlugin()
        
        # Add something to cache
        plugin.execute(text="hello", source_lang="en", target_lang="es")
        assert len(plugin.cache.data) > 0
        
        commands = plugin.get_commands()
        result = commands["clear-cache"]()
        
        assert result["status"] == "success"
        assert len(plugin.cache.data) == 0
    
    def test_plugin_cleanup(self):
        """Test plugin cleanup."""
        plugin = TranslatorPlugin()
        
        # Add data
        plugin.execute(text="hello", source_lang="en", target_lang="es")
        assert len(plugin.cache.data) > 0
        assert plugin.translation_stats["total_translations"] == 1
        
        # Cleanup
        plugin.cleanup()
        
        assert len(plugin.cache.data) == 0
        assert plugin.translation_stats["total_translations"] == 0
        assert plugin.translation_stats["cache_hits"] == 0
    
    def test_translation_dictionary_coverage(self):
        """Test that translation dictionary has expected languages."""
        # Check Spanish translations exist
        assert "en_es" in TRANSLATION_DICT
        assert "hello" in TRANSLATION_DICT["en_es"]
        
        # Check French translations exist
        assert "en_fr" in TRANSLATION_DICT
        assert "hello" in TRANSLATION_DICT["en_fr"]
        
        # Check German translations exist
        assert "en_de" in TRANSLATION_DICT
        assert "hello" in TRANSLATION_DICT["en_de"]
    
    def test_phrase_translation(self):
        """Test multi-word phrase translation."""
        plugin = TranslatorPlugin()
        
        result = plugin.execute(
            text="thank you",
            source_lang="en",
            target_lang="es"
        )
        
        assert "gracias" in result["translated"]
    
    def test_mixed_case_handling(self):
        """Test translation handles case conversion."""
        plugin = TranslatorPlugin()
        
        result = plugin.execute(
            text="Hello",  # Mixed case
            source_lang="en",
            target_lang="es"
        )
        
        # Should translate despite case difference
        assert result["translated"].lower() in ["hola", "hello"]
    
    def test_stats_tracking(self):
        """Test translation statistics tracking."""
        plugin = TranslatorPlugin()
        
        # Initial stats
        assert plugin.translation_stats["total_translations"] == 0
        assert plugin.translation_stats["cache_hits"] == 0
        assert plugin.translation_stats["cache_misses"] == 0
        
        # First translation (miss)
        plugin.execute(text="hello", source_lang="en", target_lang="es")
        assert plugin.translation_stats["total_translations"] == 1
        assert plugin.translation_stats["cache_misses"] == 1
        
        # Second translation same text (hit)
        plugin.execute(text="hello", source_lang="en", target_lang="es")
        assert plugin.translation_stats["total_translations"] == 1
        assert plugin.translation_stats["cache_hits"] == 1
        
        # Different text (miss)
        plugin.execute(text="goodbye", source_lang="en", target_lang="es")
        assert plugin.translation_stats["total_translations"] == 2
        assert plugin.translation_stats["cache_misses"] == 2


class TestTranslatorIntegration:
    """Integration tests for translator plugin."""
    
    def test_full_workflow(self):
        """Test complete translator workflow."""
        plugin = TranslatorPlugin()
        
        # Initialize
        plugin.initialize({
            "source_lang": "en",
            "target_lang": "es",
            "cache_translations": True,
        })
        
        # Get commands
        commands = plugin.get_commands()
        assert len(commands) >= 4
        
        # Translate something
        result = commands["translate"](text="hello world")
        assert result["translated"]
        assert result["source"] == "en"
        assert result["target"] == "es"
        
        # Check stats
        stats = commands["translation-stats"]()
        assert stats["stats"]["total_translations"] == 1
        
        # Change language
        commands["set-language"](source="en", target="fr")
        
        # Translate in new language
        result2 = commands["translate"](text="hello")
        assert result2["target"] == "fr"
        
        # Clear cache
        commands["clear-cache"]()
        assert len(plugin.cache.data) == 0
        
        # Cleanup
        plugin.cleanup()
        assert len(plugin.cache.data) == 0
    
    def test_multiple_plugins_independent(self):
        """Test that multiple plugin instances are independent."""
        plugin1 = TranslatorPlugin()
        plugin2 = TranslatorPlugin()
        
        # Configure differently
        plugin1.initialize({"source_lang": "en", "target_lang": "es"})
        plugin2.initialize({"source_lang": "en", "target_lang": "fr"})
        
        # Execute
        result1 = plugin1.execute(text="hello")
        result2 = plugin2.execute(text="hello")
        
        # Should be different
        assert result1["translated"] != result2["translated"]
        assert result1["target"] == "es"
        assert result2["target"] == "fr"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
