"""
Prompt Amplifier - Transform short prompts into detailed, structured instructions.

Usage:
    >>> from prompt_amplifier import PromptForge
    >>> forge = PromptForge()
    >>> forge.load_documents("./docs/")
    >>> result = forge.expand("How's the deal going?")
    >>> print(result.prompt)
"""

from __future__ import annotations

from prompt_amplifier.core.config import PromptForgeConfig
from prompt_amplifier.core.engine import PromptForge
from prompt_amplifier.models.document import Chunk, Document
from prompt_amplifier.models.result import ExpandResult, SearchResult
from prompt_amplifier.version import __version__

__all__ = [
    # Main class
    "PromptForge",
    "PromptForgeConfig",
    # Models
    "Document",
    "Chunk",
    "ExpandResult",
    "SearchResult",
    # Version
    "__version__",
]
