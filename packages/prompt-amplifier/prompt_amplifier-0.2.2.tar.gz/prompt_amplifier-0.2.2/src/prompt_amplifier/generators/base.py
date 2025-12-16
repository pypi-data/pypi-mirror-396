"""Base generator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenerationResult:
    """Result from LLM generation."""

    content: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    generation_time_ms: float = 0.0
    finish_reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"GenerationResult(len={len(self.content)}, "
            f"tokens={self.total_tokens}, "
            f"time={self.generation_time_ms:.1f}ms)"
        )


class BaseGenerator(ABC):
    """
    Abstract base class for all LLM generators.

    Implement this class to add support for new LLM providers.

    Example:
        >>> class MyGenerator(BaseGenerator):
        ...     def generate(self, prompt: str, system_prompt: str | None) -> GenerationResult:
        ...         response = my_llm.chat(prompt, system_prompt)
        ...         return GenerationResult(content=response.text, model="my-model")
    """

    def __init__(
        self,
        model: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ):
        """
        Initialize the generator.

        Args:
            model: Model name/identifier
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific configuration
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.config = kwargs

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """
        Generate a completion for the prompt.

        Args:
            prompt: User prompt/message
            system_prompt: Optional system instructions
            **kwargs: Additional generation parameters

        Returns:
            GenerationResult with the generated text

        Raises:
            GeneratorError: If generation fails
        """
        pass

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """
        Generate a streaming completion.

        Default implementation falls back to non-streaming.
        Override for true streaming support.

        Args:
            prompt: User prompt/message
            system_prompt: Optional system instructions
            **kwargs: Additional generation parameters

        Yields:
            Chunks of generated text
        """
        result = self.generate(prompt, system_prompt, **kwargs)
        yield result.content

    async def agenerate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """
        Async version of generate.

        Default implementation runs sync version.
        Override for true async support.

        Args:
            prompt: User prompt/message
            system_prompt: Optional system instructions
            **kwargs: Additional generation parameters

        Returns:
            GenerationResult with the generated text
        """
        # Default: run sync version
        # Subclasses should override with true async implementation
        return self.generate(prompt, system_prompt, **kwargs)

    async def agenerate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Async streaming generation.

        Default implementation falls back to non-streaming async.
        Override for true async streaming support.

        Args:
            prompt: User prompt/message
            system_prompt: Optional system instructions
            **kwargs: Additional generation parameters

        Yields:
            Chunks of generated text
        """
        result = await self.agenerate(prompt, system_prompt, **kwargs)
        yield result.content

    @property
    def generator_name(self) -> str:
        """Name of this generator."""
        return self.__class__.__name__

    @property
    def supports_streaming(self) -> bool:
        """Whether this generator supports true streaming."""
        return False

    @property
    def supports_async(self) -> bool:
        """Whether this generator supports true async."""
        return False

    def __repr__(self) -> str:
        return (
            f"{self.generator_name}("
            f"model={self.model}, "
            f"temp={self.temperature}, "
            f"max_tokens={self.max_tokens})"
        )
