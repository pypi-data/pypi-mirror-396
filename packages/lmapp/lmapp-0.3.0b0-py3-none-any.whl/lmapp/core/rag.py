"""
Retrieval-Augmented Generation (RAG) for LMAPP v0.2.4.

Simple file indexing and search system for context injection into LLM prompts.
Supports keyword-based search with document chunking.
"""

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Document:
    """Represents a document chunk."""

    id: str
    title: str
    content: str
    source_path: str
    chunk_index: int = 0
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "source_path": self.source_path,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata or {},
        }


class DocumentChunker:
    """Splits documents into searchable chunks."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        """Initialize chunker."""
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(
        self,
        text: str,
        title: str,
        source_path: str,
    ) -> List[Document]:
        """Split text into chunks."""
        if len(text) <= self.chunk_size:
            doc_id = self._generate_id(title, source_path, 0)
            return [
                Document(
                    id=doc_id,
                    title=title,
                    content=text,
                    source_path=source_path,
                    chunk_index=0,
                    metadata={"file_size": len(text)},
                )
            ]

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # Try to break at sentence boundary
            if end < len(text):
                for i in range(end - 1, max(start, end - 200), -1):
                    if text[i] in ".!?\n":
                        end = i + 1
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                doc_id = self._generate_id(title, source_path, chunk_index)
                chunks.append(
                    Document(
                        id=doc_id,
                        title=title,
                        content=chunk_text,
                        source_path=source_path,
                        chunk_index=chunk_index,
                        metadata={
                            "start_pos": start,
                            "end_pos": end,
                            "total_chunks": 0,
                        },
                    )
                )
                chunk_index += 1

            start = end - self.overlap if end < len(text) else len(text)

        # Set total chunks in metadata
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)

        return chunks

    @staticmethod
    def _generate_id(title: str, path: str, index: int) -> str:
        """Generate unique chunk ID."""
        key = f"{path}:{title}:{index}"
        return hashlib.md5(key.encode()).hexdigest()[:12]


class DocumentIndex:
    """In-memory index of documents for search."""

    def __init__(self):
        """Initialize index."""
        self.documents: Dict[str, Document] = {}
        self.word_index: Dict[str, List[str]] = {}

    def add_document(self, document: Document) -> None:
        """Add document to index."""
        self.documents[document.id] = document

        words = self._extract_words(document.content)
        for word in set(words):
            if word not in self.word_index:
                self.word_index[word] = []
            if document.id not in self.word_index[word]:
                self.word_index[word].append(document.id)

    def remove_document(self, doc_id: str) -> None:
        """Remove document from index."""
        if doc_id in self.documents:
            del self.documents[doc_id]

        for word in list(self.word_index.keys()):
            if doc_id in self.word_index[word]:
                self.word_index[word].remove(doc_id)
            if not self.word_index[word]:
                del self.word_index[word]

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Search documents by keyword."""
        query_words = self._extract_words(query)
        if not query_words:
            return []

        doc_scores: Dict[str, float] = {}
        for word in query_words:
            if word in self.word_index:
                for doc_id in self.word_index[word]:
                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = 0
                    doc_scores[doc_id] += 1

        sorted_docs = sorted(
            doc_scores.items(), key=lambda x: x[1], reverse=True
        )

        results = []
        for doc_id, score in sorted_docs[:top_k]:
            doc = self.documents[doc_id]
            normalized_score = score / len(query_words)
            results.append((doc, min(normalized_score, 1.0)))

        return results

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get document by ID."""
        return self.documents.get(doc_id)

    def list_documents(self) -> List[Document]:
        """List all documents."""
        return list(self.documents.values())

    @staticmethod
    def _extract_words(text: str) -> List[str]:
        """Extract and normalize words from text."""
        words = re.findall(r"\b\w+\b", text.lower())
        stopwords = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "he", "in", "is", "it", "its", "of", "on", "or", "that",
            "the", "to", "was", "will", "with", "this", "but", "have",
        }
        return [w for w in words if len(w) > 2 and w not in stopwords]


class RAGSystem:
    """Retrieval-Augmented Generation system."""

    def __init__(self, index_dir: Optional[Path] = None):
        """Initialize RAG system."""
        if index_dir is None:
            home = Path.home()
            index_dir = home / ".lmapp" / "rag"

        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.chunker = DocumentChunker()
        self.index = DocumentIndex()
        self._load_index()

    def add_file(self, file_path: Path, title: Optional[str] = None) -> int:
        """Add file to RAG system. Returns number of chunks added."""
        if not file_path.exists():
            return 0

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            title = title or file_path.name

            chunks = self.chunker.chunk_text(content, title, str(file_path))
            for chunk in chunks:
                self.index.add_document(chunk)

            self._save_index()
            return len(chunks)
        except Exception:
            return 0

    def add_directory(self, dir_path: Path, pattern: str = "*.txt") -> int:
        """Add all files matching pattern in directory."""
        total = 0
        for file_path in dir_path.rglob(pattern):
            total += self.add_file(file_path)
        return total

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search indexed documents."""
        results = self.index.search(query, top_k)
        return [
            {
                "document": doc.to_dict(),
                "relevance": score,
                "preview": (doc.content[:100] + "..."
                            if len(doc.content) > 100
                            else doc.content),
            }
            for doc, score in results
        ]

    def get_context(self, query: str, max_length: int = 2000) -> str:
        """Get context for LLM prompt injection."""
        results = self.index.search(query, top_k=5)

        context_parts = []
        total_length = 0

        for doc, score in results:
            if total_length >= max_length:
                break

            part = f"[From {doc.title}]\n{doc.content}\n"
            if total_length + len(part) <= max_length:
                context_parts.append(part)
                total_length += len(part)

        if not context_parts:
            return ""

        return "Context from local files:\n\n" + "\n".join(context_parts)

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all indexed documents."""
        docs = self.index.list_documents()

        by_source: Dict[str, List[Document]] = {}
        for doc in docs:
            if doc.source_path not in by_source:
                by_source[doc.source_path] = []
            by_source[doc.source_path].append(doc)

        result = []
        for source, docs_list in by_source.items():
            result.append({
                "source": source,
                "chunks": len(docs_list),
                "total_chars": sum(len(d.content) for d in docs_list),
            })

        return sorted(result, key=lambda x: x["source"])

    def clear_index(self) -> None:
        """Clear all indexed documents."""
        self.index = DocumentIndex()
        self._save_index()

    def _save_index(self) -> None:
        """Save index to disk."""
        index_file = self.index_dir / "index.json"
        data = {
            "documents": {
                doc_id: doc.to_dict()
                for doc_id, doc in self.index.documents.items()
            }
        }
        index_file.write_text(json.dumps(data, indent=2))

    def _load_index(self) -> None:
        """Load index from disk."""
        index_file = self.index_dir / "index.json"
        if not index_file.exists():
            return

        try:
            data = json.loads(index_file.read_text())
            for doc_dict in data.get("documents", {}).values():
                doc = Document(
                    id=doc_dict["id"],
                    title=doc_dict["title"],
                    content=doc_dict["content"],
                    source_path=doc_dict["source_path"],
                    chunk_index=doc_dict.get("chunk_index", 0),
                    metadata=doc_dict.get("metadata"),
                )
                self.index.add_document(doc)
        except (json.JSONDecodeError, KeyError):
            pass


_rag_system: Optional[RAGSystem] = None


def get_rag_system(index_dir: Optional[Path] = None) -> RAGSystem:
    """Get or create the global RAGSystem instance."""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem(index_dir)
    return _rag_system
