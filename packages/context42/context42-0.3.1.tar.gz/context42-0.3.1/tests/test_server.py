"""
Test suite for Context42 MCP RAG Server
"""

import pytest
import tempfile
from pathlib import Path
from context42.processor import DocumentProcessor
from context42.chunker import Chunker
from context42.search import SearchEngine


class TestDocumentProcessor:
    """Test DocumentProcessor functionality"""

    def test_load_documents_basic(self):
        """Test basic document loading"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_dir = Path(temp_dir)
            (test_dir / "test1.md").write_text("# Test document 1")
            (test_dir / "test2.txt").write_text("Test document 2")

            processor = DocumentProcessor()
            docs = processor.load(str(test_dir), [".md", ".txt"], 10)

            assert len(docs) == 2
            assert docs[0]["filename"] == "test1.md"
            assert docs[1]["filename"] == "test2.txt"
            assert docs[0]["extension"] == ".md"
            assert docs[1]["extension"] == ".txt"

    def test_load_nonexistent_directory(self):
        """Test loading from non-existent directory"""
        processor = DocumentProcessor()
        with pytest.raises(FileNotFoundError):
            processor.load("/nonexistent/path", [".md"], 10)

    def test_load_with_max_files(self):
        """Test loading with file limit"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)
            # Create 5 files
            for i in range(5):
                (test_dir / f"test{i}.md").write_text(f"Content {i}")

            processor = DocumentProcessor()
            docs = processor.load(str(test_dir), [".md"], 3)

            assert len(docs) == 3


class TestChunker:
    """Test Chunker functionality"""

    def test_get_chunk_size(self):
        """Test chunk size calculation"""
        chunker = Chunker()

        assert chunker.get_chunk_size(1.0) == 1000
        assert chunker.get_chunk_size(4.0) == 250
        assert chunker.get_chunk_size(16.0) == 100
        assert chunker.get_chunk_size(64.0) == 100  # Min size
        assert chunker.get_chunk_size(128.0) == 100  # Min size

    def test_get_chunk_size_invalid(self):
        """Test invalid compression levels"""
        chunker = Chunker()

        with pytest.raises(ValueError, match="compression_level must be > 0"):
            chunker.get_chunk_size(0)

        with pytest.raises(ValueError, match="compression_level must be > 0"):
            chunker.get_chunk_size(-1)

    def test_chunk_documents(self):
        """Test document chunking"""
        documents = [
            {
                "filename": "test.md",
                "content": "This is a test document for chunking.",
                "extension": ".md",
            }
        ]

        chunker = Chunker()
        chunks = chunker.chunk(documents, 4.0)  # 250 char chunks

        assert len(chunks) > 0
        assert all(chunk["filename"] == "test.md" for chunk in chunks)
        assert all("chunk_id" in chunk for chunk in chunks)
        assert all("content" in chunk for chunk in chunks)
        assert all("start_pos" in chunk for chunk in chunks)
        assert all("end_pos" in chunk for chunk in chunks)

    def test_chunk_empty_filter(self):
        """Test empty chunk filtering"""
        documents = [{"filename": "test.md", "content": "Short", "extension": ".md"}]

        chunker = Chunker()
        chunks = chunker.chunk(documents, 1.0)  # 1000 char chunks

        # Should filter out empty chunks
        assert all(chunk["content"].strip() for chunk in chunks)


class TestSearchEngine:
    """Test SearchEngine functionality"""

    def test_search_basic(self):
        """Test basic search functionality"""
        chunks = [
            {
                "filename": "test1.md",
                "content": "This document contains machine learning algorithms.",
                "chunk_id": "test1_0",
            },
            {
                "filename": "test2.md",
                "content": "This document discusses data science topics.",
                "chunk_id": "test2_0",
            },
            {
                "filename": "test3.md",
                "content": "No relevant content here.",
                "chunk_id": "test3_0",
            },
        ]

        engine = SearchEngine()
        results = engine.search(chunks, "machine learning", 5)

        assert len(results) == 1
        assert results[0]["filename"] == "test1.md"
        assert results[0]["score"] > 0
        assert "preview" in results[0]

    def test_search_no_results(self):
        """Test search with no results"""
        chunks = [
            {
                "filename": "test.md",
                "content": "No relevant content.",
                "chunk_id": "test_0",
            }
        ]

        engine = SearchEngine()
        results = engine.search(chunks, "nonexistent term", 5)

        assert len(results) == 0

    def test_search_top_k(self):
        """Test top_k limiting"""
        chunks = [
            {
                "filename": f"test{i}.md",
                "content": f"machine learning content {i}",
                "chunk_id": f"test{i}_0",
            }
            for i in range(10)
        ]

        engine = SearchEngine()
        results = engine.search(chunks, "machine", 3)

        assert len(results) == 3
        # Should be sorted by score (highest first)
        assert all(
            results[i]["score"] >= results[i + 1]["score"]
            for i in range(len(results) - 1)
        )


class TestIntegration:
    """Integration tests"""

    def test_full_workflow(self):
        """Test complete workflow: load -> chunk -> search"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)

            # Create test documents
            (test_dir / "doc1.md").write_text(
                "# Machine Learning\nMachine learning is a subset of artificial intelligence."
            )
            (test_dir / "doc2.txt").write_text(
                "Data Science\nData science involves extracting insights from data."
            )
            (test_dir / "doc3.json").write_text(
                '{"topic": "algorithms", "description": "Algorithmic approaches"}'
            )

            # Step 1: Load documents
            processor = DocumentProcessor()
            docs = processor.load(str(test_dir), [".md", ".txt", ".json"], 10)
            assert len(docs) == 3

            # Step 2: Chunk documents
            chunker = Chunker()
            chunks = chunker.chunk(docs, 16.0)  # 100 char chunks
            assert len(chunks) > 0

            # Step 3: Search
            engine = SearchEngine()
            results = engine.search(chunks, "machine", 5)
            assert len(results) > 0

            # Verify results contain expected content
            machine_results = [r for r in results if "machine" in r["content"].lower()]
            assert len(machine_results) > 0


if __name__ == "__main__":
    pytest.main([__file__])
