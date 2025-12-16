"""
Vision utilities for semiautomatic.

Provides image understanding and captioning via multiple AI providers.

Library usage:
    from semiautomatic.lib.vision import get_caption, describe_image

    # Generate a caption (uses default provider: fal with moondream3)
    caption = get_caption("image.jpg")

    # Specify provider and model
    caption = get_caption("image.jpg", provider="fal", model="moondream3")

    # Ask a question about an image
    answer = describe_image("image.jpg", "What colors are in this image?")

Supported providers:
    - huggingface: HuggingFace Gradio Spaces (default)
        - joycaption (default model)
    - fal: FAL.ai
        - moondream3 (default model)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from semiautomatic.lib.vision.base import VisionProvider, CaptionResult
from semiautomatic.lib.vision.moondream import FalVisionProvider
from semiautomatic.lib.vision.huggingface import HuggingFaceVisionProvider

# ---------------------------------------------------------------------------
# Provider Registry
# ---------------------------------------------------------------------------

_providers: dict[str, type[VisionProvider]] = {
    "fal": FalVisionProvider,
    "huggingface": HuggingFaceVisionProvider,
}

_default_provider = "fal"
_provider_instances: dict[str, VisionProvider] = {}


def get_provider(name: Optional[str] = None) -> VisionProvider:
    """
    Get a vision provider instance.

    Args:
        name: Provider name. Defaults to "fal".

    Returns:
        VisionProvider instance.

    Raises:
        ValueError: If provider is not found.
    """
    name = name or _default_provider

    if name not in _providers:
        available = ", ".join(_providers.keys())
        raise ValueError(f"Unknown vision provider: {name}. Available: {available}")

    if name not in _provider_instances:
        _provider_instances[name] = _providers[name]()

    return _provider_instances[name]


def list_providers() -> list[str]:
    """List available vision provider names."""
    return list(_providers.keys())


def register_provider(name: str, provider_class: type[VisionProvider]) -> None:
    """
    Register a custom vision provider.

    Args:
        name: Provider name for lookup.
        provider_class: VisionProvider subclass.
    """
    _providers[name] = provider_class


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_caption(
    image_path: str | Path,
    *,
    provider: Optional[str] = None,
    length: str = "normal",
) -> str:
    """
    Generate a descriptive caption for an image.

    Args:
        image_path: Path to the image file.
        provider: Vision provider name (default: fal).
        length: Caption length - "short", "normal", or "long".

    Returns:
        Generated caption string.

    Raises:
        FileNotFoundError: If image doesn't exist.
        ValueError: If provider or length is invalid.
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    return get_provider(provider).caption(image_path, length=length)


def get_prompt(
    image_path: str | Path,
    *,
    provider: Optional[str] = None,
    max_length: int = 500,
) -> str:
    """
    Generate a short prompt describing an image.

    Suitable for upscaling, style transfer, or image generation guidance.

    Args:
        image_path: Path to the image file.
        provider: Vision provider name (default: fal).
        max_length: Maximum prompt length (truncates if longer).

    Returns:
        Generated prompt string.

    Raises:
        FileNotFoundError: If image doesn't exist.
    """
    # Use short caption as prompt
    prompt = get_caption(image_path, provider=provider, length="short")

    # Truncate if needed
    if len(prompt) > max_length:
        prompt = prompt[: max_length - 3] + "..."

    return prompt


def describe_image(
    image_path: str | Path,
    question: str = "Describe this image in detail.",
    *,
    provider: Optional[str] = None,
) -> str:
    """
    Ask a question about an image.

    Args:
        image_path: Path to the image file.
        question: Question to ask about the image.
        provider: Vision provider name (default: fal).

    Returns:
        Model's response to the question.

    Raises:
        FileNotFoundError: If image doesn't exist.
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    return get_provider(provider).query(image_path, question)


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    # Public API
    "get_caption",
    "get_prompt",
    "describe_image",
    # Provider management
    "get_provider",
    "list_providers",
    "register_provider",
    # Base classes
    "VisionProvider",
    "CaptionResult",
    # Providers
    "FalVisionProvider",
    "HuggingFaceVisionProvider",
]
