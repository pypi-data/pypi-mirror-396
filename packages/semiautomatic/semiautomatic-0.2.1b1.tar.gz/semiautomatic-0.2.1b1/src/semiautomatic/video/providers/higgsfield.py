"""
Higgsfield video generation provider.

Supports: dop-lite, dop-preview, dop-turbo models with 120 motion presets.
"""

from __future__ import annotations

import os
import random
import time
from pathlib import Path
from typing import Optional, Union

import requests

from semiautomatic.video.providers.base import (
    VideoProvider,
    VideoResult,
    VideoGenerationResult,
)
from semiautomatic.video.providers.motions import (
    HIGGSFIELD_MOTIONS,
    get_motion_id,
    is_valid_motion,
    list_motions,
)
from semiautomatic.lib.storage import get_storage_backend


# ---------------------------------------------------------------------------
# Higgsfield Model Configurations
# ---------------------------------------------------------------------------

HIGGSFIELD_MODELS = {
    "higgsfield": {
        "model": "dop-preview",
        "description": "Higgsfield DOP Preview (default, balanced quality/speed)",
    },
    "higgsfield_preview": {
        "model": "dop-preview",
        "description": "Higgsfield DOP Preview (balanced quality/speed)",
    },
    "higgsfield_lite": {
        "model": "dop-lite",
        "description": "Higgsfield DOP Lite (faster, lower quality)",
    },
    "higgsfield_turbo": {
        "model": "dop-turbo",
        "description": "Higgsfield DOP Turbo (fastest)",
    },
}

DEFAULT_MODEL = "higgsfield"
DEFAULT_MOTION = "general"
DEFAULT_MOTION_STRENGTH = 0.5

ENDPOINT = "https://platform.higgsfield.ai/v1/image2video"
POLL_ENDPOINT = "https://platform.higgsfield.ai/v1/job-sets"


def list_models() -> list[str]:
    """Return list of available Higgsfield model names."""
    return list(HIGGSFIELD_MODELS.keys())


def get_model_config(model: str) -> Optional[dict]:
    """Return configuration for a specific model, or None if not found."""
    return HIGGSFIELD_MODELS.get(model)


def get_model_info(model: str) -> dict:
    """Return public info about a model for display."""
    config = HIGGSFIELD_MODELS.get(model)
    if not config:
        return {}
    return {
        "name": model,
        "description": config.get("description", ""),
        "supports_tail_image": False,
        "supports_motion": True,
        "provider": "higgsfield",
    }


# ---------------------------------------------------------------------------
# Higgsfield Provider
# ---------------------------------------------------------------------------

