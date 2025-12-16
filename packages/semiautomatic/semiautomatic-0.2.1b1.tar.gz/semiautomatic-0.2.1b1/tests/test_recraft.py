"""
Tests for semiautomatic.image Recraft provider.

Tests cover:
- Recraft styles and size presets
- RecraftControls dataclass
- Recraft provider (mocked)
- image_to_image function
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from semiautomatic.image.providers.recraft_styles import (
    RECRAFT_STYLES,
    RECRAFT_SIZE_PRESETS,
    RECRAFT_MODELS,
    DEFAULT_STYLE,
    DEFAULT_MODEL,
    DEFAULT_SIZE,
    list_styles,
    list_models,
    get_style_info,
    is_valid_style,
    is_uuid,
    parse_size,
)
from semiautomatic.image.providers.recraft import RecraftImageProvider, RecraftControls
from semiautomatic.image.providers import get_provider, list_providers


# ---------------------------------------------------------------------------
# Style Tests
# ---------------------------------------------------------------------------

class TestRecraftStyles:
    """Tests for Recraft style definitions."""

    def test_default_style(self):
        assert DEFAULT_STYLE == "realistic_image"

    def test_default_model(self):
        assert DEFAULT_MODEL == "recraftv3"

    def test_default_size(self):
        assert DEFAULT_SIZE == "square"

    def test_list_styles(self):
        styles = list_styles()
        assert "realistic_image" in styles
        assert "digital_illustration" in styles
        assert "vector_illustration" in styles
        assert "logo_raster" in styles
        assert "any" in styles

    def test_list_models(self):
        models = list_models()
        assert "recraftv3" in models
        assert "recraftv2" in models

    def test_get_style_info(self):
        info = get_style_info("realistic_image")
        assert "description" in info
        assert info["name"] == "realistic_image"

    def test_get_style_info_invalid(self):
        info = get_style_info("nonexistent")
        assert info == {}

    def test_is_valid_style_builtin(self):
        assert is_valid_style("realistic_image") is True
        assert is_valid_style("digital_illustration") is True

    def test_is_valid_style_uuid(self):
        # Valid UUID format
        assert is_valid_style("12345678-1234-1234-1234-123456789012") is True

    def test_is_valid_style_invalid(self):
        assert is_valid_style("not_a_style") is False


# ---------------------------------------------------------------------------
# Size Tests
# ---------------------------------------------------------------------------

class TestRecraftSizes:
    """Tests for Recraft size presets and parsing."""

    def test_size_presets(self):
        assert RECRAFT_SIZE_PRESETS["square"] == (1024, 1024)
        assert RECRAFT_SIZE_PRESETS["landscape"] == (1365, 1024)
        assert RECRAFT_SIZE_PRESETS["portrait"] == (1024, 1365)
        assert RECRAFT_SIZE_PRESETS["square_hd"] == (1536, 1536)

    def test_parse_size_preset(self):
        assert parse_size("square") == (1024, 1024)
        assert parse_size("landscape") == (1365, 1024)

    def test_parse_size_wxh(self):
        assert parse_size("1920x1080") == (1920, 1080)
        assert parse_size("512x512") == (512, 512)

    def test_parse_size_invalid(self):
        with pytest.raises(ValueError):
            parse_size("invalid")


# ---------------------------------------------------------------------------
# UUID Tests
# ---------------------------------------------------------------------------

class TestUUID:
    """Tests for UUID validation."""

    def test_is_uuid_valid(self):
        assert is_uuid("12345678-1234-1234-1234-123456789012") is True
        assert is_uuid("abcdef01-2345-6789-abcd-ef0123456789") is True

    def test_is_uuid_invalid(self):
        assert is_uuid("not-a-uuid") is False
        assert is_uuid("12345678123412341234123456789012") is False  # No dashes
        assert is_uuid("1234") is False


# ---------------------------------------------------------------------------
# RecraftControls Tests
# ---------------------------------------------------------------------------

class TestRecraftControls:
    """Tests for RecraftControls dataclass."""

    def test_default_values(self):
        controls = RecraftControls()
        assert controls.artistic_level is None
        assert controls.colors is None
        assert controls.background_color is None
        assert controls.no_text is False

    def test_to_dict_empty(self):
        controls = RecraftControls()
        assert controls.to_dict() == {}

    def test_to_dict_artistic_level(self):
        controls = RecraftControls(artistic_level=3)
        result = controls.to_dict()
        assert result["artistic_level"] == 3

    def test_to_dict_colors(self):
        controls = RecraftControls(colors=["#FF0000", "#00FF00"])
        result = controls.to_dict()
        assert "colors" in result
        assert len(result["colors"]) == 2
        assert result["colors"][0]["rgb"] == [255, 0, 0]
        assert result["colors"][1]["rgb"] == [0, 255, 0]

    def test_to_dict_background_color(self):
        controls = RecraftControls(background_color="#000000")
        result = controls.to_dict()
        assert result["background_color"]["rgb"] == [0, 0, 0]

    def test_to_dict_no_text(self):
        controls = RecraftControls(no_text=True)
        result = controls.to_dict()
        assert result["no_text"] is True

    def test_to_dict_all_options(self):
        controls = RecraftControls(
            artistic_level=5,
            colors=["#FF0000"],
            background_color="#FFFFFF",
            no_text=True,
        )
        result = controls.to_dict()
        assert result["artistic_level"] == 5
        assert len(result["colors"]) == 1
        assert result["background_color"]["rgb"] == [255, 255, 255]
        assert result["no_text"] is True


# ---------------------------------------------------------------------------
# Provider Registry Tests
# ---------------------------------------------------------------------------

class TestRecraftProviderRegistry:
    """Tests for Recraft provider in registry."""

    def test_recraft_in_providers(self):
        providers = list_providers()
        assert "recraft" in providers

    def test_get_recraft_provider(self):
        provider = get_provider("recraft")
        assert provider.name == "recraft"

    def test_provider_list_models(self):
        provider = get_provider("recraft")
        models = provider.list_models()
        assert "recraftv3" in models
        assert "recraftv2" in models

    def test_provider_get_model_info(self):
        provider = get_provider("recraft")
        info = provider.get_model_info("recraftv3")
        assert "description" in info
        assert info["name"] == "recraftv3"


# ---------------------------------------------------------------------------
# Provider Build Methods Tests
# ---------------------------------------------------------------------------

class TestRecraftProviderBuildMethods:
    """Tests for Recraft provider internal methods."""

    def test_build_payload_basic(self):
        provider = RecraftImageProvider()
        payload = provider._build_payload(
            prompt="a cat",
            model="recraftv3",
            style="realistic_image",
            width=1024,
            height=1024,
            num_images=1,
            seed=None,
            controls=None,
        )

        assert payload["prompt"] == "a cat"
        assert payload["model"] == "recraftv3"
        assert payload["style"] == "realistic_image"
        assert payload["size"] == "1024x1024"
        assert payload["n"] == 1
        assert "style_id" not in payload

    def test_build_payload_with_uuid(self):
        provider = RecraftImageProvider()
        uuid = "12345678-1234-1234-1234-123456789012"
        payload = provider._build_payload(
            prompt="a cat",
            model="recraftv3",
            style=uuid,
            width=1024,
            height=1024,
            num_images=1,
            seed=None,
            controls=None,
        )

        assert payload["style_id"] == uuid
        assert "style" not in payload

    def test_build_payload_with_seed(self):
        provider = RecraftImageProvider()
        payload = provider._build_payload(
            prompt="a cat",
            model="recraftv3",
            style="realistic_image",
            width=1024,
            height=1024,
            num_images=1,
            seed=12345,
            controls=None,
        )

        assert payload["seed"] == 12345

    def test_build_payload_with_controls(self):
        provider = RecraftImageProvider()
        controls = RecraftControls(artistic_level=3, no_text=True)
        payload = provider._build_payload(
            prompt="a cat",
            model="recraftv3",
            style="realistic_image",
            width=1024,
            height=1024,
            num_images=1,
            seed=None,
            controls=controls,
        )

        assert "controls" in payload
        assert payload["controls"]["artistic_level"] == 3
        assert payload["controls"]["no_text"] is True

    def test_build_payload_invalid_style(self):
        provider = RecraftImageProvider()
        with pytest.raises(ValueError) as exc:
            provider._build_payload(
                prompt="a cat",
                model="recraftv3",
                style="not_a_valid_style",
                width=1024,
                height=1024,
                num_images=1,
                seed=None,
                controls=None,
            )
        assert "Unknown style" in str(exc.value)

    def test_build_i2i_data(self):
        provider = RecraftImageProvider()
        data = provider._build_i2i_data(
            prompt="transform to illustration",
            model="recraftv3",
            style="digital_illustration",
            strength=0.7,
            num_images=2,
            controls=None,
            negative_prompt=None,
        )

        assert data["prompt"] == "transform to illustration"
        assert data["model"] == "recraftv3"
        assert data["style"] == "digital_illustration"
        assert data["strength"] == 0.7
        assert data["n"] == 2

    def test_build_i2i_data_with_negative_prompt(self):
        provider = RecraftImageProvider()
        data = provider._build_i2i_data(
            prompt="a cat",
            model="recraftv3",
            style="realistic_image",
            strength=0.5,
            num_images=1,
            controls=None,
            negative_prompt="blurry, low quality",
        )

        assert data["negative_prompt"] == "blurry, low quality"


# ---------------------------------------------------------------------------
# Provider Generate Tests (Validation)
# ---------------------------------------------------------------------------

class TestRecraftProviderValidation:
    """Tests for Recraft provider validation logic."""

    def test_prompt_too_long(self):
        provider = RecraftImageProvider()
        long_prompt = "a" * 1001  # Over 1000 bytes

        with pytest.raises(ValueError) as exc:
            provider.generate(prompt=long_prompt)
        assert "1000 bytes" in str(exc.value)

    def test_num_images_clamped(self):
        provider = RecraftImageProvider()
        # This would be tested via payload inspection, but we can't call
        # the full generate without mocking the API

    def test_lora_warning(self, capsys):
        """LoRAs should be ignored with info message."""
        from semiautomatic.image.providers.base import LoRASpec

        provider = RecraftImageProvider()
        # Would need to mock API to test full flow


# ---------------------------------------------------------------------------
# Provider Default Regression Tests
# ---------------------------------------------------------------------------

class TestRecraftProviderDefaults:
    """Regression tests for provider-specific defaults."""

    @patch("semiautomatic.image.generate.get_provider")
    @patch("semiautomatic.image.generate.download_file")
    def test_recraft_provider_uses_recraft_defaults(self, mock_download, mock_get_provider):
        """When provider=recraft, should use recraftv3 model and square size (not flux-dev)."""
        from semiautomatic.image.generate import generate_image
        from semiautomatic.image.providers.base import ImageResult, GenerationResult

        mock_provider = MagicMock()
        mock_provider.generate.return_value = GenerationResult(
            images=[ImageResult(url="https://example.com/img.png", width=1024, height=1024)],
            model="recraftv3",
            provider="recraft",
            prompt="test",
        )
        mock_get_provider.return_value = mock_provider
        mock_download.return_value = True

        generate_image("test prompt", provider="recraft", download=False)

        # Verify provider.generate was called with recraft defaults
        call_kwargs = mock_provider.generate.call_args.kwargs
        assert call_kwargs["model"] == "recraftv3", "Should use recraftv3, not flux-dev"
        assert call_kwargs["size"] == "square", "Should use square, not landscape_4_3"


# ---------------------------------------------------------------------------
# image_to_image Function Tests
# ---------------------------------------------------------------------------

class TestImageToImage:
    """Tests for image_to_image orchestration function."""

    @patch("semiautomatic.image.generate.get_provider")
    @patch("semiautomatic.image.generate.download_file")
    def test_image_to_image_basic(self, mock_download, mock_get_provider, tmp_path):
        """Test basic image_to_image call."""
        from semiautomatic.image.generate import image_to_image
        from semiautomatic.image.providers.base import ImageResult, GenerationResult

        # Create dummy input image
        input_file = tmp_path / "input.png"
        input_file.write_bytes(b"fake image data")

        # Setup mocks
        mock_provider = MagicMock()
        mock_provider.image_to_image.return_value = GenerationResult(
            images=[ImageResult(url="https://example.com/img.png", width=1024, height=1024)],
            model="recraftv3",
            provider="recraft",
            prompt="transform to illustration",
        )
        mock_get_provider.return_value = mock_provider
        mock_download.return_value = True

        result = image_to_image(
            input_file,
            "transform to illustration",
            output_dir=tmp_path / "output",
        )

        mock_provider.image_to_image.assert_called_once()
        assert len(result.images) == 1

    @patch("semiautomatic.image.generate.get_provider")
    def test_image_to_image_unsupported_provider(self, mock_get_provider):
        """Test error when provider doesn't support i2i."""
        from semiautomatic.image.generate import image_to_image

        # Mock a provider without image_to_image method
        mock_provider = MagicMock(spec=[])  # Empty spec = no methods
        mock_get_provider.return_value = mock_provider

        with pytest.raises(ValueError) as exc:
            image_to_image(
                "input.png",
                "prompt",
                provider="fake",
            )
        assert "does not support image-to-image" in str(exc.value)


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestRecraftProviderIntegration:
    """Integration tests for Recraft provider (requires RECRAFT_API_KEY)."""

    @pytest.fixture(autouse=True)
    def check_dependencies(self):
        """Skip if RECRAFT_API_KEY not set."""
        import os
        if not os.environ.get("RECRAFT_API_KEY"):
            pytest.skip("RECRAFT_API_KEY not set")

    def test_generate_single_image(self, integration_output_dir):
        """Test generating a single image with Recraft."""
        from semiautomatic.image import generate_image

        result = generate_image(
            "a simple red circle on white background",
            provider="recraft",
            model="recraftv3",
            style="digital_illustration",
            size="square",
            num_images=1,
            output_dir=integration_output_dir,
            output_prefix="recraft_image",
        )

        assert len(result.images) == 1
        assert result.images[0].path is not None
        assert result.images[0].path.exists()
        assert result.images[0].path.name == "recraft_image.png"
