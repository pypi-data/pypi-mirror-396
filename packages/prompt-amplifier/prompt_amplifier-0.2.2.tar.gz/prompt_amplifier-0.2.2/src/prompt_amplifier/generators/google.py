"""Google Gemini generator."""

from __future__ import annotations

import os
import time
from typing import Any

from prompt_amplifier.core.exceptions import APIKeyMissingError, GeneratorError
from prompt_amplifier.generators.base import BaseGenerator, GenerationResult


class GoogleGenerator(BaseGenerator):
    """
    Google Gemini generator for prompt expansion.

    Supports Gemini 1.5 and 2.0 models.

    Example:
        >>> generator = GoogleGenerator(model="gemini-2.0-flash")
        >>> result = generator.generate("Expand this prompt", context="...")
        >>> print(result.content)

    Args:
        model: Gemini model name (default: gemini-2.0-flash)
        api_key: Google API key (or set GOOGLE_API_KEY env var)
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum output tokens
    """

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        api_key: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ):
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise APIKeyMissingError("Google", "GOOGLE_API_KEY")

        self._client = None

    def _get_client(self) -> Any:
        """Get or create Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError(
                    "google-generativeai is required for GoogleGenerator. "
                    "Install it with: pip install google-generativeai"
                )

            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)

        return self._client

    def generate(
        self,
        prompt: str,
        context: str | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """
        Generate expanded prompt using Gemini.

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
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()

        if context:
            full_prompt = f"{system_prompt}\n\nCONTEXT:\n{context}\n\nUSER PROMPT:\n{prompt}\n\nGenerate an expanded, structured prompt:"
        else:
            full_prompt = f"{system_prompt}\n\nUSER PROMPT:\n{prompt}\n\nGenerate an expanded, structured prompt:"

        try:
            response = client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": kwargs.get("temperature", self.temperature),
                    "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
                },
            )
        except Exception as e:
            raise GeneratorError(f"Gemini generation failed: {e}")

        generation_time = (time.time() - start_time) * 1000

        content = response.text if response.text else ""

        # Estimate token counts (Gemini doesn't always provide exact counts)
        input_tokens = len(full_prompt.split()) * 1.3  # Rough estimate
        output_tokens = len(content.split()) * 1.3

        return GenerationResult(
            content=content,
            model=self.model,
            input_tokens=int(input_tokens),
            output_tokens=int(output_tokens),
            total_tokens=int(input_tokens + output_tokens),
            generation_time_ms=generation_time,
            finish_reason="stop",
        )

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for expansion."""
        return """You are an expert prompt engineer. Transform brief user inputs into comprehensive, well-structured prompts.

When expanding a prompt:
1. Add a clear GOAL statement
2. Include relevant CONTEXT from provided information
3. Define specific SECTIONS to cover
4. Provide detailed INSTRUCTIONS
5. Specify expected OUTPUT FORMAT

Make the expanded prompt actionable and specific. Use tables, lists, and clear structure."""

    @property
    def supports_streaming(self) -> bool:
        """Whether this generator supports streaming."""
        return True


# Alias for backward compatibility
GeminiGenerator = GoogleGenerator