class HiggsfieldVideoProvider(VideoProvider):
    """Video generation provider using Higgsfield API."""

    @property
    def name(self) -> str:
        return "higgsfield"

    def list_models(self) -> list[str]:
        """Return list of available model names."""
        return list_models()

    def get_model_info(self, model: str) -> dict:
        """Return public info about a model."""
        return get_model_info(model)

    def supports_tail_image(self, model: str) -> bool:
        """Higgsfield does not support tail images."""
        return False

    def supports_motion(self) -> bool:
        """Higgsfield supports motion presets."""
        return True

    def list_motions(self) -> list[str]:
        """Return list of available motion preset names."""
        return list_motions()

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
        motion: Optional[str] = None,
        motion_strength: Optional[float] = None,
        **kwargs,
    ) -> VideoGenerationResult:
        """
        Generate video using Higgsfield API.

        Args:
            prompt: Text prompt for video generation
            model: Model name (defaults to higgsfield/dop-preview)
            image: Path to local image file or URL
            tail_image: Ignored (not supported)
            duration: Ignored (fixed duration)
            aspect_ratio: Ignored (controlled by input image)
            negative_prompt: Ignored
            seed: Random seed (uses random if not specified)
            cfg_scale: Ignored
            loop: Ignored
            motion: Motion preset name (e.g., "zoom_in", "dolly_out")
            motion_strength: Motion intensity (0.0-1.0, default 0.5)

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
            raise ValueError(f"Unknown Higgsfield model: {model}. Available: {available}")

        api_key = os.environ.get("HIGGSFIELD_API_KEY")
        api_secret = os.environ.get("HIGGSFIELD_SECRET")
        if not api_key or not api_secret:
            raise RuntimeError(
                "HIGGSFIELD_API_KEY and HIGGSFIELD_SECRET environment variables required"
            )

        # Validate motion preset
        motion = motion or DEFAULT_MOTION
        if not is_valid_motion(motion):
            raise ValueError(
                f"Unknown motion preset: {motion}. "
                f"Use list_motions() to see available presets."
            )

        # Resolve image URL
        if not image:
            raise ValueError("Higgsfield requires an input image")

        image_url = self._resolve_image_url(image)

        # Build request
        motion_strength = motion_strength if motion_strength is not None else DEFAULT_MOTION_STRENGTH
        seed = seed if seed is not None else random.randint(1, 999999)

        request_body = {
            "params": {
                "model": config["model"],
                "prompt": prompt,
                "seed": seed,
                "motions": [
                    {
                        "id": get_motion_id(motion),
                        "strength": motion_strength,
                    }
                ],
                "input_images": [
                    {
                        "type": "image_url",
                        "image_url": image_url,
                    }
                ],
                "enhance_prompt": True,
                "check_nsfw": True,
            }
        }

        # Submit request
        response = requests.post(
            ENDPOINT,
            headers={
                "hf-api-key": api_key,
                "hf-secret": api_secret,
                "Content-Type": "application/json",
            },
            json=request_body,
            timeout=60,
        )

        if not response.ok:
            raise RuntimeError(f"Higgsfield API error: {response.status_code} - {response.text}")

        result = response.json()
        job_id = result.get("id")

        if not job_id:
            raise RuntimeError(f"No job ID returned: {result}")

        # Poll for result
        video_url = self._poll_for_result(job_id, api_key, api_secret)

        return VideoGenerationResult(
            video=VideoResult(url=video_url),
            model=model,
            provider=self.name,
            prompt=prompt,
            seed=seed,
            input_image=Path(image) if image and not str(image).startswith(("http://", "https://")) else None,
            metadata={
                "motion": motion,
                "motion_strength": motion_strength,
            },
        )

    def _resolve_image_url(self, image: Union[str, Path]) -> str:
        """
        Resolve image to URL.

        Higgsfield requires image URLs, not base64. For local files,
        we upload to storage first.
        """
        if isinstance(image, Path):
            image = str(image)

        if image.startswith(("http://", "https://")):
            return image

        # Local file - need to upload
        path = Path(image)
        if not path.exists():
            raise ValueError(f"Image file not found: {image}")

        # Try to get storage backend
        try:
            storage = get_storage_backend()
            key = f"input/{path.name}"
            url = storage.upload(path, key)
            return url
        except Exception as e:
            raise RuntimeError(
                f"Failed to upload local image. Higgsfield requires image URLs. "
                f"Either provide a URL or configure R2 storage. Error: {e}"
            )

    def _poll_for_result(
        self,
        job_id: str,
        api_key: str,
        api_secret: str,
        max_attempts: int = 180,
        poll_interval: int = 5,
    ) -> str:
        """Poll Higgsfield API for generation result."""
        poll_url = f"{POLL_ENDPOINT}/{job_id}"

        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    poll_url,
                    headers={
                        "hf-api-key": api_key,
                        "hf-secret": api_secret,
                    },
                    timeout=10,
                )

                if response.ok:
                    data = response.json()

                    if "jobs" in data and len(data["jobs"]) > 0:
                        job = data["jobs"][0]
                        status = job.get("status")

                        if status == "completed":
                            results = job.get("results", {})

                            # Prefer min quality (smaller file), fallback to raw
                            video_url = None
                            if "min" in results and results["min"].get("url"):
                                video_url = results["min"]["url"]
                            elif "raw" in results and results["raw"].get("url"):
                                video_url = results["raw"]["url"]

                            if video_url:
                                return video_url
                            raise RuntimeError(f"No video URL in completed result: {results}")

                        elif status == "failed":
                            error_msg = job.get("error", "Unknown error")
                            raise RuntimeError(f"Video generation failed: {error_msg}")

                        # Continue polling for queued, processing, in_progress

            except requests.exceptions.RequestException as e:
                # Log but continue polling on network errors
                if attempt >= max_attempts - 1:
                    raise RuntimeError(f"Network error polling result: {e}")

            time.sleep(poll_interval)

        raise RuntimeError(f"Polling timeout after {max_attempts * poll_interval} seconds")
