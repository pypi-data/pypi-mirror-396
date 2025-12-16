"""Ollama generator for local LLM inference."""

from __future__ import annotations

from typing import Optional

from prompt_amplifier.core.exceptions import GeneratorError
from prompt_amplifier.generators.base import BaseGenerator


class OllamaGenerator(BaseGenerator):
    """
    Generator using Ollama for local LLM inference.

    Ollama allows running LLMs locally without API keys:
    - llama3.2: Meta's Llama 3.2
    - mistral: Mistral 7B
    - codellama: Code-optimized Llama
    - phi3: Microsoft's Phi-3

    Example:
        >>> generator = OllamaGenerator(model="llama3.2")
        >>> response = generator.generate(
        ...     prompt="Expand this prompt",
        ...     context="Context information..."
        ... )
        >>> print(response)
    """

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the Ollama generator.

        Args:
            model: Ollama model name (must be pulled first with `ollama pull model`).
            base_url: Ollama server URL (default: http://localhost:11434).
            temperature: Sampling temperature (0-1).
            max_tokens: Maximum tokens in response.
            system_prompt: Optional system prompt to prepend.
        """
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt or self._default_system_prompt()
        self._client = None

    def _default_system_prompt(self) -> str:
        """Return the default system prompt for prompt expansion."""
        return """You are an expert prompt engineer. Your task is to expand short,
ambiguous user prompts into detailed, well-structured prompts that will help
LLMs provide better responses.

When expanding prompts:
1. Add clear structure with sections and bullet points
2. Include specific instructions and constraints
3. Define expected output format
4. Add relevant context from the provided information
5. Keep the expanded prompt focused and actionable

Output only the expanded prompt, no explanations."""

    def _get_client(self):
        """Get or create Ollama client."""
        if self._client is None:
            try:
                import ollama
            except ImportError:
                raise ImportError(
                    "ollama is required for OllamaGenerator. " "Install it with: pip install ollama"
                )
            self._client = ollama.Client(host=self.base_url)
        return self._client

    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate expanded prompt using Ollama.

        Args:
            prompt: The user's short prompt to expand.
            context: Retrieved context to inform the expansion.
            **kwargs: Additional parameters for the API.

        Returns:
            The expanded prompt string.
        """
        client = self._get_client()

        # Build the user message
        user_message = f"Expand this prompt: {prompt}"
        if context:
            user_message = f"""Context from knowledge base:
{context}

---

Expand this prompt: {prompt}"""

        try:
            response = client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message},
                ],
                options={
                    "temperature": kwargs.get("temperature", self.temperature),
                    "num_predict": kwargs.get("max_tokens", self.max_tokens),
                },
            )

            return response["message"]["content"]

        except Exception as e:
            raise GeneratorError(f"Ollama generation failed: {e}") from e

    def list_models(self) -> list[str]:
        """
        List available Ollama models.

        Returns:
            List of model names available locally.
        """
        client = self._get_client()
        try:
            models = client.list()
            return [m["name"] for m in models.get("models", [])]
        except Exception as e:
            raise GeneratorError(f"Failed to list models: {e}") from e


class MistralGenerator(BaseGenerator):
    """
    Generator using Mistral AI's API.

    Mistral offers high-quality models:
    - mistral-tiny: Fast and cheap
    - mistral-small: Balanced
    - mistral-medium: High quality
    - mistral-large: Best quality

    Example:
        >>> generator = MistralGenerator(model="mistral-small-latest")
        >>> response = generator.generate(
        ...     prompt="Expand this prompt",
        ...     context="Context information..."
        ... )
    """

    def __init__(
        self,
        model: str = "mistral-small-latest",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the Mistral generator.

        Args:
            model: Mistral model name.
            api_key: Mistral API key. If not provided, uses MISTRAL_API_KEY env var.
            temperature: Sampling temperature (0-1).
            max_tokens: Maximum tokens in response.
            system_prompt: Optional system prompt.
        """
        import os

        self.model = model
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt or self._default_system_prompt()

        if not self.api_key:
            from prompt_amplifier.core.exceptions import APIKeyMissingError

            raise APIKeyMissingError(
                "API key for Mistral is missing. " "Set the MISTRAL_API_KEY environment variable."
            )

        self._client = None

    def _default_system_prompt(self) -> str:
        """Return the default system prompt."""
        return """You are an expert prompt engineer. Expand short prompts into
detailed, well-structured prompts. Include clear sections, specific instructions,
and expected output format. Output only the expanded prompt."""

    def _get_client(self):
        """Get or create Mistral client."""
        if self._client is None:
            try:
                from mistralai.client import MistralClient
            except ImportError:
                raise ImportError(
                    "mistralai is required for MistralGenerator. "
                    "Install it with: pip install mistralai"
                )
            self._client = MistralClient(api_key=self.api_key)
        return self._client

    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate expanded prompt using Mistral AI.

        Args:
            prompt: The user's short prompt to expand.
            context: Retrieved context.
            **kwargs: Additional parameters.

        Returns:
            The expanded prompt string.
        """
        client = self._get_client()
        from mistralai.models.chat_completion import ChatMessage

        # Build message
        user_message = f"Expand this prompt: {prompt}"
        if context:
            user_message = f"Context:\n{context}\n\n---\n\nExpand this prompt: {prompt}"

        try:
            response = client.chat(
                model=self.model,
                messages=[
                    ChatMessage(role="system", content=self.system_prompt),
                    ChatMessage(role="user", content=user_message),
                ],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            return response.choices[0].message.content

        except Exception as e:
            raise GeneratorError(f"Mistral generation failed: {e}") from e


class TogetherGenerator(BaseGenerator):
    """
    Generator using Together AI's API.

    Together AI provides access to many open-source models:
    - meta-llama/Llama-3.2-3B-Instruct
    - mistralai/Mistral-7B-Instruct-v0.3
    - Qwen/Qwen2.5-72B-Instruct

    Example:
        >>> generator = TogetherGenerator(model="meta-llama/Llama-3.2-3B-Instruct")
        >>> response = generator.generate(prompt="Expand this")
    """

    def __init__(
        self,
        model: str = "meta-llama/Llama-3.2-3B-Instruct",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the Together AI generator.

        Args:
            model: Together AI model name.
            api_key: Together API key. If not provided, uses TOGETHER_API_KEY env var.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens.
            system_prompt: Optional system prompt.
        """
        import os

        self.model = model
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt or self._default_system_prompt()

        if not self.api_key:
            from prompt_amplifier.core.exceptions import APIKeyMissingError

            raise APIKeyMissingError(
                "API key for Together AI is missing. "
                "Set the TOGETHER_API_KEY environment variable."
            )

    def _default_system_prompt(self) -> str:
        """Return the default system prompt."""
        return """You are an expert prompt engineer. Expand short prompts into
detailed, well-structured prompts. Output only the expanded prompt."""

    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate expanded prompt using Together AI.

        Args:
            prompt: The user's short prompt.
            context: Retrieved context.
            **kwargs: Additional parameters.

        Returns:
            The expanded prompt string.
        """
        try:
            import requests
        except ImportError:
            raise ImportError("requests is required. Install with: pip install requests")

        user_message = f"Expand this prompt: {prompt}"
        if context:
            user_message = f"Context:\n{context}\n\n---\n\nExpand this prompt: {prompt}"

        try:
            response = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "temperature": kwargs.get("temperature", self.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                },
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            raise GeneratorError(f"Together AI generation failed: {e}") from e
