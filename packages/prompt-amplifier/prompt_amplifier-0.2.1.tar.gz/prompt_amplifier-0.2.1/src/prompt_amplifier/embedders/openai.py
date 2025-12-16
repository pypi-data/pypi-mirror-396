"""OpenAI embeddings."""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from typing import Any

from prompt_amplifier.core.exceptions import APIKeyMissingError, EmbedderError
from prompt_amplifier.embedders.base import BaseEmbedder
from prompt_amplifier.models.embedding import EmbeddingResult


class OpenAIEmbedder(BaseEmbedder):
    """
    OpenAI embeddings API.

    High quality embeddings, requires API key.

    Models:
        - text-embedding-3-small: 1536 dims, fast, cheap
        - text-embedding-3-large: 3072 dims, best quality
        - text-embedding-ada-002: 1536 dims (legacy)

    Requires: openai

    Example:
        >>> embedder = OpenAIEmbedder(model="text-embedding-3-small")
        >>> result = embedder.embed(["Hello world"])
    """

    MODEL_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
        batch_size: int = 100,
        dimensions: int | None = None,
        **kwargs: Any,
    ):
        """
        Initialize OpenAI embedder.

        Args:
            model: Model name
            api_key: API key (or set OPENAI_API_KEY env var)
            batch_size: Batch size for API calls
            dimensions: Output dimensions (for text-embedding-3-* models)
        """
        super().__init__(model=model, **kwargs)

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise APIKeyMissingError("OpenAI", "OPENAI_API_KEY")

        self.batch_size = batch_size
        self.dimensions = dimensions
        self._client = None

        # Set dimension based on model or custom
        if dimensions:
            self._dimension = dimensions
        else:
            self._dimension = self.MODEL_DIMENSIONS.get(model, 1536)

    def _get_client(self) -> Any:
        """Get or create OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError(
                    "openai is required for OpenAIEmbedder. " "Install it with: pip install openai"
                )

            self._client = OpenAI(api_key=self.api_key)

        return self._client

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """
        Generate embeddings using OpenAI API.

        Args:
            texts: Texts to embed

        Returns:
            EmbeddingResult with embeddings
        """
        if not texts:
            return EmbeddingResult(
                embeddings=[],
                model=self.model,
                dimension=self.dimension,
            )

        client = self._get_client()
        start_time = time.time()

        all_embeddings = []
        total_tokens = 0

        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = list(texts[i : i + self.batch_size])

            try:
                kwargs: dict[str, Any] = {
                    "model": self.model,
                    "input": batch,
                }

                # Add dimensions for newer models
                if self.dimensions and "text-embedding-3" in self.model:
                    kwargs["dimensions"] = self.dimensions

                response = client.embeddings.create(**kwargs)

                for item in response.data:
                    all_embeddings.append(item.embedding)

                total_tokens += response.usage.total_tokens

            except Exception as e:
                raise EmbedderError(f"OpenAI embedding failed: {e}")

        embedding_time = (time.time() - start_time) * 1000

        return EmbeddingResult(
            embeddings=all_embeddings,
            model=self.model,
            dimension=self._dimension,
            input_texts=list(texts),
            embedding_time_ms=embedding_time,
            usage={"total_tokens": total_tokens},
        )

    @property
    def dimension(self) -> int:
        return self._dimension


class CohereEmbedder(BaseEmbedder):
    """
    Cohere embeddings API.

    High quality multilingual embeddings.

    Models:
        - embed-english-v3.0: 1024 dims
        - embed-multilingual-v3.0: 1024 dims
        - embed-english-light-v3.0: 384 dims (faster)

    Requires: cohere

    Example:
        >>> embedder = CohereEmbedder(model="embed-english-v3.0")
        >>> result = embedder.embed(["Hello world"])
    """

    MODEL_DIMENSIONS = {
        "embed-english-v3.0": 1024,
        "embed-multilingual-v3.0": 1024,
        "embed-english-light-v3.0": 384,
        "embed-multilingual-light-v3.0": 384,
    }

    def __init__(
        self,
        model: str = "embed-english-v3.0",
        api_key: str | None = None,
        input_type: str = "search_document",
        batch_size: int = 96,
        **kwargs: Any,
    ):
        """
        Initialize Cohere embedder.

        Args:
            model: Model name
            api_key: API key (or set COHERE_API_KEY env var)
            input_type: Type of input ('search_document', 'search_query', etc.)
            batch_size: Batch size for API calls
        """
        super().__init__(model=model, **kwargs)

        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise APIKeyMissingError("Cohere", "COHERE_API_KEY")

        self.input_type = input_type
        self.batch_size = batch_size
        self._client = None
        self._dimension = self.MODEL_DIMENSIONS.get(model, 1024)

    def _get_client(self) -> Any:
        """Get or create Cohere client."""
        if self._client is None:
            try:
                import cohere
            except ImportError:
                raise ImportError(
                    "cohere is required for CohereEmbedder. " "Install it with: pip install cohere"
                )

            self._client = cohere.Client(self.api_key)

        return self._client

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """Generate embeddings using Cohere API."""
        if not texts:
            return EmbeddingResult(
                embeddings=[],
                model=self.model,
                dimension=self.dimension,
            )

        client = self._get_client()
        start_time = time.time()

        all_embeddings = []

        for i in range(0, len(texts), self.batch_size):
            batch = list(texts[i : i + self.batch_size])

            try:
                response = client.embed(
                    texts=batch,
                    model=self.model,
                    input_type=self.input_type,
                )
                all_embeddings.extend(response.embeddings)

            except Exception as e:
                raise EmbedderError(f"Cohere embedding failed: {e}")

        embedding_time = (time.time() - start_time) * 1000

        return EmbeddingResult(
            embeddings=all_embeddings,
            model=self.model,
            dimension=self._dimension,
            input_texts=list(texts),
            embedding_time_ms=embedding_time,
        )

    def embed_query(self, query: str) -> list[float]:
        """Embed a search query (uses search_query input type)."""
        original_type = self.input_type
        self.input_type = "search_query"
        try:
            result = self.embed([query])
            return result.embeddings[0]
        finally:
            self.input_type = original_type

    @property
    def dimension(self) -> int:
        return self._dimension
