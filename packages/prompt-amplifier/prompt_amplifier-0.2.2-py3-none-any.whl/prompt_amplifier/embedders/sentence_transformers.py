"""Sentence Transformers embedder (HuggingFace)."""

from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any

from prompt_amplifier.core.exceptions import EmbedderError
from prompt_amplifier.embedders.base import BaseEmbedder
from prompt_amplifier.models.embedding import EmbeddingResult


class SentenceTransformerEmbedder(BaseEmbedder):
    """
    Sentence Transformers embedder using HuggingFace models.

    Free, local embeddings with high quality. Many models available.

    Popular models:
        - all-MiniLM-L6-v2: Fast, good quality (384 dims)
        - all-mpnet-base-v2: Best quality (768 dims)
        - multi-qa-mpnet-base-dot-v1: Optimized for QA (768 dims)
        - paraphrase-multilingual-MiniLM-L12-v2: Multilingual (384 dims)

    Requires: sentence-transformers

    Example:
        >>> embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
        >>> result = embedder.embed(["Hello world"])
        >>> print(result.dimension)  # 384
    """

    # Common models with their dimensions
    MODEL_DIMENSIONS = {
        "all-MiniLM-L6-v2": 384,
        "all-MiniLM-L12-v2": 384,
        "all-mpnet-base-v2": 768,
        "multi-qa-mpnet-base-dot-v1": 768,
        "multi-qa-MiniLM-L6-cos-v1": 384,
        "paraphrase-MiniLM-L6-v2": 384,
        "paraphrase-multilingual-MiniLM-L12-v2": 384,
        "msmarco-MiniLM-L6-cos-v5": 384,
    }

    def __init__(
        self,
        model: str = "all-MiniLM-L6-v2",
        device: str | None = None,
        batch_size: int = 32,
        normalize_embeddings: bool = True,
        **kwargs: Any,
    ):
        """
        Initialize Sentence Transformer embedder.

        Args:
            model: Model name from HuggingFace
            device: Device to use (None = auto-detect, 'cpu', 'cuda', 'mps')
            batch_size: Batch size for encoding
            normalize_embeddings: Whether to L2-normalize embeddings
        """
        super().__init__(model=model, **kwargs)
        self.device = device
        self.batch_size = batch_size
        self.normalize_embeddings = normalize_embeddings

        self._model = None
        self._dimension = self.MODEL_DIMENSIONS.get(model)

    def _load_model(self) -> Any:
        """Lazy load the model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for SentenceTransformerEmbedder. "
                    "Install it with: pip install sentence-transformers"
                )

            self._model = SentenceTransformer(self.model, device=self.device)
            self._dimension = self._model.get_sentence_embedding_dimension()

        return self._model

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """
        Generate embeddings for texts.

        Args:
            texts: Texts to embed

        Returns:
            EmbeddingResult with dense embeddings
        """
        if not texts:
            return EmbeddingResult(
                embeddings=[],
                model=self.model,
                dimension=self.dimension,
            )

        model = self._load_model()
        start_time = time.time()

        try:
            embeddings = model.encode(
                list(texts),
                batch_size=self.batch_size,
                normalize_embeddings=self.normalize_embeddings,
                show_progress_bar=False,
            )
        except Exception as e:
            raise EmbedderError(f"Embedding failed: {e}")

        embedding_time = (time.time() - start_time) * 1000

        return EmbeddingResult(
            embeddings=embeddings.tolist(),
            model=self.model,
            dimension=self._dimension,
            input_texts=list(texts),
            embedding_time_ms=embedding_time,
        )

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        if self._dimension is None:
            # Load model to get dimension
            self._load_model()
        return self._dimension or 384  # Default fallback


class FastEmbedEmbedder(BaseEmbedder):
    """
    FastEmbed embedder from Qdrant.

    Optimized for speed, uses ONNX runtime.
    Good balance of speed and quality.

    Requires: fastembed

    Example:
        >>> embedder = FastEmbedEmbedder("BAAI/bge-small-en-v1.5")
        >>> result = embedder.embed(["Hello world"])
    """

    MODEL_DIMENSIONS = {
        "BAAI/bge-small-en-v1.5": 384,
        "BAAI/bge-base-en-v1.5": 768,
        "BAAI/bge-large-en-v1.5": 1024,
        "sentence-transformers/all-MiniLM-L6-v2": 384,
    }

    def __init__(
        self,
        model: str = "BAAI/bge-small-en-v1.5",
        batch_size: int = 256,
        parallel: int | None = None,
        **kwargs: Any,
    ):
        """
        Initialize FastEmbed embedder.

        Args:
            model: Model name
            batch_size: Batch size for encoding
            parallel: Number of parallel workers (None = auto)
        """
        super().__init__(model=model, **kwargs)
        self.batch_size = batch_size
        self.parallel = parallel

        self._model = None
        self._dimension = self.MODEL_DIMENSIONS.get(model, 384)

    def _load_model(self) -> Any:
        """Lazy load the model."""
        if self._model is None:
            try:
                from fastembed import TextEmbedding
            except ImportError:
                raise ImportError(
                    "fastembed is required for FastEmbedEmbedder. "
                    "Install it with: pip install fastembed"
                )

            self._model = TextEmbedding(
                model_name=self.model,
                batch_size=self.batch_size,
                parallel=self.parallel,
            )

        return self._model

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """Generate embeddings for texts."""
        if not texts:
            return EmbeddingResult(
                embeddings=[],
                model=self.model,
                dimension=self.dimension,
            )

        model = self._load_model()
        start_time = time.time()

        try:
            # FastEmbed returns a generator
            embeddings = list(model.embed(list(texts)))
        except Exception as e:
            raise EmbedderError(f"Embedding failed: {e}")

        embedding_time = (time.time() - start_time) * 1000

        return EmbeddingResult(
            embeddings=[e.tolist() for e in embeddings],
            model=self.model,
            dimension=self._dimension,
            input_texts=list(texts),
            embedding_time_ms=embedding_time,
        )

    @property
    def dimension(self) -> int:
        return self._dimension
