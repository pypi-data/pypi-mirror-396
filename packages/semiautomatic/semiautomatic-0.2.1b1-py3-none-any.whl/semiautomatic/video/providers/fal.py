"""
FAL video generation provider.

Supports Kling, Seedance, and Hailuo video models via FAL.ai.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union

from semiautomatic.video.providers.base import (
    VideoProvider,
    VideoResult,
    VideoGenerationResult,
)
from semiautomatic.video.providers.fal_models import (
    FAL_VIDEO_MODELS,
    DEFAULT_MODEL,
    get_model_config,
    get_model_info,
    list_models,
    normalize_duration,
)
from semiautomatic.lib.logging import log_info, log_error


# ---------------------------------------------------------------------------
# FAL Video Provider
# ---------------------------------------------------------------------------

class FALVideoProvider(VideoProvider):
    """
    FAL.ai video generation provider.

    Supports Kling (1.5-2.6, O1), Seedance, and Hailuo models.

    Requires FAL_KEY environment variable.
    """

    def __init__(self):
        """Initialize FAL provider."""
        self._fal_client = None

    @property
    def name(self) -> str:
        return "fal"

    def _get_client(self):
        """Get FAL client, lazily initialized."""
        if self._fal_client is None:
            try:
                import fal_client
            except ImportError:
                raise ImportError(
                    "fal-client package not found. "
                    "Install with: pip install semiautomatic[generate]"
                )

            api_key = os.environ.get("FAL_KEY")
            if api_key:
                fal_client.api_key = api_key
            else:
                log_error("FAL_KEY environment variable not set")

            self._fal_client = fal_client

        return self._fal_client

    def list_models(self) -> list[str]:
        """List available FAL video model names."""
        return list_models()

    def get_model_info(self, model: str) -> dict:
        """Get information about a specific model."""
        return get_model_info(model)

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
        cfg_scale: Optional[float] = None,
        loop: bool = False,
        on_progress: Optional[callable] = None,
        **kwargs,
    ) -> VideoGenerationResult:
        """
        Generate a video using FAL.

        Args:
            prompt: Text description of the video.
            model: Model name (default: kling2.1).
            image: Input image URL or path for image-to-video.
            tail_image: End image URL or path for transitions.
            duration: Video duration in seconds (5 or 10).
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1).
            negative_prompt: Things to avoid in the video.
            seed: Random seed for reproducibility.
            cfg_scale: Classifier-free guidance scale.
            loop: Use same image as start and end for looping effect.
            on_progress: Optional callback for progress updates.
            **kwargs: Additional model-specific parameters.

        Returns:
            VideoGenerationResult with generated video.
        """
        model = model or DEFAULT_MODEL
        config = get_model_config(model)

        if not config:
            available = ", ".join(list_models())
            raise ValueError(f"Unknown model: {model}. Available: {available}")

        # Auto-fallback for loop mode
        if loop and not config.get("supports_tail_image"):
            fallback_model = "kling2.5"
            log_info(f"[INFO] --loop requires tail image support, switching to {fallback_model}")
            model = fallback_model
            config = get_model_config(model)

        fal_client = self._get_client()

        # Build arguments
        args = self._build_arguments(
            model=model,
            config=config,
            prompt=prompt,
            image=image,
            tail_image=tail_image,
            duration=duration,
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
            seed=seed,
            cfg_scale=cfg_scale,
            loop=loop,
            **kwargs,
        )

        # Progress callback wrapper
        def on_queue_update(update):
            if on_progress and hasattr(update, 'logs'):
                for log in update.logs:
                    on_progress(log.get('message', str(log)))

        # Submit and wait for result
        if on_progress:
            on_progress(f"Generating video with {model}...")

        result = fal_client.subscribe(
            config["endpoint"],
            arguments=args,
            with_logs=True,
            on_queue_update=on_queue_update,
        )

        # Parse result
        return self._parse_result(result, model, prompt, image)

    def _build_arguments(
        self,
        model: str,
        config: dict,
        prompt: str,
        image: Optional[Union[str, Path]],
        tail_image: Optional[Union[str, Path]],
        duration: int,
        aspect_ratio: str,
        negative_prompt: Optional[str],
        seed: Optional[int],
        cfg_scale: Optional[float],
        loop: bool,
        **kwargs,
    ) -> dict:
        """Build FAL API arguments."""
        # Start with default params
        args = config.get("default_params", {}).copy()

        # Add prompt
        args["prompt"] = prompt

        # Add image if provided
        if image:
            start_param = config.get("start_image_param", "image_url")
            image_url = self._resolve_image_url(image)
            args[start_param] = image_url

            # Handle loop mode (tail image = start image)
            if loop and config.get("supports_tail_image"):
                tail_param = config.get("tail_image_param", "tail_image_url")
                args[tail_param] = image_url
            elif tail_image and config.get("supports_tail_image"):
                tail_param = config.get("tail_image_param", "tail_image_url")
                args[tail_param] = self._resolve_image_url(tail_image)
            elif tail_image and not config.get("supports_tail_image"):
                log_info(f"[WARN] --tail-image ignored: {model} does not support it. Try kling2.5 or seedance1.0")

        # Normalize duration for model
        normalized_duration = normalize_duration(model, duration)

        # Handle duration format (some models expect string, others int)
        if model.startswith("seedance"):
            args["duration"] = str(normalized_duration)
        elif model.startswith("hailuo"):
            args["duration"] = str(normalized_duration)
        elif model.startswith("kling"):
            args["duration"] = normalized_duration

        # Add aspect ratio if model supports it
        if "aspect_ratio" in config.get("default_params", {}):
            args["aspect_ratio"] = aspect_ratio

        # Override negative prompt if provided
        if negative_prompt is not None:
            args["negative_prompt"] = negative_prompt

        # Add optional parameters
        if seed is not None:
            args["seed"] = seed

        if cfg_scale is not None:
            args["cfg_scale"] = cfg_scale

        # Add any additional kwargs
        args.update(kwargs)

        return args

    def _resolve_image_url(self, image: Union[str, Path]) -> str:
        """
        Resolve image to URL.

        If image is a local path, uploads to FAL storage first.
        """
        if isinstance(image, Path):
            image = str(image)

        # Check if it's already a URL
        if image.startswith(("http://", "https://")):
            return image

        # Local file - upload to FAL storage
        local_path = Path(image)
        if not local_path.exists():
            raise FileNotFoundError(f"Image file not found: {image}")

        log_info(f"Uploading {local_path.name} to FAL storage...")
        fal_client = self._get_client()
        url = fal_client.upload_file(image)
        log_info("Upload complete, submitting generation request...")
        return url

    def _parse_result(
        self,
        result: dict,
        model: str,
        prompt: str,
        input_image: Optional[Union[str, Path]],
    ) -> VideoGenerationResult:
        """Parse FAL API result into VideoGenerationResult."""
        video_info = result.get("video", {})

        if not video_info:
            raise ValueError(f"No video in result: {result}")

        video_url = video_info.get("url")
        if not video_url:
            raise ValueError(f"No video URL in result: {result}")

        video = VideoResult(
            url=video_url,
            width=video_info.get("width"),
            height=video_info.get("height"),
            duration=video_info.get("duration"),
            content_type=video_info.get("content_type", "video/mp4"),
        )

        return VideoGenerationResult(
            video=video,
            model=model,
            provider=self.name,
            prompt=prompt,
            seed=result.get("seed"),
            input_image=Path(input_image) if input_image else None,
            metadata=result,
        )
