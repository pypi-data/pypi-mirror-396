"""Tests for embedders."""

from __future__ import annotations

import numpy as np
import pytest

from prompt_amplifier.core.exceptions import EmbedderError
from prompt_amplifier.embedders import TFIDFEmbedder
from prompt_amplifier.embedders.base import BaseSparseEmbedder


class TestTFIDFEmbedder:
    """Tests for TFIDFEmbedder."""

    def test_fit(self, tfidf_embedder, sample_texts):
        """Test fitting the embedder."""
        assert not tfidf_embedder.is_fitted

        tfidf_embedder.fit(sample_texts)

        assert tfidf_embedder.is_fitted
        assert tfidf_embedder.vocabulary_size > 0

    def test_embed_after_fit(self, fitted_tfidf_embedder, sample_texts):
        """Test embedding after fitting."""
        result = fitted_tfidf_embedder.embed(sample_texts[:2])

        assert result.count == 2
        assert result.dimension == fitted_tfidf_embedder.dimension
        assert len(result.embeddings[0]) == result.dimension

    def test_embed_without_fit_raises(self, tfidf_embedder):
        """Test that embedding without fitting raises error."""
        with pytest.raises(EmbedderError):
            tfidf_embedder.embed(["test text"])

    def test_fit_embed(self, tfidf_embedder, sample_texts):
        """Test fit_embed convenience method."""
        result = tfidf_embedder.fit_embed(sample_texts)

        assert tfidf_embedder.is_fitted
        assert result.count == len(sample_texts)

    def test_embed_single(self, fitted_tfidf_embedder):
        """Test embedding single text."""
        embedding = fitted_tfidf_embedder.embed_single("test query")

        assert isinstance(embedding, list)
        assert len(embedding) == fitted_tfidf_embedder.dimension

    def test_embed_empty_list(self, fitted_tfidf_embedder):
        """Test embedding empty list."""
        result = fitted_tfidf_embedder.embed([])

        assert result.count == 0
        assert result.embeddings == []

    def test_embed_chunks(self, fitted_tfidf_embedder, sample_chunks):
        """Test embedding chunks."""
        # Chunks should not have embeddings yet
        assert not sample_chunks[0].has_embedding

        fitted_tfidf_embedder.embed_chunks(sample_chunks)

        # Now they should have embeddings
        assert sample_chunks[0].has_embedding
        assert sample_chunks[0].embedding_dim == fitted_tfidf_embedder.dimension

    def test_is_sparse(self, tfidf_embedder):
        """Test that TF-IDF is sparse embedder."""
        assert tfidf_embedder.is_sparse
        assert isinstance(tfidf_embedder, BaseSparseEmbedder)

    def test_feature_names(self, fitted_tfidf_embedder):
        """Test getting feature names."""
        features = fitted_tfidf_embedder.feature_names

        assert isinstance(features, list)
        assert len(features) == fitted_tfidf_embedder.vocabulary_size

    def test_ngram_range(self, sample_texts):
        """Test n-gram configuration."""
        embedder = TFIDFEmbedder(ngram_range=(1, 3))
        embedder.fit(sample_texts)

        # With trigrams, vocabulary should be larger
        assert embedder.vocabulary_size > 0

    def test_max_features(self, sample_texts):
        """Test max features limit."""
        embedder = TFIDFEmbedder(max_features=10)
        embedder.fit(sample_texts)

        assert embedder.vocabulary_size <= 10


def _has_rank_bm25():
    """Check if rank_bm25 is installed."""
    try:
        import rank_bm25

        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _has_rank_bm25(), reason="rank_bm25 not installed")
class TestBM25Embedder:
    """Tests for BM25Embedder."""

    @pytest.fixture
    def bm25_embedder(self):
        """Create BM25 embedder."""
        from prompt_amplifier.embedders.tfidf import BM25Embedder

        return BM25Embedder()

    def test_fit(self, bm25_embedder, sample_texts):
        """Test fitting BM25."""
        bm25_embedder.fit(sample_texts)

        assert bm25_embedder.is_fitted
        assert bm25_embedder.vocabulary_size > 0

    def test_get_scores(self, bm25_embedder, sample_texts):
        """Test getting BM25 scores."""
        bm25_embedder.fit(sample_texts)
        scores = bm25_embedder.get_scores("sales revenue")

        assert len(scores) == len(sample_texts)
        # First doc mentions "sales" and "revenue"
        assert scores[0] > 0

    def test_get_top_n(self, bm25_embedder, sample_texts):
        """Test getting top N results."""
        bm25_embedder.fit(sample_texts)
        top_results = bm25_embedder.get_top_n("customer satisfaction", n=2)

        assert len(top_results) == 2
        # Results should be (index, score) tuples
        assert isinstance(top_results[0], tuple)
        assert len(top_results[0]) == 2


def _has_sentence_transformers():
    """Check if sentence-transformers is installed."""
    try:
        import sentence_transformers

        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _has_sentence_transformers(), reason="sentence-transformers not installed")
class TestSentenceTransformerEmbedder:
    """Tests for SentenceTransformerEmbedder (if available)."""

    @pytest.fixture
    def st_embedder(self):
        """Create Sentence Transformer embedder."""
        from prompt_amplifier.embedders import SentenceTransformerEmbedder

        return SentenceTransformerEmbedder(model="all-MiniLM-L6-v2")

    def test_embed(self, st_embedder, sample_texts):
        """Test embedding with Sentence Transformers."""
        result = st_embedder.embed(sample_texts[:2])

        assert result.count == 2
        assert result.dimension == 384  # all-MiniLM-L6-v2 dimension

    def test_not_sparse(self, st_embedder):
        """Test that ST is dense embedder."""
        assert not st_embedder.is_sparse

    def test_normalized_embeddings(self, st_embedder):
        """Test that embeddings are normalized."""
        result = st_embedder.embed(["test text"])
        embedding = np.array(result.embeddings[0])

        # L2 norm should be ~1 for normalized vectors
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 0.01


class TestEmbedderInterface:
    """Tests for embedder interface compliance."""

    def test_embedder_name(self, tfidf_embedder):
        """Test embedder_name property."""
        assert tfidf_embedder.embedder_name == "TFIDFEmbedder"

    def test_repr(self, tfidf_embedder, sample_texts):
        """Test string representation."""
        tfidf_embedder.fit(sample_texts)
        repr_str = repr(tfidf_embedder)

        assert "TFIDFEmbedder" in repr_str
        assert "dim=" in repr_str
