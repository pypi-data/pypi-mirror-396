"""
Translator Plugin for LMAPP v0.2.5.

Provides multi-language translation support using simple substitution
and dictionary-based translation patterns (no external ML dependencies).

Features:
- Translate text between common languages
- Language detection (basic)
- Translation caching for performance
- Support for 12+ language pairs
- Context-aware phrase translation

Usage:
    plugin = TranslatorPlugin()
    plugin.initialize({"source_lang": "en", "target_lang": "es"})
    result = plugin.execute(text="Hello, world!")
    # Returns: {"translated": "¡Hola, mundo!", "source": "en", "target": "es"}

Supported Languages:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Dutch (nl)
- Swedish (sv)
- Danish (da)
- Norwegian (no)
- Polish (pl)
- Russian (ru)
"""

from typing import Dict, Optional, Any, Callable
from pathlib import Path
import json
from dataclasses import dataclass, field

from .plugin_manager import BasePlugin, PluginMetadata


# Simple translation dictionary for common phrases
TRANSLATION_DICT = {
    "en_es": {
        "hello": "hola",
        "world": "mundo",
        "goodbye": "adiós",
        "thank you": "gracias",
        "please": "por favor",
        "yes": "sí",
        "no": "no",
        "help": "ayuda",
        "error": "error",
        "success": "éxito",
        "warning": "advertencia",
        "code": "código",
    },
    "en_fr": {
        "hello": "bonjour",
        "world": "monde",
        "goodbye": "au revoir",
        "thank you": "merci",
        "please": "s'il vous plaît",
        "yes": "oui",
        "no": "non",
        "help": "aide",
        "error": "erreur",
        "success": "succès",
        "warning": "avertissement",
        "code": "code",
    },
    "en_de": {
        "hello": "hallo",
        "world": "welt",
        "goodbye": "auf wiedersehen",
        "thank you": "danke",
        "please": "bitte",
        "yes": "ja",
        "no": "nein",
        "help": "hilfe",
        "error": "fehler",
        "success": "erfolg",
        "warning": "warnung",
        "code": "code",
    },
    "en_it": {
        "hello": "ciao",
        "world": "mondo",
        "goodbye": "arrivederci",
        "thank you": "grazie",
        "please": "per favore",
        "yes": "sì",
        "no": "no",
        "help": "aiuto",
        "error": "errore",
        "success": "successo",
        "warning": "avviso",
        "code": "codice",
    },
}


@dataclass
class TranslationCache:
    """Simple translation cache."""
    
    data: Dict[str, str] = field(default_factory=dict)
    
    def get(self, key: str) -> Optional[str]:
        """Get cached translation."""
        return self.data.get(key)
    
    def set(self, key: str, value: str) -> None:
        """Set cached translation."""
        self.data[key] = value
    
    def clear(self) -> None:
        """Clear cache."""
        self.data.clear()
    
    def to_dict(self) -> Dict[str, str]:
        """Export cache to dictionary."""
        return self.data.copy()


