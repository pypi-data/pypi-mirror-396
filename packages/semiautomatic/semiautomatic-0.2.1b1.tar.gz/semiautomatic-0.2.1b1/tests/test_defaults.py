"""
Tests for semiautomatic.defaults module.

Tests cover:
- Default values are defined
- Defaults can be imported
"""

from semiautomatic.defaults import (
    # Image
    IMAGE_DEFAULT_PROVIDER,
    IMAGE_DEFAULT_MODEL,
    IMAGE_DEFAULT_SIZE,
    IMAGE_DEFAULT_NUM_IMAGES,
    IMAGE_DEFAULT_OUTPUT_FORMAT,
    # Video
    VIDEO_DEFAULT_PROVIDER,
    VIDEO_DEFAULT_MODEL,
    VIDEO_DEFAULT_DURATION,
    VIDEO_DEFAULT_ASPECT_RATIO,
    # Upscale
    UPSCALE_DEFAULT_PROVIDER,
    UPSCALE_DEFAULT_SCALE,
    UPSCALE_DEFAULT_ENGINE,
    # Vision
    VISION_DEFAULT_PROVIDER,
    VISION_DEFAULT_LENGTH,
    # Storage
    STORAGE_DEFAULT_BACKEND,
    # API
    API_DEFAULT_POLL_INTERVAL,
    API_DEFAULT_POLL_TIMEOUT,
    API_DEFAULT_DOWNLOAD_TIMEOUT,
    # Batch
    BATCH_DEFAULT_WORKERS,
)


class TestImageDefaults:
    """Tests for image generation defaults."""

    def test_provider_is_fal(self):
        assert IMAGE_DEFAULT_PROVIDER == "fal"

    def test_model_is_flux_dev(self):
        assert IMAGE_DEFAULT_MODEL == "flux-dev"

    def test_size_is_landscape(self):
        assert IMAGE_DEFAULT_SIZE == "landscape_4_3"

    def test_num_images_is_one(self):
        assert IMAGE_DEFAULT_NUM_IMAGES == 1

    def test_format_is_png(self):
        assert IMAGE_DEFAULT_OUTPUT_FORMAT == "png"


class TestVideoDefaults:
    """Tests for video generation defaults."""

    def test_provider_is_fal(self):
        assert VIDEO_DEFAULT_PROVIDER == "fal"

    def test_model_is_kling(self):
        assert VIDEO_DEFAULT_MODEL == "kling2.6"

    def test_duration_is_five(self):
        assert VIDEO_DEFAULT_DURATION == 5

    def test_aspect_ratio_is_16_9(self):
        assert VIDEO_DEFAULT_ASPECT_RATIO == "16:9"


class TestUpscaleDefaults:
    """Tests for upscaling defaults."""

    def test_provider_is_freepik(self):
        assert UPSCALE_DEFAULT_PROVIDER == "freepik"

    def test_scale_is_2x(self):
        assert UPSCALE_DEFAULT_SCALE == "2x"

    def test_engine_is_automatic(self):
        assert UPSCALE_DEFAULT_ENGINE == "automatic"


class TestVisionDefaults:
    """Tests for vision defaults."""

    def test_provider_is_huggingface(self):
        assert VISION_DEFAULT_PROVIDER == "huggingface"

    def test_length_is_normal(self):
        assert VISION_DEFAULT_LENGTH == "normal"


class TestStorageDefaults:
    """Tests for storage defaults."""

    def test_backend_is_r2(self):
        assert STORAGE_DEFAULT_BACKEND == "r2"


class TestApiDefaults:
    """Tests for API defaults."""

    def test_poll_interval_is_five_seconds(self):
        assert API_DEFAULT_POLL_INTERVAL == 5.0

    def test_poll_timeout_is_five_minutes(self):
        assert API_DEFAULT_POLL_TIMEOUT == 300.0

    def test_download_timeout_is_one_minute(self):
        assert API_DEFAULT_DOWNLOAD_TIMEOUT == 60


class TestBatchDefaults:
    """Tests for batch processing defaults."""

    def test_workers_is_four(self):
        assert BATCH_DEFAULT_WORKERS == 4
