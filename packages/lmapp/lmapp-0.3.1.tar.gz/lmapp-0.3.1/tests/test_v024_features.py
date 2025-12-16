"""
Tests for LMAPP v0.2.4 advanced features.

Tests for RAG system, plugin system, and batch processing.
"""

import pytest
import json
import tempfile
from pathlib import Path

# RAG System tests
from lmapp.rag.rag_system import Document, SearchResult, SimpleVectorizer, DocumentIndex, RAGSystem


class TestDocument:
    """Test Document class."""
    
    def test_document_creation(self):
        """Test basic document creation."""
        doc = Document("doc1", "Test", "Test content")
        assert doc.doc_id == "doc1"
        assert doc.title == "Test"
        assert doc.content == "Test content"
        assert doc.created_at is not None
    
    def test_document_to_dict(self):
        """Test document serialization."""
        doc = Document("doc1", "Test", "Content", file_path="/path/to/file.txt")
        data = doc.to_dict()
        assert data["doc_id"] == "doc1"
        assert data["title"] == "Test"
    
    def test_document_from_dict(self):
        """Test document deserialization."""
        original = Document("doc1", "Test", "Content", metadata={"key": "value"})
        data = original.to_dict()
        restored = Document.from_dict(data)
        assert restored.doc_id == original.doc_id
        assert restored.metadata == original.metadata


class TestSimpleVectorizer:
    """Test SimpleVectorizer class."""
    
    def test_tokenize(self):
        """Test text tokenization."""
        text = "Hello, world! This is a test."
        tokens = SimpleVectorizer.tokenize(text)
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
    
    def test_term_frequency(self):
        """Test term frequency calculation."""
        tokens = ["hello", "world", "hello", "test"]
        freq = SimpleVectorizer.get_term_frequency(tokens)
        assert 0 < freq["hello"] < 1
        assert 0 < freq["world"] < 1
        assert freq["hello"] > freq["world"]
    
    def test_similarity_high(self):
        """Test high similarity case."""
        query = ["hello", "world"]
        doc = ["hello", "world", "test"]
        score = SimpleVectorizer.calculate_similarity(query, doc)
        assert score > 0.5
    
    def test_similarity_low(self):
        """Test low similarity case."""
        query = ["apple", "banana"]
        doc = ["orange", "grape"]
        score = SimpleVectorizer.calculate_similarity(query, doc)
        assert score == 0.0
    
    def test_similarity_partial(self):
        """Test partial similarity."""
        query = ["hello", "world"]
        doc = ["hello", "universe"]
        score = SimpleVectorizer.calculate_similarity(query, doc)
        assert 0.0 < score < 0.5


class TestDocumentIndex:
    """Test DocumentIndex class."""
    
    def test_add_document(self):
        """Test adding documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = DocumentIndex(Path(tmpdir))
            doc = Document("doc1", "Test", "Hello world")
            index.add_document(doc)
            
            retrieved = index.get_document("doc1")
            assert retrieved is not None
            assert retrieved.title == "Test"
    
    def test_search_documents(self):
        """Test searching documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = DocumentIndex(Path(tmpdir))
            index.add_document(Document("doc1", "Python", "Python is great for programming"))
            index.add_document(Document("doc2", "Java", "Java is used in enterprise apps"))
            
            results = index.search("Python programming", top_k=1)
            assert len(results) == 1
            assert results[0].document.doc_id == "doc1"
    
    def test_remove_document(self):
        """Test removing documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = DocumentIndex(Path(tmpdir))
            doc = Document("doc1", "Test", "Content")
            index.add_document(doc)
            
            success = index.remove_document("doc1")
            assert success
            assert index.get_document("doc1") is None
    
    def test_persistence(self):
        """Test index persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create and save
            index1 = DocumentIndex(tmppath)
            index1.add_document(Document("doc1", "Test", "Content"))
            
            # Load
            index2 = DocumentIndex(tmppath)
            doc = index2.get_document("doc1")
            assert doc is not None
            assert doc.title == "Test"


