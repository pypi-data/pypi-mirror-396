"""
Recraft AI style definitions and size presets.

Built-in styles supported by Recraft V3 API.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Built-in Styles
# ---------------------------------------------------------------------------

RECRAFT_STYLES = {
    "any": {
        "description": "Catch-all style option",
    },
    "realistic_image": {
        "description": "Photorealistic image generation (default)",
    },
    "digital_illustration": {
        "description": "Digital illustration style",
    },
    "vector_illustration": {
        "description": "Vector illustration style",
    },
    "logo_raster": {
        "description": "Raster-based logo creation",
    },
}

DEFAULT_STYLE = "realistic_image"


# ---------------------------------------------------------------------------
# Size Presets
# ---------------------------------------------------------------------------

RECRAFT_SIZE_PRESETS = {
    "square": (1024, 1024),
    "landscape": (1365, 1024),
    "portrait": (1024, 1365),
    "square_hd": (1536, 1536),
}

DEFAULT_SIZE = "square"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

RECRAFT_MODELS = {
    "recraftv3": {
        "description": "Recraft V3 - latest model with best quality",
    },
    "recraftv2": {
        "description": "Recraft V2 - previous generation model",
    },
}

DEFAULT_MODEL = "recraftv3"


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def list_styles() -> list[str]:
    """List available Recraft style names."""
    return list(RECRAFT_STYLES.keys())


def get_style_info(style: str) -> dict:
    """Get information about a style."""
    if style in RECRAFT_STYLES:
        return {"name": style, **RECRAFT_STYLES[style]}
    return {}


def is_valid_style(style: str) -> bool:
    """Check if style is a valid built-in style or UUID."""
    if style in RECRAFT_STYLES:
        return True
    # Check if it's a UUID format (36 chars with dashes)
    if is_uuid(style):
        return True
    return False


def is_uuid(value: str) -> bool:
    """Check if value is a UUID format."""
    return (
        len(value) == 36 and
        value[8] == '-' and
        value[13] == '-' and
        value[18] == '-' and
        value[23] == '-'
    )


def parse_size(size: str) -> tuple[int, int]:
    """
    Parse size string to (width, height) tuple.

    Args:
        size: Size preset name or "WxH" format.

    Returns:
        Tuple of (width, height).

    Raises:
        ValueError: If size format is invalid.
    """
    # Check preset first
    if size in RECRAFT_SIZE_PRESETS:
        return RECRAFT_SIZE_PRESETS[size]

    # Try WxH format
    if 'x' in size.lower():
        try:
            parts = size.lower().split('x')
            return (int(parts[0]), int(parts[1]))
        except (ValueError, IndexError):
            pass

    raise ValueError(
        f"Invalid size format: {size}. "
        f"Use WxH (e.g., 1024x1024) or preset: {', '.join(RECRAFT_SIZE_PRESETS.keys())}"
    )


def list_models() -> list[str]:
    """List available Recraft model names."""
    return list(RECRAFT_MODELS.keys())
