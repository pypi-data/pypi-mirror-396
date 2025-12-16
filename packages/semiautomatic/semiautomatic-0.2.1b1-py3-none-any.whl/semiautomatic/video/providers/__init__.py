"""
Video generation provider registry.

Provides access to video generation providers with automatic registration.

Usage:
    from semiautomatic.video.providers import get_provider, list_providers

    # Get default provider
    provider = get_provider()

    # Get specific provider
    provider = get_provider("fal")

    # List all available providers
    providers = list_providers()
"""

from __future__ import annotations

from typing import Optional

from semiautomatic.video.providers.base import (
    VideoProvider,
    VideoResult,
    VideoGenerationResult,
)
from semiautomatic.video.providers.fal import FALVideoProvider
from semiautomatic.video.providers.wavespeed import WavespeedVideoProvider
from semiautomatic.video.providers.higgsfield import HiggsfieldVideoProvider


# ---------------------------------------------------------------------------
# Provider Registry
# ---------------------------------------------------------------------------

_providers: dict[str, type[VideoProvider]] = {
    "fal": FALVideoProvider,
    "wavespeed": WavespeedVideoProvider,
    "higgsfield": HiggsfieldVideoProvider,
}

_provider_instances: dict[str, VideoProvider] = {}


def register_provider(name: str, provider_class: type[VideoProvider]) -> None:
    """
    Register a new video provider.

    Args:
        name: Provider name for lookup.
        provider_class: Provider class (not instance).
    """
    _providers[name] = provider_class


def list_providers() -> list[str]:
    """List all registered provider names."""
    return list(_providers.keys())


def get_provider(name: Optional[str] = None) -> VideoProvider:
    """
    Get a video provider instance.

    Args:
        name: Provider name. Defaults to "fal".

    Returns:
        VideoProvider instance.

    Raises:
        ValueError: If provider not found.
    """
    name = name or "fal"

    if name not in _providers:
        available = ", ".join(_providers.keys())
        raise ValueError(f"Unknown video provider: {name}. Available: {available}")

    # Return cached instance
    if name not in _provider_instances:
        _provider_instances[name] = _providers[name]()

    return _provider_instances[name]


def list_all_models() -> dict[str, list[str]]:
    """
    List all models across all providers.

    Returns:
        Dict mapping provider names to lists of model names.
    """
    result = {}
    for name in _providers:
        provider = get_provider(name)
        result[name] = provider.list_models()
    return result


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    # Registry
    "register_provider",
    "list_providers",
    "get_provider",
    "list_all_models",
    # Base classes
    "VideoProvider",
    "VideoResult",
    "VideoGenerationResult",
    # Providers
    "FALVideoProvider",
    "WavespeedVideoProvider",
    "HiggsfieldVideoProvider",
]
