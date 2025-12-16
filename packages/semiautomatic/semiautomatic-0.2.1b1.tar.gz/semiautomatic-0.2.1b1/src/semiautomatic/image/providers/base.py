"""
Base classes for image generation providers.

Provides abstract base class and data classes for image generation operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class LoRASpec:
    """Specification for a LoRA to apply during generation."""

    path: str  # URL or local path
    scale: float = 1.0

    @classmethod
    def from_string(cls, spec: str) -> "LoRASpec":
        """
        Parse LoRA spec from string.

        Formats:
            "path/to/lora.safetensors"
            "path/to/lora.safetensors:0.8"
        """
        if ":" in spec:
            # Check if last segment is a scale (not part of path)
            parts = spec.rsplit(":", 1)
            try:
                scale = float(parts[1])
                return cls(path=parts[0], scale=scale)
            except ValueError:
                pass

        return cls(path=spec, scale=1.0)


@dataclass
class ImageResult:
    """Result from an image generation operation."""

    url: str
    width: int
    height: int
    path: Optional[Path] = None  # Set after download
    content_type: Optional[str] = None
    seed: Optional[int] = None


@dataclass
class GenerationResult:
    """Result from a generation request (may contain multiple images)."""

    images: list[ImageResult]
    model: str
    provider: str
    prompt: str
    seed: Optional[int] = None
    metadata: dict = field(default_factory=dict)

    @property
    def image(self) -> Optional[ImageResult]:
        """Get first image (convenience for single-image requests)."""
        return self.images[0] if self.images else None


@dataclass
class ImageSize:
    """Image dimensions."""

    width: int
    height: int

    @classmethod
    def from_string(cls, size_str: str) -> "ImageSize":
        """
        Parse size from string.

        Formats:
            "1024x768"
            "1024" (square)
        """
        if "x" in size_str.lower():
            width, height = size_str.lower().split("x")
            return cls(width=int(width), height=int(height))
        else:
            dim = int(size_str)
            return cls(width=dim, height=dim)


# ---------------------------------------------------------------------------
# Size Presets
# ---------------------------------------------------------------------------

IMAGE_SIZE_PRESETS = {
    "square": ImageSize(1024, 1024),
    "square_hd": ImageSize(1536, 1536),
    "portrait_4_3": ImageSize(768, 1024),
    "portrait_16_9": ImageSize(576, 1024),
    "landscape_4_3": ImageSize(1024, 768),
    "landscape_16_9": ImageSize(1024, 576),
}


def parse_image_size(size: Union[str, ImageSize, dict]) -> Union[ImageSize, str]:
    """
    Parse image size from various formats.

    Args:
        size: Size as preset name, "WxH" string, ImageSize, or dict.

    Returns:
        ImageSize object or preset string (for API compatibility).
    """
    if isinstance(size, ImageSize):
        return size

    if isinstance(size, dict):
        return ImageSize(width=size["width"], height=size["height"])

    if isinstance(size, str):
        if size in IMAGE_SIZE_PRESETS:
            return IMAGE_SIZE_PRESETS[size]
        if "x" in size.lower():
            return ImageSize.from_string(size)
        # Return as-is for API preset names
        return size

    raise ValueError(f"Invalid size format: {size}")


# ---------------------------------------------------------------------------
# Abstract Base Class
# ---------------------------------------------------------------------------

class ImageProvider(ABC):
    """
    Abstract base class for image generation providers.

    Implement this class to add support for new image generation services.
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
        size: Union[str, ImageSize] = "landscape_4_3",
        num_images: int = 1,
        seed: Optional[int] = None,
        loras: Optional[list[LoRASpec]] = None,
        **kwargs,
    ) -> GenerationResult:
        """
        Generate images from a text prompt.

        Args:
            prompt: Text description of the image to generate.
            model: Model name (provider-specific).
            size: Image size as preset name or ImageSize.
            num_images: Number of images to generate (1-4).
            seed: Random seed for reproducibility.
            loras: List of LoRA specifications to apply.
            **kwargs: Additional provider-specific parameters.

        Returns:
            GenerationResult with generated images.
        """
        pass

    def get_model_info(self, model: str) -> dict:
        """
        Get information about a specific model.

        Args:
            model: Model name.

        Returns:
            Dict with model metadata (description, supports_loras, etc.)
        """
        return {}
