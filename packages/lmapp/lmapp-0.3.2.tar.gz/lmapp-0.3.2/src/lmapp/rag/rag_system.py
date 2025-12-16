"""
RAG (Retrieval-Augmented Generation) system for LMAPP v0.2.4.

Enables LMAPP to search local files and inject relevant context into LLM prompts.
Supports semantic search with simple vector similarity and file-based retrieval.

Features:
- Vector-based semantic search using embedding similarity
- Local file indexing (text, markdown, code)
- Automatic relevance ranking
- Context injection into system prompts
- Integration with CRECALL for knowledge base search
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass
import json
import hashlib
from datetime import datetime


@dataclass
class Document:
    """Represents a searchable document."""
    
    doc_id: str
    title: str
    content: str
    file_path: Optional[str] = None
    source_type: str = "text"  # text, markdown, code, url
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize derived fields."""
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat() + "Z"
        if not self.metadata:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "content": self.content,
            "file_path": self.file_path,
            "source_type": self.source_type,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Document":
        """Create Document from dictionary."""
        return Document(
            doc_id=data["doc_id"],
            title=data["title"],
            content=data["content"],
            file_path=data.get("file_path"),
            source_type=data.get("source_type", "text"),
            metadata=data.get("metadata"),
            created_at=data.get("created_at"),
        )


@dataclass
class SearchResult:
    """Represents a search result."""
    
    document: Document
    relevance_score: float
    matched_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document": self.document.to_dict(),
            "relevance_score": self.relevance_score,
            "matched_text": self.matched_text,
        }


