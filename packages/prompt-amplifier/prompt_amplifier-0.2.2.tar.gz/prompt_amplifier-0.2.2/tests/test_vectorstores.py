"""Tests for vector stores."""

from __future__ import annotations

import pytest

from prompt_amplifier.core.exceptions import DocumentNotFoundError, VectorStoreError
from prompt_amplifier.models.document import Chunk
from prompt_amplifier.vectorstores import MemoryStore


class TestMemoryStore:
    """Tests for MemoryStore."""

    def test_create_store(self):
        """Test creating a memory store."""
        store = MemoryStore(collection_name="test")

        assert store.collection_name == "test"
        assert store.count == 0
        assert not store.is_persistent

    def test_add_chunks(self, memory_store, sample_chunks, fitted_tfidf_embedder):
        """Test adding chunks to store."""
        # Embed chunks first
        fitted_tfidf_embedder.embed_chunks(sample_chunks)

        ids = memory_store.add(sample_chunks)

        assert len(ids) == len(sample_chunks)
        assert memory_store.count == len(sample_chunks)

    def test_add_chunks_without_embeddings(self, memory_store, sample_chunks):
        """Test that adding chunks without embeddings raises error."""
        with pytest.raises(VectorStoreError):
            memory_store.add(sample_chunks)

    def test_search(self, populated_memory_store, fitted_tfidf_embedder):
        """Test searching the store."""
        query_embedding = fitted_tfidf_embedder.embed_single("chunk one")

        results = populated_memory_store.search(query_embedding, top_k=2)

        assert len(results) <= 2
        assert results.results[0].score >= results.results[1].score  # Sorted by score

    def test_search_empty_store(self, memory_store):
        """Test searching empty store."""
        results = memory_store.search([0.1, 0.2, 0.3], top_k=5)

        assert len(results) == 0

    def test_get_chunks(self, populated_memory_store, sample_chunks):
        """Test retrieving chunks by ID."""
        ids = [sample_chunks[0].id, sample_chunks[1].id]
        chunks = populated_memory_store.get(ids)

        assert len(chunks) == 2
        assert chunks[0].id == ids[0]

    def test_get_nonexistent_chunk(self, populated_memory_store):
        """Test getting nonexistent chunk raises error."""
        with pytest.raises(DocumentNotFoundError):
            populated_memory_store.get(["nonexistent-id"])

    def test_delete_chunks(self, populated_memory_store, sample_chunks):
        """Test deleting chunks."""
        initial_count = populated_memory_store.count

        populated_memory_store.delete([sample_chunks[0].id])

        assert populated_memory_store.count == initial_count - 1

    def test_clear(self, populated_memory_store):
        """Test clearing the store."""
        assert populated_memory_store.count > 0

        populated_memory_store.clear()

        assert populated_memory_store.count == 0

    def test_len(self, populated_memory_store, sample_chunks):
        """Test __len__ method."""
        assert len(populated_memory_store) == len(sample_chunks)

    def test_cosine_similarity(self, memory_store, fitted_tfidf_embedder):
        """Test cosine similarity metric."""
        # Create chunks with known content
        chunks = [
            Chunk(content="apple orange banana", document_id="doc", chunk_index=0),
            Chunk(content="car truck vehicle", document_id="doc", chunk_index=1),
        ]
        fitted_tfidf_embedder.embed_chunks(chunks)
        memory_store.add(chunks)

        # Search for fruit-related query
        query_emb = fitted_tfidf_embedder.embed_single("apple fruit")
        results = memory_store.search(query_emb, top_k=2)

        # Fruit chunk should rank higher
        assert len(results) == 2

    def test_filter_search(self, memory_store, fitted_tfidf_embedder):
        """Test search with metadata filter."""
        chunks = [
            Chunk(
                content="Content A", document_id="doc", chunk_index=0, metadata={"category": "A"}
            ),
            Chunk(
                content="Content B", document_id="doc", chunk_index=1, metadata={"category": "B"}
            ),
        ]
        fitted_tfidf_embedder.embed_chunks(chunks)
        memory_store.add(chunks)

        query_emb = fitted_tfidf_embedder.embed_single("content")

        # Filter by category
        results = memory_store.search(query_emb, top_k=10, filter={"category": "A"})

        # Should only return category A
        assert len(results) == 1
        assert results.results[0].chunk.metadata["category"] == "A"


class TestChromaStore:
    """Tests for ChromaStore (if available)."""

    @pytest.fixture
    def chroma_store(self, temp_dir):
        """Create ChromaDB store."""
        try:
            from prompt_amplifier.vectorstores import ChromaStore

            return ChromaStore(
                collection_name="test",
                persist_directory=str(temp_dir / "chroma"),
            )
        except ImportError:
            pytest.skip("chromadb not installed")

    def test_create_store(self, chroma_store):
        """Test creating ChromaDB store."""
        assert chroma_store.count == 0
        assert chroma_store.is_persistent

    def test_add_and_search(self, chroma_store, sample_chunks, fitted_tfidf_embedder):
        """Test adding and searching."""
        fitted_tfidf_embedder.embed_chunks(sample_chunks)
        chroma_store.add(sample_chunks)

        assert chroma_store.count == len(sample_chunks)

        query_emb = fitted_tfidf_embedder.embed_single("chunk")
        results = chroma_store.search(query_emb, top_k=2)

        assert len(results) <= 2

    def test_delete(self, chroma_store, sample_chunks, fitted_tfidf_embedder):
        """Test deleting from ChromaDB."""
        fitted_tfidf_embedder.embed_chunks(sample_chunks)
        chroma_store.add(sample_chunks)

        initial_count = chroma_store.count
        chroma_store.delete([sample_chunks[0].id])

        assert chroma_store.count == initial_count - 1


class TestFAISSStore:
    """Tests for FAISSStore (if available)."""

    @pytest.fixture
    def faiss_store(self, temp_dir):
        """Create FAISS store."""
        try:
            from prompt_amplifier.vectorstores import FAISSStore

            return FAISSStore(
                collection_name="test",
                persist_directory=str(temp_dir / "faiss"),
            )
        except ImportError:
            pytest.skip("faiss not installed")

    def test_create_store(self, faiss_store):
        """Test creating FAISS store."""
        assert faiss_store.count == 0

    def test_add_and_search(self, faiss_store, sample_chunks, fitted_tfidf_embedder):
        """Test adding and searching FAISS."""
        fitted_tfidf_embedder.embed_chunks(sample_chunks)
        faiss_store.add(sample_chunks)

        assert faiss_store.count == len(sample_chunks)

        query_emb = fitted_tfidf_embedder.embed_single("chunk")
        results = faiss_store.search(query_emb, top_k=2)

        assert len(results) <= 2

    def test_persistence(self, faiss_store, sample_chunks, fitted_tfidf_embedder, temp_dir):
        """Test FAISS persistence."""
        from prompt_amplifier.vectorstores import FAISSStore

        fitted_tfidf_embedder.embed_chunks(sample_chunks)
        faiss_store.add(sample_chunks)
        faiss_store.persist()

        # Create new store from same directory
        new_store = FAISSStore(
            collection_name="test",
            persist_directory=str(temp_dir / "faiss"),
        )

        assert new_store.count == len(sample_chunks)
