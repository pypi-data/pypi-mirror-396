"""
Q&A Bot Plugin for LMAPP v0.2.5.

Question answering over documents using simple pattern matching and indexing.
Finds relevant passages and extracts answers (no ML, no external API calls).
"""

from typing import Dict, Optional, Any, Callable, List
from dataclasses import dataclass, field
import re

from .plugin_manager import BasePlugin, PluginMetadata


@dataclass
class Document:
    """Document in Q&A knowledge base."""
    id: str
    title: str
    content: str
    passages: List[str] = field(default_factory=list)
    
    def extract_passages(self, min_length: int = 20) -> None:
        """Extract sentences as passages."""
        self.passages = [
            p.strip() for p in re.split(r'[.!?]+', self.content)
            if p.strip() and len(p.strip()) > min_length
        ]


class QABotPlugin(BasePlugin):
    """Question-answering plugin for document-based Q&A."""
    
    def __init__(self):
        self._metadata = PluginMetadata(
            name="qa-bot",
            version="0.1.0",
            description="Question answering over document knowledge base",
            author="LMAPP Team",
            license="MIT",
            dependencies=[],
            entry_point="example_qa_bot:QABotPlugin",
            tags=["qa", "question-answering", "knowledge-base", "search"],
        )
        self.documents: Dict[str, Document] = {}
        self.stats = {"questions_answered": 0, "documents_indexed": 0}
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        if config:
            docs = config.get("documents", [])
            for doc in docs:
                self.add_document(doc["id"], doc["title"], doc["content"])
    
    def add_document(self, doc_id: str, title: str, content: str) -> None:
        """Add document to knowledge base."""
        doc = Document(id=doc_id, title=title, content=content)
        doc.extract_passages()
        self.documents[doc_id] = doc
        self.stats["documents_indexed"] += 1
    
    def _match_score(self, question: str, passage: str) -> float:
        """Calculate relevance score between question and passage."""
        q_words = set(re.findall(r'\w+', question.lower()))
        p_words = set(re.findall(r'\w+', passage.lower()))
        
        common = q_words & p_words
        return len(common) / max(len(q_words), 1) if q_words else 0
    
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Answer a question.
        
        Args:
            question: Question to answer
            top_k: Number of passages to return (default: 3)
        
        Returns:
            Dict with answers and matching passages
        """
        question = kwargs.get("question", "") or (args[0] if args else "")
        if not question:
            return {"status": "error", "message": "No question provided"}
        
        if not self.documents:
            return {"status": "error", "message": "No documents in knowledge base"}
        
        top_k = kwargs.get("top_k", 3)
        
        # Score all passages
        all_scores = []
        for doc_id, doc in self.documents.items():
            for passage in doc.passages:
                score = self._match_score(question, passage)
                all_scores.append((score, doc_id, doc.title, passage))
        
        # Get top passages
        top_passages = sorted(all_scores, key=lambda x: x[0], reverse=True)[:top_k]
        
        self.stats["questions_answered"] += 1
        
        return {
            "question": question,
            "answers": [
                {
                    "relevance": round(score, 3),
                    "document": title,
                    "passage": passage
                }
                for score, doc_id, title, passage in top_passages
            ],
            "num_documents_searched": len(self.documents),
            "num_passages_searched": sum(len(d.passages) for d in self.documents.values()),
        }
    
    def cleanup(self) -> None:
        self.documents.clear()
        self.stats = {"questions_answered": 0, "documents_indexed": 0}
    
    def get_commands(self) -> Dict[str, Callable]:
        return {
            "ask": lambda *a, **k: self.execute(*a, **k),
            "add-document": self._add_doc_command,
            "qa-stats": lambda *a, **k: {"stats": self.stats.copy()},
        }
    
    def _add_doc_command(self, *args, **kwargs) -> Dict[str, Any]:
        doc_id = kwargs.get("id", "")
        title = kwargs.get("title", "")
        content = kwargs.get("content", "")
        
        if not all([doc_id, title, content]):
            return {"error": "id, title, and content required"}
        
        self.add_document(doc_id, title, content)
        return {"status": "success", "message": f"Added document '{title}'"}


__all__ = ["QABotPlugin", "Document"]

PLUGIN_MANIFEST = {
    "name": "qa-bot",
    "version": "0.1.0",
    "author": "LMAPP Team",
    "description": "Question answering over document knowledge base",
    "repository": "https://github.com/nabaznyl/lmapp/tree/mother/src/lmapp/plugins",
    "tags": ["qa", "question-answering", "knowledge-base", "search"],
    "dependencies": [],
    "license": "MIT",
}
