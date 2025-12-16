"""
Video generation orchestration for semiautomatic.

Provides high-level API for image-to-video generation with automatic provider
selection and download support.

Library usage:
    from semiautomatic.video import generate_video

    # Basic i2v
    result = generate_video("cat turns head", image="cat.jpg")
    print(result.video.path)  # Path to downloaded video

    # With options
    result = generate_video(
        "walking forward",
        image="person.jpg",
        model="kling2.6",
        duration=10,
    )

CLI usage:
    semiautomatic generate-video --prompt "cat turns head" --image cat.jpg
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from semiautomatic.lib.logging import log_info, log_error
from semiautomatic.lib.api import download_file
from semiautomatic.defaults import (
    VIDEO_DEFAULT_PROVIDER,
    VIDEO_DEFAULT_MODEL,
    VIDEO_DEFAULT_DURATION,
    VIDEO_DEFAULT_ASPECT_RATIO,
)
from semiautomatic.video.providers import (
    get_provider,
    list_providers,
    list_all_models,
    VideoGenerationResult,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_video(
    prompt: str,
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    image: Optional[Union[str, Path]] = None,
    tail_image: Optional[Union[str, Path]] = None,
    duration: int = None,
    aspect_ratio: str = None,
    negative_prompt: Optional[str] = None,
    seed: Optional[int] = None,
    loop: bool = False,
    motion: Optional[str] = None,
    motion_strength: Optional[float] = None,
    output_dir: Optional[Path] = None,
    output_prefix: Optional[str] = None,
    download: bool = True,
    **kwargs,
) -> VideoGenerationResult:
    """
    Generate a video from an image and text prompt (image-to-video).

    Args:
        prompt: Text description of the motion/action.
        provider: Provider name (default: "fal").
        model: Model name (default: "kling2.6").
        image: Input image (required - all models are i2v).
        tail_image: End image for video transitions.
        duration: Video duration in seconds (5 or 10).
        aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1).
        negative_prompt: Things to avoid in the video.
        seed: Random seed for reproducibility.
        loop: Use input image as both start and end for looping.
        motion: Motion preset for Higgsfield (e.g., zoom_in, dolly_out).
        motion_strength: Motion intensity 0.0-1.0 for Higgsfield.
        output_dir: Directory to save generated video.
        output_prefix: Filename prefix (without extension) for output.
        download: Whether to download result locally.
        **kwargs: Additional provider-specific parameters.

    Returns:
        VideoGenerationResult with URL and optional local path.

    Example:
        result = generate_video("a cat walking", model="kling2.1")
        print(result.video.path)  # ./output/video.mp4
    """
    provider_name = provider or VIDEO_DEFAULT_PROVIDER
    model = model or VIDEO_DEFAULT_MODEL
    duration = duration or VIDEO_DEFAULT_DURATION
    aspect_ratio = aspect_ratio or VIDEO_DEFAULT_ASPECT_RATIO

    # Get provider
    video_provider = get_provider(provider_name)

    # All current models are image-to-video only
    if image is None:
        raise ValueError(
            "An input image is required (--image). "
            "Text-to-video is not yet supported."
        )

    log_info(f"Generating video with {model}...")

    # Build extra kwargs for provider-specific params
    extra_kwargs = dict(kwargs)
    if motion is not None:
        extra_kwargs["motion"] = motion
    if motion_strength is not None:
        extra_kwargs["motion_strength"] = motion_strength

    # Generate
    result = video_provider.generate(
        prompt=prompt,
        model=model,
        image=image,
        tail_image=tail_image,
        duration=duration,
        aspect_ratio=aspect_ratio,
        negative_prompt=negative_prompt,
        seed=seed,
        loop=loop,
        **extra_kwargs,
    )

    log_info(f"Generation complete")

    # Download if requested
    if download and result.video.url:
        output_dir = output_dir or Path("./output")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build output filename
        if output_prefix:
            output_filename = f"{output_prefix}.mp4"
        else:
            # Use first few words of prompt as filename
            prompt_slug = _slugify(prompt)[:50]
            output_filename = f"{prompt_slug}_{model}.mp4"
        output_path = output_dir / output_filename

        # Ensure unique filename (only for auto-generated names)
        if not output_prefix:
            counter = 1
            while output_path.exists():
                output_path = output_dir / f"{prompt_slug}_{model}_{counter}.mp4"
                counter += 1

        if download_file(result.video.url, output_path):
            result.video.path = output_path
            log_info(f"Saved: {output_path}")
        else:
            log_error(f"Failed to download: {result.video.url}")

    return result


def _slugify(text: str) -> str:
    """Convert text to a safe filename slug."""
    import re
    # Convert to lowercase, replace spaces with underscores
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '_', slug)
    return slug.strip('_')


# ---------------------------------------------------------------------------
# CLI Handler
# ---------------------------------------------------------------------------

def run_generate_video(args) -> bool:
    """
    CLI handler for generate-video command.

    Args:
        args: Parsed argparse namespace.

    Returns:
        True if successful, False otherwise.
    """
    # Handle --list-models
    if getattr(args, "list_models", False):
        all_models = list_all_models()
        for provider_name, models in all_models.items():
            print(f"\n{provider_name}:")
            provider = get_provider(provider_name)
            for model in models:
                info = provider.get_model_info(model)
                desc = info.get("description", "")
                tail = " [supports tail image]" if info.get("supports_tail_image") else ""
                motion = " [supports motion]" if info.get("supports_motion") else ""
                print(f"  {model}: {desc}{tail}{motion}")
        return True

    # Handle --list-motions
    if getattr(args, "list_motions", False):
        from semiautomatic.video.providers.motions import (
            list_motions,
            CAMERA_MOTIONS,
            EFFECT_MOTIONS,
            ACTION_MOTIONS,
        )
        print("\nCamera Motions:")
        for m in sorted(CAMERA_MOTIONS):
            print(f"  {m}")
        print("\nEffect Motions:")
        for m in sorted(EFFECT_MOTIONS):
            print(f"  {m}")
        print("\nAction Motions:")
        for m in sorted(ACTION_MOTIONS):
            print(f"  {m}")
        print(f"\nTotal: {len(list_motions())} motion presets")
        return True

    # Get prompt
    prompt = getattr(args, "prompt", None)
    if not prompt:
        log_error("No prompt provided. Use --prompt or --list-models")
        return False

    # Get settings from args
    provider = getattr(args, "provider", None)
    model = getattr(args, "model", None)
    image = getattr(args, "image", None)
    tail_image = getattr(args, "tail_image", None)
    duration = getattr(args, "duration", VIDEO_DEFAULT_DURATION)
    aspect_ratio = getattr(args, "aspect_ratio", VIDEO_DEFAULT_ASPECT_RATIO)
    negative_prompt = getattr(args, "negative_prompt", None)
    seed = getattr(args, "seed", None)
    loop = getattr(args, "loop", False)
    motion = getattr(args, "motion", None)
    motion_strength = getattr(args, "motion_strength", None)

    # Parse output path
    output_arg = getattr(args, "output", None)
    if output_arg:
        output_path = Path(output_arg)
        output_dir = output_path.parent or Path(".")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_prefix = output_path.stem
    else:
        output_dir = Path(getattr(args, "output_dir", "./output"))
        output_prefix = None

    log_info(f"Model: {model or VIDEO_DEFAULT_MODEL}, Duration: {duration}s")

    try:
        result = generate_video(
            prompt=prompt,
            provider=provider,
            model=model,
            image=image,
            tail_image=tail_image,
            duration=duration,
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
            seed=seed,
            loop=loop,
            motion=motion,
            motion_strength=motion_strength,
            output_dir=output_dir,
            output_prefix=output_prefix,
        )

        if result.video.path and result.video.path.exists():
            log_info(f"Success! Video saved to: {result.video.path}")
            return True
        else:
            log_info(f"Video URL: {result.video.url}")
            return True

    except Exception as e:
        log_error(f"Video generation failed: {e}")
        return False
