"""
Summarizer Plugin for LMAPP v0.2.5.

Provides text summarization using extractive methods (no ML needed).
Identifies key sentences and creates concise summaries.
"""

from typing import Dict, Optional, Any, Callable, List
from dataclasses import dataclass
import re

from .plugin_manager import BasePlugin, PluginMetadata


@dataclass
class Summary:
    """Summarization result."""
    original_length: int
    summary_length: int
    reduction_ratio: float
    key_sentences: List[str]


class SummarizerPlugin(BasePlugin):
    """Text summarization plugin using extractive methods."""
    
    def __init__(self):
        self._metadata = PluginMetadata(
            name="summarizer",
            version="0.1.0",
            description="Extract key sentences to create text summaries",
            author="LMAPP Team",
            license="MIT",
            dependencies=[],
            entry_point="example_summarizer:SummarizerPlugin",
            tags=["summarization", "nlp", "text-processing"],
        )
        self.compression_ratio = 0.3  # Keep 30% of original
        self.stats = {"summaries_created": 0}
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        if config:
            self.compression_ratio = config.get("compression_ratio", 0.3)
    
    def _sentence_importance(self, sentence: str, doc_words: set) -> float:
        """Score sentence importance based on word frequency."""
        words = set(re.findall(r'\w+', sentence.lower()))
        common_words = words & doc_words
        return len(common_words) / max(len(words), 1)
    
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Summarize text.
        
        Args:
            text: Text to summarize
            compression_ratio: How much to compress (0.1-0.9)
        
        Returns:
            Summary with key sentences
        """
        text = kwargs.get("text", "") or (args[0] if args else "")
        if not text:
            return {"status": "error", "message": "No text provided"}
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return {
                "summary": text,
                "original_length": len(text),
                "key_sentences": sentences,
            }
        
        # Calculate target summary length
        num_sentences = max(1, int(len(sentences) * self.compression_ratio))
        
        # Score and rank sentences
        doc_words = set(re.findall(r'\w+', text.lower()))
        scores = [(i, s, self._sentence_importance(s, doc_words)) 
                  for i, s in enumerate(sentences)]
        
        # Keep top sentences in original order
        top_sentences = sorted(
            sorted(scores, key=lambda x: x[2], reverse=True)[:num_sentences],
            key=lambda x: x[0]
        )
        key_sentences = [s[1] for s in top_sentences]
        summary = ". ".join(key_sentences) + "."
        
        self.stats["summaries_created"] += 1
        
        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(text),
            "key_sentences": key_sentences,
            "num_sentences_kept": len(key_sentences),
        }
    
    def cleanup(self) -> None:
        self.stats = {"summaries_created": 0}
    
    def get_commands(self) -> Dict[str, Callable]:
        return {
            "summarize": lambda *a, **k: self.execute(*a, **k),
            "set-compression": self._set_compression,
        }
    
    def _set_compression(self, *args, **kwargs) -> Dict[str, Any]:
        ratio = kwargs.get("ratio", 0.3)
        self.compression_ratio = max(0.1, min(0.9, ratio))
        return {"status": "success", "compression_ratio": self.compression_ratio}


__all__ = ["SummarizerPlugin"]

PLUGIN_MANIFEST = {
    "name": "summarizer",
    "version": "0.1.0",
    "author": "LMAPP Team",
    "description": "Extract key sentences to create text summaries",
    "repository": "https://github.com/nabaznyl/lmapp/tree/mother/src/lmapp/plugins",
    "tags": ["summarization", "nlp", "text-processing"],
    "dependencies": [],
    "license": "MIT",
}
