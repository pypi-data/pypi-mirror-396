"""
Freepik image upscaling provider.

Supports 2x and 4x upscaling with various optimization presets.
"""

from __future__ import annotations

import base64
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union, Literal

from semiautomatic.lib.logging import log_info, log_error
from semiautomatic.lib.api import download_file
from semiautomatic.defaults import (
    API_DEFAULT_POLL_INTERVAL,
    API_DEFAULT_POLL_TIMEOUT,
)


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

ScaleFactor = Literal["2x", "4x", "8x", "16x"]
UpscaleEngine = Literal["automatic", "magnific_illusio", "magnific_sharpy", "magnific_sparkle"]
OptimizedFor = Literal[
    "standard",
    "soft_portraits",
    "hard_portraits",
    "art_n_illustration",
    "videogame_assets",
    "nature_n_landscapes",
    "films_n_photography",
    "3d_renders",
    "science_fiction_n_horror",
]


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class UpscaleSettings:
    """
    Settings for image upscaling.

    Attributes:
        scale: Scale factor ("2x" or "4x").
        engine: Upscaling engine to use.
        optimized_for: Optimization preset for content type.
        creativity: Creativity level 0-10 (higher = more creative).
        hdr: HDR enhancement level 0-10.
        resemblance: Resemblance to original 0-10.
        fractality: Detail fractality 0-10.
        prompt: Optional text prompt to guide upscaling.
    """
    scale: ScaleFactor = "2x"
    engine: UpscaleEngine = "automatic"
    optimized_for: OptimizedFor = "standard"
    creativity: int = 0
    hdr: int = 0
    resemblance: int = 0
    fractality: int = 0
    prompt: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to API payload format."""
        payload = {
            "scale_factor": self.scale,
            "engine": self.engine,
            "optimized_for": self.optimized_for,
            "creativity": self.creativity,
            "hdr": self.hdr,
            "resemblance": self.resemblance,
            "fractality": self.fractality,
        }
        if self.prompt:
            payload["prompt"] = self.prompt
        return payload


@dataclass
class UpscaleResult:
    """Result from an upscale operation."""
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    path: Optional[Path] = None
    task_id: Optional[str] = None
    original_path: Optional[Path] = None


# ---------------------------------------------------------------------------
# Freepik Provider
# ---------------------------------------------------------------------------

class FreepikUpscaleProvider:
    """
    Freepik AI image upscaling provider.

    Supports 2x and 4x upscaling with multiple engines and optimization presets.

    Requires FREEPIK_API_KEY environment variable.
    """

    API_URL = "https://api.freepik.com/v1/ai/image-upscaler"
    TASK_STATUS_URL = "https://api.freepik.com/v1/ai/image-upscaler/"

    def __init__(self):
        """Initialize Freepik provider."""
        self._api_key = None

    @property
    def name(self) -> str:
        return "freepik"

    @property
    def _freepik_api_key(self) -> str:
        """Get API key, raising error if not set."""
        if self._api_key is None:
            self._api_key = os.environ.get("FREEPIK_API_KEY")
            if not self._api_key:
                raise EnvironmentError(
                    "FREEPIK_API_KEY environment variable not set. "
                    "Add FREEPIK_API_KEY=your-key to your .env file."
                )
        return self._api_key

    def upscale(
        self,
        image: Union[str, Path, bytes],
        *,
        settings: Optional[UpscaleSettings] = None,
        scale: ScaleFactor = "2x",
        engine: UpscaleEngine = "automatic",
        optimized_for: OptimizedFor = "standard",
        prompt: Optional[str] = None,
        creativity: int = 0,
        hdr: int = 0,
        resemblance: int = 0,
        fractality: int = 0,
        poll_interval: float = None,
        poll_timeout: float = None,
        on_progress: Optional[callable] = None,
    ) -> UpscaleResult:
        """
        Upscale an image.

        Args:
            image: Image path or bytes.
            settings: UpscaleSettings object (overrides individual params).
            scale: Scale factor ("2x" or "4x").
            engine: Upscaling engine.
            optimized_for: Optimization preset.
            prompt: Text prompt to guide upscaling.
            creativity: Creativity level 0-10.
            hdr: HDR enhancement level 0-10.
            resemblance: Resemblance to original 0-10.
            fractality: Detail fractality 0-10.
            poll_interval: Seconds between status checks.
            poll_timeout: Maximum seconds to wait for result.
            on_progress: Optional callback for progress updates.

        Returns:
            UpscaleResult with URL to upscaled image.
        """
        poll_interval = poll_interval or API_DEFAULT_POLL_INTERVAL
        poll_timeout = poll_timeout or API_DEFAULT_POLL_TIMEOUT

        # Build settings
        if settings is None:
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

        # Encode image
        image_data, original_path = self._encode_image(image)

        # Submit task
        task_id = self._submit_task(image_data, settings)

        if on_progress:
            on_progress(f"Task submitted: {task_id[:8]}...")

        # Poll for result
        download_url = self._poll_for_result(
            task_id=task_id,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
            on_progress=on_progress,
        )

        return UpscaleResult(
            url=download_url,
            task_id=task_id,
            original_path=original_path,
        )

    def _encode_image(self, image: Union[str, Path, bytes]) -> tuple[str, Optional[Path]]:
        """Encode image to base64."""
        if isinstance(image, bytes):
            return base64.b64encode(image).decode('utf-8'), None

        image_path = Path(image)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image}")

        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8'), image_path

    def _submit_task(self, image_data: str, settings: UpscaleSettings) -> str:
        """Submit upscale task and return task ID."""
        import requests

        payload = settings.to_dict()
        payload["image"] = image_data

        response = requests.post(
            self.API_URL,
            headers={
                "Content-Type": "application/json",
                "x-freepik-api-key": self._freepik_api_key,
            },
            json=payload,
            timeout=60,
        )

        response.raise_for_status()
        result = response.json()

        task_id = result.get("data", {}).get("task_id")
        if not task_id:
            raise ValueError(f"No task ID in response: {result}")

        return task_id

    def _poll_for_result(
        self,
        task_id: str,
        poll_interval: float,
        poll_timeout: float,
        on_progress: Optional[callable],
    ) -> str:
        """Poll for task completion and return download URL."""
        import requests

        start_time = time.time()
        attempt = 0

        while time.time() - start_time < poll_timeout:
            attempt += 1

            try:
                response = requests.get(
                    f"{self.TASK_STATUS_URL}{task_id}",
                    headers={"x-freepik-api-key": self._freepik_api_key},
                    timeout=30,
                )

                if response.status_code != 200:
                    if on_progress:
                        on_progress(f"Poll error: {response.status_code}")
                    time.sleep(poll_interval)
                    continue

                result = response.json()
                data = result.get("data", {})
                status = data.get("status", "").lower()

                if on_progress and attempt % 3 == 0:
                    on_progress(f"Status: {status} (attempt {attempt})")

                if status in ["succeeded", "completed"]:
                    download_url = self._find_download_url(result)
                    if download_url:
                        return download_url

                elif status in ["failed", "error"]:
                    error_msg = data.get("error", result.get("error", "Unknown error"))
                    raise RuntimeError(f"Upscale failed: {error_msg}")

            except requests.RequestException as e:
                if on_progress:
                    on_progress(f"Request error: {e}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Upscale timed out after {poll_timeout}s")

    def _find_download_url(self, data: dict) -> Optional[str]:
        """Extract download URL from API response."""
        if isinstance(data, dict) and "data" in data:
            data_obj = data["data"]
            if "generated" in data_obj and isinstance(data_obj["generated"], list):
                if data_obj["generated"]:
                    return data_obj["generated"][0]

        # Recursive search
        if not isinstance(data, dict):
            return None

        for key, value in data.items():
            if key == "generated" and isinstance(value, list) and value:
                return value[0]
            if key == "download_url":
                return value
            if key == "url" and isinstance(value, str) and value.startswith("http"):
                return value
            if isinstance(value, dict):
                url = self._find_download_url(value)
                if url:
                    return url

        return None

    def get_engines(self) -> list[str]:
        """List available upscaling engines."""
        return ["automatic", "magnific_illusio", "magnific_sharpy", "magnific_sparkle"]

    def get_optimization_presets(self) -> list[str]:
        """List available optimization presets."""
        return [
            "standard",
            "soft_portraits",
            "hard_portraits",
            "art_n_illustration",
            "videogame_assets",
            "nature_n_landscapes",
            "films_n_photography",
            "3d_renders",
            "science_fiction_n_horror",
        ]
