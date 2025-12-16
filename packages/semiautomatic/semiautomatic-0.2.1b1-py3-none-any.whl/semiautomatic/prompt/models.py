"""
Platform configurations and system prompt templates for prompt generation.

Contains model-specific configurations for image and video prompt generation.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Image Platform Configurations
# ---------------------------------------------------------------------------

IMAGE_PLATFORM_CONFIGS = {
    "midjourney": {
        "name": "Midjourney",
        "description": "Verbose narrative prompts with technical parameters",
        "max_words": 50,
        "style": "narrative",
        "include_technical_params": True,
    },
    "flux": {
        "name": "FLUX (Krea/Dev/Schnell)",
        "description": "Direct, concise prompts without technical jargon",
        "max_words": 40,
        "style": "direct",
        "include_technical_params": False,
    }
}


# ---------------------------------------------------------------------------
# Video Model Configurations
# ---------------------------------------------------------------------------

VIDEO_MODEL_CONFIGS = {
    "kling": {
        "name": "Kling",
        "description": "Direct, natural language motion prompts",
        "max_words": 15,
        "style": "natural",
        "focus": "motion and action",
    },
    "higgsfield": {
        "name": "Higgsfield",
        "description": "Concise motion prompts, works with motion presets",
        "max_words": 12,
        "style": "direct",
        "focus": "primary motion action",
        "supports_motion_presets": True,
    },
    "generic": {
        "name": "Generic Video",
        "description": "General purpose motion prompts",
        "max_words": 15,
        "style": "natural",
        "focus": "motion and expression",
    }
}


# ---------------------------------------------------------------------------
# Banned Words (Midjourney-specific)
# ---------------------------------------------------------------------------

BANNED_WORDS = {
    r'\bblood\b': 'crimson liquid',
    r'\bblood-red\b': 'deep crimson',
    r'\bbloody\b': 'crimson-stained',
    r'\bbloodstained\b': 'crimson-stained',
    r'\bgore\b': 'viscera',
    r'\bgory\b': 'visceral',
    r'\bviolent\b': 'intense',
    r'\bviolence\b': 'intensity'
}
