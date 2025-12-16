"""
Wavespeed video generation provider.

Supports: Kling 2.5, WAN 2.2, WAN 2.5, Sora 2
"""

from __future__ import annotations

import base64
import os
import time
from pathlib import Path
from typing import Optional, Union

import requests

from semiautomatic.video.providers.base import (
    VideoProvider,
    VideoResult,
    VideoGenerationResult,
)


# ---------------------------------------------------------------------------
# Wavespeed Model Configurations
# ---------------------------------------------------------------------------

WAVESPEED_MODELS = {
    "kling2.5-wavespeed": {
        "endpoint": "https://api.wavespeed.ai/api/v3/kwaivgi/kling-v2.5-turbo-pro/image-to-video",
        "supports_tail_image": False,
        "duration_type": "string",  # Uses "5" not 5
        "description": "Kling 2.5 Turbo Pro via Wavespeed",
        "default_params": {
            "duration": "5",
            "guidance_scale": 0.5,
        },
    },
    "wan2.2": {
        "endpoint": "https://api.wavespeed.ai/api/v3/wavespeed-ai/wan-2.2/i2v-720p",
        "supports_tail_image": True,
        "tail_image_param": "last_image",
        "duration_type": "integer",
        "description": "WAN 2.2 image-to-video 720p",
        "default_params": {
            "duration": 5,
            "negative_prompt": "",
            "seed": -1,
        },
    },
    "wan2.5": {
        "endpoint": "https://api.wavespeed.ai/api/v3/alibaba/wan-2.5/image-to-video",
        "supports_tail_image": False,
        "duration_type": "integer",
        "description": "WAN 2.5 Alibaba image-to-video",
        "default_params": {
            "duration": 10,
            "enable_prompt_expansion": True,
            "resolution": "1080p",
            "seed": -1,
        },
    },
    "sora2": {
        "endpoint": "https://api.wavespeed.ai/api/v3/openai/sora-2/image-to-video-pro",
        "supports_tail_image": False,
        "duration_type": "integer",
        "description": "Sora 2 image-to-video (via Wavespeed)",
        "default_params": {
            "duration": 12,
            "resolution": "1080p",
        },
    },
}

DEFAULT_MODEL = "wan2.5"


def list_models() -> list[str]:
    """Return list of available Wavespeed model names."""
    return list(WAVESPEED_MODELS.keys())


def get_model_config(model: str) -> Optional[dict]:
    """Return configuration for a specific model, or None if not found."""
    return WAVESPEED_MODELS.get(model)


def get_model_info(model: str) -> dict:
    """Return public info about a model for display."""
    config = WAVESPEED_MODELS.get(model)
    if not config:
        return {}
    return {
        "name": model,
        "description": config.get("description", ""),
        "supports_tail_image": config.get("supports_tail_image", False),
        "provider": "wavespeed",
    }


# ---------------------------------------------------------------------------
# Wavespeed Provider
# ---------------------------------------------------------------------------