class TestRAGSystem:
    """Test RAGSystem class."""
    
    def test_index_file(self):
        """Test indexing a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test file
            test_file = tmppath / "test.txt"
            test_file.write_text("Python is a great programming language")
            
            rag = RAGSystem(tmppath / "index")
            doc_id = rag.index_file(test_file)
            
            assert doc_id is not None
            assert rag.index.get_document(doc_id) is not None
    
    def test_index_directory(self):
        """Test indexing a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test files
            (tmppath / "file1.txt").write_text("Python content")
            (tmppath / "file2.py").write_text("def hello():\n    pass")
            
            rag = RAGSystem(tmppath / "index")
            count = rag.index_directory(tmppath)
            
            assert count >= 2
    
    def test_search(self):
        """Test searching indexed documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            rag = RAGSystem(tmppath / "index")
            rag.index.add_document(Document("doc1", "Python", "Python programming language"))
            
            results = rag.search("Python", top_k=5)
            assert len(results) > 0
            assert results[0].document.doc_id == "doc1"
    
    def test_get_context_for_prompt(self):
        """Test getting context for prompt injection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            rag = RAGSystem(tmppath / "index")
            rag.index.add_document(Document("doc1", "Python", "Python is a programming language"))
            
            context = rag.get_context_for_prompt("Python")
            assert len(context) > 0
            assert "Python" in context


# Plugin System tests
from lmapp.plugins.plugin_manager import (
    PluginMetadata, BasePlugin, PluginInfo, PluginManager
)


class TestPluginMetadata:
    """Test PluginMetadata class."""
    
    def test_metadata_creation(self):
        """Test creating plugin metadata."""
        meta = PluginMetadata(
            name="test",
            version="1.0.0",
            description="Test",
            author="Author"
        )
        assert meta.name == "test"
        assert meta.version == "1.0.0"
    
    def test_metadata_to_dict(self):
        """Test metadata serialization."""
        meta = PluginMetadata(
            name="test",
            version="1.0.0",
            description="Test",
            author="Author",
            tags=["test", "demo"]
        )
        data = meta.to_dict()
        assert data["name"] == "test"
        assert "test" in data["tags"]
    
    def test_metadata_from_dict(self):
        """Test metadata deserialization."""
        original = PluginMetadata(
            name="test",
            version="1.0.0",
            description="Test",
            author="Author"
        )
        data = original.to_dict()
        restored = PluginMetadata.from_dict(data)
        assert restored.name == original.name


