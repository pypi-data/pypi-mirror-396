"""OpenAI LLM generator."""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from typing import Any

from prompt_amplifier.core.exceptions import APIKeyMissingError, GeneratorError
from prompt_amplifier.generators.base import BaseGenerator, GenerationResult


class OpenAIGenerator(BaseGenerator):
    """
    OpenAI GPT generator.

    Requires: openai

    Example:
        >>> generator = OpenAIGenerator(model="gpt-4o-mini")
        >>> result = generator.generate("Expand this prompt", system_prompt="...")
        >>> print(result.content)
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        base_url: str | None = None,
        **kwargs: Any,
    ):
        """
        Initialize OpenAI generator.

        Args:
            model: Model name (gpt-4o, gpt-4o-mini, gpt-4-turbo, etc.)
            api_key: API key (or set OPENAI_API_KEY env var)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            base_url: Custom API base URL (for proxies/Azure)
        """
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise APIKeyMissingError("OpenAI", "OPENAI_API_KEY")

        self.base_url = base_url
        self._client = None

    def _get_client(self) -> Any:
        """Get or create OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError(
                    "openai is required for OpenAIGenerator. " "Install it with: pip install openai"
                )

            kwargs: dict[str, Any] = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url

            self._client = OpenAI(**kwargs)

        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """
        Generate completion using OpenAI.

        Args:
            prompt: User message
            system_prompt: System instructions
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            GenerationResult with generated text
        """
        client = self._get_client()
        start_time = time.time()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
        except Exception as e:
            raise GeneratorError(f"OpenAI generation failed: {e}")

        generation_time = (time.time() - start_time) * 1000

        choice = response.choices[0]
        usage = response.usage

        return GenerationResult(
            content=choice.message.content or "",
            model=response.model,
            input_tokens=usage.prompt_tokens if usage else None,
            output_tokens=usage.completion_tokens if usage else None,
            total_tokens=usage.total_tokens if usage else None,
            generation_time_ms=generation_time,
            finish_reason=choice.finish_reason,
        )

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Stream generation."""
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                stream=True,
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise GeneratorError(f"OpenAI streaming failed: {e}")

    @property
    def supports_streaming(self) -> bool:
        return True


class AnthropicGenerator(BaseGenerator):
    """
    Anthropic Claude generator.

    Requires: anthropic

    Example:
        >>> generator = AnthropicGenerator(model="claude-3-haiku-20240307")
        >>> result = generator.generate("Expand this prompt")
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
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """Generate completion using Claude."""
        client = self._get_client()
        start_time = time.time()

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
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

    @property
    def supports_streaming(self) -> bool:
        return True


class GeminiGenerator(BaseGenerator):
    """
    Google Gemini generator.

    Requires: google-generativeai

    Example:
        >>> generator = GeminiGenerator(model="gemini-1.5-flash")
        >>> result = generator.generate("Expand this prompt")
    """

    def __init__(
        self,
        model: str = "gemini-1.5-flash",
        api_key: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ):
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise APIKeyMissingError("Google", "GOOGLE_API_KEY")

        self._model = None

    def _get_model(self) -> Any:
        """Get or create Gemini model."""
        if self._model is None:
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError(
                    "google-generativeai is required for GeminiGenerator. "
                    "Install it with: pip install google-generativeai"
                )

            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model)

        return self._model

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """Generate completion using Gemini."""
        model = self._get_model()
        start_time = time.time()

        # Combine system and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        try:
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": kwargs.get("temperature", self.temperature),
                    "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
                },
            )
        except Exception as e:
            raise GeneratorError(f"Gemini generation failed: {e}")

        generation_time = (time.time() - start_time) * 1000

        return GenerationResult(
            content=response.text,
            model=self.model,
            generation_time_ms=generation_time,
        )
