"""TF-IDF sparse embedder."""

from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from prompt_amplifier.core.exceptions import EmbedderError
from prompt_amplifier.embedders.base import BaseSparseEmbedder
from prompt_amplifier.models.embedding import EmbeddingResult


class TFIDFEmbedder(BaseSparseEmbedder):
    """
    TF-IDF (Term Frequency-Inverse Document Frequency) embedder.

    Creates sparse vector representations based on word frequencies.
    Free, fast, and works well for keyword-based retrieval.

    Note: Must be fitted on a corpus before use, or use fit_embed().

    Example:
        >>> embedder = TFIDFEmbedder(max_features=10000)
        >>> embedder.fit(corpus_texts)
        >>> result = embedder.embed(["query text"])

    Example (fit and embed in one step):
        >>> embedder = TFIDFEmbedder()
        >>> result = embedder.fit_embed(texts)
    """

    def __init__(
        self,
        max_features: int = 50000,
        ngram_range: tuple[int, int] = (1, 2),
        min_df: int | float = 1,
        max_df: float = 0.95,
        sublinear_tf: bool = True,
        **kwargs: Any,
    ):
        """
        Initialize TF-IDF embedder.

        Args:
            max_features: Maximum vocabulary size
            ngram_range: Range of n-grams (min, max)
            min_df: Minimum document frequency for terms
            max_df: Maximum document frequency for terms
            sublinear_tf: Apply sublinear tf scaling (1 + log(tf))
        """
        super().__init__(model="tfidf", **kwargs)

        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        self.sublinear_tf = sublinear_tf

        self._vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            min_df=min_df,
            max_df=max_df,
            sublinear_tf=sublinear_tf,
        )

    def fit(self, texts: Sequence[str]) -> TFIDFEmbedder:
        """
        Fit the TF-IDF vectorizer on a corpus.

        Args:
            texts: Corpus of texts to fit on

        Returns:
            Self for chaining
        """
        if not texts:
            raise EmbedderError("Cannot fit on empty corpus")

        self._vectorizer.fit(texts)
        self._fitted = True
        self._vocabulary_size = len(self._vectorizer.vocabulary_)
        self._dimension = len(self._vectorizer.get_feature_names_out())

        return self

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """
        Generate TF-IDF embeddings for texts.

        Args:
            texts: Texts to embed

        Returns:
            EmbeddingResult with sparse vectors converted to dense
        """
        if not self._fitted:
            raise EmbedderError(
                "TFIDFEmbedder must be fitted before embedding. " "Call fit() or fit_embed() first."
            )

        if not texts:
            return EmbeddingResult(
                embeddings=[],
                model="tfidf",
                dimension=self.dimension,
            )

        start_time = time.time()

        # Transform to sparse matrix
        sparse_matrix = self._vectorizer.transform(texts)

        # Convert to dense for compatibility with vector stores
        # Note: For very large vocabularies, consider keeping sparse
        embeddings = sparse_matrix.toarray().tolist()

        embedding_time = (time.time() - start_time) * 1000

        return EmbeddingResult(
            embeddings=embeddings,
            model="tfidf",
            dimension=self.dimension,
            input_texts=list(texts),
            embedding_time_ms=embedding_time,
        )

    def embed_sparse(self, texts: Sequence[str]) -> Any:
        """
        Get sparse matrix directly (more memory efficient).

        Args:
            texts: Texts to embed

        Returns:
            scipy sparse matrix
        """
        if not self._fitted:
            raise EmbedderError("TFIDFEmbedder must be fitted first.")

        return self._vectorizer.transform(texts)

    @property
    def dimension(self) -> int:
        """Dimension equals vocabulary size."""
        if self._dimension is None:
            raise EmbedderError("Dimension unknown until fitted.")
        return self._dimension

    @property
    def feature_names(self) -> list[str]:
        """Get vocabulary terms."""
        if not self._fitted:
            raise EmbedderError("Not fitted yet.")
        return list(self._vectorizer.get_feature_names_out())


class BM25Embedder(BaseSparseEmbedder):
    """
    BM25 (Best Match 25) embedder.

    A probabilistic ranking function used by search engines.
    Often works better than TF-IDF for short queries.

    Uses rank_bm25 library for scoring.

    Example:
        >>> embedder = BM25Embedder()
        >>> embedder.fit(corpus_texts)
        >>> scores = embedder.get_scores("query text")
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        **kwargs: Any,
    ):
        """
        Initialize BM25 embedder.

        Args:
            k1: Term frequency saturation parameter
            b: Document length normalization parameter
        """
        super().__init__(model="bm25", **kwargs)
        self.k1 = k1
        self.b = b
        self._bm25 = None
        self._corpus_tokens: list[list[str]] = []

    def _tokenize(self, text: str) -> list[str]:
        """Simple whitespace tokenization."""
        return text.lower().split()

    def fit(self, texts: Sequence[str]) -> BM25Embedder:
        """
        Fit BM25 on a corpus.

        Args:
            texts: Corpus of texts

        Returns:
            Self for chaining
        """
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            raise ImportError(
                "rank_bm25 is required for BM25Embedder. " "Install it with: pip install rank-bm25"
            )

        if not texts:
            raise EmbedderError("Cannot fit on empty corpus")

        self._corpus_tokens = [self._tokenize(text) for text in texts]
        self._bm25 = BM25Okapi(self._corpus_tokens, k1=self.k1, b=self.b)
        self._fitted = True
        self._vocabulary_size = len(
            set(token for tokens in self._corpus_tokens for token in tokens)
        )

        return self

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """
        Get BM25 scores for texts against the corpus.

        Note: BM25 doesn't produce traditional embeddings.
        Instead, it returns scores against each document in the corpus.

        Args:
            texts: Query texts

        Returns:
            EmbeddingResult where each "embedding" is scores against corpus
        """
        if not self._fitted or self._bm25 is None:
            raise EmbedderError("BM25Embedder must be fitted first.")

        start_time = time.time()

        embeddings = []
        for text in texts:
            query_tokens = self._tokenize(text)
            scores = self._bm25.get_scores(query_tokens)
            embeddings.append(scores.tolist())

        embedding_time = (time.time() - start_time) * 1000

        return EmbeddingResult(
            embeddings=embeddings,
            model="bm25",
            dimension=len(self._corpus_tokens),
            input_texts=list(texts),
            embedding_time_ms=embedding_time,
        )

    def get_scores(self, query: str) -> np.ndarray:
        """
        Get BM25 scores for a query against the corpus.

        Args:
            query: Query text

        Returns:
            Array of scores (one per corpus document)
        """
        if not self._fitted or self._bm25 is None:
            raise EmbedderError("BM25Embedder must be fitted first.")

        query_tokens = self._tokenize(query)
        return self._bm25.get_scores(query_tokens)

    def get_top_n(self, query: str, n: int = 10) -> list[tuple[int, float]]:
        """
        Get top-n documents for a query.

        Args:
            query: Query text
            n: Number of results

        Returns:
            List of (document_index, score) tuples
        """
        scores = self.get_scores(query)
        top_indices = np.argsort(scores)[::-1][:n]
        return [(int(idx), float(scores[idx])) for idx in top_indices]

    @property
    def dimension(self) -> int:
        """Dimension equals corpus size for BM25."""
        return len(self._corpus_tokens) if self._corpus_tokens else 0