class WavespeedVideoProvider(VideoProvider):
    """Video generation provider using Wavespeed API."""

    @property
    def name(self) -> str:
        return "wavespeed"

    def list_models(self) -> list[str]:
        """Return list of available model names."""
        return list_models()

    def get_model_info(self, model: str) -> dict:
        """Return public info about a model."""
        return get_model_info(model)

    def supports_tail_image(self, model: str) -> bool:
        """Check if model supports tail images."""
        config = get_model_config(model)
        return config.get("supports_tail_image", False) if config else False

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        image: Optional[str] = None,
        tail_image: Optional[str] = None,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        cfg_scale: Optional[float] = None,
        loop: bool = False,
        **kwargs,  # Accept and ignore provider-specific params (e.g., motion_strength)
    ) -> VideoGenerationResult:
        """
        Generate video using Wavespeed API.

        Args:
            prompt: Text prompt for video generation
            model: Model name (defaults to wan2.5)
            image: Path to local image file or URL
            tail_image: Path to end frame image (if supported)
            duration: Video duration in seconds
            aspect_ratio: Aspect ratio (ignored - controlled by model)
            negative_prompt: Negative prompt (model-dependent)
            seed: Random seed (-1 for random)
            cfg_scale: Guidance scale (model-dependent)
            loop: Use same image as start and end

        Returns:
            VideoGenerationResult with video URL

        Raises:
            RuntimeError: If generation fails
            ValueError: If configuration is invalid
        """
        model = model or DEFAULT_MODEL
        config = get_model_config(model)
        if not config:
            available = ", ".join(list_models())
            raise ValueError(f"Unknown Wavespeed model: {model}. Available: {available}")

        api_key = os.environ.get("WAVESPEED_API_KEY")
        if not api_key:
            raise RuntimeError("WAVESPEED_API_KEY environment variable not set")

        # Resolve image to base64
        if not image:
            raise ValueError("Wavespeed requires an input image")

        b64_image = self._resolve_image_to_base64(image)

        # Build arguments
        args = self._build_arguments(
            model=model,
            config=config,
            prompt=prompt,
            b64_image=b64_image,
            tail_image=tail_image,
            duration=duration,
            negative_prompt=negative_prompt,
            seed=seed,
            cfg_scale=cfg_scale,
            loop=loop,
        )

        # Submit request
        response = requests.post(
            config["endpoint"],
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=args,
            timeout=60,
        )

        if not response.ok:
            raise RuntimeError(f"Wavespeed API error: {response.status_code} - {response.text}")

        response_data = response.json()

        # Extract request ID (handle different response formats)
        if response_data.get("code") == 200 and "data" in response_data:
            request_id = response_data["data"].get("id")
        else:
            request_id = response_data.get("id")

        if not request_id:
            raise RuntimeError(f"No request ID returned: {response_data}")

        # Poll for result
        video_url = self._poll_for_result(request_id, api_key)

        return VideoGenerationResult(
            video=VideoResult(url=video_url),
            model=model,
            provider=self.name,
            prompt=prompt,
            seed=seed,
            input_image=Path(image) if image and not str(image).startswith(("http://", "https://", "data:")) else None,
            metadata={"duration": duration},
        )

    def _resolve_image_to_base64(self, image: Union[str, Path]) -> str:
        """Convert image path or URL to base64 data URI."""
        if isinstance(image, Path):
            image = str(image)

        if image.startswith("data:"):
            # Already a data URI
            return image

        if image.startswith(("http://", "https://")):
            # Download and encode
            response = requests.get(image, timeout=30)
            response.raise_for_status()
            b64 = base64.b64encode(response.content).decode("utf-8")
            content_type = response.headers.get("Content-Type", "image/jpeg")
            return f"data:{content_type};base64,{b64}"

        # Local file
        path = Path(image)
        if not path.exists():
            raise ValueError(f"Image file not found: {image}")

        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        # Detect content type from extension
        ext = path.suffix.lower()
        content_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }
        content_type = content_types.get(ext, "image/jpeg")
        return f"data:{content_type};base64,{b64}"

    def _build_arguments(
        self,
        *,
        model: str,
        config: dict,
        prompt: str,
        b64_image: str,
        tail_image: Optional[str],
        duration: int,
        negative_prompt: Optional[str],
        seed: Optional[int],
        cfg_scale: Optional[float],
        loop: bool,
    ) -> dict:
        """Build API arguments for Wavespeed request."""
        args = config["default_params"].copy()

        args["prompt"] = prompt
        args["image"] = b64_image

        # Handle duration type
        if config.get("duration_type") == "string":
            args["duration"] = str(duration)
        else:
            args["duration"] = duration

        # Handle tail image / loop
        if config.get("supports_tail_image"):
            tail_param = config.get("tail_image_param", "last_image")
            if loop:
                # Use same image for start and end
                args[tail_param] = b64_image
            elif tail_image:
                args[tail_param] = self._resolve_image_to_base64(tail_image)

        # Override defaults with explicit params
        if negative_prompt is not None and "negative_prompt" in args:
            args["negative_prompt"] = negative_prompt

        if seed is not None and "seed" in args:
            args["seed"] = seed

        if cfg_scale is not None and "guidance_scale" in args:
            args["guidance_scale"] = cfg_scale

        return args

    def _poll_for_result(
        self,
        request_id: str,
        api_key: str,
        max_attempts: int = 180,
        poll_interval: int = 5,
    ) -> str:
        """Poll Wavespeed API for generation result."""
        poll_url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"

        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    poll_url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10,
                )

                if response.ok:
                    result_data = response.json()

                    # Handle wrapped response
                    if result_data.get("code") == 200 and "data" in result_data:
                        result = result_data["data"]
                    else:
                        result = result_data

                    status = result.get("status")

                    if status == "completed":
                        outputs = result.get("outputs", [])
                        if outputs and len(outputs) > 0:
                            return outputs[0]
                        raise RuntimeError(f"No video URL in completed result: {result}")

                    elif status == "failed":
                        error_msg = result.get("error", "Unknown error")
                        raise RuntimeError(f"Video generation failed: {error_msg}")

                    # Continue polling for created, processing, etc.

            except requests.exceptions.RequestException as e:
                # Log but continue polling on network errors
                if attempt >= max_attempts - 1:
                    raise RuntimeError(f"Network error polling result: {e}")

            time.sleep(poll_interval)

        raise RuntimeError(f"Polling timeout after {max_attempts * poll_interval} seconds")
