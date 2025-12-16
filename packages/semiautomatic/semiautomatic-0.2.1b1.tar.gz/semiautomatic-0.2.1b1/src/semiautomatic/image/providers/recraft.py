"""
Recraft image generation provider.

Supports text-to-image and image-to-image generation via Recraft API.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

from semiautomatic.lib.logging import log_info, log_error
from semiautomatic.lib.api import download_file
from semiautomatic.image.providers.base import (
    ImageProvider,
    ImageResult,
    GenerationResult,
    ImageSize,
    LoRASpec,
)
from semiautomatic.image.providers.recraft_styles import (
    RECRAFT_STYLES,
    RECRAFT_SIZE_PRESETS,
    RECRAFT_MODELS,
    DEFAULT_STYLE,
    DEFAULT_MODEL,
    DEFAULT_SIZE,
    is_uuid,
    is_valid_style,
    parse_size as parse_recraft_size,
    list_styles,
    list_models as list_recraft_models,
)


# ---------------------------------------------------------------------------
# Recraft Controls
# ---------------------------------------------------------------------------

@dataclass
class RecraftControls:
    """
    Recraft generation controls.

    Attributes:
        artistic_level: Artistic tone 0-5 (0=static/clean, 5=dynamic/eccentric).
        colors: List of hex colors for preferred palette (e.g., ["#FF0000", "#00FF00"]).
        background_color: Desired background color as hex (e.g., "#000000").
        no_text: If True, do not embed text layouts in the image.
    """
    artistic_level: Optional[int] = None
    colors: Optional[list[str]] = None
    background_color: Optional[str] = None
    no_text: bool = False

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        controls = {}

        if self.artistic_level is not None:
            controls["artistic_level"] = self.artistic_level

        if self.colors:
            controls["colors"] = [
                {"rgb": self._hex_to_rgb(c)} for c in self.colors
            ]

        if self.background_color:
            controls["background_color"] = {
                "rgb": self._hex_to_rgb(self.background_color)
            }

        if self.no_text:
            controls["no_text"] = True

        return controls

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> list[int]:
        """Convert hex color to RGB list."""
        h = hex_color.lstrip("#")
        return [int(h[i:i+2], 16) for i in (0, 2, 4)]


# ---------------------------------------------------------------------------
# Recraft Provider
# ---------------------------------------------------------------------------

class RecraftImageProvider(ImageProvider):
    """
    Recraft AI image generation provider.

    Supports text-to-image and image-to-image generation with built-in
    and custom styles.

    Requires RECRAFT_API_KEY environment variable.
    """

    API_BASE = "https://external.api.recraft.ai/v1"

    def __init__(self):
        """Initialize Recraft provider."""
        self._api_key = None

    @property
    def name(self) -> str:
        return "recraft"

    @property
    def _recraft_api_key(self) -> str:
        """Get API key, raising error if not set."""
        if self._api_key is None:
            self._api_key = os.environ.get("RECRAFT_API_KEY")
            if not self._api_key:
                raise EnvironmentError(
                    "RECRAFT_API_KEY environment variable not set. "
                    "Add RECRAFT_API_KEY=your-key to your .env file."
                )
        return self._api_key

    def list_models(self) -> list[str]:
        """List available Recraft model names."""
        return list_recraft_models()

    def get_model_info(self, model: str) -> dict:
        """Get information about a specific model."""
        if model in RECRAFT_MODELS:
            return {"name": model, **RECRAFT_MODELS[model]}
        return {}

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        size: Union[str, ImageSize] = None,
        num_images: int = 1,
        seed: Optional[int] = None,
        loras: Optional[list[LoRASpec]] = None,
        style: Optional[str] = None,
        controls: Optional[RecraftControls] = None,
        output_format: str = "png",
        **kwargs,
    ) -> GenerationResult:
        """
        Generate images from a text prompt.

        Args:
            prompt: Text description of the image (max 1000 bytes).
            model: Model version (recraftv3 or recraftv2).
            size: Size preset or ImageSize.
            num_images: Number of images to generate (1-6).
            seed: Random seed for reproducibility.
            loras: Not supported by Recraft (ignored).
            style: Style name or custom style UUID.
            controls: RecraftControls for fine-tuning generation.
            output_format: Output format ("png" or "jpeg").
            **kwargs: Additional parameters.

        Returns:
            GenerationResult with generated images.
        """
        model = model or DEFAULT_MODEL
        style = style or DEFAULT_STYLE
        size = size or DEFAULT_SIZE

        # Warn if LoRAs provided (not supported)
        if loras:
            log_info("Recraft does not support LoRAs, ignoring")

        # Validate prompt length
        if len(prompt.encode('utf-8')) > 1000:
            raise ValueError("Prompt exceeds 1000 bytes limit")

        # Clamp num_images to 1-6
        num_images = max(1, min(6, num_images))

        # Parse size
        if isinstance(size, ImageSize):
            width, height = size.width, size.height
        elif isinstance(size, str):
            width, height = parse_recraft_size(size)
        else:
            width, height = 1024, 1024

        # Build payload
        payload = self._build_payload(
            prompt=prompt,
            model=model,
            style=style,
            width=width,
            height=height,
            num_images=num_images,
            seed=seed,
            controls=controls,
        )

        # Make API request
        result = self._api_request(
            endpoint="/images/generations",
            payload=payload,
        )

        return self._parse_result(result, model, prompt, style)

    def image_to_image(
        self,
        input_image: Union[str, Path],
        prompt: str,
        *,
        model: Optional[str] = None,
        style: Optional[str] = None,
        strength: float = 0.5,
        num_images: int = 1,
        controls: Optional[RecraftControls] = None,
        output_format: str = "png",
        negative_prompt: Optional[str] = None,
        **kwargs,
    ) -> GenerationResult:
        """
        Apply style transformation to an existing image.

        Args:
            input_image: Path to input image file.
            prompt: Text description of desired changes.
            model: Model version (recraftv3 or recraftv2).
            style: Style name or custom style UUID.
            strength: Transformation strength 0-1 (0=minimal change, 1=full transformation).
            num_images: Number of variations to generate (1-6).
            controls: RecraftControls for fine-tuning.
            output_format: Output format ("png" or "jpeg").
            negative_prompt: Text description of undesired elements.
            **kwargs: Additional parameters.

        Returns:
            GenerationResult with generated images.
        """
        model = model or DEFAULT_MODEL
        style = style or DEFAULT_STYLE

        input_path = Path(input_image)
        if not input_path.exists():
            raise FileNotFoundError(f"Input image not found: {input_image}")

        # Validate prompt length
        if len(prompt.encode('utf-8')) > 1000:
            raise ValueError("Prompt exceeds 1000 bytes limit")

        # Validate strength
        if not 0 <= strength <= 1:
            raise ValueError("Strength must be between 0 and 1")

        # Clamp num_images to 1-6
        num_images = max(1, min(6, num_images))

        # Build form data
        data = self._build_i2i_data(
            prompt=prompt,
            model=model,
            style=style,
            strength=strength,
            num_images=num_images,
            controls=controls,
            negative_prompt=negative_prompt,
        )

        # Make API request with file upload
        result = self._api_request_multipart(
            endpoint="/images/imageToImage",
            data=data,
            image_path=input_path,
        )

        return self._parse_result(result, model, prompt, style)

    def _build_payload(
        self,
        prompt: str,
        model: str,
        style: str,
        width: int,
        height: int,
        num_images: int,
        seed: Optional[int],
        controls: Optional[RecraftControls],
    ) -> dict:
        """Build API payload for text-to-image."""
        payload = {
            "prompt": prompt,
            "model": model,
            "size": f"{width}x{height}",
            "n": num_images,
            "response_format": "url",
        }

        # Handle style (built-in vs custom UUID)
        if is_uuid(style):
            payload["style_id"] = style
        else:
            if style not in RECRAFT_STYLES:
                raise ValueError(
                    f"Unknown style: {style}. "
                    f"Available: {', '.join(RECRAFT_STYLES.keys())} or provide a custom UUID"
                )
            payload["style"] = style

        if seed is not None:
            payload["seed"] = seed

        if controls:
            controls_dict = controls.to_dict()
            if controls_dict:
                payload["controls"] = controls_dict

        return payload

    def _build_i2i_data(
        self,
        prompt: str,
        model: str,
        style: str,
        strength: float,
        num_images: int,
        controls: Optional[RecraftControls],
        negative_prompt: Optional[str],
    ) -> dict:
        """Build form data for image-to-image."""
        import json

        data = {
            "prompt": prompt,
            "model": model,
            "strength": strength,
            "n": num_images,
            "response_format": "url",
        }

        # Handle style (built-in vs custom UUID)
        if is_uuid(style):
            data["style_id"] = style
        else:
            if style not in RECRAFT_STYLES:
                raise ValueError(
                    f"Unknown style: {style}. "
                    f"Available: {', '.join(RECRAFT_STYLES.keys())} or provide a custom UUID"
                )
            data["style"] = style

        if negative_prompt:
            data["negative_prompt"] = negative_prompt

        if controls:
            controls_dict = controls.to_dict()
            if controls_dict:
                data["controls"] = json.dumps(controls_dict)

        return data

    def _api_request(self, endpoint: str, payload: dict) -> dict:
        """Make JSON API request."""
        import requests

        response = requests.post(
            f"{self.API_BASE}{endpoint}",
            headers={
                "Authorization": f"Bearer {self._recraft_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )

        response.raise_for_status()
        return response.json()

    def _api_request_multipart(
        self,
        endpoint: str,
        data: dict,
        image_path: Path,
    ) -> dict:
        """Make multipart form API request with image upload."""
        import requests

        with open(image_path, 'rb') as f:
            files = {'image': (image_path.name, f, 'image/png')}

            response = requests.post(
                f"{self.API_BASE}{endpoint}",
                headers={"Authorization": f"Bearer {self._recraft_api_key}"},
                data=data,
                files=files,
                timeout=120,
            )

        response.raise_for_status()
        return response.json()

    def _parse_result(
        self,
        result: dict,
        model: str,
        prompt: str,
        style: str,
    ) -> GenerationResult:
        """Parse API response into GenerationResult."""
        if "data" not in result:
            raise ValueError(f"Unexpected API response format: {result}")

        images = []
        for img_data in result["data"]:
            url = img_data.get("url", "")
            if not url:
                continue

            images.append(ImageResult(
                url=url,
                width=img_data.get("width", 0),
                height=img_data.get("height", 0),
                content_type=img_data.get("content_type"),
            ))

        if not images:
            raise ValueError("No images returned from Recraft API")

        return GenerationResult(
            images=images,
            model=model,
            provider=self.name,
            prompt=prompt,
            metadata={"style": style, "raw_result": result},
        )
