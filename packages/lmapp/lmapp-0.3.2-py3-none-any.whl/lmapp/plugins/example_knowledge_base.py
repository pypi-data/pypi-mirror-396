"""
Knowledge Base Builder Plugin - Personal knowledge management system.

Converts conversations into searchable knowledge graphs with auto-tagging,
categorization, query expansion, and export capabilities.

Author: LMAPP Community
License: MIT
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from lmapp.plugins.plugin_manager import BasePlugin, PluginMetadata


@dataclass
class KnowledgeEntry:
    """A single knowledge base entry with metadata."""

    entry_id: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    category: str = "uncategorized"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    importance: int = 5  # 1-10 scale
    related_entries: List[str] = field(default_factory=list)


@dataclass
class SearchResult:
    """Result of a knowledge base search."""

    query: str
    results: List[KnowledgeEntry] = field(default_factory=list)
    expanded_queries: List[str] = field(default_factory=list)
    total_results: int = 0


@dataclass
class KnowledgeBaseStats:
    """Statistics about the knowledge base."""

    total_entries: int = 0
    total_tags: int = 0
    categories: Dict[str, int] = field(default_factory=dict)
    average_importance: float = 0.0
    tag_frequency: Dict[str, int] = field(default_factory=dict)


class KnowledgeBasePlugin(BasePlugin):
    """Personal knowledge management with auto-tagging and search."""

    def __init__(self):
        """Initialize the knowledge base."""
        super().__init__()
        self.kb: Dict[str, KnowledgeEntry] = {}
        self.synonyms: Dict[str, List[str]] = self._load_default_synonyms()

    @property
    def metadata(self) -> PluginMetadata:
        """Plugin metadata."""
        return PluginMetadata(
            name="knowledge-base",
            version="0.1.0",
            author="community",
            description="Build and search personal knowledge graphs with auto-tagging",
            license="MIT",
            dependencies=[],
            tags=["knowledge", "search", "learning"],
        )

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize plugin with optional configuration."""
        if config and "kb_data" in config:
            # Load existing knowledge base
            self.kb = config["kb_data"]

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute knowledge base action.

        Actions:
            - "add": Add entry to knowledge base
            - "search": Search knowledge base
            - "get": Get specific entry by ID
            - "list": List all entries
            - "export": Export to JSON/markdown
            - "stats": Get knowledge base statistics
            - "update_importance": Update entry importance
        """
        if action == "add":
            return self._add_entry(
                kwargs.get("title", ""),
                kwargs.get("content", ""),
                kwargs.get("category", "uncategorized"),
                kwargs.get("importance", 5),
            )
        elif action == "search":
            return self._search(kwargs.get("query", ""))
        elif action == "get":
            return self._get_entry(kwargs.get("entry_id", ""))
        elif action == "list":
            return self._list_entries()
        elif action == "export":
            return self._export(kwargs.get("format", "json"))
        elif action == "stats":
            return self._get_stats()
        elif action == "update_importance":
            return self._update_importance(
                kwargs.get("entry_id", ""), kwargs.get("importance", 5)
            )
        return {"success": False, "error": f"Unknown action: {action}"}

    def _add_entry(
        self, title: str, content: str, category: str = "uncategorized", importance: int = 5
    ) -> Dict[str, Any]:
        """Add entry to knowledge base."""
        if not title or not content:
            return {"success": False, "error": "Title and content required"}

        entry_id = f"kb_{len(self.kb) + 1}"

        # Auto-extract tags
        tags = self._extract_tags(content)

        # Find related entries
        related = self._find_related_entries(content)

        entry = KnowledgeEntry(
            entry_id=entry_id,
            title=title,
            content=content,
            tags=tags,
            category=category,
            importance=importance,
            related_entries=related,
        )

        self.kb[entry_id] = entry

        return {
            "success": True,
            "entry_id": entry_id,
            "tags": tags,
            "related_count": len(related),
        }

    def _search(self, query: str) -> Dict[str, Any]:
        """Search knowledge base with query expansion."""
        if not query:
            return {"success": False, "error": "Query required"}

        # Expand query with synonyms
        expanded_queries = self._expand_query(query)

        # Search with expanded queries
        results: List[KnowledgeEntry] = []
        seen_ids: Set[str] = set()

        for search_term in [query] + expanded_queries:
            for entry_id, entry in self.kb.items():
                if entry_id in seen_ids:
                    continue

                # Search in title, content, and tags
                if (
                    search_term.lower() in entry.title.lower()
                    or search_term.lower() in entry.content.lower()
                    or any(search_term.lower() in tag.lower() for tag in entry.tags)
                ):
                    results.append(entry)
                    seen_ids.add(entry_id)

        # Sort by importance and relevance
        results.sort(key=lambda e: (-e.importance, -len(e.related_entries)))

        return {
            "success": True,
            "query": query,
            "expanded_queries": expanded_queries,
            "results": [
                {
                    "entry_id": r.entry_id,
                    "title": r.title,
                    "content": r.content[:100] + "...",
                    "tags": r.tags,
                    "category": r.category,
                    "importance": r.importance,
                }
                for r in results
            ],
            "total_results": len(results),
        }

    def _get_entry(self, entry_id: str) -> Dict[str, Any]:
        """Get specific entry by ID."""
        if entry_id not in self.kb:
            return {"success": False, "error": f"Entry {entry_id} not found"}

        entry = self.kb[entry_id]
        return {
            "success": True,
            "entry": {
                "entry_id": entry.entry_id,
                "title": entry.title,
                "content": entry.content,
                "tags": entry.tags,
                "category": entry.category,
                "created_at": entry.created_at,
                "importance": entry.importance,
                "related_entries": entry.related_entries,
            },
        }

    def _list_entries(self) -> Dict[str, Any]:
        """List all knowledge base entries."""
        entries = sorted(self.kb.values(), key=lambda e: -e.importance)

        return {
            "success": True,
            "entries": [
                {
                    "entry_id": e.entry_id,
                    "title": e.title,
                    "category": e.category,
                    "importance": e.importance,
                    "tags": e.tags,
                    "created_at": e.created_at,
                }
                for e in entries
            ],
            "total_entries": len(entries),
        }

    def _export(self, format: str) -> Dict[str, Any]:
        """Export knowledge base."""
        entries = list(self.kb.values())

        if format == "json":
            data = {
                "entries": [
                    {
                        "entry_id": e.entry_id,
                        "title": e.title,
                        "content": e.content,
                        "tags": e.tags,
                        "category": e.category,
                        "created_at": e.created_at,
                        "importance": e.importance,
                        "related_entries": e.related_entries,
                    }
                    for e in entries
                ],
                "exported_at": datetime.now().isoformat(),
            }
            return {"success": True, "format": "json", "data": data}

        elif format == "markdown":
            markdown = "# Knowledge Base Export\n\n"
            for category in set(e.category for e in entries):
                markdown += f"\n## {category.title()}\n\n"
                for entry in [e for e in entries if e.category == category]:
                    markdown += f"### {entry.title}\n"
                    markdown += f"**Importance:** {entry.importance}/10\n"
                    markdown += f"**Tags:** {', '.join(entry.tags)}\n"
                    markdown += f"{entry.content}\n\n"

            return {"success": True, "format": "markdown", "data": markdown}

        return {"success": False, "error": f"Unknown format: {format}"}

    def _get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        if not self.kb:
            return {
                "success": True,
                "total_entries": 0,
                "categories": {},
                "tags": {},
            }

        categories: Dict[str, int] = {}
        tags: Dict[str, int] = {}
        total_importance = 0

        for entry in self.kb.values():
            categories[entry.category] = categories.get(entry.category, 0) + 1
            total_importance += entry.importance

            for tag in entry.tags:
                tags[tag] = tags.get(tag, 0) + 1

        avg_importance = total_importance / len(self.kb) if self.kb else 0

        return {
            "success": True,
            "total_entries": len(self.kb),
            "total_tags": len(tags),
            "categories": categories,
            "average_importance": round(avg_importance, 2),
            "tag_frequency": dict(sorted(tags.items(), key=lambda x: -x[1])[:10]),
        }

    def _update_importance(self, entry_id: str, importance: int) -> Dict[str, Any]:
        """Update entry importance."""
        if entry_id not in self.kb:
            return {"success": False, "error": f"Entry {entry_id} not found"}

        importance = max(1, min(10, importance))  # Clamp to 1-10
        self.kb[entry_id].importance = importance

        return {"success": True, "entry_id": entry_id, "new_importance": importance}

    def _extract_tags(self, content: str) -> List[str]:
        """Auto-extract tags from content."""
        # Extract hashtags
        hashtags = re.findall(r"#(\w+)", content)

        # Extract common concepts (capitalized words)
        words = content.split()
        concepts = [w.lower() for w in words if w[0].isupper() and len(w) > 3]

        # Combine and deduplicate
        tags = list(set(hashtags + concepts))[:5]  # Limit to 5 tags

        return tags

    def _find_related_entries(self, content: str) -> List[str]:
        """Find related entries based on content."""
        related = []
        keywords = set(content.lower().split())

        for entry_id, entry in self.kb.items():
            entry_keywords = set(entry.content.lower().split())
            overlap = len(keywords & entry_keywords)

            if overlap > 3:  # Threshold for relation
                related.append(entry_id)

        return related[:3]  # Return top 3 related

    def _expand_query(self, query: str) -> List[str]:
        """Expand query with synonyms."""
        expanded = []

        words = query.lower().split()
        for word in words:
            if word in self.synonyms:
                expanded.extend(self.synonyms[word])

        return expanded

    @staticmethod
    def _load_default_synonyms() -> Dict[str, List[str]]:
        """Load default synonym mappings."""
        return {
            "python": ["py", "programming"],
            "javascript": ["js", "web"],
            "database": ["db", "sql"],
            "algorithm": ["algo", "logic"],
            "optimization": ["optimize", "performance"],
            "refactor": ["refactoring", "improve"],
            "bug": ["issue", "error", "problem"],
            "feature": ["functionality", "enhancement"],
            "test": ["testing", "validation"],
            "security": ["auth", "encryption"],
        }
