"""
LLM utilities for semiautomatic.

Provides text completion via multiple AI providers.

Library usage:
    from semiautomatic.lib.llm import complete, get_provider

    # Simple usage (uses default provider: claude)
    response = complete([{"role": "user", "content": "Hello"}])

    # With provider selection
    response = complete(messages, provider="openai", model="gpt-4o")

    # With system prompt
    response = complete(
        [{"role": "user", "content": "Write a haiku"}],
        system="You are a poet."
    )

    # Vision (images in messages)
    response = complete_with_vision(messages_with_images, provider="claude")

Supported providers:
    - claude: Anthropic Claude models (default)
    - openai: OpenAI GPT models
"""

from __future__ import annotations

from typing import Optional

from semiautomatic.lib.llm.base import LLMProvider, CompletionResult
from semiautomatic.lib.llm.claude import ClaudeProvider
from semiautomatic.lib.llm.openai import OpenAIProvider


# ---------------------------------------------------------------------------
# Provider Registry
# ---------------------------------------------------------------------------

_providers: dict[str, type[LLMProvider]] = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
}

_default_provider = "claude"
_provider_instances: dict[str, LLMProvider] = {}


def get_provider(name: Optional[str] = None) -> LLMProvider:
    """
    Get an LLM provider instance.

    Args:
        name: Provider name. Defaults to "claude".

    Returns:
        LLMProvider instance.

    Raises:
        ValueError: If provider is not found.
    """
    name = name or _default_provider

    if name not in _providers:
        available = ", ".join(_providers.keys())
        raise ValueError(f"Unknown LLM provider: {name}. Available: {available}")

    if name not in _provider_instances:
        _provider_instances[name] = _providers[name]()

    return _provider_instances[name]


def list_providers() -> list[str]:
    """List available LLM provider names."""
    return list(_providers.keys())


def register_provider(name: str, provider_class: type[LLMProvider]) -> None:
    """
    Register a custom LLM provider.

    Args:
        name: Provider name for lookup.
        provider_class: LLMProvider subclass.
    """
    _providers[name] = provider_class


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def complete(
    messages: list[dict],
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    system: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 1.0,
    **kwargs,
) -> str:
    """
    Generate a completion from messages.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.
        provider: LLM provider name (default: claude).
        model: Specific model to use (default varies by provider).
        system: System prompt to use.
        max_tokens: Maximum tokens in response.
        temperature: Sampling temperature.
        **kwargs: Additional provider-specific options.

    Returns:
        Generated text content.

    Examples:
        # Simple usage
        response = complete([{"role": "user", "content": "Hello"}])

        # With system prompt
        response = complete(
            [{"role": "user", "content": "Write a haiku"}],
            system="You are a poet."
        )

        # With specific provider and model
        response = complete(
            [{"role": "user", "content": "Hello"}],
            provider="openai",
            model="gpt-4o"
        )
    """
    return get_provider(provider).complete(
        messages,
        model=model,
        system=system,
        max_tokens=max_tokens,
        temperature=temperature,
        **kwargs,
    )


def complete_with_vision(
    messages: list[dict],
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    system: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 1.0,
    **kwargs,
) -> str:
    """
    Generate a completion from messages that may include images.

    Args:
        messages: List of message dicts. Content can include image blocks.
        provider: LLM provider name (default: claude).
        model: Specific model to use (default varies by provider).
        system: System prompt to use.
        max_tokens: Maximum tokens in response.
        temperature: Sampling temperature.
        **kwargs: Additional provider-specific options.

    Returns:
        Generated text content.

    Examples:
        # Claude vision format
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}},
                {"type": "text", "text": "What's in this image?"}
            ]
        }]
        response = complete_with_vision(messages)
    """
    return get_provider(provider).complete_with_vision(
        messages,
        model=model,
        system=system,
        max_tokens=max_tokens,
        temperature=temperature,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    # Public API
    "complete",
    "complete_with_vision",
    # Provider management
    "get_provider",
    "list_providers",
    "register_provider",
    # Base classes
    "LLMProvider",
    "CompletionResult",
    # Providers
    "ClaudeProvider",
    "OpenAIProvider",
]
