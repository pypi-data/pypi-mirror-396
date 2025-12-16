#!/usr/bin/env python3
"""
Tests for Document Chatbot Plugin
"""


from lmapp.plugins.example_document_chatbot import (
    DocumentChatbotPlugin,
    ConversationMemory,
    ConversationTurn,
    Citation,
)


class TestCitation:
    """Test citation data class"""

    def test_citation_creation(self):
        """Test citation can be created"""
        citation = Citation(
            document="doc.txt",
            page=1,
            line=42,
            context="Example text",
        )
        assert citation.document == "doc.txt"
        assert citation.line == 42


class TestConversationTurn:
    """Test conversation turn data class"""

    def test_turn_creation(self):
        """Test turn can be created"""
        turn = ConversationTurn(
            id="turn_1",
            user_message="What is AI?",
            bot_response="AI is artificial intelligence",
        )
        assert turn.id == "turn_1"
        assert turn.user_message == "What is AI?"
        assert turn.confidence == 0.0


class TestConversationMemory:
    """Test conversation memory"""

    def test_memory_initialization(self):
        """Test memory can be initialized"""
        memory = ConversationMemory()
        assert len(memory.turns) == 0

    def test_add_turn(self):
        """Test adding turn to memory"""
        memory = ConversationMemory()
        turn = ConversationTurn(
            id="turn_1",
            user_message="Test",
            bot_response="Response",
        )

        memory.add_turn(turn)
        assert len(memory.turns) == 1
        assert memory.turns[0].id == "turn_1"

    def test_memory_max_turns_limit(self):
        """Test memory respects max turns limit"""
        memory = ConversationMemory(max_turns=3)

        for i in range(5):
            turn = ConversationTurn(
                id=f"turn_{i}",
                user_message=f"Message {i}",
                bot_response=f"Response {i}",
            )
            memory.add_turn(turn)

        assert len(memory.turns) == 3  # Should only keep last 3

    def test_get_context_for_response(self):
        """Test context generation"""
        memory = ConversationMemory()

        turn1 = ConversationTurn(
            id="turn_1",
            user_message="First question",
            bot_response="First answer",
        )
        turn2 = ConversationTurn(
            id="turn_2",
            user_message="Second question",
            bot_response="Second answer",
        )

        memory.add_turn(turn1)
        memory.add_turn(turn2)

        context = memory.get_context_for_response("Test query")

        assert "First question" in context
        assert "First answer" in context
        assert "Second question" in context

    def test_get_conversation_summary(self):
        """Test conversation summary"""
        memory = ConversationMemory()

        turn = ConversationTurn(
            id="turn_1",
            user_message="Tell me about Python programming",
            bot_response="Python is great",
        )

        memory.add_turn(turn)

        summary = memory.get_conversation_summary()

        assert "Python" in summary or "programming" in summary

    def test_clear_conversation(self):
        """Test clearing conversation"""
        memory = ConversationMemory()

        turn = ConversationTurn(
            id="turn_1",
            user_message="Test",
            bot_response="Response",
        )

        memory.add_turn(turn)
        assert len(memory.turns) > 0

        memory.clear()
        assert len(memory.turns) == 0


