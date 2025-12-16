"""
Prompt generation utilities for semiautomatic.

Generates platform-specific prompts for image and video generation.

Library usage:
    from semiautomatic.prompt import generate_image_prompt, generate_video_prompt

    # Image prompt (basic)
    result = generate_image_prompt("person dancing at a rave")
    print(result.prompt)

    # Image prompt with schema
    result = generate_image_prompt(
        "person dancing",
        schema_path="aesthetic.json",
        platform="flux"
    )

    # Video prompt from image
    result = generate_video_prompt("portrait.jpg")
    print(result.prompt)

    # Video prompt with schema
    result = generate_video_prompt(
        "portrait.jpg",
        schema_path="aesthetic.json",
        video_model="higgsfield"
    )

CLI usage:
    semiautomatic generate-image-prompt "person dancing"
    semiautomatic generate-image-prompt "person dancing" --schema aesthetic.json
    semiautomatic generate-video-prompt --input image.jpg
    semiautomatic generate-video-prompt --input image.jpg --schema aesthetic.json
"""

from __future__ import annotations

from semiautomatic.prompt.image import (
    generate_image_prompt,
    ImagePromptResult,
    run_generate_image_prompt,
)
from semiautomatic.prompt.video import (
    generate_video_prompt,
    VideoPromptResult,
    run_generate_video_prompt,
)
from semiautomatic.prompt.models import (
    IMAGE_PLATFORM_CONFIGS,
    VIDEO_MODEL_CONFIGS,
)


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    # Image prompt generation
    "generate_image_prompt",
    "ImagePromptResult",
    "run_generate_image_prompt",
    # Video prompt generation
    "generate_video_prompt",
    "VideoPromptResult",
    "run_generate_video_prompt",
    # Configurations
    "IMAGE_PLATFORM_CONFIGS",
    "VIDEO_MODEL_CONFIGS",
]
