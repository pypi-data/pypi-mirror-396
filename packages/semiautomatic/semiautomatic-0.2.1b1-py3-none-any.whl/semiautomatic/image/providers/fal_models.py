"""
FAL model configurations for image generation.

Centralizes all FAL model configs in one place for easy maintenance.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Model Configurations
# ---------------------------------------------------------------------------

FAL_MODELS = {
    "flux-dev": {
        "endpoint": "fal-ai/flux/dev",
        "description": "FLUX.1 Dev - balanced quality and speed",
        "architecture": "flux",
        "supports_loras": False,
        "default_params": {
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "enable_safety_checker": True,
            "output_format": "png",
        },
    },
    "flux-schnell": {
        "endpoint": "fal-ai/flux/schnell",
        "description": "FLUX.1 Schnell - ultra-fast generation (4 steps)",
        "architecture": "flux",
        "supports_loras": False,
        "default_params": {
            "num_inference_steps": 4,
            "enable_safety_checker": True,
            "output_format": "png",
        },
    },
    "flux-pro": {
        "endpoint": "fal-ai/flux-pro",
        "description": "FLUX.1 Pro - highest quality generation",
        "architecture": "flux",
        "supports_loras": False,
        "default_params": {
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "enable_safety_checker": True,
            "output_format": "png",
        },
    },
    "flux-krea": {
        "endpoint": "fal-ai/flux-krea-lora",
        "description": "FLUX.1 Krea [dev] with LoRA support",
        "architecture": "flux",
        "supports_loras": True,
        "default_params": {
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "enable_safety_checker": True,
            "output_format": "png",
        },
    },
    "qwen": {
        "endpoint": "fal-ai/qwen-image",
        "description": "Qwen Image - high-quality with LoRA support",
        "architecture": "qwen",
        "supports_loras": True,
        "default_params": {
            "num_inference_steps": 30,
            "guidance_scale": 2.5,
            "enable_safety_checker": True,
            "output_format": "png",
        },
    },
    "wan-22": {
        "endpoint": "fal-ai/wan/v2.2-a14b/text-to-image/lora",
        "description": "WAN 2.2 14B - enhanced prompt alignment with LoRA",
        "architecture": "wan",
        "supports_loras": True,
        "supports_batch": False,  # WAN-22 doesn't support batch generation
        "default_params": {
            "num_inference_steps": 36,
            "guidance_scale": 3.5,
            "guidance_scale_2": 4,
            "shift": 2,
            "enable_safety_checker": False,
            "enable_output_safety_checker": False,
            "enable_prompt_expansion": False,
            "output_format": "png",
        },
    },
}

# Default model when none specified
DEFAULT_MODEL = "flux-dev"


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def get_model_config(model_name: str) -> dict:
    """
    Get configuration for a model.

    Args:
        model_name: Model name.

    Returns:
        Model configuration dict.

    Raises:
        ValueError: If model not found.
    """
    if model_name not in FAL_MODELS:
        available = ", ".join(FAL_MODELS.keys())
        raise ValueError(f"Unknown FAL model: {model_name}. Available: {available}")

    return FAL_MODELS[model_name]


def list_models() -> list[str]:
    """List available FAL model names."""
    return list(FAL_MODELS.keys())


def get_models_with_lora_support() -> list[str]:
    """List models that support LoRA."""
    return [
        name for name, config in FAL_MODELS.items()
        if config.get("supports_loras", False)
    ]
