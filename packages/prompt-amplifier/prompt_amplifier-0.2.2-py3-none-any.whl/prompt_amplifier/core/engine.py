"""Main PromptForge engine - orchestrates the prompt expansion pipeline."""

from __future__ import annotations

import logging
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from prompt_amplifier.cache.base import BaseCache, CacheConfig, generate_cache_key
from prompt_amplifier.cache.memory import MemoryCache
from prompt_amplifier.chunkers.base import BaseChunker
from prompt_amplifier.core.config import PromptForgeConfig
from prompt_amplifier.core.exceptions import ConfigurationError, EmbedderError
from prompt_amplifier.embedders.base import BaseEmbedder
from prompt_amplifier.generators.base import BaseGenerator
from prompt_amplifier.loaders.base import BaseLoader, DirectoryLoader
from prompt_amplifier.models.document import Chunk, Document
from prompt_amplifier.models.result import ExpandResult, SearchResults
from prompt_amplifier.retrievers.base import BaseRetriever
from prompt_amplifier.vectorstores.base import BaseVectorStore

# Configure module logger
logger = logging.getLogger("prompt_amplifier")

# Constants for validation
MAX_PROMPT_LENGTH = 100000
MIN_DOCUMENTS_FOR_TFIDF = 2

# Default system prompt for prompt expansion
DEFAULT_SYSTEM_PROMPT = """You are an AI Prompt Assistant. Your job is to transform a short user intent
into a complete, structured prompt instruction that another AI will later use to generate output.
Do NOT generate the final output yourself - only generate the detailed prompt.

Core principles:
- Interpret the user's goal and identify relevant data fields/categories
- Output a clear, structured prompt with sections, tables, and explicit requirements
- Keep language concise and actionable
- Keep internal reasoning private. Only output the final prompt instruction.

The detailed prompt should:
1) State the GOAL succinctly
2) List REQUIRED SECTIONS with headings
3) Specify any TABLES with exact column names
4) Name the key fields/categories to pull from
5) Include brief interpretation instructions
6) Be directly usable as an instruction for another AI"""