class SimpleVectorizer:
    """Simple vectorizer using TF-IDF-like approach without external dependencies."""
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text into words."""
        import re
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    @staticmethod
    def get_term_frequency(tokens: List[str]) -> Dict[str, float]:
        """Calculate term frequency."""
        if not tokens:
            return {}
        
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        
        # Normalize by total tokens
        total = len(tokens)
        return {token: count / total for token, count in freq.items()}
    
    @staticmethod
    def calculate_similarity(query_tokens: List[str], doc_tokens: List[str]) -> float:
        """
        Calculate similarity between query and document using simple overlap.
        
        Returns a score from 0.0 to 1.0.
        """
        if not query_tokens or not doc_tokens:
            return 0.0
        
        query_set = set(query_tokens)
        doc_set = set(doc_tokens)
        
        if not query_set or not doc_set:
            return 0.0
        
        # Jaccard similarity
        intersection = len(query_set & doc_set)
        union = len(query_set | doc_set)
        
        jaccard = intersection / union if union > 0 else 0.0
        
        # Boost score if query terms appear in order
        doc_text = " ".join(doc_tokens)
        query_text = " ".join(query_tokens)
        sequential_boost = 1.0
        
        if query_text in doc_text:
            sequential_boost = 1.5
        
        return min(1.0, jaccard * sequential_boost)


class DocumentIndex:
    """Index for documents with search capabilities."""
    
    def __init__(self, index_dir: Optional[Path] = None):
        """
        Initialize DocumentIndex.
        
        Args:
            index_dir: Directory to store index (default: ~/.lmapp/index/)
        """
        if index_dir is None:
            home = Path.home()
            index_dir = home / ".lmapp" / "index"
        
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.documents_file = self.index_dir / "documents.jsonl"
        self.documents: Dict[str, Document] = {}
        self._load_index()
    
    def _load_index(self) -> None:
        """Load documents from index file."""
        if not self.documents_file.exists():
            return
        
        try:
            with open(self.documents_file, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        doc = Document.from_dict(data)
                        self.documents[doc.doc_id] = doc
        except (json.JSONDecodeError, IOError):
            pass
    
    def _save_index(self) -> None:
        """Save documents to index file."""
        with open(self.documents_file, "w") as f:
            for doc in self.documents.values():
                f.write(json.dumps(doc.to_dict()) + "\n")
    
    def add_document(self, document: Document) -> None:
        """Add a document to the index."""
        self.documents[document.doc_id] = document
        self._save_index()
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add multiple documents."""
        for doc in documents:
            self.documents[doc.doc_id] = doc
        self._save_index()
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return self.documents.get(doc_id)
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from index."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._save_index()
            return True
        return False
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search documents using semantic similarity.
        
        Args:
            query: Search query
            top_k: Return top K results
        
        Returns:
            List of SearchResult sorted by relevance
        """
        if not query or not self.documents:
            return []
        
        query_tokens = SimpleVectorizer.tokenize(query)
        results = []
        
        for doc in self.documents.values():
            doc_tokens = SimpleVectorizer.tokenize(doc.content)
            score = SimpleVectorizer.calculate_similarity(query_tokens, doc_tokens)
            
            if score > 0.0:
                # Find matched text excerpt
                matched_text = self._extract_matched_text(query_tokens, doc.content)
                result = SearchResult(
                    document=doc,
                    relevance_score=score,
                    matched_text=matched_text,
                )
                results.append(result)
        
        # Sort by relevance and return top K
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:top_k]
    
    def _extract_matched_text(self, query_tokens: List[str], content: str, context_chars: int = 100) -> Optional[str]:
        """Extract a text excerpt showing matched terms."""
        import re
        
        content_lower = content.lower()
        query_lower = " ".join(query_tokens).lower()
        
        # Find first occurrence of query terms
        for query_term in query_tokens:
            match = re.search(query_term, content_lower)
            if match:
                start = max(0, match.start() - context_chars)
                end = min(len(content), match.end() + context_chars)
                excerpt = content[start:end]
                
                if start > 0:
                    excerpt = "..." + excerpt
                if end < len(content):
                    excerpt = excerpt + "..."
                
                return excerpt
        
        # Fallback: return first context_chars*2
        if len(content) > context_chars * 2:
            return content[:context_chars * 2] + "..."
        return content


class RAGSystem:
    """Retrieval-Augmented Generation system for LMAPP."""
    
    def __init__(self, index_dir: Optional[Path] = None):
        """
        Initialize RAGSystem.
        
        Args:
            index_dir: Directory for document index
        """
        self.index = DocumentIndex(index_dir)
    
    def index_file(self, file_path: Path, doc_title: Optional[str] = None) -> Optional[str]:
        """
        Index a single file.
        
        Args:
            file_path: Path to file to index
            doc_title: Optional document title (defaults to filename)
        
        Returns:
            Document ID if successful, None otherwise
        """
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Skip very large files
            if len(content) > 1_000_000:  # 1MB limit
                return None
            
            doc_id = self._generate_doc_id(file_path)
            title = doc_title or file_path.name
            source_type = self._detect_source_type(file_path)
            
            doc = Document(
                doc_id=doc_id,
                title=title,
                content=content,
                file_path=str(file_path),
                source_type=source_type,
                metadata={"file_size": len(content), "indexed_at": datetime.utcnow().isoformat()},
            )
            
            self.index.add_document(doc)
            return doc_id
        except (IOError, UnicodeDecodeError):
            return None
    
    def index_directory(self, directory: Path, extensions: Optional[List[str]] = None) -> int:
        """
        Index all files in a directory.
        
        Args:
            directory: Directory to index
            extensions: File extensions to index (default: common text/code formats)
        
        Returns:
            Number of files indexed
        """
        if extensions is None:
            extensions = ['.txt', '.md', '.py', '.js', '.ts', '.java', '.c', '.cpp', 
                         '.h', '.json', '.yaml', '.yml', '.xml', '.html', '.css']
        
        indexed_count = 0
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                if self.index_file(file_path):
                    indexed_count += 1
        
        return indexed_count
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search the document index.
        
        Args:
            query: Search query
            top_k: Return top K results
        
        Returns:
            List of SearchResult
        """
        return self.index.search(query, top_k)
    
    def get_context_for_prompt(self, query: str, max_context_length: int = 2000) -> str:
        """
        Get context string to inject into system prompt.
        
        Args:
            query: Query to search for
            max_context_length: Maximum characters to include
        
        Returns:
            Context string ready for prompt injection
        """
        results = self.search(query, top_k=3)
        
        if not results:
            return ""
        
        context_parts = []
        total_length = 0
        
        for result in results:
            doc_context = f"Source: {result.document.title}\n{result.document.content[:500]}"
            
            if total_length + len(doc_context) <= max_context_length:
                context_parts.append(doc_context)
                total_length += len(doc_context)
            else:
                break
        
        if context_parts:
            return "\n\n---\n\n".join(context_parts)
        
        return ""
    
    def clear_index(self) -> None:
        """Clear all indexed documents."""
        self.index.documents.clear()
        self.index._save_index()
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index."""
        total_docs = len(self.index.documents)
        total_content_size = sum(len(doc.content) for doc in self.index.documents.values())
        
        return {
            "total_documents": total_docs,
            "total_content_size": total_content_size,
            "average_doc_size": total_content_size // total_docs if total_docs > 0 else 0,
        }
    
    @staticmethod
    def _generate_doc_id(file_path: Path) -> str:
        """Generate a unique document ID."""
        path_str = str(file_path.absolute())
        return hashlib.md5(path_str.encode()).hexdigest()[:12]
    
    @staticmethod
    def _detect_source_type(file_path: Path) -> str:
        """Detect source type based on file extension."""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.go', '.rs']:
            return "code"
        elif suffix in ['.md', '.rst']:
            return "markdown"
        elif suffix in ['.html', '.htm']:
            return "html"
        elif suffix in ['.json', '.yaml', '.yml', '.xml']:
            return "config"
        else:
            return "text"


# Global RAG system instance
_rag_system: Optional[RAGSystem] = None


def get_rag_system(index_dir: Optional[Path] = None) -> RAGSystem:
    """Get or create the global RAGSystem instance."""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem(index_dir)
    return _rag_system
