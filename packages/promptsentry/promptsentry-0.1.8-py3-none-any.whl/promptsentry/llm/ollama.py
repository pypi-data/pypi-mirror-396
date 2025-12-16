"""
Ollama LLM Provider

Uses the official Ollama Python library for local LLM inference.
This is the recommended provider as it works without cloud authentication.
"""

from typing import Optional

from promptsentry.llm.base import BaseLLM
from promptsentry.models.config import LLMConfig


class OllamaLLM(BaseLLM):
    """
    Ollama LLM implementation using the official ollama-python library.

    Uses Ollama to run models like qwen3:4b locally.
    This is the default provider - no cloud auth required.
    """

    DEFAULT_MODEL = "qwen3:4b"

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize Ollama LLM.

        Args:
            config: LLM configuration
        """
        self.config = config or LLMConfig()
        self._client = None
        self._available = None

    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.config.model_name or self.DEFAULT_MODEL

    def _get_client(self):
        """Get or create the Ollama client."""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.config.ollama_base_url)
            except ImportError:
                raise ImportError(
                    "ollama package required. Install with: pip install ollama"
                )
        return self._client

    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        if self._available is not None:
            return self._available

        try:
            client = self._get_client()
            response = client.list()

            # Get model names (with and without tags)
            available_models = []
            for m in response.models:
                name = m.model
                available_models.append(name)
                if ":" in name:
                    available_models.append(name.split(":")[0])

            self._available = self.model_name in available_models
            return self._available
        except Exception:
            self._available = False
            return False

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the model.

        Args:
            prompt: The prompt to send
            **kwargs: Additional generation parameters

        Returns:
            Generated text response
        """
        return self.chat([{"role": "user", "content": prompt}], **kwargs)

    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        """
        Chat with the model using message format.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters

        Returns:
            Model's response
        """
        client = self._get_client()

        options = {
            "temperature": kwargs.get("temperature", self.config.temperature),
            "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
        }

        response = client.chat(
            model=self.model_name,
            messages=messages,
            options=options,
        )

        return response.message.content

    def list_models(self) -> list[str]:
        """List available models in Ollama."""
        try:
            client = self._get_client()
            response = client.list()
            return [m.model for m in response.models]
        except Exception:
            return []
