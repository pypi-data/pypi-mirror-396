"""Base embedder interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from prompt_amplifier.models.document import Chunk, ChunkBatch
from prompt_amplifier.models.embedding import EmbeddingResult


class BaseEmbedder(ABC):
    """
    Abstract base class for all embedding providers.

    Implement this class to add support for new embedding models.

    Example:
        >>> class MyEmbedder(BaseEmbedder):
        ...     def embed(self, texts: list[str]) -> EmbeddingResult:
        ...         vectors = my_model.encode(texts)
        ...         return EmbeddingResult(
        ...             embeddings=vectors.tolist(),
        ...             model="my-model",
        ...             dimension=len(vectors[0])
        ...         )
        ...
        ...     @property
        ...     def dimension(self) -> int:
        ...         return 384
    """

    def __init__(self, model: str = "", **kwargs: Any):
        """
        Initialize the embedder.

        Args:
            model: Model name/identifier
            **kwargs: Provider-specific configuration
        """
        self.model = model
        self.config = kwargs
        self._dimension: int | None = None

    @abstractmethod
    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            EmbeddingResult containing the embeddings

        Raises:
            EmbedderError: If embedding fails
        """
        pass

    def embed_single(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            Embedding vector as list of floats
        """
        result = self.embed([text])
        return result.embeddings[0]

    def embed_chunks(self, chunks: Sequence[Chunk]) -> list[Chunk]:
        """
        Generate embeddings for a list of chunks and attach them.

        Args:
            chunks: List of Chunk objects

        Returns:
            Same chunks with embeddings attached
        """
        texts = [c.content for c in chunks]
        result = self.embed(texts)

        for chunk, embedding in zip(chunks, result.embeddings):
            chunk.embedding = embedding

        return list(chunks)

    def embed_batch(self, batch: ChunkBatch) -> ChunkBatch:
        """
        Generate embeddings for a chunk batch.

        Args:
            batch: ChunkBatch object

        Returns:
            Same batch with embeddings attached to chunks
        """
        result = self.embed(batch.contents)
        batch.set_embeddings(result.embeddings)
        return batch

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        The dimension of the embedding vectors.

        Returns:
            Integer dimension
        """
        pass

    @property
    def embedder_name(self) -> str:
        """Name of this embedder."""
        return self.__class__.__name__

    @property
    def is_sparse(self) -> bool:
        """
        Whether this embedder produces sparse vectors.

        Returns:
            True for sparse embedders (TF-IDF, BM25), False for dense
        """
        return False

    def __repr__(self) -> str:
        return f"{self.embedder_name}(model={self.model}, dim={self.dimension})"


class BaseSparseEmbedder(BaseEmbedder):
    """
    Base class for sparse embedding providers (TF-IDF, BM25).

    Sparse embedders need to be fitted on a corpus before use.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._fitted = False
        self._vocabulary_size: int = 0

    @abstractmethod
    def fit(self, texts: Sequence[str]) -> BaseSparseEmbedder:
        """
        Fit the embedder on a corpus.

        Args:
            texts: Corpus of texts to fit on

        Returns:
            Self for chaining
        """
        pass

    def fit_embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """
        Fit on corpus and embed in one step.

        Args:
            texts: Texts to fit on and embed

        Returns:
            EmbeddingResult with embeddings
        """
        self.fit(texts)
        return self.embed(texts)

    @property
    def is_sparse(self) -> bool:
        return True

    @property
    def is_fitted(self) -> bool:
        """Whether the embedder has been fitted."""
        return self._fitted

    @property
    def vocabulary_size(self) -> int:
        """Size of the vocabulary (after fitting)."""
        return self._vocabulary_size