class TestPluginManager:
    """Test PluginManager class."""
    
    def test_discover_plugins(self):
        """Test plugin discovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create plugin directory
            plugin_dir = tmppath / "test_plugin"
            plugin_dir.mkdir()
            (plugin_dir / "plugin.json").write_text(json.dumps({
                "name": "test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Author"
            }))
            
            manager = PluginManager(tmppath)
            plugins = manager.discover_plugins()
            assert len(plugins) >= 0
    
    def test_list_plugins(self):
        """Test listing loaded plugins."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = PluginManager(Path(tmpdir))
            plugins_list = manager.list_plugins()
            assert isinstance(plugins_list, list)
    
    def test_get_plugin_stats(self):
        """Test getting plugin statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = PluginManager(Path(tmpdir))
            stats = manager.get_plugin_stats()
            assert "total_plugins" in stats


# Batch Processing tests
from lmapp.batch.batch_processor import (
    BatchInput, BatchResult, BatchJob, BatchProcessor, OutputFormat
)


class TestBatchInput:
    """Test BatchInput class."""
    
    def test_input_creation(self):
        """Test creating batch input."""
        input_item = BatchInput("input1", "Test content")
        assert input_item.input_id == "input1"
        assert input_item.content == "Test content"
    
    def test_input_to_dict(self):
        """Test input serialization."""
        input_item = BatchInput("input1", "Content", metadata={"key": "value"})
        data = input_item.to_dict()
        assert data["input_id"] == "input1"
        assert data["metadata"]["key"] == "value"


class TestBatchResult:
    """Test BatchResult class."""
    
    def test_result_creation(self):
        """Test creating batch result."""
        result = BatchResult("input1", "output")
        assert result.input_id == "input1"
        assert result.output == "output"
        assert result.status == "success"
    
    def test_result_error(self):
        """Test result with error."""
        result = BatchResult("input1", None, status="error", error="Error message")
        assert result.status == "error"
        assert result.error == "Error message"


class TestBatchJob:
    """Test BatchJob class."""
    
    def test_job_creation(self):
        """Test creating batch job."""
        inputs = [BatchInput("input1", "content1")]
        job = BatchJob("job1", inputs)
        assert job.job_id == "job1"
        assert len(job.inputs) == 1


class TestBatchProcessor:
    """Test BatchProcessor class."""
    
    def test_create_batch_job(self):
        """Test creating a batch job."""
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = BatchProcessor(Path(tmpdir))
            inputs = [BatchInput("input1", "content1")]
            job = processor.create_batch_job("job1", inputs)
            
            assert job.job_id == "job1"
            assert len(job.inputs) == 1
    
    def test_process_batch(self):
        """Test processing a batch."""
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = BatchProcessor(Path(tmpdir))
            inputs = [
                BatchInput("input1", "test1"),
                BatchInput("input2", "test2"),
            ]
            job = processor.create_batch_job("job1", inputs)
            
            def processor_fn(content):
                return f"processed: {content}", None
            
            result_job = processor.process_batch("job1", processor_fn)
            assert result_job.status.value == "completed"
            assert result_job.total_processed == 2
    
    def test_load_inputs_from_file_json(self):
        """Test loading inputs from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create JSON file
            input_file = tmppath / "inputs.json"
            input_file.write_text(json.dumps([
                {"content": "Test 1"},
                {"content": "Test 2"},
            ]))
            
            processor = BatchProcessor(tmppath / "batch")
            inputs = processor.load_inputs_from_file(input_file)
            
            assert len(inputs) == 2
            # IDs are auto-generated if not provided
            assert inputs[0].input_id.startswith("input_")
    
    def test_save_results_json(self):
        """Test saving results as JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            processor = BatchProcessor(tmppath / "batch")
            inputs = [BatchInput("input1", "content")]
            job = processor.create_batch_job("job1", inputs)
            job.results.append(BatchResult("input1", "output"))
            
            output_file = tmppath / "results.json"
            success = processor.save_results("job1", output_file, OutputFormat.JSON)
            
            assert success
            assert output_file.exists()
    
    def test_get_job_stats(self):
        """Test getting job statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = BatchProcessor(Path(tmpdir))
            inputs = [BatchInput("input1", "content")]
            job = processor.create_batch_job("job1", inputs)
            
            stats = processor.get_job_stats("job1")
            assert stats is not None
            assert stats["total_inputs"] == 1


# Integration tests
class TestV024Integration:
    """Integration tests for v0.2.4 features."""
    
    def test_rag_with_batch_processing(self):
        """Test RAG system with batch processing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Index documents
            rag = RAGSystem(tmppath / "index")
            rag.index.add_document(Document("doc1", "Python", "Python programming"))
            rag.index.add_document(Document("doc2", "Java", "Java programming"))
            
            # Process batch
            processor = BatchProcessor(tmppath / "batch")
            inputs = [
                BatchInput("q1", "How to use Python?"),
                BatchInput("q2", "How to use Java?"),
            ]
            job = processor.create_batch_job("job1", inputs)
            
            def processor_fn(query):
                results = rag.search(query, top_k=1)
                if results:
                    return results[0].document.title, None
                return None, "No results"
            
            result_job = processor.process_batch("job1", processor_fn)
            assert result_job.total_processed > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
