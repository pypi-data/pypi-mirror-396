"""
FAL video model configurations.

Centralizes all FAL video model configurations in one place.
"""

from __future__ import annotations

from typing import Optional


# ---------------------------------------------------------------------------
# Model Configurations
# ---------------------------------------------------------------------------

FAL_VIDEO_MODELS = {
    "kling1.5": {
        "endpoint": "fal-ai/kling-video/v1.5/pro/image-to-video",
        "description": "Kling 1.5 Pro - balanced quality and speed",
        "supports_tail_image": True,
        "tail_image_param": "tail_image_url",
        "start_image_param": "image_url",
        "durations": [5, 10],
        "default_params": {
            "aspect_ratio": "16:9",
            "negative_prompt": "blur, distort, and low quality",
            "cfg_scale": 0.5,
        },
    },
    "kling1.6": {
        "endpoint": "fal-ai/kling-video/v1.6/pro/image-to-video",
        "description": "Kling 1.6 Pro - improved motion consistency",
        "supports_tail_image": True,
        "tail_image_param": "tail_image_url",
        "start_image_param": "image_url",
        "durations": [5, 10],
        "default_params": {
            "aspect_ratio": "16:9",
            "negative_prompt": "blur, distort, and low quality",
            "cfg_scale": 0.5,
        },
    },
    "kling2.0": {
        "endpoint": "fal-ai/kling-video/v2/master/image-to-video",
        "description": "Kling 2.0 Master - high quality, no tail image",
        "supports_tail_image": False,
        "start_image_param": "image_url",
        "durations": [5, 10],
        "default_params": {
            "aspect_ratio": "16:9",
            "negative_prompt": "blur, distort, and low quality",
            "cfg_scale": 0.5,
        },
    },
    "kling2.1": {
        "endpoint": "fal-ai/kling-video/v2.1/pro/image-to-video",
        "description": "Kling 2.1 Pro - excellent motion quality (default)",
        "supports_tail_image": True,
        "tail_image_param": "tail_image_url",
        "start_image_param": "image_url",
        "durations": [5, 10],
        "default_params": {
            "aspect_ratio": "16:9",
            "negative_prompt": "blur, distort, and low quality",
            "cfg_scale": 0.5,
        },
    },
    "kling2.5": {
        "endpoint": "fal-ai/kling-video/v2.5-turbo/pro/image-to-video",
        "description": "Kling 2.5 Turbo Pro - fast generation",
        "supports_tail_image": True,
        "tail_image_param": "tail_image_url",
        "start_image_param": "image_url",
        "durations": [5, 10],
        "default_params": {
            "aspect_ratio": "16:9",
            "negative_prompt": "blur, distort, and low quality",
            "cfg_scale": 0.5,
        },
    },
    "kling2.6": {
        "endpoint": "fal-ai/kling-video/v2.6/pro/image-to-video",
        "description": "Kling 2.6 Pro - latest version with audio support",
        "supports_tail_image": False,
        "start_image_param": "image_url",
        "supports_audio": True,
        "durations": [5, 10],
        "default_params": {
            "negative_prompt": "blur, distort, and low quality",
        },
    },
    "klingo1": {
        "endpoint": "fal-ai/kling-video/o1/image-to-video",
        "description": "Kling O1 - reasoning model with end image support",
        "supports_tail_image": True,
        "start_image_param": "start_image_url",
        "tail_image_param": "end_image_url",
        "max_file_size": 10 * 1024 * 1024,  # 10MB limit
        "durations": [5, 10],
        "default_params": {},
    },
    "seedance1.0": {
        "endpoint": "fal-ai/bytedance/seedance/v1/pro/image-to-video",
        "description": "Seedance 1.0 Pro - ByteDance video model",
        "supports_tail_image": True,
        "tail_image_param": "end_image_url",
        "start_image_param": "image_url",
        "durations": [5, 10],
        "default_params": {
            "resolution": "1080p",
            "camera_fixed": False,
        },
    },
    "hailuo2.0": {
        "endpoint": "fal-ai/minimax/hailuo-02/standard/image-to-video",
        "description": "Hailuo 2.0 - MiniMax video model",
        "supports_tail_image": False,
        "start_image_param": "image_url",
        "durations": [6, 10],  # Hailuo uses 6s instead of 5s
        "default_params": {
            "prompt_optimizer": True,
        },
    },
}


# Default model
DEFAULT_MODEL = "kling2.1"


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def list_models() -> list[str]:
    """List all available FAL video model names."""
    return list(FAL_VIDEO_MODELS.keys())


def get_model_config(model: str) -> Optional[dict]:
    """Get configuration for a specific model."""
    return FAL_VIDEO_MODELS.get(model)


def get_model_info(model: str) -> dict:
    """Get display info for a model."""
    config = get_model_config(model)
    if not config:
        return {}

    return {
        "name": model,
        "description": config.get("description", ""),
        "endpoint": config.get("endpoint", ""),
        "supports_tail_image": config.get("supports_tail_image", False),
        "supports_audio": config.get("supports_audio", False),
        "durations": config.get("durations", [5, 10]),
        "max_file_size": config.get("max_file_size"),
    }


def normalize_duration(model: str, duration: int) -> int:
    """
    Normalize duration to valid value for model.

    Some models only support specific durations (e.g., Hailuo uses 6s not 5s).
    """
    config = get_model_config(model)
    if not config:
        return duration

    valid_durations = config.get("durations", [5, 10])

    # Find closest valid duration
    if duration in valid_durations:
        return duration

    # For Hailuo, 5 -> 6
    if duration <= min(valid_durations):
        return min(valid_durations)

    return max(valid_durations)
