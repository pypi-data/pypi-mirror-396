"""
Tests for Higgsfield video generation provider.

Tests cover:
- Motion presets registry
- Higgsfield model configurations
- HiggsfieldVideoProvider
- Argument building
- Polling logic
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock

from semiautomatic.video.providers.motions import (
    HIGGSFIELD_MOTIONS,
    CAMERA_MOTIONS,
    EFFECT_MOTIONS,
    ACTION_MOTIONS,
    list_motions,
    get_motion_id,
    is_valid_motion,
    get_motions_by_category,
)
from semiautomatic.video.providers.higgsfield import (
    HiggsfieldVideoProvider,
    HIGGSFIELD_MODELS,
    DEFAULT_MODEL,
    DEFAULT_MOTION,
    DEFAULT_MOTION_STRENGTH,
    list_models,
    get_model_config,
    get_model_info,
)
from semiautomatic.video.providers.base import VideoResult, VideoGenerationResult
from semiautomatic.video.providers import get_provider, list_providers, list_all_models


# ---------------------------------------------------------------------------
# Motion Presets Tests
# ---------------------------------------------------------------------------

class TestMotionPresets:
    """Tests for Higgsfield motion presets."""

    def test_motion_count(self):
        """Should have 120 motion presets."""
        assert len(HIGGSFIELD_MOTIONS) == 120

    def test_list_motions(self):
        """list_motions returns sorted list."""
        motions = list_motions()
        assert len(motions) == 120
        assert motions == sorted(motions)

    def test_get_motion_id_valid(self):
        """get_motion_id returns UUID for valid motion."""
        motion_id = get_motion_id("zoom_in")
        assert motion_id == "fbcbec5b-30f8-4b17-ba6e-8e8d5b265562"

    def test_get_motion_id_invalid(self):
        """get_motion_id returns None for invalid motion."""
        motion_id = get_motion_id("nonexistent")
        assert motion_id is None

    def test_is_valid_motion(self):
        """is_valid_motion checks motion existence."""
        assert is_valid_motion("zoom_in") is True
        assert is_valid_motion("dolly_out") is True
        assert is_valid_motion("nonexistent") is False

    def test_camera_motions(self):
        """CAMERA_MOTIONS contains camera-related motions."""
        assert "zoom_in" in CAMERA_MOTIONS
        assert "zoom_out" in CAMERA_MOTIONS
        assert "dolly_in" in CAMERA_MOTIONS
        assert "crane_up" in CAMERA_MOTIONS
        assert "handheld" in CAMERA_MOTIONS

    def test_effect_motions(self):
        """EFFECT_MOTIONS contains visual effect motions."""
        assert "fire_breathe" in EFFECT_MOTIONS
        assert "freezing" in EFFECT_MOTIONS
        assert "glowshift" in EFFECT_MOTIONS

    def test_action_motions(self):
        """ACTION_MOTIONS contains action/movement motions."""
        assert "boxing" in ACTION_MOTIONS
        assert "catwalk" in ACTION_MOTIONS
        assert "moonwalk_left" in ACTION_MOTIONS

    def test_get_motions_by_category(self):
        """get_motions_by_category returns motions for category."""
        camera = get_motions_by_category("camera")
        assert len(camera) > 0
        assert "zoom_in" in camera

        effect = get_motions_by_category("effect")
        assert len(effect) > 0

        action = get_motions_by_category("action")
        assert len(action) > 0

        # Invalid category returns empty
        invalid = get_motions_by_category("invalid")
        assert invalid == []


# ---------------------------------------------------------------------------
# Model Configuration Tests
# ---------------------------------------------------------------------------

class TestHiggsfieldModels:
    """Tests for Higgsfield model configurations."""

    def test_default_model(self):
        assert DEFAULT_MODEL == "higgsfield"

    def test_default_motion(self):
        assert DEFAULT_MOTION == "general"

    def test_default_motion_strength(self):
        assert DEFAULT_MOTION_STRENGTH == 0.5

    def test_list_models(self):
        models = list_models()
        assert "higgsfield" in models
        assert "higgsfield_lite" in models
        assert "higgsfield_preview" in models
        assert "higgsfield_turbo" in models
        assert len(models) == 4

    def test_get_model_config_valid(self):
        config = get_model_config("higgsfield")
        assert config is not None
        assert "model" in config
        assert "description" in config

    def test_get_model_config_invalid(self):
        config = get_model_config("nonexistent")
        assert config is None

    def test_get_model_info(self):
        info = get_model_info("higgsfield")
        assert info["name"] == "higgsfield"
        assert "description" in info
        assert info["supports_motion"] is True
        assert info["provider"] == "higgsfield"

    def test_get_model_info_invalid(self):
        info = get_model_info("nonexistent")
        assert info == {}

    def test_model_dop_types(self):
        """Each model should have a specific DOP model type."""
        assert get_model_config("higgsfield")["model"] == "dop-preview"
        assert get_model_config("higgsfield_preview")["model"] == "dop-preview"
        assert get_model_config("higgsfield_lite")["model"] == "dop-lite"
        assert get_model_config("higgsfield_turbo")["model"] == "dop-turbo"


# ---------------------------------------------------------------------------
# Provider Registry Tests
# ---------------------------------------------------------------------------

class TestProviderRegistry:
    """Tests for Higgsfield in provider registry."""

    def test_higgsfield_in_providers(self):
        providers = list_providers()
        assert "higgsfield" in providers

    def test_get_higgsfield_provider(self):
        provider = get_provider("higgsfield")
        assert isinstance(provider, HiggsfieldVideoProvider)

    def test_higgsfield_in_all_models(self):
        all_models = list_all_models()
        assert "higgsfield" in all_models
        assert "higgsfield" in all_models["higgsfield"]


# ---------------------------------------------------------------------------
# Provider Tests
# ---------------------------------------------------------------------------

class TestHiggsfieldProvider:
    """Tests for HiggsfieldVideoProvider."""

    def test_name(self):
        provider = HiggsfieldVideoProvider()
        assert provider.name == "higgsfield"

    def test_list_models(self):
        provider = HiggsfieldVideoProvider()
        models = provider.list_models()
        assert "higgsfield" in models
        assert len(models) == 4

    def test_get_model_info(self):
        provider = HiggsfieldVideoProvider()
        info = provider.get_model_info("higgsfield")
        assert info["name"] == "higgsfield"
        assert "description" in info

    def test_get_model_info_invalid(self):
        provider = HiggsfieldVideoProvider()
        info = provider.get_model_info("nonexistent")
        assert info == {}

    def test_supports_tail_image(self):
        provider = HiggsfieldVideoProvider()
        # Higgsfield doesn't support tail images
        assert provider.supports_tail_image("higgsfield") is False
        assert provider.supports_tail_image("higgsfield_turbo") is False

    def test_supports_motion(self):
        provider = HiggsfieldVideoProvider()
        assert provider.supports_motion() is True

    def test_list_motions(self):
        provider = HiggsfieldVideoProvider()
        motions = provider.list_motions()
        assert len(motions) == 120

    def test_resolve_image_url_already_url(self):
        provider = HiggsfieldVideoProvider()
        url = provider._resolve_image_url("https://example.com/image.jpg")
        assert url == "https://example.com/image.jpg"

    def test_resolve_image_url_local_file_not_found(self):
        provider = HiggsfieldVideoProvider()
        with pytest.raises(ValueError) as exc:
            provider._resolve_image_url("/nonexistent/path.jpg")
        assert "not found" in str(exc.value)


# ---------------------------------------------------------------------------
# Polling Tests
# ---------------------------------------------------------------------------

class TestPolling:
    """Tests for result polling."""

    @patch("semiautomatic.video.providers.higgsfield.requests.get")
    def test_poll_for_result_success(self, mock_get):
        provider = HiggsfieldVideoProvider()

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "jobs": [
                {
                    "status": "completed",
                    "results": {
                        "min": {"url": "https://example.com/video.mp4"},
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        result = provider._poll_for_result("job-123", "api-key", "secret")

        assert result == "https://example.com/video.mp4"

    @patch("semiautomatic.video.providers.higgsfield.requests.get")
    def test_poll_for_result_raw_fallback(self, mock_get):
        """Should use raw URL if min not available."""
        provider = HiggsfieldVideoProvider()

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "jobs": [
                {
                    "status": "completed",
                    "results": {
                        "raw": {"url": "https://example.com/video_raw.mp4"},
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        result = provider._poll_for_result("job-123", "api-key", "secret")

        assert result == "https://example.com/video_raw.mp4"

    @patch("semiautomatic.video.providers.higgsfield.requests.get")
    def test_poll_for_result_failed(self, mock_get):
        provider = HiggsfieldVideoProvider()

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "jobs": [
                {
                    "status": "failed",
                    "error": "Content policy violation",
                }
            ]
        }
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError) as exc:
            provider._poll_for_result("job-123", "api-key", "secret")

        assert "Content policy violation" in str(exc.value)

    @patch("semiautomatic.video.providers.higgsfield.time.sleep")
    @patch("semiautomatic.video.providers.higgsfield.requests.get")
    def test_poll_for_result_processing_then_complete(self, mock_get, mock_sleep):
        provider = HiggsfieldVideoProvider()

        # First call: processing, second call: completed
        mock_response_processing = Mock()
        mock_response_processing.ok = True
        mock_response_processing.json.return_value = {
            "jobs": [{"status": "processing"}]
        }

        mock_response_complete = Mock()
        mock_response_complete.ok = True
        mock_response_complete.json.return_value = {
            "jobs": [
                {
                    "status": "completed",
                    "results": {"min": {"url": "https://example.com/video.mp4"}},
                }
            ]
        }

        mock_get.side_effect = [mock_response_processing, mock_response_complete]

        result = provider._poll_for_result("job-123", "api-key", "secret")

        assert result == "https://example.com/video.mp4"
        assert mock_sleep.call_count == 1

    @patch("semiautomatic.video.providers.higgsfield.time.sleep")
    @patch("semiautomatic.video.providers.higgsfield.requests.get")
    def test_poll_for_result_timeout(self, mock_get, mock_sleep):
        provider = HiggsfieldVideoProvider()

        # Always return processing
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "jobs": [{"status": "processing"}]
        }
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError) as exc:
            provider._poll_for_result("job-123", "api-key", "secret", max_attempts=2, poll_interval=1)

        assert "timeout" in str(exc.value).lower()


# ---------------------------------------------------------------------------
# Generation Tests (Mocked)
# ---------------------------------------------------------------------------

class TestGeneration:
    """Tests for generate() method with mocks."""

    @patch("semiautomatic.video.providers.higgsfield.requests.get")
    @patch("semiautomatic.video.providers.higgsfield.requests.post")
    @patch.dict("os.environ", {"HIGGSFIELD_API_KEY": "test-key", "HIGGSFIELD_SECRET": "test-secret"})
    def test_generate_success(self, mock_post, mock_get):
        provider = HiggsfieldVideoProvider()

        # Mock submit response
        mock_post_response = Mock()
        mock_post_response.ok = True
        mock_post_response.json.return_value = {"id": "job-123"}
        mock_post.return_value = mock_post_response

        # Mock poll response
        mock_get_response = Mock()
        mock_get_response.ok = True
        mock_get_response.json.return_value = {
            "jobs": [
                {
                    "status": "completed",
                    "results": {"min": {"url": "https://example.com/video.mp4"}},
                }
            ]
        }
        mock_get.return_value = mock_get_response

        result = provider.generate(
            prompt="dancing",
            image="https://example.com/person.jpg",
            model="higgsfield",
            motion="zoom_in",
        )

        assert isinstance(result, VideoGenerationResult)
        assert result.video.url == "https://example.com/video.mp4"
        assert result.model == "higgsfield"
        assert result.provider == "higgsfield"
        assert result.prompt == "dancing"
        assert result.metadata["motion"] == "zoom_in"

    def test_generate_missing_api_key(self):
        provider = HiggsfieldVideoProvider()

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError) as exc:
                provider.generate(prompt="test", image="https://example.com/img.jpg")
            assert "HIGGSFIELD_API_KEY" in str(exc.value)

    @patch.dict("os.environ", {"HIGGSFIELD_API_KEY": "test-key", "HIGGSFIELD_SECRET": "test-secret"})
    def test_generate_missing_image(self):
        provider = HiggsfieldVideoProvider()

        with pytest.raises(ValueError) as exc:
            provider.generate(prompt="test")
        assert "requires an input image" in str(exc.value)

    @patch.dict("os.environ", {"HIGGSFIELD_API_KEY": "test-key", "HIGGSFIELD_SECRET": "test-secret"})
    def test_generate_invalid_model(self):
        provider = HiggsfieldVideoProvider()

        with pytest.raises(ValueError) as exc:
            provider.generate(prompt="test", image="https://example.com/img.jpg", model="invalid")
        assert "Unknown Higgsfield model" in str(exc.value)

    @patch.dict("os.environ", {"HIGGSFIELD_API_KEY": "test-key", "HIGGSFIELD_SECRET": "test-secret"})
    def test_generate_invalid_motion(self):
        provider = HiggsfieldVideoProvider()

        with pytest.raises(ValueError) as exc:
            provider.generate(prompt="test", image="https://example.com/img.jpg", motion="invalid_motion")
        assert "Unknown motion preset" in str(exc.value)

    @patch("semiautomatic.video.providers.higgsfield.requests.post")
    @patch.dict("os.environ", {"HIGGSFIELD_API_KEY": "test-key", "HIGGSFIELD_SECRET": "test-secret"})
    def test_generate_api_error(self, mock_post):
        provider = HiggsfieldVideoProvider()

        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc:
            provider.generate(prompt="test", image="https://example.com/img.jpg")
        assert "500" in str(exc.value)


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestHiggsfieldIntegration:
    """Integration tests for Higgsfield provider (requires HIGGSFIELD_API_KEY)."""

    @pytest.fixture(autouse=True)
    def check_dependencies(self):
        """Skip if HIGGSFIELD_API_KEY or FAL_KEY not set."""
        import os
        if not os.environ.get("HIGGSFIELD_API_KEY"):
            pytest.skip("HIGGSFIELD_API_KEY not set")
        if not os.environ.get("HIGGSFIELD_SECRET"):
            pytest.skip("HIGGSFIELD_SECRET not set")
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
            output_prefix="higgsfield_source",
        )
        return result.images[0].url

    def test_generate_video_with_motion(self, generated_image_url, integration_output_dir):
        """Test video generation with Higgsfield and motion preset."""
        from semiautomatic.video import generate_video

        result = generate_video(
            prompt="higgsfield zoom test",
            image=generated_image_url,
            provider="higgsfield",
            model="higgsfield",
            motion="zoom_in",
            motion_strength=0.7,
            output_dir=integration_output_dir,
        )

        assert result is not None
        assert result.video is not None
        assert result.video.path is not None
        assert result.video.path.exists()
        assert result.video.path.suffix == ".mp4"
        assert result.metadata.get("motion") == "zoom_in"
        assert "higgsfield" in result.video.path.name