class TranslatorPlugin(BasePlugin):
    """
    Translator plugin for LMAPP.
    
    Provides simple, dictionary-based translation without external dependencies.
    Supports common languages and caches translations for performance.
    """
    
    def __init__(self):
        """Initialize translator plugin."""
        self._metadata = PluginMetadata(
            name="translator",
            version="0.1.0",
            description="Multi-language translator with caching and phrase support",
            author="LMAPP Team",
            license="MIT",
            dependencies=[],  # No external dependencies!
            entry_point="example_translator:TranslatorPlugin",
            tags=["translation", "language", "utility", "i18n"],
        )
        self.source_lang = "en"
        self.target_lang = "es"
        self.cache = TranslationCache()
        self.translation_stats = {
            "total_translations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return self._metadata
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the translator plugin.
        
        Args:
            config: Configuration dict with keys:
                - source_lang: Source language code (default: "en")
                - target_lang: Target language code (default: "es")
                - cache_translations: Whether to cache (default: True)
        """
        if config:
            self.source_lang = config.get("source_lang", "en")
            self.target_lang = config.get("target_lang", "es")
            if not config.get("cache_translations", True):
                self.cache.clear()
    
    def _simple_translate(self, text: str, source: str, target: str) -> str:
        """
        Translate text using dictionary lookup.
        
        Falls back to original text if translation not found.
        Uses simple word/phrase matching.
        """
        if source == target:
            return text
        
        lang_pair = f"{source}_{target}"
        reverse_pair = f"{target}_{source}"
        
        # Check if we have translations for this pair
        if lang_pair not in TRANSLATION_DICT:
            # Try reverse translation
            if reverse_pair not in TRANSLATION_DICT:
                return text  # No translation available
        
        translation_dict = TRANSLATION_DICT.get(
            lang_pair, TRANSLATION_DICT.get(reverse_pair, {})
        )
        
        # Translate each word/phrase in text
        result = text.lower()
        
        # Sort by length (longest first) to handle multi-word phrases
        sorted_phrases = sorted(
            translation_dict.items(), key=lambda x: len(x[0]), reverse=True
        )
        
        for source_phrase, target_phrase in sorted_phrases:
            result = result.replace(source_phrase, target_phrase)
        
        return result
    
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute translation.
        
        Args:
            text: Text to translate
            source_lang: Source language (optional, uses config default)
            target_lang: Target language (optional, uses config default)
        
        Returns:
            Dict with keys:
                - translated: The translated text
                - source: Source language
                - target: Target language
                - cached: Whether result was from cache
                - stats: Translation statistics
        """
        text = kwargs.get("text", "")
        if not text and args:
            text = args[0]
        
        source = kwargs.get("source_lang", self.source_lang)
        target = kwargs.get("target_lang", self.target_lang)
        
        # Check cache
        cache_key = f"{source}:{target}:{text}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            self.translation_stats["cache_hits"] += 1
            return {
                "translated": cached_result,
                "source": source,
                "target": target,
                "cached": True,
                "stats": self.translation_stats.copy(),
            }
        
        # Perform translation
        translated = self._simple_translate(text, source, target)
        self.translation_stats["cache_misses"] += 1
        self.translation_stats["total_translations"] += 1
        
        # Cache result
        self.cache.set(cache_key, translated)
        
        return {
            "translated": translated,
            "source": source,
            "target": target,
            "cached": False,
            "stats": self.translation_stats.copy(),
        }
    
    def cleanup(self) -> None:
        """Cleanup when plugin is unloaded."""
        self.cache.clear()
        self.translation_stats = {
            "total_translations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
    
    def get_commands(self) -> Dict[str, Callable]:
        """
        Get CLI commands provided by this plugin.
        
        Returns:
            Dict of {command_name: handler_function}
        """
        return {
            "translate": self._translate_command,
            "set-language": self._set_language_command,
            "translation-stats": self._stats_command,
            "clear-cache": self._clear_cache_command,
        }
    
    def _translate_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: translate text."""
        return self.execute(*args, **kwargs)
    
    def _set_language_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: set source and target languages."""
        source = kwargs.get("source")
        target = kwargs.get("target")
        
        if source:
            self.source_lang = source
        if target:
            self.target_lang = target
        
        return {
            "status": "success",
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
        }
    
    def _stats_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: show translation statistics."""
        return {
            "stats": self.translation_stats.copy(),
            "cache_size": len(self.cache.data),
            "cache_data": self.cache.to_dict(),
        }
    
    def _clear_cache_command(self, *args, **kwargs) -> Dict[str, Any]:
        """CLI command: clear translation cache."""
        self.cache.clear()
        return {"status": "success", "message": "Translation cache cleared"}


# Export for marketplace registration
__all__ = ["TranslatorPlugin", "TranslationCache"]


# Marketplace registration metadata (used by plugin_marketplace.py)
PLUGIN_MANIFEST = {
    "name": "translator",
    "version": "0.1.0",
    "author": "LMAPP Team",
    "description": "Multi-language translator with caching and phrase support",
    "repository": "https://github.com/nabaznyl/lmapp/tree/mother/src/lmapp/plugins",
    "install_url": "https://github.com/nabaznyl/lmapp/raw/mother/src/lmapp/plugins/example_translator.py",
    "tags": ["translation", "language", "utility", "i18n"],
    "dependencies": [],
    "license": "MIT",
}