class PromptForge:
    """
    Main class for prompt expansion.

    PromptForge transforms short, ambiguous user prompts into detailed,
    structured instructions by leveraging domain context from documents.

    Example:
        >>> forge = PromptForge()
        >>> forge.load_documents("./docs/")
        >>> result = forge.expand("How's the deal going?")
        >>> print(result.prompt)

    Example with custom components:
        >>> from prompt_amplifier.embedders import OpenAIEmbedder
        >>> from prompt_amplifier.vectorstores import ChromaStore
        >>>
        >>> forge = PromptForge(
        ...     embedder=OpenAIEmbedder(model="text-embedding-3-small"),
        ...     vectorstore=ChromaStore(persist_directory="./db"),
        ... )
    """

    def __init__(
        self,
        config: PromptForgeConfig | None = None,
        *,
        # Component overrides (take precedence over config)
        loader: BaseLoader | None = None,
        chunker: BaseChunker | None = None,
        embedder: BaseEmbedder | None = None,
        vectorstore: BaseVectorStore | None = None,
        retriever: BaseRetriever | None = None,
        generator: BaseGenerator | None = None,
        # Caching options
        cache: BaseCache | None = None,
        cache_config: CacheConfig | None = None,
        enable_cache: bool = True,
    ):
        """
        Initialize PromptForge.

        Args:
            config: Configuration object (optional)
            loader: Document loader (optional override)
            chunker: Text chunker (optional override)
            embedder: Embedding provider (optional override)
            vectorstore: Vector store (optional override)
            retriever: Retriever (optional override)
            generator: LLM generator (optional override)
            cache: Custom cache implementation (optional)
            cache_config: Cache configuration (optional)
            enable_cache: Enable/disable caching (default: True)
        """
        self.config = config or PromptForgeConfig()

        # Initialize components (lazy loading for optional deps)
        self._loader = loader
        self._chunker = chunker
        self._embedder = embedder
        self._vectorstore = vectorstore
        self._retriever = retriever
        self._generator = generator

        # Initialize cache
        if enable_cache:
            if cache is not None:
                self._cache = cache
            else:
                cache_cfg = cache_config or CacheConfig()
                self._cache = MemoryCache(cache_cfg)
            logger.debug(f"Caching enabled: {type(self._cache).__name__}")
        else:
            self._cache = None
            logger.debug("Caching disabled")

        # Track loaded documents
        self._documents: list[Document] = []
        self._chunks: list[Chunk] = []
        self._initialized = False

    @property
    def loader(self) -> BaseLoader:
        """Get or create the document loader."""
        if self._loader is None:
            self._loader = self._create_default_loader()
        return self._loader

    @property
    def chunker(self) -> BaseChunker:
        """Get or create the chunker."""
        if self._chunker is None:
            self._chunker = self._create_default_chunker()
        return self._chunker

    @property
    def embedder(self) -> BaseEmbedder:
        """Get or create the embedder."""
        if self._embedder is None:
            self._embedder = self._create_default_embedder()
        return self._embedder

    @property
    def vectorstore(self) -> BaseVectorStore:
        """Get or create the vector store."""
        if self._vectorstore is None:
            self._vectorstore = self._create_default_vectorstore()
        return self._vectorstore

    @property
    def retriever(self) -> BaseRetriever:
        """Get or create the retriever."""
        if self._retriever is None:
            self._retriever = self._create_default_retriever()
        return self._retriever

    @property
    def generator(self) -> BaseGenerator:
        """Get or create the LLM generator."""
        if self._generator is None:
            self._generator = self._create_default_generator()
        return self._generator

    def _create_default_loader(self) -> BaseLoader:
        """Create default directory loader with all available loaders."""
        # Import concrete loaders here to avoid circular imports
        # and allow optional dependencies

        loaders: list[BaseLoader] = []

        # Try to import each loader, skip if deps missing
        try:
            from prompt_amplifier.loaders.txt import TxtLoader

            loaders.append(TxtLoader())
        except ImportError:
            pass

        try:
            from prompt_amplifier.loaders.csv import CSVLoader

            loaders.append(CSVLoader())
        except ImportError:
            pass

        try:
            from prompt_amplifier.loaders.docx import DocxLoader

            loaders.append(DocxLoader())
        except ImportError:
            pass

        try:
            from prompt_amplifier.loaders.excel import ExcelLoader

            loaders.append(ExcelLoader())
        except ImportError:
            pass

        try:
            from prompt_amplifier.loaders.pdf import PDFLoader

            loaders.append(PDFLoader())
        except ImportError:
            pass

        return DirectoryLoader(loaders=loaders)

    def _create_default_chunker(self) -> BaseChunker:
        """Create default chunker based on config."""
        from prompt_amplifier.chunkers.recursive import RecursiveChunker

        cfg = self.config.chunker
        return RecursiveChunker(
            chunk_size=cfg.chunk_size,
            chunk_overlap=cfg.chunk_overlap,
        )

    def _create_default_embedder(self) -> BaseEmbedder:
        """Create default embedder based on config."""
        cfg = self.config.embedder

        if cfg.provider == "tfidf":
            from prompt_amplifier.embedders.tfidf import TFIDFEmbedder

            return TFIDFEmbedder(
                max_features=cfg.max_features,
                ngram_range=cfg.ngram_range,
            )
        elif cfg.provider == "sentence-transformers":
            from prompt_amplifier.embedders.sentence_transformers import SentenceTransformerEmbedder

            return SentenceTransformerEmbedder(model=cfg.model)
        elif cfg.provider == "openai":
            from prompt_amplifier.embedders.openai import OpenAIEmbedder

            return OpenAIEmbedder(model=cfg.model, api_key=cfg.api_key)
        else:
            # Default to TF-IDF (no external deps)
            from prompt_amplifier.embedders.tfidf import TFIDFEmbedder

            return TFIDFEmbedder()

    def _create_default_vectorstore(self) -> BaseVectorStore:
        """Create default vector store based on config."""
        cfg = self.config.vectorstore

        if cfg.provider == "memory":
            from prompt_amplifier.vectorstores.memory import MemoryStore

            return MemoryStore(collection_name=cfg.collection_name)
        elif cfg.provider == "chroma":
            from prompt_amplifier.vectorstores.chroma import ChromaStore

            return ChromaStore(
                collection_name=cfg.collection_name,
                persist_directory=cfg.persist_directory,
            )
        elif cfg.provider == "faiss":
            from prompt_amplifier.vectorstores.faiss import FAISSStore

            return FAISSStore(
                collection_name=cfg.collection_name,
                persist_directory=cfg.persist_directory,
            )
        else:
            # Default to in-memory
            from prompt_amplifier.vectorstores.memory import MemoryStore

            return MemoryStore(collection_name=cfg.collection_name)

    def _create_default_retriever(self) -> BaseRetriever:
        """Create default retriever based on config."""
        from prompt_amplifier.retrievers.vector import VectorRetriever

        cfg = self.config.retriever
        return VectorRetriever(
            embedder=self.embedder,
            vectorstore=self.vectorstore,
            top_k=cfg.top_k,
        )

    def _create_default_generator(self) -> BaseGenerator:
        """Create default generator based on config."""
        cfg = self.config.generator

        if cfg.provider == "openai":
            from prompt_amplifier.generators.openai import OpenAIGenerator

            return OpenAIGenerator(
                model=cfg.model,
                api_key=cfg.api_key,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
        elif cfg.provider == "anthropic":
            from prompt_amplifier.generators.anthropic import AnthropicGenerator

            return AnthropicGenerator(
                model=cfg.model,
                api_key=cfg.api_key,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
        elif cfg.provider == "google":
            from prompt_amplifier.generators.google import GoogleGenerator

            return GoogleGenerator(
                model=cfg.model,
                api_key=cfg.api_key,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
        elif cfg.provider == "ollama":
            from prompt_amplifier.generators.ollama import OllamaGenerator

            return OllamaGenerator(
                model=cfg.model,
                base_url=cfg.base_url,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
        else:
            raise ConfigurationError(
                f"Unknown generator provider: {cfg.provider}", details={"provider": cfg.provider}
            )

    def load_documents(
        self,
        source: str | Path,
        loader: BaseLoader | None = None,
    ) -> int:
        """
        Load documents from a source.

        Args:
            source: File or directory path
            loader: Optional specific loader (uses default if None)

        Returns:
            Number of documents loaded

        Raises:
            ValueError: If source path doesn't exist
            FileNotFoundError: If no documents found in directory
        """
        # Input validation
        if not source:
            raise ValueError("Source path cannot be empty")
        
        loader = loader or self.loader
        path = Path(source)

        logger.info(f"Loading documents from: {path}")

        if path.is_dir():
            docs = loader.load(path)
            if not docs:
                raise FileNotFoundError(
                    f"No documents found in directory: {path}. "
                    f"Supported formats: .txt, .pdf, .docx, .csv, .json, .xlsx"
                )
        elif path.is_file():
            docs = loader.load(path)
            if not docs:
                raise ValueError(f"Failed to load document: {path}")
        else:
            raise FileNotFoundError(
                f"Source not found: {source}. "
                f"Please provide a valid file or directory path."
            )

        logger.info(f"Loaded {len(docs)} documents")
        self._documents.extend(docs)

        # Chunk documents
        chunks = self.chunker.chunk_documents(docs)
        self._chunks.extend(chunks)
        logger.debug(f"Created {len(chunks)} chunks")

        # Embed and store chunks
        if chunks:
            self._embed_and_store(chunks)

        self._initialized = True
        return len(docs)

    def add_texts(
        self,
        texts: Sequence[str],
        source: str = "manual",
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """
        Add raw texts directly.

        Args:
            texts: List of text strings
            source: Source identifier
            metadata: Optional metadata for all texts

        Returns:
            Number of chunks created

        Raises:
            ValueError: If texts is empty or contains only empty strings
        """
        # Input validation
        if not texts:
            raise ValueError("texts cannot be empty")
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("All provided texts are empty")
        
        if len(valid_texts) < len(texts):
            logger.warning(
                f"Filtered out {len(texts) - len(valid_texts)} empty texts"
            )
        
        logger.info(f"Adding {len(valid_texts)} texts from source: {source}")
        
        docs = [
            Document(
                content=text,
                source=source,
                source_type="text",
                metadata=metadata or {},
            )
            for text in valid_texts
        ]

        self._documents.extend(docs)

        # Chunk and store
        chunks = self.chunker.chunk_documents(docs)
        self._chunks.extend(chunks)
        
        logger.debug(f"Created {len(chunks)} chunks from {len(docs)} documents")

        if chunks:
            self._embed_and_store(chunks)

        self._initialized = True
        return len(chunks)

    def _embed_and_store(self, chunks: list[Chunk]) -> None:
        """
        Embed chunks and add to vector store.

        Handles sparse embedders (TF-IDF, BM25) that need fitting.

        Raises:
            EmbedderError: If embedding fails (e.g., too few documents for TF-IDF)
        """
        from prompt_amplifier.embedders.base import BaseSparseEmbedder

        logger.debug(f"Embedding {len(chunks)} chunks with {type(self.embedder).__name__}")

        # Check if embedder needs fitting (sparse embedders like TF-IDF)
        if isinstance(self.embedder, BaseSparseEmbedder):
            if not self.embedder.is_fitted:
                # Fit on all chunks we have
                all_texts = [c.content for c in self._chunks]
                
                # Validate minimum documents for TF-IDF
                if len(all_texts) < MIN_DOCUMENTS_FOR_TFIDF:
                    raise EmbedderError(
                        f"TF-IDF requires at least {MIN_DOCUMENTS_FOR_TFIDF} documents, "
                        f"but only {len(all_texts)} provided. "
                        f"Either add more documents or use a dense embedder like "
                        f"SentenceTransformerEmbedder which works with any number of documents."
                    )
                
                try:
                    self.embedder.fit(all_texts)
                    logger.debug(f"Fitted sparse embedder on {len(all_texts)} texts")
                except ValueError as e:
                    # Catch sklearn errors and provide helpful message
                    raise EmbedderError(
                        f"Failed to fit embedder: {e}. "
                        f"Try adding more documents or using SentenceTransformerEmbedder."
                    ) from e

        # Now embed the chunks
        try:
            self.embedder.embed_chunks(chunks)
            self.vectorstore.add(chunks)
            logger.debug(f"Successfully stored {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Failed to embed/store chunks: {e}")
            raise

    def expand(
        self,
        short_prompt: str,
        top_k: int | None = None,
        system_prompt: str | None = None,
        use_cache: bool = True,
    ) -> ExpandResult:
        """
        Expand a short prompt into a detailed, structured prompt.

        Args:
            short_prompt: The short user prompt to expand
            top_k: Number of context chunks to retrieve
            system_prompt: Custom system prompt (uses default if None)
            use_cache: Whether to use cached results (default: True)

        Returns:
            ExpandResult with the expanded prompt and metadata

        Raises:
            ValueError: If prompt is empty or too long
            ConfigurationError: If no documents loaded and context is required
        """
        # Input validation
        if not short_prompt:
            raise ValueError("Prompt cannot be empty")
        
        short_prompt = short_prompt.strip()
        if not short_prompt:
            raise ValueError("Prompt cannot be only whitespace")
        
        if len(short_prompt) > MAX_PROMPT_LENGTH:
            raise ValueError(
                f"Prompt too long: {len(short_prompt)} characters "
                f"(maximum: {MAX_PROMPT_LENGTH})"
            )

        top_k = top_k or self.config.retriever.top_k
        
        # Check cache for expansion results
        cache_key = None
        if use_cache and self._cache and self._cache.config.cache_generations:
            cache_key = generate_cache_key(
                short_prompt, 
                top_k, 
                system_prompt or "default",
                self.vectorstore.count,
                prefix="expand"
            )
            cached_result = self._cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache HIT for prompt: '{short_prompt[:30]}...'")
                cached_result.metadata["cache_hit"] = True
                return cached_result

        logger.info(f"Expanding prompt: '{short_prompt[:50]}{'...' if len(short_prompt) > 50 else ''}'")
        logger.debug(f"Using embedder: {type(self.embedder).__name__}")
        logger.debug(f"Using generator: {type(self.generator).__name__}")
        
        start_time = time.time()

        # Retrieve relevant context
        retrieval_start = time.time()

        if self._initialized and self.vectorstore.count > 0:
            results = self.retriever.retrieve(short_prompt, top_k=top_k)
            context_chunks = results.chunks
        else:
            results = SearchResults(results=[], query=short_prompt)
            context_chunks = []

        retrieval_time = (time.time() - retrieval_start) * 1000

        # Build prompt with context
        context_text = self._format_context(context_chunks)

        expansion_prompt = f"""# USER REQUEST
Short prompt: "{short_prompt}"

# RETRIEVED CONTEXT
{context_text if context_text else "(No context available)"}

# TASK
Transform the short prompt above into a detailed, structured prompt instruction.
The output should be a complete prompt that another AI can use to generate the actual response.

Output ONLY the detailed prompt - no explanations or meta-commentary."""

        # Generate expanded prompt
        generation_start = time.time()
        gen_result = self.generator.generate(
            prompt=expansion_prompt,
            system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT,
        )
        generation_time = (time.time() - generation_start) * 1000

        total_time = (time.time() - start_time) * 1000

        logger.info(
            f"Expansion complete: {len(gen_result.content)} chars, "
            f"{total_time:.0f}ms total ({retrieval_time:.0f}ms retrieval, "
            f"{generation_time:.0f}ms generation)"
        )

        result = ExpandResult(
            prompt=gen_result.content,
            original_prompt=short_prompt,
            context_chunks=context_chunks,
            retrieval_time_ms=retrieval_time,
            generation_time_ms=generation_time,
            total_time_ms=total_time,
            input_tokens=gen_result.input_tokens,
            output_tokens=gen_result.output_tokens,
            total_tokens=gen_result.total_tokens,
            metadata={
                "model": gen_result.model,
                "top_k": top_k,
                "context_count": len(context_chunks),
                "cache_hit": False,
            },
        )
        
        # Store in cache
        if cache_key and self._cache:
            self._cache.set(cache_key, result)
            logger.debug(f"Cached expansion result for key: {cache_key}")
        
        return result

    def _format_context(self, chunks: list[Chunk]) -> str:
        """Format context chunks for the prompt."""
        if not chunks:
            return ""

        formatted = []
        for i, chunk in enumerate(chunks, 1):
            source = Path(chunk.source).name if chunk.source else "unknown"
            formatted.append(f"[{i}] Source: {source}\n{chunk.content}")

        return "\n\n---\n\n".join(formatted)

    def search(
        self,
        query: str,
        top_k: int | None = None,
        use_cache: bool = True,
    ) -> SearchResults:
        """
        Search for relevant chunks without expanding.

        Useful for debugging retrieval.

        Args:
            query: Search query
            top_k: Number of results
            use_cache: Whether to use cached results (default: True)

        Returns:
            SearchResults with ranked chunks

        Raises:
            ValueError: If query is empty
        """
        # Input validation
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        
        top_k = top_k or self.config.retriever.top_k
        
        # Check cache for search results
        cache_key = None
        if use_cache and self._cache and self._cache.config.cache_searches:
            cache_key = generate_cache_key(
                query, 
                top_k, 
                self.vectorstore.count,
                prefix="search"
            )
            cached_result = self._cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT for search: '{query[:30]}...'")
                return cached_result
        
        logger.debug(f"Searching for: '{query[:50]}...' with top_k={top_k}")
        
        results = self.retriever.retrieve(query, top_k=top_k)
        logger.debug(f"Found {len(results.results)} results")
        
        # Store in cache
        if cache_key and self._cache:
            self._cache.set(cache_key, results)
        
        return results

    @property
    def document_count(self) -> int:
        """Number of loaded documents."""
        return len(self._documents)

    @property
    def chunk_count(self) -> int:
        """Number of chunks in store."""
        return self.vectorstore.count

    @property
    def cache(self) -> BaseCache | None:
        """Get the cache instance."""
        return self._cache

    @property
    def cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self._cache is not None and self._cache.config.enabled

    def get_cache_stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache hit rate, size, etc.
            Returns empty dict if caching is disabled.
        """
        if self._cache is None:
            return {"enabled": False}
        return {
            "enabled": True,
            **self._cache.get_stats(),
        }

    def clear_cache(self) -> int:
        """Clear all cached entries.
        
        Returns:
            Number of entries cleared.
        """
        if self._cache is None:
            return 0
        count = self._cache.clear()
        logger.info(f"Cleared {count} cache entries")
        return count

    def __repr__(self) -> str:
        cache_info = f", cache={'on' if self.cache_enabled else 'off'}"
        return (
            f"PromptForge("
            f"docs={self.document_count}, "
            f"chunks={self.chunk_count}, "
            f"embedder={self.embedder.embedder_name}, "
            f"store={self.vectorstore.store_name}"
            f"{cache_info})"
        )
