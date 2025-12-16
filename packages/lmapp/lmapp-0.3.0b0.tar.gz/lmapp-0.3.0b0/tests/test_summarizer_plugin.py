"""Tests for Summarizer Plugin (v0.2.5) - 12 tests."""

import pytest
from lmapp.plugins.example_summarizer import SummarizerPlugin


class TestSummarizerPlugin:
    def test_metadata(self):
        plugin = SummarizerPlugin()
        assert plugin.metadata.name == "summarizer"
        assert "summarization" in plugin.metadata.tags
    
    def test_summarize_text(self):
        plugin = SummarizerPlugin()
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = plugin.execute(text=text)
        
        assert "summary" in result
        assert len(result["summary"]) < len(text)
        assert result["key_sentences"]
    
    def test_compression_ratio(self):
        plugin = SummarizerPlugin()
        text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
        result = plugin.execute(text=text)
        
        assert "compression_ratio" in result
        assert 0 < result["compression_ratio"] < 1
    
    def test_short_text(self):
        plugin = SummarizerPlugin()
        text = "Only one sentence."
        result = plugin.execute(text=text)
        
        assert result["summary"] == text
    
    def test_no_text_error(self):
        plugin = SummarizerPlugin()
        result = plugin.execute()
        
        assert result["status"] == "error"
    
    def test_set_compression(self):
        plugin = SummarizerPlugin()
        commands = plugin.get_commands()
        
        result = commands["set-compression"](ratio=0.5)
        assert plugin.compression_ratio == 0.5
    
    def test_compression_bounds(self):
        plugin = SummarizerPlugin()
        commands = plugin.get_commands()
        
        commands["set-compression"](ratio=1.5)  # Should clamp
        assert plugin.compression_ratio == 0.9
        
        commands["set-compression"](ratio=0.05)  # Should clamp
        assert plugin.compression_ratio == 0.1
    
    def test_stats_tracking(self):
        plugin = SummarizerPlugin()
        plugin.execute(text="Sentence one. Sentence two.")
        plugin.execute(text="Another one. Another two.")
        
        assert plugin.stats["summaries_created"] == 2
    
    def test_cleanup(self):
        plugin = SummarizerPlugin()
        plugin.execute(text="Text here. More text.")
        assert plugin.stats["summaries_created"] > 0
        
        plugin.cleanup()
        assert plugin.stats["summaries_created"] == 0
    
    def test_key_sentences_extraction(self):
        plugin = SummarizerPlugin()
        text = "Important concept first. Relevant second idea. Key point third."
        result = plugin.execute(text=text)
        
        assert len(result["key_sentences"]) > 0
        for sentence in result["key_sentences"]:
            assert sentence in text
    
    def test_summarize_command(self):
        plugin = SummarizerPlugin()
        commands = plugin.get_commands()
        
        result = commands["summarize"](text="Text one. Text two. Text three.")
        assert "summary" in result
    
    def test_multiple_plugins_independent(self):
        p1 = SummarizerPlugin()
        p2 = SummarizerPlugin()
        
        p1.initialize({"compression_ratio": 0.2})
        p2.initialize({"compression_ratio": 0.8})
        
        assert p1.compression_ratio == 0.2
        assert p2.compression_ratio == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
