"""Tests for data models."""

from __future__ import annotations

import pytest

from prompt_amplifier.models.document import Chunk, ChunkBatch, Document
from prompt_amplifier.models.embedding import EmbeddingResult, SparseEmbedding
from prompt_amplifier.models.result import ExpandResult, SearchResult, SearchResults


class TestDocument:
    """Tests for Document model."""

    def test_create_document(self):
        """Test basic document creation."""
        doc = Document(
            content="Test content",
            source="test.txt",
            source_type="txt",
        )

        assert doc.content == "Test content"
        assert doc.source == "test.txt"
        assert doc.source_type == "txt"
        assert doc.id is not None
        assert doc.created_at is not None

    def test_document_content_hash(self):
        """Test content hash generation."""
        doc1 = Document(content="Same content", source="a.txt")
        doc2 = Document(content="Same content", source="b.txt")
        doc3 = Document(content="Different content", source="c.txt")

        # Same content = same hash
        assert doc1.content_hash == doc2.content_hash
        # Different content = different hash
        assert doc1.content_hash != doc3.content_hash

    def test_document_length(self):
        """Test document length."""
        doc = Document(content="12345", source="test.txt")
        assert len(doc) == 5

    def test_document_repr(self):
        """Test document string representation."""
        doc = Document(content="Test content here", source="test.txt")
        repr_str = repr(doc)
        assert "Document" in repr_str
        assert "test.txt" in repr_str


class TestChunk:
    """Tests for Chunk model."""

    def test_create_chunk(self):
        """Test basic chunk creation."""
        chunk = Chunk(
            content="Chunk content",
            document_id="doc-123",
            chunk_index=0,
            source="test.txt",
        )

        assert chunk.content == "Chunk content"
        assert chunk.document_id == "doc-123"
        assert chunk.chunk_index == 0
        assert chunk.id is not None
        assert chunk.char_count == len("Chunk content")

    def test_chunk_embedding(self):
        """Test chunk embedding handling."""
        chunk = Chunk(
            content="Test",
            document_id="doc-123",
            chunk_index=0,
        )

        # No embedding initially
        assert not chunk.has_embedding
        assert chunk.embedding_dim is None

        # Add embedding
        chunk.embedding = [0.1, 0.2, 0.3]
        assert chunk.has_embedding
        assert chunk.embedding_dim == 3

    def test_chunk_length(self):
        """Test chunk length."""
        chunk = Chunk(content="12345", document_id="doc", chunk_index=0)
        assert len(chunk) == 5


class TestChunkBatch:
    """Tests for ChunkBatch model."""

    def test_chunk_batch_contents(self):
        """Test batch content extraction."""
        chunks = [
            Chunk(content="One", document_id="doc", chunk_index=0),
            Chunk(content="Two", document_id="doc", chunk_index=1),
        ]
        batch = ChunkBatch(chunks=chunks)

        assert batch.contents == ["One", "Two"]
        assert len(batch) == 2

    def test_set_embeddings(self):
        """Test setting embeddings on batch."""
        chunks = [
            Chunk(content="One", document_id="doc", chunk_index=0),
            Chunk(content="Two", document_id="doc", chunk_index=1),
        ]
        batch = ChunkBatch(chunks=chunks)

        embeddings = [[0.1, 0.2], [0.3, 0.4]]
        batch.set_embeddings(embeddings)

        assert chunks[0].embedding == [0.1, 0.2]
        assert chunks[1].embedding == [0.3, 0.4]

    def test_set_embeddings_mismatch(self):
        """Test error on embedding count mismatch."""
        chunks = [
            Chunk(content="One", document_id="doc", chunk_index=0),
        ]
        batch = ChunkBatch(chunks=chunks)

        with pytest.raises(ValueError):
            batch.set_embeddings([[0.1], [0.2]])  # Too many embeddings


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_search_result(self):
        """Test search result creation."""
        chunk = Chunk(content="Found content", document_id="doc", chunk_index=0, source="test.txt")
        result = SearchResult(chunk=chunk, score=0.95, rank=1)

        assert result.content == "Found content"
        assert result.source == "test.txt"
        assert result.score == 0.95
        assert result.rank == 1


class TestSearchResults:
    """Tests for SearchResults collection."""

    def test_search_results(self):
        """Test search results collection."""
        chunk1 = Chunk(content="One", document_id="doc", chunk_index=0)
        chunk2 = Chunk(content="Two", document_id="doc", chunk_index=1)

        results = SearchResults(
            results=[
                SearchResult(chunk=chunk1, score=0.9, rank=1),
                SearchResult(chunk=chunk2, score=0.8, rank=2),
            ],
            query="test query",
        )

        assert len(results) == 2
        assert results.top_score == 0.9
        assert results.contents == ["One", "Two"]
        assert results[0].score == 0.9


class TestExpandResult:
    """Tests for ExpandResult model."""

    def test_expand_result(self):
        """Test expand result creation."""
        chunk = Chunk(content="Context", document_id="doc", chunk_index=0, source="a.txt")

        result = ExpandResult(
            prompt="Expanded detailed prompt...",
            original_prompt="short",
            context_chunks=[chunk],
        )

        assert result.prompt == "Expanded detailed prompt..."
        assert result.original_prompt == "short"
        assert result.context_count == 1
        assert result.context_sources == ["a.txt"]

    def test_expansion_ratio(self):
        """Test expansion ratio calculation."""
        result = ExpandResult(
            prompt="A" * 100,  # 100 chars
            original_prompt="A" * 10,  # 10 chars
        )

        assert result.expansion_ratio == 10.0

    def test_to_dict(self):
        """Test serialization to dict."""
        result = ExpandResult(
            prompt="Expanded",
            original_prompt="short",
        )

        data = result.to_dict()
        assert "prompt" in data
        assert "original_prompt" in data
        assert "expansion_ratio" in data


class TestEmbeddingResult:
    """Tests for EmbeddingResult model."""

    def test_embedding_result(self):
        """Test embedding result creation."""
        result = EmbeddingResult(
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            model="test-model",
            dimension=2,
        )

        assert result.count == 2
        assert result.dimension == 2
        assert len(result) == 2
        assert result[0] == [0.1, 0.2]


class TestSparseEmbedding:
    """Tests for SparseEmbedding model."""

    def test_sparse_embedding(self):
        """Test sparse embedding creation."""
        sparse = SparseEmbedding(
            indices=[0, 2, 5],
            values=[0.1, 0.2, 0.3],
            dimension=10,
        )

        assert sparse.nnz == 3
        assert sparse.sparsity == 0.3

    def test_to_dense(self):
        """Test conversion to dense vector."""
        sparse = SparseEmbedding(
            indices=[0, 2],
            values=[1.0, 2.0],
            dimension=4,
        )

        dense = sparse.to_dense()
        assert dense == [1.0, 0.0, 2.0, 0.0]

    def test_from_dense(self):
        """Test creation from dense vector."""
        dense = [1.0, 0.0, 2.0, 0.0]
        sparse = SparseEmbedding.from_dense(dense)

        assert sparse.indices == [0, 2]
        assert sparse.values == [1.0, 2.0]
        assert sparse.dimension == 4
