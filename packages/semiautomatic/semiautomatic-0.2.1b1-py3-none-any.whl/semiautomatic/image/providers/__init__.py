"""
Image generation providers for semiautomatic.

Provides a registry of available image generation providers.

Library usage:
    from semiautomatic.image.providers import get_provider, list_providers

    # Get default provider (FAL)
    provider = get_provider()
    result = provider.generate("a cat")

    # Get specific provider
    provider = get_provider("fal")

    # List available providers
    providers = list_providers()

    # Register custom provider
    from semiautomatic.image.providers import register_provider
    register_provider("custom", MyCustomProvider)
"""

from __future__ import annotations

from typing import Optional

from semiautomatic.image.providers.base import (
    ImageProvider,
    ImageResult,
    GenerationResult,
    ImageSize,
    LoRASpec,
    parse_image_size,
    IMAGE_SIZE_PRESETS,
)
from semiautomatic.image.providers.fal import FALImageProvider
from semiautomatic.image.providers.recraft import RecraftImageProvider, RecraftControls


# ---------------------------------------------------------------------------
# Provider Registry
# ---------------------------------------------------------------------------

_providers: dict[str, type[ImageProvider]] = {
    "fal": FALImageProvider,
    "recraft": RecraftImageProvider,
}

_default_provider = "fal"
_provider_instances: dict[str, ImageProvider] = {}


def get_provider(name: Optional[str] = None) -> ImageProvider:
    """
    Get an image provider instance.

    Args:
        name: Provider name. Defaults to "fal".

    Returns:
        ImageProvider instance.

    Raises:
        ValueError: If provider is not found.
    """
    name = name or _default_provider

    if name not in _providers:
        available = ", ".join(_providers.keys())
        raise ValueError(f"Unknown image provider: {name}. Available: {available}")

    if name not in _provider_instances:
        _provider_instances[name] = _providers[name]()

    return _provider_instances[name]


def list_providers() -> list[str]:
    """List available provider names."""
    return list(_providers.keys())


def register_provider(name: str, provider_class: type[ImageProvider]) -> None:
    """
    Register a custom image provider.

    Args:
        name: Provider name for lookup.
        provider_class: ImageProvider subclass.
    """
    _providers[name] = provider_class
    # Clear cached instance if exists
    if name in _provider_instances:
        del _provider_instances[name]


def list_all_models() -> dict[str, list[str]]:
    """
    List all available models across all providers.

    Returns:
        Dict mapping provider name to list of model names.
    """
    result = {}
    for provider_name in _providers:
        try:
            provider = get_provider(provider_name)
            result[provider_name] = provider.list_models()
        except Exception:
            result[provider_name] = []
    return result


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    # Registry functions
    "get_provider",
    "list_providers",
    "register_provider",
    "list_all_models",
    # Base classes
    "ImageProvider",
    "ImageResult",
    "GenerationResult",
    "ImageSize",
    "LoRASpec",
    "parse_image_size",
    "IMAGE_SIZE_PRESETS",
    # Providers
    "FALImageProvider",
    "RecraftImageProvider",
    "RecraftControls",
]
