"""
HuggingFace vision provider.

Uses HuggingFace Gradio Spaces for image captioning. Supports JoyCaption models.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from semiautomatic.lib.vision.base import VisionProvider


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Model configurations (Gradio space + API details)
MODEL_CONFIGS = {
    "joycaption": {
        "space": "fancyfeast/joy-caption-beta-one",
        "api_name": "/generate_caption",
        "caption_types": {
            "short": ("Brief", "50"),
            "normal": ("Descriptive", "150"),
            "long": ("Detailed", "300"),
        },
    },
}

DEFAULT_MODEL = "joycaption"

VALID_LENGTHS = ("short", "normal", "long")


# ---------------------------------------------------------------------------
# Provider Implementation
# ---------------------------------------------------------------------------

class HuggingFaceVisionProvider(VisionProvider):
    """
    HuggingFace vision provider via Gradio Spaces.

    Supports JoyCaption and other vision models hosted on HuggingFace.
    Uses gradio_client for API access.
    """

    def __init__(self):
        self._clients: dict[str, object] = {}

    @property
    def name(self) -> str:
        return "huggingface"

    @property
    def default_model(self) -> str:
        return DEFAULT_MODEL

    def list_models(self) -> list[str]:
        return list(MODEL_CONFIGS.keys())

    def _get_client(self, model: str):
        """Get or create Gradio client for model."""
        if model not in self._clients:
            try:
                from gradio_client import Client
            except ImportError:
                raise ImportError(
                    "gradio_client package not found. Install with: pip install gradio_client"
                )

            config = MODEL_CONFIGS.get(model)
            if not config:
                available = ", ".join(MODEL_CONFIGS.keys())
                raise ValueError(f"Unknown model '{model}'. Available: {available}")

            self._clients[model] = Client(config["space"])

        return self._clients[model]

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
            model: Model to use (default: joycaption).

        Returns:
            Generated caption string.

        Raises:
            ValueError: If length or model is invalid.
            FileNotFoundError: If image doesn't exist.
        """
        model = model or self.default_model

        if length not in VALID_LENGTHS:
            raise ValueError(
                f"Invalid length '{length}'. Use: {', '.join(VALID_LENGTHS)}"
            )

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        config = MODEL_CONFIGS.get(model)
        if not config:
            available = ", ".join(MODEL_CONFIGS.keys())
            raise ValueError(f"Unknown model '{model}'. Available: {available}")

        client = self._get_client(model)
        caption_type, word_count = config["caption_types"].get(length, ("Descriptive", "150"))

        result = client.predict(
            str(image_path),
            caption_type,
            word_count,
            api_name=config["api_name"]
        )

        return result

    def query(
        self,
        image_path: Path,
        question: str,
        *,
        model: Optional[str] = None,
    ) -> str:
        """
        Ask a question about an image.

        Note: JoyCaption is primarily a captioning model, not a VQA model.
        For actual VQA, use a different provider (e.g., fal with moondream3).

        Args:
            image_path: Path to the image file.
            question: Question to ask about the image.
            model: Model to use (default: joycaption).

        Returns:
            Model's response (a detailed caption for joycaption).

        Raises:
            ValueError: If model is invalid.
            FileNotFoundError: If image doesn't exist.
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # JoyCaption doesn't support VQA, return detailed caption
        # Other models added later may support actual VQA
        return self.caption(image_path, length="long", model=model)
