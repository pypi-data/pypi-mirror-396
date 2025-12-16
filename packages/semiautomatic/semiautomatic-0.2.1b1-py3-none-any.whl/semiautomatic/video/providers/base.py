"""
Base classes for video generation providers.

Provides abstract base class and data classes for video generation operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union, Literal


# ---------------------------------------------------------------------------
# Type Definitions
# ---------------------------------------------------------------------------

AspectRatio = Literal["16:9", "9:16", "1:1", "4:3", "3:4"]
VideoDuration = Literal[5, 6, 10]


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class VideoResult:
    """Result from a video generation operation."""

    url: str
    path: Optional[Path] = None  # Set after download
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    task_id: Optional[str] = None
    content_type: Optional[str] = None


@dataclass
class VideoGenerationResult:
    """Result from a video generation request."""

    video: VideoResult
    model: str
    provider: str
    prompt: str
    seed: Optional[int] = None
    input_image: Optional[Path] = None
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract Base Class
# ---------------------------------------------------------------------------

class VideoProvider(ABC):
    """
    Abstract base class for video generation providers.

    Implement this class to add support for new video generation services.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for identification."""
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        """List available model names."""
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        image: Optional[Union[str, Path]] = None,
        tail_image: Optional[Union[str, Path]] = None,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        on_progress: Optional[callable] = None,
        **kwargs,
    ) -> VideoGenerationResult:
        """
        Generate a video from a text prompt and optional input image.

        Args:
            prompt: Text description of the video to generate.
            model: Model name (provider-specific).
            image: Optional input image for image-to-video generation.
            tail_image: Optional end image for video (creates transition).
            duration: Video duration in seconds (model-dependent).
            aspect_ratio: Video aspect ratio.
            negative_prompt: Things to avoid in the video.
            seed: Random seed for reproducibility.
            on_progress: Optional callback for progress updates.
            **kwargs: Additional provider-specific parameters.

        Returns:
            VideoGenerationResult with generated video.
        """
        pass

    def get_model_info(self, model: str) -> dict:
        """
        Get information about a specific model.

        Args:
            model: Model name.

        Returns:
            Dict with model metadata (description, supports_tail_image, etc.)
        """
        return {}

    def supports_tail_image(self, model: str) -> bool:
        """Check if a model supports tail/end images."""
        info = self.get_model_info(model)
        return info.get("supports_tail_image", False)
