"""Voyage AI embedding provider."""

from __future__ import annotations

import os
from typing import Optional

from prompt_amplifier.core.exceptions import APIKeyMissingError, EmbedderError
from prompt_amplifier.embedders.base import BaseEmbedder
from prompt_amplifier.models.embedding import EmbeddingResult


class VoyageEmbedder(BaseEmbedder):
    """
    Embedder using Voyage AI's embedding API.

    Voyage AI offers specialized embeddings for different domains:
    - voyage-large-2: General purpose, high quality
    - voyage-code-2: Optimized for code
    - voyage-lite-02-instruct: Lightweight, fast

    Example:
        >>> embedder = VoyageEmbedder()
        >>> result = embedder.embed(["Hello world"])
        >>> print(result.dimension)
        1024

        >>> # For code
        >>> embedder = VoyageEmbedder(model="voyage-code-2")
        >>> result = embedder.embed(["def hello(): pass"])
    """

    MODELS = {
        "voyage-large-2": 1024,
        "voyage-code-2": 1536,
        "voyage-2": 1024,
        "voyage-lite-02-instruct": 1024,
        "voyage-large-2-instruct": 1024,
    }

    def __init__(
        self,
        model: str = "voyage-large-2",
        api_key: Optional[str] = None,
        input_type: Optional[str] = None,
        batch_size: int = 128,
    ):
        """
        Initialize the Voyage embedder.

        Args:
            model: Voyage AI model name.
            api_key: Voyage API key. If not provided, uses VOYAGE_API_KEY env var.
            input_type: Optional input type ("query" or "document").
            batch_size: Number of texts to embed in each API call.
        """
        self.model = model
        self.api_key = api_key or os.getenv("VOYAGE_API_KEY")
        self.input_type = input_type
        self.batch_size = batch_size

        if not self.api_key:
            raise APIKeyMissingError(
                "API key for Voyage AI is missing. "
                "Set the VOYAGE_API_KEY environment variable or pass api_key parameter."
            )

        if model not in self.MODELS:
            raise ValueError(f"Unknown model: {model}. Available: {list(self.MODELS.keys())}")

        self._dimension = self.MODELS[model]
        self._client = None

    def _get_client(self):
        """Get or create Voyage client."""
        if self._client is None:
            try:
                import voyageai
            except ImportError:
                raise ImportError(
                    "voyageai is required for VoyageEmbedder. "
                    "Install it with: pip install voyageai"
                )
            self._client = voyageai.Client(api_key=self.api_key)
        return self._client

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self._dimension

    def embed(self, texts: list[str]) -> EmbeddingResult:
        """
        Embed texts using Voyage AI API.

        Args:
            texts: List of texts to embed.

        Returns:
            EmbeddingResult with embeddings and metadata.
        """
        if not texts:
            return EmbeddingResult(
                embeddings=[],
                dimension=self._dimension,
                model=self.model,
            )

        client = self._get_client()
        all_embeddings = []

        try:
            # Process in batches
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i : i + self.batch_size]

                result = client.embed(
                    texts=batch,
                    model=self.model,
                    input_type=self.input_type,
                )

                all_embeddings.extend(result.embeddings)

        except Exception as e:
            raise EmbedderError(f"Voyage AI embedding failed: {e}") from e

        return EmbeddingResult(
            embeddings=all_embeddings,
            dimension=self._dimension,
            model=self.model,
        )


