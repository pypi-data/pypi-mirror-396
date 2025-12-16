"""Configuration management for PromptForge."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Literal, Optional


@dataclass
class ChunkerConfig:
    """Configuration for text chunking."""

    strategy: Literal["fixed", "sentence", "paragraph", "recursive", "semantic"] = "recursive"
    chunk_size: int = 1000  # characters
    chunk_overlap: int = 200  # characters

    # For sentence/paragraph chunking
    min_chunk_size: int = 100
    max_chunk_size: int = 2000

    # For semantic chunking
    semantic_threshold: float = 0.5


@dataclass
class EmbedderConfig:
    """Configuration for embedding generation."""

    provider: Literal["tfidf", "bm25", "sentence-transformers", "openai", "cohere", "google"] = (
        "tfidf"
    )
    model: str = ""  # Model name (provider-specific)

    # API settings
    api_key: Optional[str] = None
    batch_size: int = 100

    # For TF-IDF/BM25
    max_features: int = 50000
    ngram_range: tuple[int, int] = (1, 2)

    def __post_init__(self) -> None:
        """Set default models and load API keys from environment."""
        if not self.model:
            self.model = self._default_model()

        if not self.api_key:
            self.api_key = self._load_api_key()

    def _default_model(self) -> str:
        """Get default model for provider."""
        defaults = {
            "tfidf": "tfidf",
            "bm25": "bm25",
            "sentence-transformers": "all-MiniLM-L6-v2",
            "openai": "text-embedding-3-small",
            "cohere": "embed-english-v3.0",
            "google": "text-embedding-004",
        }
        return defaults.get(self.provider, "")

    def _load_api_key(self) -> Optional[str]:
        """Load API key from environment variable."""
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "cohere": "COHERE_API_KEY",
            "google": "GOOGLE_API_KEY",
        }
        env_var = env_vars.get(self.provider)
        return os.getenv(env_var) if env_var else None


@dataclass
class VectorStoreConfig:
    """Configuration for vector storage."""

    provider: Literal["memory", "chroma", "faiss", "lancedb", "pinecone", "qdrant", "weaviate"] = (
        "memory"
    )

    # Persistence
    persist_directory: Optional[str] = None
    collection_name: str = "prompt_amplifier"

    # Cloud settings
    api_key: Optional[str] = None
    environment: Optional[str] = None  # For Pinecone
    url: Optional[str] = None  # For Qdrant cloud, Weaviate

    # Index settings
    index_type: str = "flat"  # For FAISS: flat, ivf, hnsw
    metric: Literal["cosine", "euclidean", "dot"] = "cosine"

    def __post_init__(self) -> None:
        """Load API keys from environment."""
        if not self.api_key:
            self.api_key = self._load_api_key()

    def _load_api_key(self) -> Optional[str]:
        """Load API key from environment variable."""
        env_vars = {
            "pinecone": "PINECONE_API_KEY",
            "qdrant": "QDRANT_API_KEY",
            "weaviate": "WEAVIATE_API_KEY",
        }
        env_var = env_vars.get(self.provider)
        return os.getenv(env_var) if env_var else None


@dataclass
class RetrieverConfig:
    """Configuration for retrieval."""

    strategy: Literal["vector", "keyword", "hybrid", "mmr"] = "vector"
    top_k: int = 10

    # For hybrid search
    keyword_weight: float = 0.3
    vector_weight: float = 0.7

    # For MMR (Maximal Marginal Relevance)
    mmr_lambda: float = 0.5  # Balance between relevance and diversity

    # Reranking
    use_reranker: bool = False
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_top_k: int = 5  # Final results after reranking


@dataclass
class GeneratorConfig:
    """Configuration for LLM generation."""

    provider: Literal["openai", "anthropic", "google", "ollama", "huggingface"] = "openai"
    model: str = ""

    # API settings
    api_key: Optional[str] = None
    base_url: Optional[str] = None  # For Ollama, custom endpoints

    # Generation parameters
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0

    # System prompt
    system_prompt: Optional[str] = None

    def __post_init__(self) -> None:
        """Set default models and load API keys."""
        if not self.model:
            self.model = self._default_model()

        if not self.api_key:
            self.api_key = self._load_api_key()

    def _default_model(self) -> str:
        """Get default model for provider."""
        defaults = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-haiku-20240307",
            "google": "gemini-2.0-flash",
            "ollama": "llama3.2",
            "huggingface": "meta-llama/Llama-3.2-3B-Instruct",
        }
        return defaults.get(self.provider, "")

    def _load_api_key(self) -> Optional[str]:
        """Load API key from environment variable."""
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
        }
        env_var = env_vars.get(self.provider)
        return os.getenv(env_var) if env_var else None


@dataclass
class PromptForgeConfig:
    """
    Main configuration for PromptForge.

    Example:
        >>> config = PromptForgeConfig(
        ...     embedder=EmbedderConfig(provider="openai"),
        ...     vectorstore=VectorStoreConfig(provider="chroma", persist_directory="./db"),
        ...     generator=GeneratorConfig(provider="openai", model="gpt-4o"),
        ... )
        >>> forge = PromptForge(config=config)
    """

    chunker: ChunkerConfig = field(default_factory=ChunkerConfig)
    embedder: EmbedderConfig = field(default_factory=EmbedderConfig)
    vectorstore: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    retriever: RetrieverConfig = field(default_factory=RetrieverConfig)
    generator: GeneratorConfig = field(default_factory=GeneratorConfig)

    # Schema path (optional)
    schema_path: Optional[str] = None

    # Logging
    verbose: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PromptForgeConfig:
        """Create config from dictionary."""
        return cls(
            chunker=ChunkerConfig(**data.get("chunker", {})),
            embedder=EmbedderConfig(**data.get("embedder", {})),
            vectorstore=VectorStoreConfig(**data.get("vectorstore", {})),
            retriever=RetrieverConfig(**data.get("retriever", {})),
            generator=GeneratorConfig(**data.get("generator", {})),
            schema_path=data.get("schema_path"),
            verbose=data.get("verbose", False),
            log_level=data.get("log_level", "INFO"),
        )

    @classmethod
    def from_yaml(cls, path: str) -> PromptForgeConfig:
        """Load config from YAML file."""
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        from dataclasses import asdict

        return asdict(self)
