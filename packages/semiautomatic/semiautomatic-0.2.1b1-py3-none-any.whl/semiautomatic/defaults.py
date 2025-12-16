"""
Centralized defaults for semiautomatic.

Edit this file to change default models, providers, and settings.
These defaults are used when no explicit value is provided via CLI or API.
"""

# ---------------------------------------------------------------------------
# Image Generation
# ---------------------------------------------------------------------------

IMAGE_DEFAULT_PROVIDER = "fal"
IMAGE_DEFAULT_MODEL = "flux-dev"
IMAGE_DEFAULT_SIZE = "landscape_4_3"
IMAGE_DEFAULT_NUM_IMAGES = 1
IMAGE_DEFAULT_OUTPUT_FORMAT = "png"

# Recraft-specific defaults
RECRAFT_DEFAULT_MODEL = "recraftv3"
RECRAFT_DEFAULT_STYLE = "realistic_image"
RECRAFT_DEFAULT_SIZE = "square"
RECRAFT_DEFAULT_STRENGTH = 0.5  # For i2i mode

# ---------------------------------------------------------------------------
# Video Generation
# ---------------------------------------------------------------------------

VIDEO_DEFAULT_PROVIDER = "fal"
VIDEO_DEFAULT_MODEL = "kling2.6"
VIDEO_DEFAULT_DURATION = 5
VIDEO_DEFAULT_ASPECT_RATIO = "16:9"

# ---------------------------------------------------------------------------
# Image Upscaling
# ---------------------------------------------------------------------------

UPSCALE_DEFAULT_PROVIDER = "freepik"
UPSCALE_DEFAULT_SCALE = "2x"
UPSCALE_DEFAULT_ENGINE = "automatic"

# ---------------------------------------------------------------------------
# Vision / Captioning
# ---------------------------------------------------------------------------

VISION_DEFAULT_PROVIDER = "huggingface"
VISION_DEFAULT_MODEL = "joycaption"
VISION_DEFAULT_LENGTH = "normal"

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

LLM_DEFAULT_PROVIDER = "claude"
LLM_DEFAULT_MODEL = "claude-sonnet-4-5-20250929"

# ---------------------------------------------------------------------------
# Prompt Generation
# ---------------------------------------------------------------------------

PROMPT_IMAGE_DEFAULT_PLATFORM = "flux"
PROMPT_VIDEO_DEFAULT_MODEL = "higgsfield"

# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

STORAGE_DEFAULT_BACKEND = "r2"

# ---------------------------------------------------------------------------
# API / Polling
# ---------------------------------------------------------------------------

API_DEFAULT_POLL_INTERVAL = 5.0  # seconds
API_DEFAULT_POLL_TIMEOUT = 300.0  # 5 minutes
API_DEFAULT_DOWNLOAD_TIMEOUT = 60  # seconds

# ---------------------------------------------------------------------------
# Batch Processing
# ---------------------------------------------------------------------------

BATCH_DEFAULT_WORKERS = 4
