"""Anthropic Claude generator."""

from __future__ import annotations

import os
import time
from typing import Any

from prompt_amplifier.core.exceptions import APIKeyMissingError, GeneratorError
from prompt_amplifier.generators.base import BaseGenerator, GenerationResult


class AnthropicGenerator(BaseGenerator):
    """
    Anthropic Claude generator for prompt expansion.

    Supports Claude 3 family: Opus, Sonnet, Haiku.

    Example:
        >>> generator = AnthropicGenerator(model="claude-3-haiku-20240307")
        >>> result = generator.generate("Expand this prompt", context="...")
        >>> print(result.content)

    Args:
        model: Claude model name (default: claude-3-haiku-20240307)
        api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum output tokens
    """

    def __init__(
        self,
        model: str = "claude-3-haiku-20240307",
        api_key: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ):
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise APIKeyMissingError("Anthropic", "ANTHROPIC_API_KEY")

        self._client = None

    def _get_client(self) -> Any:
        """Get or create Anthropic client."""
        if self._client is None:
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "anthropic is required for AnthropicGenerator. "
                    "Install it with: pip install anthropic"
                )

            self._client = anthropic.Anthropic(api_key=self.api_key)

        return self._client

    def generate(
        self,
        prompt: str,
        context: str | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """
        Generate expanded prompt using Claude.

        Args:
            prompt: The user's original prompt
            context: Retrieved context to include
            system_prompt: Custom system instructions
            **kwargs: Additional generation parameters

        Returns:
            GenerationResult with expanded prompt
        """
        client = self._get_client()
        start_time = time.time()

        # Build the full prompt
        if context:
            full_prompt = f"CONTEXT:\n{context}\n\nUSER PROMPT:\n{prompt}"
        else:
            full_prompt = prompt

        # Use default system prompt if not provided
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                system=system_prompt,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=kwargs.get("temperature", self.temperature),
            )
        except Exception as e:
            raise GeneratorError(f"Anthropic generation failed: {e}")

        generation_time = (time.time() - start_time) * 1000

        content = response.content[0].text if response.content else ""

        return GenerationResult(
            content=content,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            generation_time_ms=generation_time,
            finish_reason=response.stop_reason,
        )

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for expansion."""
        return """You are an expert prompt engineer. Your task is to transform brief user inputs into comprehensive, well-structured prompts.

When expanding a prompt:
1. Add a clear GOAL statement
2. Include relevant CONTEXT from the provided information
3. Define specific SECTIONS to cover
4. Provide detailed INSTRUCTIONS
5. Specify the expected OUTPUT FORMAT

Make the expanded prompt actionable and specific. Include tables, lists, and structure where appropriate."""

    @property
    def supports_streaming(self) -> bool:
        """Whether this generator supports streaming."""
        return True

