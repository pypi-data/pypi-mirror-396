"""
Base classes for LLM providers.

Provides abstract base class and data classes for LLM operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class CompletionResult:
    """Result from a completion operation."""

    content: str
    provider: str
    model: str
    usage: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract Base Class
# ---------------------------------------------------------------------------

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Implement this class to add support for new LLM models.

    Example:
        class CustomProvider(LLMProvider):
            @property
            def name(self) -> str:
                return "custom"

            def complete(self, messages: list[dict], **kwargs) -> str:
                # Implementation...
                pass

            def list_models(self) -> list[str]:
                return ["custom-model"]
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for identification."""
        pass

    @property
    def default_model(self) -> str:
        """Default model for this provider."""
        return "default"

    @abstractmethod
    def complete(
        self,
        messages: list[dict],
        *,
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
            model: Specific model to use (provider-dependent).
            system: System prompt to use.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.
            **kwargs: Additional provider-specific options.

        Returns:
            Generated text content.
        """
        pass

    @abstractmethod
    def complete_with_vision(
        self,
        messages: list[dict],
        *,
        model: Optional[str] = None,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        **kwargs,
    ) -> str:
        """
        Generate a completion from messages that may include images.

        Args:
            messages: List of message dicts. Content can be a list with
                      text and image blocks for vision-capable models.
            model: Specific model to use (provider-dependent).
            system: System prompt to use.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.
            **kwargs: Additional provider-specific options.

        Returns:
            Generated text content.
        """
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        """
        List available models for this provider.

        Returns:
            List of model names.
        """
        pass
