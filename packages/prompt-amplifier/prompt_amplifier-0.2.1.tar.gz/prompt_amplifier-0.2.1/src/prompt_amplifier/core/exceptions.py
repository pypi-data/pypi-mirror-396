"""Custom exceptions for PromptForge."""

from __future__ import annotations


class PromptForgeError(Exception):
    """Base exception for all PromptForge errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class LoaderError(PromptForgeError):
    """Error during document loading."""

    pass


class ChunkerError(PromptForgeError):
    """Error during text chunking."""

    pass


class EmbedderError(PromptForgeError):
    """Error during embedding generation."""

    pass


class VectorStoreError(PromptForgeError):
    """Error during vector store operations."""

    pass


class RetrieverError(PromptForgeError):
    """Error during retrieval operations."""

    pass


class GeneratorError(PromptForgeError):
    """Error during LLM generation."""

    pass


class ConfigurationError(PromptForgeError):
    """Error in configuration."""

    pass


class SchemaError(PromptForgeError):
    """Error in schema loading or validation."""

    pass


class DocumentNotFoundError(PromptForgeError):
    """Document not found in store."""

    pass


class EmbeddingDimensionMismatchError(EmbedderError):
    """Embedding dimensions don't match."""

    def __init__(self, expected: int, got: int):
        super().__init__(
            f"Embedding dimension mismatch: expected {expected}, got {got}",
            details={"expected": expected, "got": got},
        )
        self.expected = expected
        self.got = got


class APIKeyMissingError(ConfigurationError):
    """Required API key is missing."""

    def __init__(self, provider: str, env_var: str):
        super().__init__(
            f"API key for {provider} is missing. Set the {env_var} environment variable.",
            details={"provider": provider, "env_var": env_var},
        )
        self.provider = provider
        self.env_var = env_var


class ModelNotFoundError(PromptForgeError):
    """Requested model not found."""

    def __init__(self, model: str, provider: str):
        super().__init__(
            f"Model '{model}' not found for provider '{provider}'",
            details={"model": model, "provider": provider},
        )
        self.model = model
        self.provider = provider


class RateLimitError(PromptForgeError):
    """API rate limit exceeded."""

    def __init__(self, provider: str, retry_after: float | None = None):
        message = f"Rate limit exceeded for {provider}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message, details={"provider": provider, "retry_after": retry_after})
        self.provider = provider
        self.retry_after = retry_after
