"""LLM generators for prompt expansion."""

from __future__ import annotations

from prompt_amplifier.generators.base import BaseGenerator, GenerationResult

__all__ = [
    "BaseGenerator",
    "GenerationResult",
]

# OpenAI Generator
try:
    from prompt_amplifier.generators.openai import OpenAIGenerator

    __all__.append("OpenAIGenerator")
except ImportError:
    pass

# Anthropic Generator
try:
    from prompt_amplifier.generators.anthropic import AnthropicGenerator

    __all__.append("AnthropicGenerator")
except ImportError:
    pass

# Google/Gemini Generator
try:
    from prompt_amplifier.generators.google import GoogleGenerator, GeminiGenerator

    __all__.append("GoogleGenerator")
    __all__.append("GeminiGenerator")
except ImportError:
    pass

# Ollama Generator (local LLMs)
try:
    from prompt_amplifier.generators.ollama import OllamaGenerator

    __all__.append("OllamaGenerator")
except ImportError:
    pass

# Mistral Generator
try:
    from prompt_amplifier.generators.ollama import MistralGenerator

    __all__.append("MistralGenerator")
except ImportError:
    pass

# Together AI Generator
try:
    from prompt_amplifier.generators.ollama import TogetherGenerator

    __all__.append("TogetherGenerator")
except ImportError:
    pass
