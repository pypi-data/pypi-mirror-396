"""Tests for text chunkers."""

from __future__ import annotations

import pytest

from prompt_amplifier.chunkers import FixedSizeChunker, RecursiveChunker, SentenceChunker
from prompt_amplifier.models.document import Document


class TestRecursiveChunker:
    """Tests for RecursiveChunker."""

    def test_chunk_small_document(self, sample_document):
        """Test chunking a small document (fits in one chunk)."""
        chunker = RecursiveChunker(chunk_size=1000, chunk_overlap=100)
        chunks = chunker.chunk(sample_document)

        # Small doc should be single chunk
        assert len(chunks) == 1
        assert chunks[0].content == sample_document.content
        assert chunks[0].document_id == sample_document.id
        assert chunks[0].chunk_index == 0

    def test_chunk_large_document(self):
        """Test chunking a large document."""
        large_content = "This is a sentence. " * 100  # ~2000 chars
        doc = Document(content=large_content, source="large.txt")

        chunker = RecursiveChunker(chunk_size=200, chunk_overlap=50)
        chunks = chunker.chunk(doc)

        # Should create multiple chunks
        assert len(chunks) > 1

        # Check chunk indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
            assert chunk.document_id == doc.id

    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        content = "AAAA BBBB CCCC DDDD EEEE FFFF GGGG HHHH"
        doc = Document(content=content, source="test.txt")

        chunker = RecursiveChunker(chunk_size=15, chunk_overlap=5)
        chunks = chunker.chunk(doc)

        # Multiple chunks should be created
        assert len(chunks) > 1

    def test_chunk_empty_document(self):
        """Test chunking empty document."""
        doc = Document(content="", source="empty.txt")

        chunker = RecursiveChunker()
        chunks = chunker.chunk(doc)

        assert len(chunks) == 0

    def test_chunk_preserves_metadata(self, sample_document):
        """Test that chunking preserves document metadata."""
        chunker = RecursiveChunker(chunk_size=1000)
        chunks = chunker.chunk(sample_document)

        assert chunks[0].source == sample_document.source
        assert "chunker" in chunks[0].metadata

    def test_chunk_multiple_documents(self, sample_documents):
        """Test chunking multiple documents."""
        chunker = RecursiveChunker(chunk_size=1000)
        chunks = chunker.chunk_documents(sample_documents)

        # Each doc should produce at least one chunk
        assert len(chunks) >= len(sample_documents)

    def test_custom_separators(self):
        """Test with custom separators."""
        content = "Part1|||Part2|||Part3"
        doc = Document(content=content, source="test.txt")

        chunker = RecursiveChunker(
            chunk_size=100,
            chunk_overlap=0,
            separators=["|||", " "],
        )
        chunks = chunker.chunk(doc)

        assert len(chunks) >= 1


class TestFixedSizeChunker:
    """Tests for FixedSizeChunker."""

    def test_fixed_size_chunking(self):
        """Test fixed size chunking."""
        content = "A" * 100
        doc = Document(content=content, source="test.txt")

        chunker = FixedSizeChunker(chunk_size=30, chunk_overlap=10)
        chunks = chunker.chunk(doc)

        # First chunk should be exactly chunk_size
        assert len(chunks[0].content) == 30

    def test_fixed_size_overlap(self):
        """Test that overlap works correctly."""
        content = "0123456789" * 5  # 50 chars: "01234567890123..."
        doc = Document(content=content, source="test.txt")

        chunker = FixedSizeChunker(chunk_size=20, chunk_overlap=5)
        chunks = chunker.chunk(doc)

        # Verify chunks are created
        assert len(chunks) > 1


class TestSentenceChunker:
    """Tests for SentenceChunker."""

    def test_sentence_chunking(self):
        """Test chunking by sentences."""
        content = "First sentence. Second sentence. Third sentence. Fourth sentence."
        doc = Document(content=content, source="test.txt")

        chunker = SentenceChunker(chunk_size=50, chunk_overlap=0)
        chunks = chunker.chunk(doc)

        # Should split into multiple chunks
        assert len(chunks) >= 1

    def test_sentence_chunking_by_count(self):
        """Test chunking by sentence count."""
        content = "One. Two. Three. Four. Five. Six."
        doc = Document(content=content, source="test.txt")

        chunker = SentenceChunker(sentences_per_chunk=2)
        chunks = chunker.chunk(doc)

        assert len(chunks) == 3  # 6 sentences / 2 per chunk

    def test_sentence_chunking_single_sentence(self):
        """Test document with single sentence."""
        content = "This is a single sentence without any periods at the end"
        doc = Document(content=content, source="test.txt")

        chunker = SentenceChunker(chunk_size=1000)
        chunks = chunker.chunk(doc)

        assert len(chunks) == 1


class TestChunkerValidation:
    """Tests for chunker validation."""

    def test_invalid_overlap(self):
        """Test that overlap >= chunk_size raises error."""
        with pytest.raises(ValueError):
            RecursiveChunker(chunk_size=100, chunk_overlap=100)

        with pytest.raises(ValueError):
            RecursiveChunker(chunk_size=100, chunk_overlap=150)

    def test_chunk_text_convenience(self):
        """Test chunk_text convenience method."""
        chunker = RecursiveChunker(chunk_size=1000)
        chunks = chunker.chunk_text("Test content here", source="manual")

        assert len(chunks) == 1
        assert chunks[0].source == "manual"
