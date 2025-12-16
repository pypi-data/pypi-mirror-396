"""
FAL image generation provider.

Supports FLUX, Qwen, and WAN models via FAL.ai API.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union

from semiautomatic.lib.logging import log_info, log_error
from semiautomatic.image.providers.base import (
    ImageProvider,
    ImageResult,
    GenerationResult,
    ImageSize,
    LoRASpec,
    parse_image_size,
    IMAGE_SIZE_PRESETS,
)
from semiautomatic.image.providers.fal_models import (
    FAL_MODELS,
    DEFAULT_MODEL,
    get_model_config,
    list_models as list_fal_models,
)


# ---------------------------------------------------------------------------
# FAL Provider
# ---------------------------------------------------------------------------

class FALImageProvider(ImageProvider):
    """
    FAL.ai image generation provider.

    Supports FLUX, Qwen, and WAN models with optional LoRA support.

    Requires FAL_KEY environment variable.
    """

    def __init__(self, storage_backend=None):
        """
        Initialize FAL provider.

        Args:
            storage_backend: Optional storage backend for LoRA uploads.
                If not provided, will use default from lib.storage.
        """
        self._client = None
        self._storage = storage_backend

    @property
    def name(self) -> str:
        return "fal"

    @property
    def _fal_client(self):
        """Lazy-load FAL client."""
        if self._client is None:
            try:
                import fal_client
            except ImportError:
                raise ImportError(
                    "fal_client package not found. "
                    "Install with: pip install semiautomatic[generate]"
                )

            api_key = os.environ.get("FAL_KEY")
            if not api_key:
                raise EnvironmentError(
                    "FAL_KEY environment variable not set. "
                    "Add FAL_KEY=your-key to your .env file."
                )

            fal_client.api_key = api_key
            self._client = fal_client

        return self._client

    def list_models(self) -> list[str]:
        """List available FAL model names."""
        return list_fal_models()

    def get_model_info(self, model: str) -> dict:
        """Get information about a specific model."""
        try:
            config = get_model_config(model)
            return {
                "name": model,
                "description": config.get("description", ""),
                "supports_loras": config.get("supports_loras", False),
                "architecture": config.get("architecture", ""),
            }
        except ValueError:
            return {}

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        size: Union[str, ImageSize] = "landscape_4_3",
        num_images: int = 1,
        seed: Optional[int] = None,
        loras: Optional[list[LoRASpec]] = None,
        steps: Optional[int] = None,
        guidance: Optional[float] = None,
        output_format: str = "png",
        on_progress: Optional[callable] = None,
        **kwargs,
    ) -> GenerationResult:
        """
        Generate images from a text prompt.

        Args:
            prompt: Text description of the image to generate.
            model: Model name (default: flux-dev).
            size: Image size as preset name, "WxH", or ImageSize.
            num_images: Number of images to generate (1-4).
            seed: Random seed for reproducibility.
            loras: List of LoRA specifications to apply.
            steps: Override number of inference steps.
            guidance: Override guidance scale.
            output_format: Output format ("png" or "jpeg").
            on_progress: Optional callback for progress updates.
            **kwargs: Additional model-specific parameters.

        Returns:
            GenerationResult with generated images.
        """
        model = model or DEFAULT_MODEL
        config = get_model_config(model)

        # Build arguments
        args = self._build_arguments(
            prompt=prompt,
            config=config,
            size=size,
            num_images=num_images,
            seed=seed,
            loras=loras,
            steps=steps,
            guidance=guidance,
            output_format=output_format,
            **kwargs,
        )

        # Handle WAN-22 which doesn't support batch generation
        if not config.get("supports_batch", True) and num_images > 1:
            return self._generate_sequential(
                model=model,
                config=config,
                args=args,
                num_images=num_images,
                prompt=prompt,
                on_progress=on_progress,
            )

        # Standard generation
        return self._generate_batch(
            model=model,
            config=config,
            args=args,
            prompt=prompt,
            on_progress=on_progress,
        )

    def _build_arguments(
        self,
        prompt: str,
        config: dict,
        size: Union[str, ImageSize],
        num_images: int,
        seed: Optional[int],
        loras: Optional[list[LoRASpec]],
        steps: Optional[int],
        guidance: Optional[float],
        output_format: str,
        **kwargs,
    ) -> dict:
        """Build FAL API arguments."""
        # Start with model defaults
        args = config.get("default_params", {}).copy()

        # Set prompt
        args["prompt"] = prompt

        # Set image size
        parsed_size = parse_image_size(size)
        if isinstance(parsed_size, ImageSize):
            args["image_size"] = {"width": parsed_size.width, "height": parsed_size.height}
        else:
            args["image_size"] = parsed_size

        # Set num images (clamped to 1-4)
        args["num_images"] = max(1, min(4, num_images))

        # Optional overrides
        if seed is not None:
            args["seed"] = seed

        if steps is not None:
            args["num_inference_steps"] = steps

        if guidance is not None:
            args["guidance_scale"] = guidance

        if output_format:
            args["output_format"] = output_format

        # Handle LoRAs
        if loras and config.get("supports_loras", False):
            args["loras"] = self._prepare_loras(loras, config.get("architecture"))
        elif loras:
            log_info(f"Model {config.get('name', 'unknown')} does not support LoRAs, ignoring")

        # Merge any additional kwargs
        args.update(kwargs)

        return args

    def _prepare_loras(
        self,
        loras: list[LoRASpec],
        architecture: Optional[str] = None,
    ) -> list[dict]:
        """Prepare LoRA specifications for API call."""
        prepared = []

        for lora in loras:
            lora_url = lora.path

            # If it's a local path, upload to storage
            if not lora.path.startswith("http"):
                lora_path = Path(lora.path)
                if lora_path.exists():
                    lora_url = self._upload_lora(lora_path)
                else:
                    log_error(f"LoRA file not found: {lora.path}")
                    continue

            prepared.append({
                "path": lora_url,
                "scale": lora.scale,
            })

        return prepared

    def _upload_lora(self, lora_path: Path) -> str:
        """Upload LoRA file to storage and return URL."""
        if self._storage is None:
            from semiautomatic.lib.storage import get_storage_backend
            self._storage = get_storage_backend()

        log_info(f"Uploading LoRA: {lora_path.name}")
        return self._storage.upload_lora(lora_path)

    def _generate_batch(
        self,
        model: str,
        config: dict,
        args: dict,
        prompt: str,
        on_progress: Optional[callable],
    ) -> GenerationResult:
        """Generate images in a single batch request."""
        fal = self._fal_client

        def handle_queue_update(update):
            if on_progress and hasattr(update, "logs"):
                for log in update.logs:
                    on_progress(log.get("message", ""))

        result = fal.subscribe(
            config["endpoint"],
            arguments=args,
            with_logs=True,
            on_queue_update=handle_queue_update,
        )

        return self._parse_result(result, model, prompt)

    def _generate_sequential(
        self,
        model: str,
        config: dict,
        args: dict,
        num_images: int,
        prompt: str,
        on_progress: Optional[callable],
    ) -> GenerationResult:
        """Generate images sequentially (for models that don't support batch)."""
        import time

        fal = self._fal_client
        args["num_images"] = 1

        all_images = []

        for i in range(num_images):
            if on_progress:
                on_progress(f"Generating image {i + 1}/{num_images}...")

            def handle_queue_update(update):
                if on_progress and hasattr(update, "logs"):
                    for log in update.logs:
                        on_progress(log.get("message", ""))

            result = fal.subscribe(
                config["endpoint"],
                arguments=args,
                with_logs=True,
                on_queue_update=handle_queue_update,
            )

            # Parse and collect images
            parsed = self._parse_result(result, model, prompt)
            all_images.extend(parsed.images)

            # Small delay between requests
            if i < num_images - 1:
                time.sleep(0.5)

        return GenerationResult(
            images=all_images,
            model=model,
            provider=self.name,
            prompt=prompt,
        )

    def _parse_result(self, result: dict, model: str, prompt: str) -> GenerationResult:
        """Parse FAL API result into GenerationResult."""
        # Handle both formats: {"images": [...]} and {"image": {...}}
        images_data = result.get("images", [])
        if not images_data and "image" in result:
            images_data = [result["image"]]

        if not images_data:
            raise ValueError(f"No images returned from FAL API. Result: {result}")

        images = []
        for img_data in images_data:
            images.append(ImageResult(
                url=img_data.get("url", ""),
                width=img_data.get("width", 0),
                height=img_data.get("height", 0),
                content_type=img_data.get("content_type"),
            ))

        return GenerationResult(
            images=images,
            model=model,
            provider=self.name,
            prompt=prompt,
            seed=result.get("seed"),
            metadata={"raw_result": result},
        )
