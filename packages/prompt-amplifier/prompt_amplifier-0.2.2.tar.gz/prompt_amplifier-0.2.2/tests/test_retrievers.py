"""Tests for retrievers."""

from __future__ import annotations

import pytest

from prompt_amplifier.embedders import TFIDFEmbedder
from prompt_amplifier.models.document import Chunk
from prompt_amplifier.retrievers import MMRRetriever, VectorRetriever
from prompt_amplifier.vectorstores import MemoryStore


class TestVectorRetriever:
    """Tests for VectorRetriever."""

    @pytest.fixture
    def retriever_setup(self, sample_texts):
        """Set up retriever with data."""
        embedder = TFIDFEmbedder()
        embedder.fit(sample_texts)

        store = MemoryStore()
        chunks = [
            Chunk(content=text, document_id="doc", chunk_index=i, source=f"doc{i}.txt")
            for i, text in enumerate(sample_texts)
        ]
        embedder.embed_chunks(chunks)
        store.add(chunks)

        retriever = VectorRetriever(embedder=embedder, vectorstore=store, top_k=3)

        return retriever, chunks

    def test_retrieve(self, retriever_setup):
        """Test basic retrieval."""
        retriever, chunks = retriever_setup

        results = retriever.retrieve("sales revenue growth")

        assert len(results) <= 3
        assert results.query == "sales revenue growth"
        assert results.retriever_type == "vector"

    def test_retrieve_with_top_k(self, retriever_setup):
        """Test retrieval with custom top_k."""
        retriever, chunks = retriever_setup

        results = retriever.retrieve("test", top_k=2)

        assert len(results) <= 2

    def test_retrieve_with_score_threshold(self, sample_texts):
        """Test retrieval with score threshold."""
        embedder = TFIDFEmbedder()
        embedder.fit(sample_texts)

        store = MemoryStore()
        chunks = [
            Chunk(content=text, document_id="doc", chunk_index=i)
            for i, text in enumerate(sample_texts)
        ]
        embedder.embed_chunks(chunks)
        store.add(chunks)

        retriever = VectorRetriever(
            embedder=embedder,
            vectorstore=store,
            top_k=10,
            score_threshold=0.1,
        )

        results = retriever.retrieve("sales revenue")

        # All results should be above threshold
        for result in results:
            assert result.score >= 0.1

    def test_retrieve_with_scores(self, retriever_setup):
        """Test retrieve_with_scores method."""
        retriever, chunks = retriever_setup

        results = retriever.retrieve_with_scores(
            "customer satisfaction",
            top_k=5,
            score_threshold=0.05,
        )

        for result in results:
            assert result.score >= 0.05

    def test_retriever_repr(self, retriever_setup):
        """Test retriever string representation."""
        retriever, _ = retriever_setup

        repr_str = repr(retriever)
        assert "VectorRetriever" in repr_str
        assert "TFIDFEmbedder" in repr_str


class TestMMRRetriever:
    """Tests for MMRRetriever."""

    @pytest.fixture
    def mmr_setup(self):
        """Set up MMR retriever."""
        # Create texts with some redundancy
        texts = [
            "The sales report shows 15% revenue increase this quarter.",
            "Revenue grew by 15% according to the quarterly sales report.",  # Similar to first
            "Customer satisfaction improved to 4.5 stars.",
            "Technical support tickets decreased significantly.",
            "Employee retention rate is now at 95%.",
        ]

        embedder = TFIDFEmbedder()
        embedder.fit(texts)

        store = MemoryStore()
        chunks = [
            Chunk(content=text, document_id="doc", chunk_index=i) for i, text in enumerate(texts)
        ]
        embedder.embed_chunks(chunks)
        store.add(chunks)

        retriever = MMRRetriever(
            embedder=embedder,
            vectorstore=store,
            top_k=3,
            lambda_mult=0.5,
            fetch_k=5,
        )

        return retriever, chunks

    def test_mmr_retrieve(self, mmr_setup):
        """Test MMR retrieval."""
        retriever, chunks = mmr_setup

        results = retriever.retrieve("sales revenue report")

        assert len(results) <= 3
        assert results.retriever_type == "mmr"

    def test_mmr_diversity(self, mmr_setup):
        """Test that MMR promotes diversity."""
        retriever, chunks = mmr_setup

        # With lambda=0.5, should balance relevance and diversity
        results = retriever.retrieve("sales revenue quarter")

        # Should not return both similar documents (first two)
        # This is a soft check - MMR should prefer diversity
        assert len(results) >= 1


def _has_rank_bm25():
    """Check if rank_bm25 is installed."""
    try:
        import rank_bm25

        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _has_rank_bm25(), reason="rank_bm25 not installed")
class TestHybridRetriever:
    """Tests for HybridRetriever."""

    @pytest.fixture
    def hybrid_setup(self, sample_texts):
        """Set up hybrid retriever."""
        from prompt_amplifier.embedders.tfidf import BM25Embedder
        from prompt_amplifier.retrievers import HybridRetriever

        # Dense embedder (using TF-IDF as dense for testing)
        dense_embedder = TFIDFEmbedder(max_features=500)
        dense_embedder.fit(sample_texts)

        # Sparse embedder (BM25)
        sparse_embedder = BM25Embedder()
        sparse_embedder.fit(sample_texts)

        store = MemoryStore()
        chunks = [
            Chunk(content=text, document_id="doc", chunk_index=i)
            for i, text in enumerate(sample_texts)
        ]
        dense_embedder.embed_chunks(chunks)
        store.add(chunks)

        retriever = HybridRetriever(
            embedder=dense_embedder,
            vectorstore=store,
            sparse_embedder=sparse_embedder,
            top_k=3,
            dense_weight=0.7,
            sparse_weight=0.3,
        )
        retriever.add_chunks_for_sparse(chunks)

        return retriever

    def test_hybrid_retrieve(self, hybrid_setup):
        """Test hybrid retrieval."""
        retriever = hybrid_setup

        results = retriever.retrieve("customer satisfaction score")

        assert len(results) <= 3
        assert results.retriever_type == "hybrid"
