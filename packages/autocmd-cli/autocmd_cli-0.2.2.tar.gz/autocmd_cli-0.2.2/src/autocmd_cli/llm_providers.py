"""
LLM Provider abstraction layer for autocmd.

This module provides a unified interface for multiple LLM providers,
making it easy to add new providers without changing the main application logic.
"""

import os
from abc import ABC, abstractmethod
from typing import Iterator, Optional


class LLMProvider(ABC):
    """Base class for all LLM providers."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or self.default_model()

    @abstractmethod
    def default_model(self) -> str:
        """Return the default model name for this provider."""
        pass

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate a non-streaming response."""
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, max_tokens: int = 200) -> Iterator[str]:
        """Generate a streaming response."""
        pass

    @classmethod
    @abstractmethod
    def env_var_name(cls) -> str:
        """Return the environment variable name for the API key."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def default_model(self) -> str:
        return "claude-haiku-4-5-20251001"

    @classmethod
    def env_var_name(cls) -> str:
        return "ANTHROPIC_API_KEY"

    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        from anthropic import Anthropic
        client = Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def generate_stream(self, prompt: str, max_tokens: int = 200) -> Iterator[str]:
        from anthropic import Anthropic
        client = Anthropic(api_key=self.api_key)
        with client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                yield text


class OpenAICompatibleProvider(LLMProvider):
    """Generic provider for OpenAI-compatible APIs."""

    def __init__(self, api_key: str, model: Optional[str] = None, base_url: Optional[str] = None):
        self.base_url = base_url
        super().__init__(api_key, model)

    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def generate_stream(self, prompt: str, max_tokens: int = 200) -> Iterator[str]:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        stream = client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI GPT provider."""

    def default_model(self) -> str:
        return "gpt-4o-mini"

    @classmethod
    def env_var_name(cls) -> str:
        return "OPENAI_API_KEY"


class GroqProvider(OpenAICompatibleProvider):
    """Groq provider."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model, base_url="https://api.groq.com/openai/v1")

    def default_model(self) -> str:
        return "llama-3.3-70b-versatile"

    @classmethod
    def env_var_name(cls) -> str:
        return "GROQ_API_KEY"


class GrokProvider(OpenAICompatibleProvider):
    """xAI Grok provider."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model, base_url="https://api.x.ai/v1")

    def default_model(self) -> str:
        return "grok-beta"

    @classmethod
    def env_var_name(cls) -> str:
        return "XAI_API_KEY"


class DeepseekProvider(OpenAICompatibleProvider):
    """Deepseek provider."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model, base_url="https://api.deepseek.com")

    def default_model(self) -> str:
        return "deepseek-chat"

    @classmethod
    def env_var_name(cls) -> str:
        return "DEEPSEEK_API_KEY"


class OpenrouterProvider(OpenAICompatibleProvider):
    """Openrouter provider."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model, base_url="https://openrouter.ai/api/v1")

    def default_model(self) -> str:
        return "anthropic/claude-3.5-sonnet"

    @classmethod
    def env_var_name(cls) -> str:
        return "OPENROUTER_API_KEY"


# Registry of all available providers
PROVIDERS = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "groq": GroqProvider,
    "grok": GrokProvider,
    "deepseek": DeepseekProvider,
    "openrouter": OpenrouterProvider,
}


def get_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> LLMProvider:
    """
    Get an LLM provider instance.

    Args:
        provider_name: Name of the provider (e.g., 'anthropic', 'openai', 'groq').
                      If None, uses AUTOCMD_PROVIDER env var or defaults to 'anthropic'.
        api_key: API key for the provider. If None, uses the provider's env var.
        model: Model name to use. If None, uses the provider's default model or AUTOCMD_MODEL env var.

    Returns:
        An instance of the requested LLM provider.

    Raises:
        ValueError: If the provider is not found or API key is not available.
    """
    # Determine provider name
    if provider_name is None:
        provider_name = os.environ.get("AUTOCMD_PROVIDER", "anthropic").lower()

    if provider_name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{provider_name}'. Available: {available}")

    provider_class = PROVIDERS[provider_name]

    # Get API key
    if api_key is None:
        api_key = os.environ.get(provider_class.env_var_name())
        if not api_key:
            raise ValueError(
                f"API key not found. Set {provider_class.env_var_name()} environment variable "
                f"or pass api_key parameter."
            )

    # Get model
    if model is None:
        model = os.environ.get("AUTOCMD_MODEL")

    return provider_class(api_key=api_key, model=model)
