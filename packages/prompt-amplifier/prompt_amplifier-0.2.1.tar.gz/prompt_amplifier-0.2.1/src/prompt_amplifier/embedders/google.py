"""Google/Gemini embeddings."""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from typing import Any

from prompt_amplifier.core.exceptions import APIKeyMissingError, EmbedderError
from prompt_amplifier.embedders.base import BaseEmbedder
from prompt_amplifier.models.embedding import EmbeddingResult


class GoogleEmbedder(BaseEmbedder):
    """
    Google/Gemini embeddings API.

    Uses Google's text-embedding models via the Generative AI SDK.

    Models:
        - text-embedding-004: Latest model (768 dims)
        - embedding-001: Legacy model (768 dims)

    Requires: google-generativeai

    Example:
        >>> embedder = GoogleEmbedder(model="text-embedding-004")
        >>> result = embedder.embed(["Hello world"])
    """

    MODEL_DIMENSIONS = {
        "text-embedding-004": 768,
        "embedding-001": 768,
        "models/text-embedding-004": 768,
        "models/embedding-001": 768,
    }

    def __init__(
        self,
        model: str = "text-embedding-004",
        api_key: str | None = None,
        task_type: str = "RETRIEVAL_DOCUMENT",
        batch_size: int = 100,
        **kwargs: Any,
    ):
        """
        Initialize Google embedder.

        Args:
            model: Model name
            api_key: API key (or set GOOGLE_API_KEY env var)
            task_type: Task type for embedding (RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, etc.)
            batch_size: Batch size for API calls
        """
        super().__init__(model=model, **kwargs)

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise APIKeyMissingError("Google", "GOOGLE_API_KEY")

        self.task_type = task_type
        self.batch_size = batch_size
        self._configured = False
        self._dimension = self.MODEL_DIMENSIONS.get(model, 768)

    def _configure(self) -> None:
        """Configure the Google API."""
        if self._configured:
            return

        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai is required for GoogleEmbedder. "
                "Install it with: pip install google-generativeai"
            )

        genai.configure(api_key=self.api_key)
        self._configured = True

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """
        Generate embeddings using Google API.

        Args:
            texts: Texts to embed

        Returns:
            EmbeddingResult with embeddings
        """
        import google.generativeai as genai

        if not texts:
            return EmbeddingResult(
                embeddings=[],
                model=self.model,
                dimension=self.dimension,
            )

        self._configure()
        start_time = time.time()

        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = list(texts[i : i + self.batch_size])

            try:
                # Use embed_content for batch embedding
                result = genai.embed_content(
                    model=(
                        f"models/{self.model}"
                        if not self.model.startswith("models/")
                        else self.model
                    ),
                    content=batch,
                    task_type=self.task_type,
                )

                # Handle both single and batch responses
                if isinstance(result["embedding"][0], list):
                    all_embeddings.extend(result["embedding"])
                else:
                    all_embeddings.append(result["embedding"])

            except Exception as e:
                raise EmbedderError(f"Google embedding failed: {e}")

        embedding_time = (time.time() - start_time) * 1000

        return EmbeddingResult(
            embeddings=all_embeddings,
            model=self.model,
            dimension=self._dimension,
            input_texts=list(texts),
            embedding_time_ms=embedding_time,
        )

    def embed_query(self, query: str) -> list[float]:
        """Embed a search query (uses RETRIEVAL_QUERY task type)."""
        original_type = self.task_type
        self.task_type = "RETRIEVAL_QUERY"
        try:
            result = self.embed([query])
            return result.embeddings[0]
        finally:
            self.task_type = original_type

    @property
    def dimension(self) -> int:
        return self._dimension


class VertexAIEmbedder(BaseEmbedder):
    """
    Vertex AI embeddings (Google Cloud).

    For enterprise/production use with Google Cloud.
    Requires Google Cloud authentication.

    Models:
        - textembedding-gecko@003: 768 dims
        - textembedding-gecko-multilingual@001: 768 dims

    Requires: google-cloud-aiplatform

    Example:
        >>> embedder = VertexAIEmbedder(
        ...     model="textembedding-gecko@003",
        ...     project_id="your-project"
        ... )
    """

    MODEL_DIMENSIONS = {
        "textembedding-gecko@003": 768,
        "textembedding-gecko@002": 768,
        "textembedding-gecko@001": 768,
        "textembedding-gecko-multilingual@001": 768,
        "text-embedding-004": 768,
    }

    def __init__(
        self,
        model: str = "textembedding-gecko@003",
        project_id: str | None = None,
        location: str = "us-central1",
        batch_size: int = 250,
        **kwargs: Any,
    ):
        """
        Initialize Vertex AI embedder.

        Args:
            model: Model name
            project_id: Google Cloud project ID
            location: Google Cloud region
            batch_size: Batch size for API calls
        """
        super().__init__(model=model, **kwargs)

        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.batch_size = batch_size
        self._model = None
        self._dimension = self.MODEL_DIMENSIONS.get(model, 768)

    def _get_model(self) -> Any:
        """Get or create Vertex AI model."""
        if self._model is None:
            try:
                import vertexai
                from vertexai.language_models import TextEmbeddingModel
            except ImportError:
                raise ImportError(
                    "google-cloud-aiplatform is required for VertexAIEmbedder. "
                    "Install it with: pip install google-cloud-aiplatform"
                )

            if self.project_id:
                vertexai.init(project=self.project_id, location=self.location)

            self._model = TextEmbeddingModel.from_pretrained(self.model)

        return self._model

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        """Generate embeddings using Vertex AI."""
        if not texts:
            return EmbeddingResult(
                embeddings=[],
                model=self.model,
                dimension=self.dimension,
            )

        model = self._get_model()
        start_time = time.time()

        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = list(texts[i : i + self.batch_size])

            try:
                embeddings = model.get_embeddings(batch)
                for emb in embeddings:
                    all_embeddings.append(emb.values)
            except Exception as e:
                raise EmbedderError(f"Vertex AI embedding failed: {e}")

        embedding_time = (time.time() - start_time) * 1000

        return EmbeddingResult(
            embeddings=all_embeddings,
            model=self.model,
            dimension=self._dimension,
            input_texts=list(texts),
            embedding_time_ms=embedding_time,
        )

    @property
    def dimension(self) -> int:
        return self._dimension
