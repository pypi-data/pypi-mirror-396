"""
Image generation orchestration for semiautomatic.

Provides high-level API for image generation with automatic provider selection,
image downloading, and batch processing.

Library usage:
    from semiautomatic.image import generate_image

    # Simple generation
    result = generate_image("a cat sitting on a windowsill")
    print(result.images[0].path)  # Path to downloaded image

    # With options
    result = generate_image(
        "a portrait photo",
        model="flux-dev",
        size="portrait_4_3",
        num_images=4,
        output_dir=Path("./output"),
    )

CLI usage:
    semiautomatic generate-image --prompt "a cat" --model flux-dev
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional, Union

from semiautomatic.lib.logging import log_info, log_error
from semiautomatic.lib.api import download_file
from semiautomatic.defaults import (
    IMAGE_DEFAULT_PROVIDER,
    IMAGE_DEFAULT_MODEL,
    IMAGE_DEFAULT_SIZE,
    IMAGE_DEFAULT_NUM_IMAGES,
    IMAGE_DEFAULT_OUTPUT_FORMAT,
)
from semiautomatic.image.providers import (
    get_provider,
    list_providers,
    list_all_models,
    ImageProvider,
    ImageResult,
    GenerationResult,
    ImageSize,
    LoRASpec,
    RecraftControls,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_image(
    prompt: str,
    *,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    size: Union[str, ImageSize] = None,
    num_images: int = None,
    seed: Optional[int] = None,
    loras: Optional[list[Union[str, LoRASpec]]] = None,
    output_dir: Optional[Path] = None,
    output_prefix: Optional[str] = None,
    download: bool = True,
    **kwargs,
) -> GenerationResult:
    """
    Generate images from a text prompt.

    Args:
        prompt: Text description of the image to generate.
        model: Model name (provider-specific). Uses default if not specified.
        provider: Provider name ("fal", etc.). Auto-detected from model if not specified.
        size: Image size as preset name, "WxH" string, or ImageSize.
        num_images: Number of images to generate (1-4).
        seed: Random seed for reproducibility.
        loras: List of LoRA paths or LoRASpec objects.
        output_dir: Directory to save downloaded images. Defaults to ./output.
        output_prefix: Prefix for output filenames.
        download: Whether to download images locally (default: True).
        **kwargs: Additional provider-specific parameters.

    Returns:
        GenerationResult with generated images.

    Examples:
        # Simple generation
        result = generate_image("a cat")

        # With model and size
        result = generate_image(
            "a portrait",
            model="flux-dev",
            size="portrait_4_3",
        )

        # With LoRA
        result = generate_image(
            "a cat in my style",
            model="flux-krea",
            loras=["path/to/lora.safetensors:0.8"],
        )
    """
    # Resolve provider first (explicit, inferred from model, or default)
    if provider:
        provider_name = provider
    elif model:
        provider_name = _detect_provider_for_model(model) or IMAGE_DEFAULT_PROVIDER
    else:
        provider_name = IMAGE_DEFAULT_PROVIDER
    image_provider = get_provider(provider_name)

    # Apply provider-specific defaults
    if provider_name == "recraft":
        from semiautomatic.defaults import (
            RECRAFT_DEFAULT_MODEL,
            RECRAFT_DEFAULT_SIZE,
        )
        model = model or RECRAFT_DEFAULT_MODEL
        size = size or RECRAFT_DEFAULT_SIZE
    else:
        model = model or IMAGE_DEFAULT_MODEL
        size = size or IMAGE_DEFAULT_SIZE

    num_images = num_images if num_images is not None else IMAGE_DEFAULT_NUM_IMAGES

    # Parse LoRAs
    parsed_loras = None
    if loras:
        parsed_loras = [
            lora if isinstance(lora, LoRASpec) else LoRASpec.from_string(lora)
            for lora in loras
        ]

    # Generate
    log_info(f"Generating {num_images} image(s) with {model}...")

    result = image_provider.generate(
        prompt=prompt,
        model=model,
        size=size,
        num_images=num_images,
        seed=seed,
        loras=parsed_loras,
        **kwargs,
    )

    log_info(f"Generated {len(result.images)} image(s)")

    # Download images if requested
    if download and result.images:
        output_dir = output_dir or Path("./output")
        output_dir.mkdir(parents=True, exist_ok=True)

        prefix = output_prefix or f"gen_{int(time.time())}"

        for i, img in enumerate(result.images):
            # Determine extension from URL or content type
            ext = _get_extension(img.url, img.content_type)

            if len(result.images) == 1:
                filename = f"{prefix}{ext}"
            else:
                filename = f"{prefix}_{i + 1}{ext}"

            output_path = output_dir / filename

            if download_file(img.url, output_path):
                img.path = output_path
                log_info(f"Saved: {output_path.name} ({img.width}x{img.height})")
            else:
                log_error(f"Failed to download: {img.url}")

    return result


def image_to_image(
    input_image: Union[str, Path],
    prompt: str,
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    style: Optional[str] = None,
    strength: float = 0.5,
    num_images: int = 1,
    controls: Optional[RecraftControls] = None,
    output_dir: Optional[Path] = None,
    output_prefix: Optional[str] = None,
    download: bool = True,
    **kwargs,
) -> GenerationResult:
    """
    Apply style transformation to an existing image.

    Currently only supported by the Recraft provider.

    Args:
        input_image: Path to input image file.
        prompt: Text description of desired changes.
        provider: Provider name (default: "recraft").
        model: Model version.
        style: Style name or custom style UUID.
        strength: Transformation strength 0-1 (0=minimal change, 1=full transformation).
        num_images: Number of variations to generate.
        controls: RecraftControls for fine-tuning.
        output_dir: Directory to save downloaded images.
        output_prefix: Prefix for output filenames.
        download: Whether to download images locally.
        **kwargs: Additional provider-specific parameters.

    Returns:
        GenerationResult with generated images.

    Example:
        result = image_to_image(
            "photo.jpg",
            "transform to digital illustration",
            style="digital_illustration",
            strength=0.7,
        )
    """
    # Default to recraft for i2i
    provider_name = provider or "recraft"
    image_provider = get_provider(provider_name)

    # Check if provider supports i2i
    if not hasattr(image_provider, "image_to_image"):
        raise ValueError(f"Provider '{provider_name}' does not support image-to-image")

    input_path = Path(input_image)
    log_info(f"Transforming {input_path.name} with {provider_name}...")

    result = image_provider.image_to_image(
        input_image=input_path,
        prompt=prompt,
        model=model,
        style=style,
        strength=strength,
        num_images=num_images,
        controls=controls,
        **kwargs,
    )

    log_info(f"Generated {len(result.images)} variation(s)")

    # Download images if requested
    if download and result.images:
        output_dir = output_dir or Path("./output")
        output_dir.mkdir(parents=True, exist_ok=True)

        prefix = output_prefix or f"i2i_{int(time.time())}"

        for i, img in enumerate(result.images):
            ext = _get_extension(img.url, img.content_type)

            if len(result.images) == 1:
                filename = f"{prefix}{ext}"
            else:
                filename = f"{prefix}_{i + 1}{ext}"

            output_path = output_dir / filename

            if download_file(img.url, output_path):
                img.path = output_path
                log_info(f"Saved: {output_path.name} ({img.width}x{img.height})")
            else:
                log_error(f"Failed to download: {img.url}")

    return result


def _detect_provider_for_model(model: str) -> Optional[str]:
    """Detect which provider supports a given model."""
    all_models = list_all_models()

    for provider_name, models in all_models.items():
        if model in models:
            return provider_name

    return None


def _get_extension(url: str, content_type: Optional[str] = None) -> str:
    """Get file extension from URL or content type."""
    # Try content type first
    if content_type:
        if "png" in content_type:
            return ".png"
        if "jpeg" in content_type or "jpg" in content_type:
            return ".jpg"

    # Fall back to URL
    url_lower = url.lower()
    if ".png" in url_lower:
        return ".png"
    if ".jpg" in url_lower or ".jpeg" in url_lower:
        return ".jpg"
    if ".webp" in url_lower:
        return ".webp"

    # Default
    return ".png"


# ---------------------------------------------------------------------------
# CLI Handler
# ---------------------------------------------------------------------------

def run_generate_image(args) -> bool:
    """
    CLI handler for generate-image command.

    Args:
        args: Parsed argparse namespace.

    Returns:
        True if successful, False otherwise.
    """
    # Handle list-models
    if getattr(args, "list_models", False):
        _print_models()
        return True

    # Validate prompt
    if not args.prompt:
        log_error("No prompt provided. Use --prompt 'your prompt here'")
        return False

    # Parse output path
    output_arg = getattr(args, "output", None)
    if output_arg:
        output_path = Path(output_arg)
        output_dir = output_path.parent or Path(".")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_prefix = output_path.stem
    else:
        output_dir = Path(args.output_dir)
        output_prefix = None

    # Get provider (explicit or inferred)
    provider = getattr(args, "provider", None)

    # If input-image is specified, use i2i mode
    input_image = getattr(args, "input_image", None)

    try:
        if input_image:
            # Image-to-image mode (Recraft)
            provider = provider or "recraft"

            # Build controls if any Recraft options specified
            controls = _build_recraft_controls(args)

            result = image_to_image(
                input_image=input_image,
                prompt=args.prompt,
                provider=provider,
                model=args.model,
                style=getattr(args, "style", None),
                strength=getattr(args, "strength", None) or 0.5,
                num_images=args.num_images,
                controls=controls,
                output_dir=output_dir,
                output_prefix=output_prefix,
                negative_prompt=getattr(args, "negative_prompt", None),
                output_format=getattr(args, "format", IMAGE_DEFAULT_OUTPUT_FORMAT),
            )
        else:
            # Text-to-image mode
            # Parse LoRAs (FAL only)
            loras = None
            if getattr(args, "lora", None):
                loras = args.lora

            # Build extra kwargs based on provider
            extra_kwargs = {}

            # FAL-specific options
            if getattr(args, "steps", None) is not None:
                extra_kwargs["steps"] = args.steps
            if getattr(args, "guidance", None) is not None:
                extra_kwargs["guidance"] = args.guidance

            # Recraft-specific options
            if getattr(args, "style", None):
                extra_kwargs["style"] = args.style

            controls = _build_recraft_controls(args)
            if controls:
                extra_kwargs["controls"] = controls

            extra_kwargs["output_format"] = getattr(args, "format", IMAGE_DEFAULT_OUTPUT_FORMAT)

            result = generate_image(
                prompt=args.prompt,
                model=args.model,
                provider=provider,
                size=args.size,
                num_images=args.num_images,
                seed=getattr(args, "seed", None),
                loras=loras,
                output_dir=output_dir,
                output_prefix=output_prefix,
                **extra_kwargs,
            )

        log_info(f"Complete! Generated {len(result.images)} image(s)")
        return True

    except Exception as e:
        log_error(f"Generation failed: {e}")
        return False


def _build_recraft_controls(args) -> Optional[RecraftControls]:
    """Build RecraftControls from CLI args if any are specified."""
    artistic_level = getattr(args, "artistic_level", None)
    colors = getattr(args, "colors", None)
    background_color = getattr(args, "background_color", None)
    no_text = getattr(args, "no_text", False)

    if artistic_level is not None or colors or background_color or no_text:
        return RecraftControls(
            artistic_level=artistic_level,
            colors=colors,
            background_color=background_color,
            no_text=no_text,
        )
    return None


def _print_models():
    """Print available models and styles."""
    all_models = list_all_models()

    print("\nAvailable models:\n")
    for provider_name, models in all_models.items():
        print(f"  {provider_name}:")
        provider = get_provider(provider_name)
        for model in models:
            info = provider.get_model_info(model)
            desc = info.get("description", "")
            lora = " [LoRA]" if info.get("supports_loras") else ""
            print(f"    {model}{lora}")
            if desc:
                print(f"      {desc}")
        print()

    # Print Recraft styles
    from semiautomatic.image.providers.recraft_styles import RECRAFT_STYLES
    print("Recraft styles:")
    for style_name, style_info in RECRAFT_STYLES.items():
        desc = style_info.get("description", "")
        print(f"  {style_name}")
        if desc:
            print(f"    {desc}")
    print()