class TestDocumentChatbotPlugin:
    """Test document chatbot plugin"""

    def test_plugin_initialization(self):
        """Test plugin can be instantiated"""
        plugin = DocumentChatbotPlugin()
        assert plugin.metadata.name == "document_chatbot"
        assert plugin.metadata.version == "1.0.0"

    def test_plugin_has_memory(self):
        """Test plugin has conversation memory"""
        plugin = DocumentChatbotPlugin()
        assert hasattr(plugin, "memory")
        assert isinstance(plugin.memory, ConversationMemory)

    def test_add_document(self):
        """Test adding document"""
        plugin = DocumentChatbotPlugin()

        result = plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Test Document",
            content="This is test content",
        )

        assert result["status"] == "success"
        assert "doc1" in plugin.indexed_documents

    def test_add_multiple_documents(self):
        """Test adding multiple documents"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Doc 1",
            content="Content 1",
        )
        plugin.execute(
            action="add_document",
            doc_id="doc2",
            name="Doc 2",
            content="Content 2",
        )

        result = plugin.execute(action="list_documents")

        assert result["total_documents"] == 2

    def test_list_documents(self):
        """Test listing documents"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Test",
            content="Content",
        )

        result = plugin.execute(action="list_documents")

        assert result["status"] == "success"
        assert "documents" in result
        assert len(result["documents"]) == 1

    def test_chat_without_documents(self):
        """Test chat fails without documents"""
        plugin = DocumentChatbotPlugin()

        result = plugin.execute(action="chat", message="Hello?")

        assert result["status"] == "error"

    def test_chat_with_documents(self):
        """Test chat with documents"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="AI Guide",
            content="Artificial intelligence is the simulation of human intelligence",
        )

        result = plugin.execute(action="chat", message="What is AI?")

        assert result["status"] == "success"
        assert "response" in result
        assert "citations" in result

    def test_chat_tracks_citations(self):
        """Test that chat response includes citations"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Python Guide",
            content="Python is a high-level programming language",
        )

        result = plugin.execute(action="chat", message="Python language")

        assert "citations" in result
        assert isinstance(result["citations"], list)

    def test_chat_tracks_sources(self):
        """Test that chat response tracks source documents"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Source Doc",
            content="Source content here",
        )

        result = plugin.execute(action="chat", message="Content test")

        assert "sources" in result

    def test_chat_has_confidence_score(self):
        """Test that response includes confidence score"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Doc",
            content="Test document content",
        )

        result = plugin.execute(action="chat", message="Test")

        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

    def test_clear_conversation(self):
        """Test clearing conversation history"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Doc",
            content="Content",
        )

        plugin.execute(action="chat", message="First message")
        plugin.execute(action="chat", message="Second message")

        result = plugin.execute(action="clear")

        assert result["status"] == "success"
        assert result["turns_cleared"] == 2

    def test_get_conversation_history(self):
        """Test getting conversation history"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Doc",
            content="Content",
        )

        plugin.execute(action="chat", message="First question")
        plugin.execute(action="chat", message="Second question")

        result = plugin.execute(action="get_history")

        assert result["status"] == "success"
        assert result["total_turns"] == 2
        assert "history" in result

    def test_conversation_memory_preserved(self):
        """Test that conversation memory is preserved across chats"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Doc",
            content="Document content about testing",
        )

        result1 = plugin.execute(action="chat", message="Testing framework")
        turn1_id = result1["turn_id"]

        plugin.execute(action="chat", message="More about it")

        history = plugin.execute(action="get_history")

        assert len(history["history"]) == 2
        assert history["history"][0]["turn_id"] == turn1_id

    def test_find_relevant_documents(self):
        """Test document relevance finding"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Python",
            content="Python is a programming language",
        )
        plugin.execute(
            action="add_document",
            doc_id="doc2",
            name="Java",
            content="Java is another language",
        )

        relevant = plugin._find_relevant_documents("Python programming")

        assert len(relevant) > 0
        assert relevant[0].document_id == "doc1"

    def test_document_metadata_tracking(self):
        """Test that document metadata is tracked"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Test Doc",
            content="Content here",
        )

        docs = plugin.execute(action="list_documents")

        assert docs["documents"][0]["name"] == "Test Doc"
        assert docs["documents"][0]["word_count"] == 2

    def test_empty_message_handling(self):
        """Test handling of empty messages"""
        plugin = DocumentChatbotPlugin()

        plugin.execute(
            action="add_document",
            doc_id="doc1",
            name="Doc",
            content="Content",
        )

        result = plugin.execute(action="chat", message="")

        assert result["status"] == "error"

    def test_plugin_has_execute_method(self):
        """Test plugin implements execute method"""
        plugin = DocumentChatbotPlugin()
        assert hasattr(plugin, "execute")
        assert callable(plugin.execute)

    def test_unknown_action_handling(self):
        """Test handling of unknown actions"""
        plugin = DocumentChatbotPlugin()

        result = plugin.execute(action="unknown_action")

        assert result["status"] == "error"
