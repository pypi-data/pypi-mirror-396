"""Embedding providers for vectorization."""

from __future__ import annotations

from prompt_amplifier.embedders.base import BaseEmbedder, BaseSparseEmbedder

# Always available (uses sklearn)
from prompt_amplifier.embedders.tfidf import TFIDFEmbedder

__all__ = [
    "BaseEmbedder",
    "BaseSparseEmbedder",
    "TFIDFEmbedder",
]

# Optional embedders - Sparse
try:
    from prompt_amplifier.embedders.tfidf import BM25Embedder

    __all__.append("BM25Embedder")
except ImportError:
    pass

# Optional embedders - Local Dense
try:
    from prompt_amplifier.embedders.sentence_transformers import SentenceTransformerEmbedder

    __all__.append("SentenceTransformerEmbedder")
except ImportError:
    pass

try:
    from prompt_amplifier.embedders.sentence_transformers import FastEmbedEmbedder

    __all__.append("FastEmbedEmbedder")
except ImportError:
    pass

# Optional embedders - OpenAI
try:
    from prompt_amplifier.embedders.openai import OpenAIEmbedder

    __all__.append("OpenAIEmbedder")
except ImportError:
    pass

# Optional embedders - Cohere
try:
    from prompt_amplifier.embedders.cohere import CohereEmbedder

    __all__.append("CohereEmbedder")
except ImportError:
    pass

try:
    from prompt_amplifier.embedders.cohere import CohereRerankEmbedder

    __all__.append("CohereRerankEmbedder")
except ImportError:
    pass

# Optional embedders - Voyage AI
try:
    from prompt_amplifier.embedders.voyage import VoyageEmbedder

    __all__.append("VoyageEmbedder")
except ImportError:
    pass

# Optional embedders - Jina AI
try:
    from prompt_amplifier.embedders.voyage import JinaEmbedder

    __all__.append("JinaEmbedder")
except ImportError:
    pass

# Optional embedders - Mistral AI
try:
    from prompt_amplifier.embedders.voyage import MistralEmbedder

    __all__.append("MistralEmbedder")
except ImportError:
    pass

# Optional embedders - Google
try:
    from prompt_amplifier.embedders.google import GoogleEmbedder

    __all__.append("GoogleEmbedder")
except ImportError:
    pass

try:
    from prompt_amplifier.embedders.google import VertexAIEmbedder

    __all__.append("VertexAIEmbedder")
except ImportError:
    pass