class JinaEmbedder(BaseEmbedder):
    """
    Embedder using Jina AI's embedding API.

    Jina offers high-quality, multilingual embeddings:
    - jina-embeddings-v2-base-en: English text
    - jina-embeddings-v2-base-de: German text
    - jina-embeddings-v2-base-code: Code embeddings

    Example:
        >>> embedder = JinaEmbedder()
        >>> result = embedder.embed(["Hello world"])
        >>> print(result.dimension)
        768
    """

    MODELS = {
        "jina-embeddings-v2-base-en": 768,
        "jina-embeddings-v2-small-en": 512,
        "jina-embeddings-v2-base-de": 768,
        "jina-embeddings-v2-base-code": 768,
        "jina-embeddings-v3": 1024,
    }

    def __init__(
        self,
        model: str = "jina-embeddings-v2-base-en",
        api_key: Optional[str] = None,
        batch_size: int = 100,
    ):
        """
        Initialize the Jina embedder.

        Args:
            model: Jina AI model name.
            api_key: Jina API key. If not provided, uses JINA_API_KEY env var.
            batch_size: Number of texts to embed in each API call.
        """
        self.model = model
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        self.batch_size = batch_size

        if not self.api_key:
            raise APIKeyMissingError(
                "API key for Jina AI is missing. "
                "Set the JINA_API_KEY environment variable or pass api_key parameter."
            )

        if model not in self.MODELS:
            raise ValueError(f"Unknown model: {model}. Available: {list(self.MODELS.keys())}")

        self._dimension = self.MODELS[model]

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self._dimension

    def embed(self, texts: list[str]) -> EmbeddingResult:
        """
        Embed texts using Jina AI API.

        Args:
            texts: List of texts to embed.

        Returns:
            EmbeddingResult with embeddings and metadata.
        """
        if not texts:
            return EmbeddingResult(
                embeddings=[],
                dimension=self._dimension,
                model=self.model,
            )

        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests is required for JinaEmbedder. " "Install it with: pip install requests"
            )

        all_embeddings = []
        url = "https://api.jina.ai/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            # Process in batches
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i : i + self.batch_size]

                response = requests.post(
                    url,
                    headers=headers,
                    json={
                        "input": batch,
                        "model": self.model,
                    },
                    timeout=60,
                )
                response.raise_for_status()
                result = response.json()

                for item in result["data"]:
                    all_embeddings.append(item["embedding"])

        except Exception as e:
            raise EmbedderError(f"Jina AI embedding failed: {e}") from e

        return EmbeddingResult(
            embeddings=all_embeddings,
            dimension=self._dimension,
            model=self.model,
        )


class MistralEmbedder(BaseEmbedder):
    """
    Embedder using Mistral AI's embedding API.

    Example:
        >>> embedder = MistralEmbedder()
        >>> result = embedder.embed(["Hello world"])
        >>> print(result.dimension)
        1024
    """

    MODELS = {
        "mistral-embed": 1024,
    }

    def __init__(
        self,
        model: str = "mistral-embed",
        api_key: Optional[str] = None,
        batch_size: int = 100,
    ):
        """
        Initialize the Mistral embedder.

        Args:
            model: Mistral embedding model name.
            api_key: Mistral API key. If not provided, uses MISTRAL_API_KEY env var.
            batch_size: Number of texts to embed in each API call.
        """
        self.model = model
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.batch_size = batch_size

        if not self.api_key:
            raise APIKeyMissingError(
                "API key for Mistral AI is missing. "
                "Set the MISTRAL_API_KEY environment variable or pass api_key parameter."
            )

        self._dimension = self.MODELS.get(model, 1024)
        self._client = None

    def _get_client(self):
        """Get or create Mistral client."""
        if self._client is None:
            try:
                from mistralai.client import MistralClient
            except ImportError:
                raise ImportError(
                    "mistralai is required for MistralEmbedder. "
                    "Install it with: pip install mistralai"
                )
            self._client = MistralClient(api_key=self.api_key)
        return self._client

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self._dimension

    def embed(self, texts: list[str]) -> EmbeddingResult:
        """
        Embed texts using Mistral AI API.

        Args:
            texts: List of texts to embed.

        Returns:
            EmbeddingResult with embeddings and metadata.
        """
        if not texts:
            return EmbeddingResult(
                embeddings=[],
                dimension=self._dimension,
                model=self.model,
            )

        client = self._get_client()
        all_embeddings = []

        try:
            # Process in batches
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i : i + self.batch_size]

                response = client.embeddings(
                    model=self.model,
                    input=batch,
                )

                for item in response.data:
                    all_embeddings.append(item.embedding)

        except Exception as e:
            raise EmbedderError(f"Mistral AI embedding failed: {e}") from e

        return EmbeddingResult(
            embeddings=all_embeddings,
            dimension=self._dimension,
            model=self.model,
        )
