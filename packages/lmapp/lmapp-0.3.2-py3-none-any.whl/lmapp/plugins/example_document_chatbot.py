#!/usr/bin/env python3
"""
Document Chatbot Plugin
Multi-document conversation with citation tracking and context awareness
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .plugin_manager import BasePlugin, PluginMetadata


@dataclass
class Citation:
    """Citation information"""
    document: str
    page: Optional[int] = None
    line: Optional[int] = None
    context: str = ""


@dataclass
class ConversationTurn:
    """Single turn in conversation"""
    id: str
    user_message: str
    bot_response: str
    citations: List[Citation] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    confidence: float = 0.0


@dataclass
class DocumentContext:
    """Context from a document"""
    document_id: str
    document_name: str
    content: str
    relevance_score: float
    chunk_index: int = 0


class ConversationMemory:
    """Maintains conversation history with document context"""

    def __init__(self, max_turns: int = 50):
        self.turns: List[ConversationTurn] = []
        self.max_turns = max_turns
        self.document_context: List[DocumentContext] = []

    def add_turn(self, turn: ConversationTurn) -> None:
        """Add conversation turn to memory"""
        self.turns.append(turn)

        # Keep only recent turns to manage memory
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns :]

    def get_context_for_response(self, query: str, depth: int = 3) -> str:
        """Build context from recent conversation for LLM response generation"""
        if not self.turns:
            return ""

        recent_turns = self.turns[-depth:]
        context_parts = []

        for turn in recent_turns:
            context_parts.append(f"User: {turn.user_message}")
            context_parts.append(f"Assistant: {turn.bot_response}")

        return "\n".join(context_parts)

    def get_conversation_summary(self) -> str:
        """Get summary of conversation topics"""
        if not self.turns:
            return "No conversation yet"

        topics = set()
        for turn in self.turns:
            # Extract key terms (simplified)
            words = turn.user_message.lower().split()
            topics.update(w for w in words if len(w) > 4)

        return f"Conversation about: {', '.join(list(topics)[:10])}"

    def clear(self) -> None:
        """Clear conversation history"""
        self.turns = []
        self.document_context = []


class DocumentChatbotPlugin(BasePlugin):
    """
    Multi-document chatbot with context awareness and citation tracking.
    
    Features:
    - Maintains conversation state across multiple documents
    - Tracks citations for each response
    - Relevance scoring for source documents
    - Conversation memory with context injection
    """

    _METADATA = PluginMetadata(
        name="document_chatbot",
        version="1.0.0",
        author="lmapp-dev",
        description="Multi-document Q&A with conversation memory and citations",
        license="MIT",
        dependencies=[],
        tags=["qa", "documents", "conversation", "search"],
    )

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return self._METADATA
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the plugin."""
        pass

    def __init__(self):
        """Initialize document chatbot"""
        super().__init__()
        self.memory = ConversationMemory()
        self.indexed_documents: Dict[str, str] = {}  # doc_id -> content
        self.document_metadata: Dict[str, Dict[str, Any]] = {}

    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute chatbot operations.
        
        Args:
            action: 'chat', 'add_document', 'list_documents', 'clear', 'get_history'
            query/message: User message
            documents: List of document contents
            
        Returns:
            Dictionary with response and citations
        """
        action = kwargs.get("action", "chat")

        if action == "chat":
            return self._handle_chat(kwargs.get("message", ""))
        elif action == "add_document":
            return self._add_document(
                kwargs.get("doc_id", ""),
                kwargs.get("name", ""),
                kwargs.get("content", ""),
            )
        elif action == "list_documents":
            return self._list_documents()
        elif action == "clear":
            return self._clear_conversation()
        elif action == "get_history":
            return self._get_conversation_history()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def _handle_chat(self, user_message: str) -> Dict[str, Any]:
        """Handle user message and generate response"""
        if not user_message:
            return {"status": "error", "message": "Empty message"}

        if not self.indexed_documents:
            return {
                "status": "error",
                "message": "No documents loaded. Use add_document action first.",
            }

        # Find relevant documents
        relevant_docs = self._find_relevant_documents(user_message)

        # Generate response (in production, would call LLM)
        bot_response = self._generate_response(user_message, relevant_docs)

        # Extract citations
        citations = self._extract_citations(user_message, relevant_docs)

        # Create conversation turn
        turn = ConversationTurn(
            id=f"turn_{len(self.memory.turns) + 1}",
            user_message=user_message,
            bot_response=bot_response,
            citations=citations,
            sources=[doc.document_name for doc in relevant_docs],
            confidence=self._calculate_confidence(relevant_docs),
        )

        self.memory.add_turn(turn)

        return {
            "status": "success",
            "response": bot_response,
            "citations": [asdict(c) for c in citations],
            "sources": turn.sources,
            "confidence": turn.confidence,
            "turn_id": turn.id,
            "context_summary": self.memory.get_conversation_summary(),
        }

    def _add_document(self, doc_id: str, name: str, content: str) -> Dict[str, Any]:
        """Add document to index"""
        if not doc_id or not content:
            return {"status": "error", "message": "doc_id and content required"}

        self.indexed_documents[doc_id] = content
        self.document_metadata[doc_id] = {
            "name": name or doc_id,
            "size_bytes": len(content.encode()),
            "added_at": time.time(),
            "word_count": len(content.split()),
        }

        return {
            "status": "success",
            "message": f"Added document: {name or doc_id}",
            "doc_id": doc_id,
            "stats": self.document_metadata[doc_id],
        }

    def _list_documents(self) -> Dict[str, Any]:
        """List all indexed documents"""
        docs_info = []
        for doc_id, metadata in self.document_metadata.items():
            docs_info.append(
                {
                    "doc_id": doc_id,
                    "name": metadata["name"],
                    "word_count": metadata["word_count"],
                    "size_kb": metadata["size_bytes"] / 1024,
                }
            )

        return {
            "status": "success",
            "total_documents": len(docs_info),
            "documents": docs_info,
        }

    def _clear_conversation(self) -> Dict[str, Any]:
        """Clear conversation history (keeps documents)"""
        turn_count = len(self.memory.turns)
        self.memory.clear()

        return {
            "status": "success",
            "message": f"Cleared {turn_count} conversation turns",
            "turns_cleared": turn_count,
        }

    def _get_conversation_history(self) -> Dict[str, Any]:
        """Get full conversation history with citations"""
        history = []
        for turn in self.memory.turns:
            history.append(
                {
                    "turn_id": turn.id,
                    "user": turn.user_message,
                    "assistant": turn.bot_response,
                    "sources": turn.sources,
                    "confidence": turn.confidence,
                    "timestamp": turn.timestamp,
                }
            )

        return {
            "status": "success",
            "total_turns": len(history),
            "history": history,
            "summary": self.memory.get_conversation_summary(),
        }

    def _find_relevant_documents(self, query: str) -> List[DocumentContext]:
        """Find documents relevant to query (simplified)"""
        relevant = []

        for doc_id, content in self.indexed_documents.items():
            # Simple keyword matching
            query_terms = set(query.lower().split())
            doc_terms = set(content.lower().split())
            matches = len(query_terms & doc_terms)

            if matches > 0:
                relevance_score = matches / len(query_terms) if query_terms else 0

                relevant.append(
                    DocumentContext(
                        document_id=doc_id,
                        document_name=self.document_metadata[doc_id]["name"],
                        content=content[:500],  # Limit content size
                        relevance_score=relevance_score,
                    )
                )

        # Sort by relevance
        relevant.sort(key=lambda x: x.relevance_score, reverse=True)
        return relevant[:3]  # Return top 3

    def _generate_response(
        self, query: str, relevant_docs: List[DocumentContext]
    ) -> str:
        """Generate response based on query and documents (simplified)"""
        if not relevant_docs:
            return "I couldn't find information about this in the available documents."

        # Build response from document content
        context = " ".join(doc.content for doc in relevant_docs)
        return f"Based on the documents, I found relevant information. {context[:200]}..."

    def _extract_citations(
        self, query: str, relevant_docs: List[DocumentContext]
    ) -> List[Citation]:
        """Extract citations from relevant documents"""
        citations = []

        for doc in relevant_docs:
            # Find first matching line (simplified)
            lines = doc.content.split("\n")
            for i, line in enumerate(lines[:10]):  # Check first 10 lines
                if any(word in line.lower() for word in query.lower().split()):
                    citations.append(
                        Citation(
                            document=doc.document_name,
                            line=i + 1,
                            context=line.strip()[:100],
                        )
                    )
                    break

        return citations

    def _calculate_confidence(self, relevant_docs: List[DocumentContext]) -> float:
        """Calculate confidence in response based on document relevance"""
        if not relevant_docs:
            return 0.0

        avg_relevance = sum(d.relevance_score for d in relevant_docs) / len(
            relevant_docs
        )
        return min(avg_relevance, 1.0)
