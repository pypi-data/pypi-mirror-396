"""
Base classes for vision providers.

Provides abstract base class and data classes for vision operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class CaptionResult:
    """Result from a caption operation."""

    caption: str
    length: str
    provider: str
    model: str
    metadata: dict = field(default_factory=dict)


@dataclass
class QueryResult:
    """Result from a query/describe operation."""

    answer: str
    question: str
    provider: str
    model: str
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract Base Class
# ---------------------------------------------------------------------------

class VisionProvider(ABC):
    """
    Abstract base class for vision providers.

    Implement this class to add support for new vision models.

    Example:
        class ClaudeVisionProvider(VisionProvider):
            @property
            def name(self) -> str:
                return "claude"

            def caption(self, image_path: Path, length: str = "normal") -> str:
                # Implementation...
                pass

            def query(self, image_path: Path, question: str) -> str:
                # Implementation...
                pass
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
    def caption(
        self,
        image_path: Path,
        *,
        length: str = "normal",
        model: Optional[str] = None,
    ) -> str:
        """
        Generate a caption for an image.

        Args:
            image_path: Path to the image file.
            length: Caption length - "short", "normal", or "long".
            model: Specific model to use (provider-dependent).

        Returns:
            Generated caption string.
        """
        pass

    @abstractmethod
    def query(
        self,
        image_path: Path,
        question: str,
        *,
        model: Optional[str] = None,
    ) -> str:
        """
        Ask a question about an image.

        Args:
            image_path: Path to the image file.
            question: Question to ask about the image.
            model: Specific model to use (provider-dependent).

        Returns:
            Model's response to the question.
        """
        pass

    def list_models(self) -> list[str]:
        """
        List available models for this provider.

        Returns:
            List of model names.
        """
        return [self.default_model]
