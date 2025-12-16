"""Cohere embedding provider."""

from __future__ import annotations

import os
from typing import Optional

from prompt_amplifier.core.exceptions import APIKeyMissingError, EmbedderError
from prompt_amplifier.embedders.base import BaseEmbedder
from prompt_amplifier.models.embedding import EmbeddingResult


class CohereEmbedder(BaseEmbedder):
    """
    Embedder using Cohere's embedding API.

    Cohere offers high-quality embeddings optimized for different tasks:
    - embed-english-v3.0: Best for English text
    - embed-multilingual-v3.0: Best for multilingual text
    - embed-english-light-v3.0: Faster, smaller embeddings

    Example:
        >>> embedder = CohereEmbedder()
        >>> result = embedder.embed(["Hello world", "How are you?"])
        >>> print(result.dimension)
        1024

        >>> # For search/retrieval
        >>> embedder = CohereEmbedder(input_type="search_document")
        >>> doc_embeddings = embedder.embed(documents)

        >>> embedder_query = CohereEmbedder(input_type="search_query")
        >>> query_embedding = embedder_query.embed([query])
    """

    MODELS = {
        "embed-english-v3.0": 1024,
        "embed-multilingual-v3.0": 1024,
        "embed-english-light-v3.0": 384,
        "embed-multilingual-light-v3.0": 384,
    }

    INPUT_TYPES = [
        "search_document",  # For documents to be searched
        "search_query",  # For search queries
        "classification",  # For classification tasks
        "clustering",  # For clustering tasks
    ]

    def __init__(
        self,
        model: str = "embed-english-v3.0",
        api_key: Optional[str] = None,
        input_type: str = "search_document",
        truncate: str = "END",
        batch_size: int = 96,
    ):
        """
        Initialize the Cohere embedder.

        Args:
            model: Cohere embedding model name.
            api_key: Cohere API key. If not provided, uses COHERE_API_KEY env var.
            input_type: Type of input for optimized embeddings.
            truncate: How to handle texts that exceed max length ("START", "END", "NONE").
            batch_size: Number of texts to embed in each API call.
        """
        self.model = model
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        self.input_type = input_type
        self.truncate = truncate
        self.batch_size = batch_size

        if not self.api_key:
            raise APIKeyMissingError(
                "API key for Cohere is missing. "
                "Set the COHERE_API_KEY environment variable or pass api_key parameter."
            )

        if model not in self.MODELS:
            raise ValueError(f"Unknown model: {model}. Available: {list(self.MODELS.keys())}")

        if input_type not in self.INPUT_TYPES:
            raise ValueError(f"Unknown input_type: {input_type}. Available: {self.INPUT_TYPES}")

        self._dimension = self.MODELS[model]
        self._client = None

    def _get_client(self):
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

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self._dimension

    def embed(self, texts: list[str]) -> EmbeddingResult:
        """
        Embed texts using Cohere API.

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

                response = client.embed(
                    texts=batch,
                    model=self.model,
                    input_type=self.input_type,
                    truncate=self.truncate,
                )

                all_embeddings.extend(response.embeddings)

        except Exception as e:
            raise EmbedderError(f"Cohere embedding failed: {e}") from e

        return EmbeddingResult(
            embeddings=all_embeddings,
            dimension=self._dimension,
            model=self.model,
        )


class CohereRerankEmbedder(BaseEmbedder):
    """
    Cohere Rerank for improving retrieval quality.

    This is not a traditional embedder but uses Cohere's rerank API
    to reorder search results by relevance.

    Example:
        >>> reranker = CohereRerankEmbedder()
        >>> results = reranker.rerank(
        ...     query="What is machine learning?",
        ...     documents=["ML is...", "Deep learning...", "Python is..."]
        ... )
        >>> for r in results:
        ...     print(f"{r['index']}: {r['relevance_score']:.3f}")
    """

    def __init__(
        self,
        model: str = "rerank-english-v3.0",
        api_key: Optional[str] = None,
        top_n: Optional[int] = None,
    ):
        """
        Initialize the Cohere reranker.

        Args:
            model: Cohere rerank model name.
            api_key: Cohere API key.
            top_n: Number of top results to return (None for all).
        """
        self.model = model
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        self.top_n = top_n
        self._client = None

        if not self.api_key:
            raise APIKeyMissingError(
                "API key for Cohere is missing. " "Set the COHERE_API_KEY environment variable."
            )

    def _get_client(self):
        """Get or create Cohere client."""
        if self._client is None:
            try:
                import cohere
            except ImportError:
                raise ImportError(
                    "cohere is required for CohereRerankEmbedder. "
                    "Install it with: pip install cohere"
                )
            self._client = cohere.Client(self.api_key)
        return self._client

    @property
    def dimension(self) -> int:
        """Reranker doesn't produce embeddings."""
        return 0

    def embed(self, texts: list[str]) -> EmbeddingResult:
        """Not implemented for reranker."""
        raise NotImplementedError(
            "CohereRerankEmbedder is for reranking, not embedding. Use rerank() method."
        )

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_n: Optional[int] = None,
    ) -> list[dict]:
        """
        Rerank documents by relevance to query.

        Args:
            query: The search query.
            documents: List of documents to rerank.
            top_n: Number of top results to return (overrides init setting).

        Returns:
            List of dicts with 'index', 'relevance_score', and 'document'.
        """
        if not documents:
            return []

        client = self._get_client()
        top_n = top_n or self.top_n or len(documents)

        try:
            response = client.rerank(
                query=query,
                documents=documents,
                model=self.model,
                top_n=top_n,
            )

            results = []
            for r in response.results:
                results.append(
                    {
                        "index": r.index,
                        "relevance_score": r.relevance_score,
                        "document": documents[r.index],
                    }
                )

            return results

        except Exception as e:
            raise EmbedderError(f"Cohere rerank failed: {e}") from e
