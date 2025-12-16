"""
FAL vision provider.

Uses FAL.ai for image captioning and queries. Supports Moondream models.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from semiautomatic.lib.vision.base import VisionProvider


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Model endpoints
MODEL_ENDPOINTS = {
    "moondream3": {
        "caption": "fal-ai/moondream3-preview/caption",
        "query": "fal-ai/moondream3-preview/query",
    },
}

DEFAULT_MODEL = "moondream3"

VALID_LENGTHS = ("short", "normal", "long")


# ---------------------------------------------------------------------------
# Provider Implementation
# ---------------------------------------------------------------------------

class FalVisionProvider(VisionProvider):
    """
    FAL vision provider.

    Supports Moondream models via FAL.ai infrastructure.
    Requires FAL_KEY environment variable.
    """

    def __init__(self):
        self._client = None

    @property
    def name(self) -> str:
        return "fal"

    @property
    def default_model(self) -> str:
        return DEFAULT_MODEL

    def list_models(self) -> list[str]:
        return list(MODEL_ENDPOINTS.keys())

    @property
    def _fal_client(self):
        """Lazy-load FAL client."""
        if self._client is None:
            try:
                import fal_client
            except ImportError:
                raise ImportError(
                    "fal_client package not found. Install with: pip install fal-client"
                )

            if not os.environ.get("FAL_KEY"):
                raise EnvironmentError(
                    "FAL_KEY environment variable not set. "
                    "Add FAL_KEY=... to your .env file."
                )

            self._client = fal_client

        return self._client

    def _get_endpoints(self, model: Optional[str] = None) -> dict:
        """Get endpoints for the specified model."""
        model = model or self.default_model
        if model not in MODEL_ENDPOINTS:
            available = ", ".join(MODEL_ENDPOINTS.keys())
            raise ValueError(f"Unknown model '{model}'. Available: {available}")
        return MODEL_ENDPOINTS[model]

    def caption(
        self,
        image_path: Path,
        *,
        length: str = "normal",
        model: Optional[str] = None,
    ) -> str:
        """
        Generate a caption for an image.

        Args:
            image_path: Path to the image file.
            length: Caption length - "short", "normal", or "long".
            model: Model to use (default: moondream3).

        Returns:
            Generated caption string.

        Raises:
            ValueError: If length or model is invalid.
            FileNotFoundError: If image doesn't exist.
        """
        if length not in VALID_LENGTHS:
            raise ValueError(
                f"Invalid length '{length}'. Use: {', '.join(VALID_LENGTHS)}"
            )

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        endpoints = self._get_endpoints(model)
        image_url = self._fal_client.upload_file(str(image_path))

        result = self._fal_client.run(
            endpoints["caption"],
            arguments={
                "image_url": image_url,
                "length": length,
            },
        )

        return result["output"]

    def query(
        self,
        image_path: Path,
        question: str,
        *,
        model: Optional[str] = None,
    ) -> str:
        """
        Ask a question about an image.

        Args:
            image_path: Path to the image file.
            question: Question to ask about the image.
            model: Model to use (default: moondream3).

        Returns:
            Model's response to the question.

        Raises:
            ValueError: If model is invalid.
            FileNotFoundError: If image doesn't exist.
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        endpoints = self._get_endpoints(model)
        image_url = self._fal_client.upload_file(str(image_path))

        result = self._fal_client.run(
            endpoints["query"],
            arguments={
                "image_url": image_url,
                "prompt": question,
            },
        )

        return result["output"]
