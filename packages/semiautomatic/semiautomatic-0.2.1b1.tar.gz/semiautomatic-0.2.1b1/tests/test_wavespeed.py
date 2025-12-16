"""
Tests for Wavespeed video generation provider.

Tests cover:
- Wavespeed model configurations
- WavespeedVideoProvider
- Image to base64 conversion
- Argument building
- Polling logic
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
import base64

from semiautomatic.video.providers.wavespeed import (
    WavespeedVideoProvider,
    WAVESPEED_MODELS,
    DEFAULT_MODEL,
    list_models,
    get_model_config,
    get_model_info,
)
from semiautomatic.video.providers.base import VideoResult, VideoGenerationResult
from semiautomatic.video.providers import get_provider, list_providers, list_all_models


# ---------------------------------------------------------------------------
# Model Configuration Tests
# ---------------------------------------------------------------------------

class TestWavespeedModels:
    """Tests for Wavespeed model configurations."""

    def test_default_model(self):
        assert DEFAULT_MODEL == "wan2.5"

    def test_list_models(self):
        models = list_models()
        assert "kling2.5-wavespeed" in models
        assert "wan2.2" in models
        assert "wan2.5" in models
        assert "sora2" in models
        assert len(models) == 4

    def test_get_model_config_valid(self):
        config = get_model_config("wan2.5")
        assert config is not None
        assert "endpoint" in config
        assert "default_params" in config

    def test_get_model_config_invalid(self):
        config = get_model_config("nonexistent")
        assert config is None

    def test_get_model_info(self):
        info = get_model_info("wan2.5")
        assert info["name"] == "wan2.5"
        assert "description" in info
        assert info["provider"] == "wavespeed"

    def test_get_model_info_invalid(self):
        info = get_model_info("nonexistent")
        assert info == {}

    def test_model_supports_tail_image(self):
        # wan2.2 supports tail images
        assert get_model_config("wan2.2")["supports_tail_image"] is True

        # Others don't
        assert get_model_config("kling2.5-wavespeed")["supports_tail_image"] is False
        assert get_model_config("wan2.5")["supports_tail_image"] is False
        assert get_model_config("sora2")["supports_tail_image"] is False

    def test_duration_types(self):
        # Kling uses string duration
        assert get_model_config("kling2.5-wavespeed")["duration_type"] == "string"

        # Others use integer
        assert get_model_config("wan2.2")["duration_type"] == "integer"
        assert get_model_config("wan2.5")["duration_type"] == "integer"
        assert get_model_config("sora2")["duration_type"] == "integer"


# ---------------------------------------------------------------------------
# Provider Registry Tests
# ---------------------------------------------------------------------------

class TestProviderRegistry:
    """Tests for Wavespeed in provider registry."""

    def test_wavespeed_in_providers(self):
        providers = list_providers()
        assert "wavespeed" in providers

    def test_get_wavespeed_provider(self):
        provider = get_provider("wavespeed")
        assert isinstance(provider, WavespeedVideoProvider)

    def test_wavespeed_in_all_models(self):
        all_models = list_all_models()
        assert "wavespeed" in all_models
        assert "wan2.5" in all_models["wavespeed"]


# ---------------------------------------------------------------------------
# Provider Tests
# ---------------------------------------------------------------------------

class TestWavespeedProvider:
    """Tests for WavespeedVideoProvider."""

    def test_name(self):
        provider = WavespeedVideoProvider()
        assert provider.name == "wavespeed"

    def test_list_models(self):
        provider = WavespeedVideoProvider()
        models = provider.list_models()
        assert "wan2.5" in models
        assert len(models) == 4

    def test_get_model_info(self):
        provider = WavespeedVideoProvider()
        info = provider.get_model_info("sora2")
        assert info["name"] == "sora2"
        assert "description" in info

    def test_get_model_info_invalid(self):
        provider = WavespeedVideoProvider()
        info = provider.get_model_info("nonexistent")
        assert info == {}

    def test_supports_tail_image(self):
        provider = WavespeedVideoProvider()
        assert provider.supports_tail_image("wan2.2") is True
        assert provider.supports_tail_image("wan2.5") is False

    def test_resolve_image_already_data_uri(self):
        provider = WavespeedVideoProvider()
        data_uri = "data:image/jpeg;base64,abc123"
        result = provider._resolve_image_to_base64(data_uri)
        assert result == data_uri

    def test_resolve_image_local_file(self, tmp_path):
        provider = WavespeedVideoProvider()

        # Create a test image file
        image_file = tmp_path / "test.jpg"
        image_content = b"fake image data"
        image_file.write_bytes(image_content)

        result = provider._resolve_image_to_base64(str(image_file))

        assert result.startswith("data:image/jpeg;base64,")
        # Verify the base64 content
        b64_part = result.split(",")[1]
        decoded = base64.b64decode(b64_part)
        assert decoded == image_content

    def test_resolve_image_local_png(self, tmp_path):
        provider = WavespeedVideoProvider()

        image_file = tmp_path / "test.png"
        image_file.write_bytes(b"png data")

        result = provider._resolve_image_to_base64(str(image_file))
        assert result.startswith("data:image/png;base64,")

    def test_resolve_image_file_not_found(self):
        provider = WavespeedVideoProvider()
        with pytest.raises(ValueError) as exc:
            provider._resolve_image_to_base64("/nonexistent/path.jpg")
        assert "not found" in str(exc.value)

    @patch("semiautomatic.video.providers.wavespeed.requests.get")
    def test_resolve_image_from_url(self, mock_get):
        provider = WavespeedVideoProvider()

        mock_response = Mock()
        mock_response.content = b"downloaded image"
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = provider._resolve_image_to_base64("https://example.com/image.png")

        assert result.startswith("data:image/png;base64,")
        mock_get.assert_called_once()


# ---------------------------------------------------------------------------
# Argument Building Tests
# ---------------------------------------------------------------------------

class TestBuildArguments:
    """Tests for argument building."""

    def test_build_arguments_basic(self):
        provider = WavespeedVideoProvider()
        config = get_model_config("wan2.5")

        args = provider._build_arguments(
            model="wan2.5",
            config=config,
            prompt="a cat walking",
            b64_image="data:image/jpeg;base64,abc123",
            tail_image=None,
            duration=10,
            negative_prompt=None,
            seed=None,
            cfg_scale=None,
            loop=False,
        )

        assert args["prompt"] == "a cat walking"
        assert args["image"] == "data:image/jpeg;base64,abc123"
        assert args["duration"] == 10

    def test_build_arguments_string_duration(self):
        provider = WavespeedVideoProvider()
        config = get_model_config("kling2.5-wavespeed")

        args = provider._build_arguments(
            model="kling2.5-wavespeed",
            config=config,
            prompt="test",
            b64_image="data:image/jpeg;base64,abc",
            tail_image=None,
            duration=5,
            negative_prompt=None,
            seed=None,
            cfg_scale=None,
            loop=False,
        )

        # Kling uses string duration
        assert args["duration"] == "5"

    def test_build_arguments_with_loop(self, tmp_path):
        provider = WavespeedVideoProvider()
        config = get_model_config("wan2.2")

        b64_image = "data:image/jpeg;base64,abc123"

        args = provider._build_arguments(
            model="wan2.2",
            config=config,
            prompt="looping",
            b64_image=b64_image,
            tail_image=None,
            duration=5,
            negative_prompt=None,
            seed=None,
            cfg_scale=None,
            loop=True,
        )

        # Loop mode should set last_image to same as image
        assert args["last_image"] == b64_image

    def test_build_arguments_with_seed(self):
        provider = WavespeedVideoProvider()
        config = get_model_config("wan2.2")

        args = provider._build_arguments(
            model="wan2.2",
            config=config,
            prompt="test",
            b64_image="data:image/jpeg;base64,abc",
            tail_image=None,
            duration=5,
            negative_prompt=None,
            seed=42,
            cfg_scale=None,
            loop=False,
        )

        assert args["seed"] == 42

    def test_build_arguments_with_guidance_scale(self):
        provider = WavespeedVideoProvider()
        config = get_model_config("kling2.5-wavespeed")

        args = provider._build_arguments(
            model="kling2.5-wavespeed",
            config=config,
            prompt="test",
            b64_image="data:image/jpeg;base64,abc",
            tail_image=None,
            duration=5,
            negative_prompt=None,
            seed=None,
            cfg_scale=0.8,
            loop=False,
        )

        assert args["guidance_scale"] == 0.8


# ---------------------------------------------------------------------------
# Polling Tests
# ---------------------------------------------------------------------------

class TestPolling:
    """Tests for result polling."""

    @patch("semiautomatic.video.providers.wavespeed.requests.get")
    def test_poll_for_result_success(self, mock_get):
        provider = WavespeedVideoProvider()

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "code": 200,
            "data": {
                "status": "completed",
                "outputs": ["https://example.com/video.mp4"],
            }
        }
        mock_get.return_value = mock_response

        result = provider._poll_for_result("request-123", "api-key")

        assert result == "https://example.com/video.mp4"

    @patch("semiautomatic.video.providers.wavespeed.requests.get")
    def test_poll_for_result_unwrapped_response(self, mock_get):
        provider = WavespeedVideoProvider()

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "status": "completed",
            "outputs": ["https://example.com/video.mp4"],
        }
        mock_get.return_value = mock_response

        result = provider._poll_for_result("request-123", "api-key")

        assert result == "https://example.com/video.mp4"

    @patch("semiautomatic.video.providers.wavespeed.requests.get")
    def test_poll_for_result_failed(self, mock_get):
        provider = WavespeedVideoProvider()

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "status": "failed",
            "error": "Content policy violation",
        }
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError) as exc:
            provider._poll_for_result("request-123", "api-key")

        assert "Content policy violation" in str(exc.value)

    @patch("semiautomatic.video.providers.wavespeed.time.sleep")
    @patch("semiautomatic.video.providers.wavespeed.requests.get")
    def test_poll_for_result_processing_then_complete(self, mock_get, mock_sleep):
        provider = WavespeedVideoProvider()

        # First call: processing, second call: completed
        mock_response_processing = Mock()
        mock_response_processing.ok = True
        mock_response_processing.json.return_value = {"status": "processing"}

        mock_response_complete = Mock()
        mock_response_complete.ok = True
        mock_response_complete.json.return_value = {
            "status": "completed",
            "outputs": ["https://example.com/video.mp4"],
        }

        mock_get.side_effect = [mock_response_processing, mock_response_complete]

        result = provider._poll_for_result("request-123", "api-key")

        assert result == "https://example.com/video.mp4"
        assert mock_sleep.call_count == 1

    @patch("semiautomatic.video.providers.wavespeed.time.sleep")
    @patch("semiautomatic.video.providers.wavespeed.requests.get")
    def test_poll_for_result_timeout(self, mock_get, mock_sleep):
        provider = WavespeedVideoProvider()

        # Always return processing
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"status": "processing"}
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError) as exc:
            provider._poll_for_result("request-123", "api-key", max_attempts=2, poll_interval=1)

        assert "timeout" in str(exc.value).lower()


# ---------------------------------------------------------------------------
# Generation Tests (Mocked)
# ---------------------------------------------------------------------------

class TestGeneration:
    """Tests for generate() method with mocks."""

    @patch("semiautomatic.video.providers.wavespeed.requests.get")
    @patch("semiautomatic.video.providers.wavespeed.requests.post")
    @patch.dict("os.environ", {"WAVESPEED_API_KEY": "test-key"})
    def test_generate_success(self, mock_post, mock_get, tmp_path):
        provider = WavespeedVideoProvider()

        # Create test image
        image_file = tmp_path / "test.jpg"
        image_file.write_bytes(b"image data")

        # Mock submit response
        mock_post_response = Mock()
        mock_post_response.ok = True
        mock_post_response.json.return_value = {
            "code": 200,
            "data": {"id": "request-123"}
        }
        mock_post.return_value = mock_post_response

        # Mock poll response
        mock_get_response = Mock()
        mock_get_response.ok = True
        mock_get_response.json.return_value = {
            "status": "completed",
            "outputs": ["https://example.com/video.mp4"],
        }
        mock_get.return_value = mock_get_response

        result = provider.generate(
            prompt="a cat walking",
            image=str(image_file),
            model="wan2.5",
        )

        assert isinstance(result, VideoGenerationResult)
        assert result.video.url == "https://example.com/video.mp4"
        assert result.model == "wan2.5"
        assert result.provider == "wavespeed"
        assert result.prompt == "a cat walking"

    def test_generate_missing_api_key(self, tmp_path):
        provider = WavespeedVideoProvider()

        image_file = tmp_path / "test.jpg"
        image_file.write_bytes(b"image data")

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError) as exc:
                provider.generate(prompt="test", image=str(image_file))
            assert "WAVESPEED_API_KEY" in str(exc.value)

    @patch.dict("os.environ", {"WAVESPEED_API_KEY": "test-key"})
    def test_generate_missing_image(self):
        provider = WavespeedVideoProvider()

        with pytest.raises(ValueError) as exc:
            provider.generate(prompt="test")
        assert "requires an input image" in str(exc.value)

    @patch.dict("os.environ", {"WAVESPEED_API_KEY": "test-key"})
    def test_generate_invalid_model(self, tmp_path):
        provider = WavespeedVideoProvider()

        image_file = tmp_path / "test.jpg"
        image_file.write_bytes(b"image data")

        with pytest.raises(ValueError) as exc:
            provider.generate(prompt="test", image=str(image_file), model="invalid")
        assert "Unknown Wavespeed model" in str(exc.value)

    @patch("semiautomatic.video.providers.wavespeed.requests.post")
    @patch.dict("os.environ", {"WAVESPEED_API_KEY": "test-key"})
    def test_generate_api_error(self, mock_post, tmp_path):
        provider = WavespeedVideoProvider()

        image_file = tmp_path / "test.jpg"
        image_file.write_bytes(b"image data")

        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc:
            provider.generate(prompt="test", image=str(image_file))
        assert "500" in str(exc.value)


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestWavespeedIntegration:
    """Integration tests for Wavespeed provider (requires WAVESPEED_API_KEY)."""

    @pytest.fixture(autouse=True)
    def check_dependencies(self):
        """Skip if WAVESPEED_API_KEY or FAL_KEY not set."""
        import os
        if not os.environ.get("WAVESPEED_API_KEY"):
            pytest.skip("WAVESPEED_API_KEY not set")
        if not os.environ.get("FAL_KEY"):
            pytest.skip("FAL_KEY not set (needed for image generation)")

    @pytest.fixture
    def generated_image_url(self, integration_output_dir):
        """Generate an image with FAL to use as video input."""
        from semiautomatic.image import generate_image

        result = generate_image(
            prompt="a serene landscape with mountains, photorealistic",
            model="flux-schnell",
            size="landscape_16_9",
            num_images=1,
            output_dir=integration_output_dir,
            output_prefix="wan22_source",
        )
        return result.images[0].url

    def test_generate_video_wan22(self, generated_image_url, integration_output_dir):
        """Test video generation with WAN 2.2."""
        from semiautomatic.video import generate_video

        result = generate_video(
            prompt="wan22 test",
            image=generated_image_url,
            provider="wavespeed",
            model="wan2.2",
            output_dir=integration_output_dir,
        )

        assert result is not None
        assert result.video is not None
        assert result.video.path is not None
        assert result.video.path.exists()
        assert result.video.path.suffix == ".mp4"
        assert "wan2.2" in result.video.path.name
