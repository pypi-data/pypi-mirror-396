"""
Image upscaling orchestration for semiautomatic.

Provides high-level API for image upscaling with automatic provider selection
and batch processing support.

Library usage:
    from semiautomatic.image import upscale_image

    # Simple upscale
    result = upscale_image("photo.jpg")
    print(result.path)  # Path to upscaled image

    # With options
    result = upscale_image(
        "photo.jpg",
        scale="4x",
        engine="magnific_sharpy",
        optimized_for="soft_portraits",
    )

CLI usage:
    semiautomatic upscale-image --input photo.jpg
    semiautomatic upscale-image --input-dir ./images --scale 4x
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional, Union

from semiautomatic.lib.logging import log_info, log_error
from semiautomatic.lib.api import download_file
from semiautomatic.defaults import (
    UPSCALE_DEFAULT_SCALE,
    UPSCALE_DEFAULT_ENGINE,
)
from semiautomatic.image.providers.freepik import (
    FreepikUpscaleProvider,
    UpscaleSettings,
    UpscaleResult,
    ScaleFactor,
    UpscaleEngine,
    OptimizedFor,
)


# ---------------------------------------------------------------------------
# Provider Registry
# ---------------------------------------------------------------------------

_upscale_providers = {
    "freepik": FreepikUpscaleProvider,
}

_provider_instances = {}


def get_upscale_provider(name: str = "freepik") -> FreepikUpscaleProvider:
    """Get an upscale provider instance."""
    if name not in _upscale_providers:
        available = ", ".join(_upscale_providers.keys())
        raise ValueError(f"Unknown upscale provider: {name}. Available: {available}")

    if name not in _provider_instances:
        _provider_instances[name] = _upscale_providers[name]()

    return _provider_instances[name]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def upscale_image(
    image: Union[str, Path],
    *,
    provider: str = "freepik",
    scale: ScaleFactor = None,
    engine: UpscaleEngine = None,
    optimized_for: OptimizedFor = "standard",
    prompt: Optional[str] = None,
    auto_prompt: bool = False,
    creativity: int = 0,
    hdr: int = 0,
    resemblance: int = 0,
    fractality: int = 0,
    output_dir: Optional[Path] = None,
    output_filename: Optional[str] = None,
    output_suffix: Optional[str] = None,
    download: bool = True,
) -> UpscaleResult:
    """
    Upscale an image.

    Args:
        image: Path to image file.
        provider: Upscale provider name (default: "freepik").
        scale: Scale factor ("2x" or "4x").
        engine: Upscaling engine.
        optimized_for: Optimization preset for content type.
        prompt: Text prompt to guide upscaling.
        auto_prompt: Generate prompt automatically from image.
        creativity: Creativity level 0-10.
        hdr: HDR enhancement level 0-10.
        resemblance: Resemblance to original 0-10.
        fractality: Detail fractality 0-10.
        output_dir: Directory to save upscaled image.
        output_filename: Explicit output filename (overrides suffix logic).
        output_suffix: Suffix for output filename (default: _{scale}).
        download: Whether to download result locally.

    Returns:
        UpscaleResult with URL and optional local path.

    Example:
        result = upscale_image("photo.jpg", scale="4x")
        print(result.path)  # ./output/photo_4x.jpg
    """
    scale = scale or UPSCALE_DEFAULT_SCALE
    engine = engine or UPSCALE_DEFAULT_ENGINE

    image_path = Path(image)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image}")

    # Auto-prompt if requested
    if auto_prompt and not prompt:
        prompt = _generate_prompt(image_path)
        log_info(f"Auto-prompt: {prompt[:60]}..." if len(prompt) > 60 else f"Auto-prompt: {prompt}")

    # Get provider
    upscale_provider = get_upscale_provider(provider)

    log_info(f"Upscaling {image_path.name} ({scale}, {engine})...")

    # Build settings
    settings = UpscaleSettings(
        scale=scale,
        engine=engine,
        optimized_for=optimized_for,
        creativity=creativity,
        hdr=hdr,
        resemblance=resemblance,
        fractality=fractality,
        prompt=prompt,
    )

    # Upscale
    result = upscale_provider.upscale(
        image=image_path,
        settings=settings,
        on_progress=lambda msg: log_info(msg),
    )

    log_info(f"Upscale complete")

    # Download if requested
    if download and result.url:
        output_dir = output_dir or Path("./output")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build output filename
        if output_filename:
            out_filename = output_filename
        else:
            suffix = output_suffix or f"_{scale}"
            if engine != "automatic":
                suffix = f"_{scale}_{engine}"

            stem = image_path.stem
            ext = image_path.suffix
            out_filename = f"{stem}{suffix}{ext}"
        output_path = output_dir / out_filename

        if download_file(result.url, output_path):
            result.path = output_path
            log_info(f"Saved: {output_path}")
        else:
            log_error(f"Failed to download: {result.url}")

    return result


def _generate_prompt(image_path: Path) -> str:
    """Generate a prompt for the image using vision model."""
    try:
        from semiautomatic.lib.vision import get_prompt
        return get_prompt(str(image_path), max_length=500)
    except ImportError:
        log_error("Auto-prompt requires FAL_KEY (or install gradio_client for free HuggingFace provider)")
        return ""
    except Exception as e:
        log_error(f"Failed to generate prompt: {e}")
        return ""


# ---------------------------------------------------------------------------
# Batch Processing
# ---------------------------------------------------------------------------

def find_images(folder: Union[str, Path]) -> list[Path]:
    """Find image files in a folder."""
    folder = Path(folder)
    if not folder.exists():
        return []

    extensions = {".jpg", ".jpeg", ".png", ".webp"}
    return sorted([
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in extensions
    ])


# ---------------------------------------------------------------------------
# CLI Handler
# ---------------------------------------------------------------------------

def run_upscale_image(args) -> bool:
    """
    CLI handler for upscale-image command.

    Args:
        args: Parsed argparse namespace.

    Returns:
        True if successful, False otherwise.
    """
    # Determine input files
    if getattr(args, "input", None):
        image_files = [Path(args.input)]
    else:
        input_dir = getattr(args, "input_dir", "./input")
        image_files = find_images(input_dir)

    if not image_files:
        log_error("No images found. Provide --input or --input-dir with images.")
        return False

    # Parse output path
    output_arg = getattr(args, "output", None)
    if output_arg:
        output_path = Path(output_arg)
        output_dir = output_path.parent or Path(".")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_filename = output_path.name
        # --output only works with single file
        if len(image_files) > 1:
            log_error("--output cannot be used with multiple input files. Use --output-dir instead.")
            return False
    else:
        output_dir = Path(getattr(args, "output_dir", "./output"))
        output_dir.mkdir(parents=True, exist_ok=True)
        output_filename = None

    # Get settings from args
    scale = getattr(args, "scale", "2x")
    engine = getattr(args, "engine", "automatic")
    optimized_for = getattr(args, "optimized_for", "standard")
    prompt = getattr(args, "prompt", None)
    auto_prompt = getattr(args, "auto_prompt", False)
    creativity = getattr(args, "creativity", 0)
    hdr = getattr(args, "hdr", 0)
    resemblance = getattr(args, "resemblance", 0)
    fractality = getattr(args, "fractality", 0)

    log_info(f"Upscaling {len(image_files)} image(s)...")
    log_info(f"Scale: {scale}, Engine: {engine}")

    success_count = 0
    for image_path in image_files:
        try:
            result = upscale_image(
                image_path,
                scale=scale,
                engine=engine,
                optimized_for=optimized_for,
                prompt=prompt,
                auto_prompt=auto_prompt,
                creativity=creativity,
                hdr=hdr,
                resemblance=resemblance,
                fractality=fractality,
                output_dir=output_dir,
                output_filename=output_filename,
            )
            if result.path and result.path.exists():
                success_count += 1
        except Exception as e:
            log_error(f"Failed to upscale {image_path.name}: {e}")

    log_info(f"Complete! Upscaled {success_count}/{len(image_files)} image(s)")
    return success_count > 0
