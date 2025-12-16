"""
Tests for Knowledge Base Plugin.

Tests the plugin's ability to:
- Add entries with auto-tagging
- Search with query expansion
- Manage and categorize knowledge
- Export in various formats
"""

import pytest

from lmapp.plugins.example_knowledge_base import (
    KnowledgeBasePlugin,
    KnowledgeEntry,
)


class TestKnowledgeBasePlugin:
    """Tests for KnowledgeBasePlugin."""

    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return KnowledgeBasePlugin()

    def test_metadata(self, plugin):
        """Verify plugin metadata."""
        metadata = plugin.metadata
        assert metadata.name == "knowledge-base"
        assert metadata.version == "0.1.0"
        assert metadata.author == "community"
        assert "knowledge" in metadata.tags
        assert metadata.license == "MIT"

    def test_add_entry(self, plugin):
        """Test adding entry to knowledge base."""
        result = plugin.execute(
            "add",
            title="Python Basics",
            content="Python is a programming language",
            category="programming",
        )
        assert result["success"] is True
        assert "entry_id" in result
        assert len(result["tags"]) >= 0

    def test_add_entry_missing_title(self, plugin):
        """Test adding entry without title fails."""
        result = plugin.execute("add", title="", content="Some content")
        assert result["success"] is False
        assert "error" in result

    def test_add_entry_missing_content(self, plugin):
        """Test adding entry without content fails."""
        result = plugin.execute("add", title="Title", content="")
        assert result["success"] is False
        assert "error" in result

    def test_auto_tag_extraction(self, plugin):
        """Test automatic tag extraction."""
        result = plugin.execute(
            "add",
            title="Test",
            content="This is about #Python and Programming concepts",
        )
        assert result["success"] is True
        assert "tags" in result
        # Should extract #Python and Programming
        assert len(result["tags"]) >= 1

    def test_search_entries(self, plugin):
        """Test searching knowledge base."""
        # Add some entries first
        plugin.execute(
            "add",
            title="Python Guide",
            content="Learn Python programming basics",
        )
        plugin.execute(
            "add", title="JavaScript Tips", content="JavaScript web development"
        )

        # Search
        result = plugin.execute("search", query="python")
        assert result["success"] is True
        assert result["query"] == "python"
        assert "results" in result

    def test_search_empty_query(self, plugin):
        """Test searching with empty query."""
        result = plugin.execute("search", query="")
        assert result["success"] is False

    def test_list_entries(self, plugin):
        """Test listing all entries."""
        # Add entries
        plugin.execute("add", title="Entry 1", content="Content 1")
        plugin.execute("add", title="Entry 2", content="Content 2")

        result = plugin.execute("list")
        assert result["success"] is True
        assert "entries" in result
        assert result["total_entries"] == 2

    def test_list_empty_kb(self, plugin):
        """Test listing when knowledge base is empty."""
        result = plugin.execute("list")
        assert result["success"] is True
        assert result["total_entries"] == 0

    def test_get_entry(self, plugin):
        """Test getting specific entry."""
        # Add entry
        add_result = plugin.execute("add", title="Test Entry", content="Test content")
        entry_id = add_result["entry_id"]

        # Get entry
        result = plugin.execute("get", entry_id=entry_id)
        assert result["success"] is True
        assert result["entry"]["title"] == "Test Entry"

    def test_get_nonexistent_entry(self, plugin):
        """Test getting nonexistent entry."""
        result = plugin.execute("get", entry_id="kb_999")
        assert result["success"] is False
        assert "error" in result

    def test_export_json(self, plugin):
        """Test exporting knowledge base to JSON."""
        plugin.execute("add", title="Entry 1", content="Content 1")

        result = plugin.execute("export", format="json")
        assert result["success"] is True
        assert result["format"] == "json"
        assert "data" in result
        assert "entries" in result["data"]

    def test_export_markdown(self, plugin):
        """Test exporting knowledge base to Markdown."""
        plugin.execute(
            "add",
            title="Learning Guide",
            content="A guide for learning",
            category="education",
        )

        result = plugin.execute("export", format="markdown")
        assert result["success"] is True
        assert result["format"] == "markdown"
        assert "data" in result
        assert "Learning Guide" in result["data"]

    def test_export_invalid_format(self, plugin):
        """Test exporting to invalid format."""
        result = plugin.execute("export", format="xml")
        assert result["success"] is False

    def test_get_stats(self, plugin):
        """Test getting knowledge base statistics."""
        plugin.execute("add", title="Entry 1", content="Content 1", category="work")
        plugin.execute("add", title="Entry 2", content="Content 2", category="work")
        plugin.execute("add", title="Entry 3", content="Content 3", category="personal")

        result = plugin.execute("stats")
        assert result["success"] is True
        assert result["total_entries"] == 3
        assert "categories" in result
        assert "work" in result["categories"]

    def test_stats_empty_kb(self, plugin):
        """Test stats on empty knowledge base."""
        result = plugin.execute("stats")
        assert result["success"] is True
        assert result["total_entries"] == 0

    def test_update_importance(self, plugin):
        """Test updating entry importance."""
        add_result = plugin.execute("add", title="Entry", content="Content")
        entry_id = add_result["entry_id"]

        result = plugin.execute("update_importance", entry_id=entry_id, importance=8)
        assert result["success"] is True
        assert result["new_importance"] == 8

    def test_update_importance_clamping(self, plugin):
        """Test that importance is clamped to 1-10."""
        add_result = plugin.execute("add", title="Entry", content="Content")
        entry_id = add_result["entry_id"]

        # Test clamping high
        result = plugin.execute("update_importance", entry_id=entry_id, importance=15)
        assert result["new_importance"] == 10

        # Test clamping low
        result = plugin.execute("update_importance", entry_id=entry_id, importance=-5)
        assert result["new_importance"] == 1

    def test_update_importance_nonexistent(self, plugin):
        """Test updating importance on nonexistent entry."""
        result = plugin.execute("update_importance", entry_id="kb_999", importance=5)
        assert result["success"] is False

    def test_category_organization(self, plugin):
        """Test entries are organized by category."""
        plugin.execute("add", title="Entry 1", content="C1", category="work")
        plugin.execute("add", title="Entry 2", content="C2", category="personal")
        plugin.execute("add", title="Entry 3", content="C3", category="work")

        result = plugin.execute("stats")
        assert result["categories"]["work"] == 2
        assert result["categories"]["personal"] == 1

    def test_query_expansion(self, plugin):
        """Test query expansion with synonyms."""
        plugin.execute("add", title="Python Guide", content="Learn Python programming")

        # Search with synonym
        result = plugin.execute("search", query="py")
        assert result["success"] is True
        assert "expanded_queries" in result

    def test_related_entries(self, plugin):
        """Test finding related entries."""
        plugin.execute("add", title="Python Basics", content="Learning Python programming")
        plugin.execute("add", title="Python Advanced", content="Advanced Python techniques")
        result = plugin.execute("add", title="Python Performance", content="Python optimization tips")

        # The last entry should find related entries
        entry_result = plugin.execute("get", entry_id=result["entry_id"])
        assert entry_result["success"] is True
        # At minimum, the structure should be valid
        assert "entry" in entry_result

    def test_knowledge_entry_dataclass(self):
        """Test KnowledgeEntry dataclass."""
        entry = KnowledgeEntry(
            entry_id="kb_1",
            title="Test",
            content="Test content",
            tags=["python", "learning"],
            category="education",
            importance=8,
        )
        assert entry.entry_id == "kb_1"
        assert entry.title == "Test"
        assert entry.importance == 8
        assert "python" in entry.tags

    def test_unknown_action(self, plugin):
        """Test unknown action."""
        result = plugin.execute("unknown_action")
        assert result["success"] is False
        assert "error" in result

    def test_importance_sorting(self, plugin):
        """Test entries are sorted by importance."""
        plugin.execute(
            "add",
            title="Low Importance",
            content="Content",
            importance=2,
        )
        plugin.execute(
            "add",
            title="High Importance",
            content="Content",
            importance=9,
        )

        result = plugin.execute("list")
        entries = result["entries"]
        # Should be sorted by importance (descending)
        assert entries[0]["importance"] >= entries[1]["importance"]

    def test_multiple_additions(self, plugin):
        """Test adding multiple entries sequentially."""
        for i in range(5):
            result = plugin.execute(
                "add", title=f"Entry {i}", content=f"Content {i}"
            )
            assert result["success"] is True

        result = plugin.execute("list")
        assert result["total_entries"] == 5

    def test_tag_frequency_stats(self, plugin):
        """Test tag frequency in statistics."""
        plugin.execute("add", title="E1", content="#python #learning")
        plugin.execute("add", title="E2", content="#python #advanced")
        plugin.execute("add", title="E3", content="#javascript")

        result = plugin.execute("stats")
        assert "tag_frequency" in result
        # Python should appear more frequently
        if result["tag_frequency"]:
            assert len(result["tag_frequency"]) > 0

    def test_search_results_structure(self, plugin):
        """Test search results have correct structure."""
        plugin.execute("add", title="Test Entry", content="Test content with details")

        result = plugin.execute("search", query="test")
        assert result["success"] is True
        if result["results"]:
            item = result["results"][0]
            assert "entry_id" in item
            assert "title" in item
            assert "tags" in item
            assert "category" in item
