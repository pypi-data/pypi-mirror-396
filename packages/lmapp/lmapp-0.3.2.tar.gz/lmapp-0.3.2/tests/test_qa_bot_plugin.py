"""Tests for Q&A Bot Plugin (v0.2.5) - 12 tests."""

import pytest
from lmapp.plugins.example_qa_bot import QABotPlugin


class TestQABotPlugin:
    def test_metadata(self):
        plugin = QABotPlugin()
        assert plugin.metadata.name == "qa-bot"
        assert "question-answering" in plugin.metadata.tags
    
    def test_add_document(self):
        plugin = QABotPlugin()
        plugin.add_document("doc1", "Title", "Content here. More content.")
        
        assert "doc1" in plugin.documents
        assert plugin.stats["documents_indexed"] == 1
    
    def test_question_answering(self):
        plugin = QABotPlugin()
        plugin.add_document(
            "faq",
            "FAQ",
            "Python is a programming language. JavaScript runs in browsers. Java is object-oriented."
        )
        
        result = plugin.execute(question="What is Python?")
        
        assert "answers" in result
        assert len(result["answers"]) > 0
        assert "relevance" in result["answers"][0]
    
    def test_no_documents_error(self):
        plugin = QABotPlugin()
        result = plugin.execute(question="What is Python?")
        
        assert result["status"] == "error"
    
    def test_no_question_error(self):
        plugin = QABotPlugin()
        plugin.add_document("doc1", "Title", "Content.")
        
        result = plugin.execute()
        assert result["status"] == "error"
    
    def test_top_k_results(self):
        plugin = QABotPlugin()
        plugin.add_document(
            "doc1",
            "Tech",
            "Python is great. JavaScript is powerful. Java works everywhere. Go is fast."
        )
        
        result = plugin.execute(question="programming", top_k=2)
        
        assert len(result["answers"]) <= 2
    
    def test_relevance_scoring(self):
        plugin = QABotPlugin()
        plugin.add_document(
            "doc1",
            "Science",
            "Earth is round. Water boils at 100C. Space is vast. Chemistry studies matter."
        )
        
        result = plugin.execute(question="chemistry")
        
        # Should find relevant passages
        assert any("relevance" in a for a in result["answers"])
        max_relevance = max(a["relevance"] for a in result["answers"])
        assert max_relevance > 0
    
    def test_stats_tracking(self):
        plugin = QABotPlugin()
        plugin.add_document("d1", "Title", "Content.")
        plugin.execute(question="test?")
        plugin.execute(question="another?")
        
        assert plugin.stats["questions_answered"] == 2
        assert plugin.stats["documents_indexed"] == 1
    
    def test_cleanup(self):
        plugin = QABotPlugin()
        plugin.add_document("d1", "T", "Content.")
        assert len(plugin.documents) > 0
        
        plugin.cleanup()
        assert len(plugin.documents) == 0
        assert plugin.stats["documents_indexed"] == 0
    
    def test_get_commands(self):
        plugin = QABotPlugin()
        commands = plugin.get_commands()
        
        assert "ask" in commands
        assert "add-document" in commands
        assert "qa-stats" in commands
    
    def test_ask_command(self):
        plugin = QABotPlugin()
        plugin.add_document("doc", "Title", "Machine learning. Deep learning.")
        
        commands = plugin.get_commands()
        result = commands["ask"](question="learning")
        
        assert "answers" in result
    
    def test_multiple_documents(self):
        plugin = QABotPlugin()
        plugin.add_document("d1", "Python", "Python syntax is simple.")
        plugin.add_document("d2", "JavaScript", "JavaScript runs in browsers.")
        
        result = plugin.execute(question="syntax")
        
        assert result["num_documents_searched"] == 2
    
    def test_add_document_command(self):
        plugin = QABotPlugin()
        commands = plugin.get_commands()
        
        result = commands["add-document"](
            id="doc1",
            title="Title",
            content="Some content here."
        )
        
        assert result["status"] == "success"
        assert "doc1" in plugin.documents


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
