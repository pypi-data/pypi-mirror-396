"""
Tests for semiautomatic.image generation.

Tests cover:
- Base classes (ImageSize, LoRASpec, GenerationResult)
- Size parsing and presets
- FAL model configurations
- FAL provider (mocked)
- Provider registry
- generate_image orchestration
- CLI handler
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from semiautomatic.image.providers.base import (
    ImageSize,
    LoRASpec,
    ImageResult,
    GenerationResult,
    parse_image_size,
    IMAGE_SIZE_PRESETS,
)
from semiautomatic.image.providers.fal_models import (
    FAL_MODELS,
    DEFAULT_MODEL,
    get_model_config,
    list_models as list_fal_models,
    get_models_with_lora_support,
)
from semiautomatic.image.providers import (
    get_provider,
    list_providers,
    list_all_models,
)


# ---------------------------------------------------------------------------
# ImageSize Tests
# ---------------------------------------------------------------------------

class TestImageSize:
    """Tests for ImageSize dataclass."""

    def test_creation(self):
        size = ImageSize(width=1024, height=768)
        assert size.width == 1024
        assert size.height == 768

    def test_from_string_wxh(self):
        size = ImageSize.from_string("1920x1080")
        assert size.width == 1920
        assert size.height == 1080

    def test_from_string_single_number(self):
        """Single number creates a square image."""
        size = ImageSize.from_string("512")
        assert size.width == 512
        assert size.height == 512

    def test_from_string_invalid(self):
        with pytest.raises(ValueError):
            ImageSize.from_string("invalid")


# ---------------------------------------------------------------------------
# LoRASpec Tests
# ---------------------------------------------------------------------------

class TestLoRASpec:
    """Tests for LoRASpec dataclass."""

    def test_creation(self):
        lora = LoRASpec(path="/path/to/lora.safetensors", scale=0.8)
        assert lora.path == "/path/to/lora.safetensors"
        assert lora.scale == 0.8

    def test_default_scale(self):
        lora = LoRASpec(path="/path/to/lora.safetensors")
        assert lora.scale == 1.0

    def test_from_string_path_only(self):
        lora = LoRASpec.from_string("/path/to/lora.safetensors")
        assert lora.path == "/path/to/lora.safetensors"
        assert lora.scale == 1.0

    def test_from_string_with_scale(self):
        lora = LoRASpec.from_string("/path/to/lora.safetensors:0.75")
        assert lora.path == "/path/to/lora.safetensors"
        assert lora.scale == 0.75

    def test_from_string_url(self):
        lora = LoRASpec.from_string("https://example.com/lora.safetensors:0.5")
        assert lora.path == "https://example.com/lora.safetensors"
        assert lora.scale == 0.5


# ---------------------------------------------------------------------------
# GenerationResult Tests
# ---------------------------------------------------------------------------

class TestGenerationResult:
    """Tests for GenerationResult dataclass."""

    def test_creation(self):
        images = [
            ImageResult(url="https://example.com/1.png", width=1024, height=768),
            ImageResult(url="https://example.com/2.png", width=1024, height=768),
        ]
        result = GenerationResult(
            images=images,
            model="flux-dev",
            provider="fal",
            prompt="a cat",
        )
        assert len(result.images) == 2
        assert result.model == "flux-dev"
        assert result.provider == "fal"
        assert result.prompt == "a cat"


# ---------------------------------------------------------------------------
# Size Parsing Tests
# ---------------------------------------------------------------------------

class TestParseImageSize:
    """Tests for parse_image_size function."""

    def test_preset_square(self):
        result = parse_image_size("square")
        assert isinstance(result, ImageSize)
        assert result.width == 1024
        assert result.height == 1024

    def test_preset_portrait(self):
        result = parse_image_size("portrait_4_3")
        assert isinstance(result, ImageSize)
        assert result.width == 768
        assert result.height == 1024

    def test_wxh_string(self):
        result = parse_image_size("1920x1080")
        assert isinstance(result, ImageSize)
        assert result.width == 1920
        assert result.height == 1080

    def test_image_size_object(self):
        size = ImageSize(width=800, height=600)
        result = parse_image_size(size)
        assert result is size

    def test_unknown_preset_returned_as_string(self):
        """Unknown preset names returned as-is for API compatibility."""
        result = parse_image_size("unknown_preset")
        assert result == "unknown_preset"


class TestImageSizePresets:
    """Tests for IMAGE_SIZE_PRESETS constant."""

    def test_has_required_presets(self):
        required = ["square", "square_hd", "portrait_4_3", "portrait_16_9",
                    "landscape_4_3", "landscape_16_9"]
        for preset in required:
            assert preset in IMAGE_SIZE_PRESETS

    def test_preset_values(self):
        square = IMAGE_SIZE_PRESETS["square"]
        assert square.width == 1024
        assert square.height == 1024

        landscape = IMAGE_SIZE_PRESETS["landscape_4_3"]
        assert landscape.width == 1024
        assert landscape.height == 768


# ---------------------------------------------------------------------------
# FAL Models Tests
# ---------------------------------------------------------------------------

class TestFALModels:
    """Tests for FAL model configurations."""

    def test_default_model(self):
        assert DEFAULT_MODEL == "flux-dev"

    def test_list_models(self):
        models = list_fal_models()
        assert "flux-dev" in models
        assert "flux-schnell" in models
        assert "flux-krea" in models
        assert "qwen" in models
        assert "wan-22" in models

    def test_get_model_config_valid(self):
        config = get_model_config("flux-dev")
        assert "endpoint" in config
        assert "architecture" in config
        assert config["architecture"] == "flux"

    def test_get_model_config_invalid(self):
        with pytest.raises(ValueError) as exc:
            get_model_config("nonexistent-model")
        assert "Unknown FAL model" in str(exc.value)

    def test_models_with_lora_support(self):
        lora_models = get_models_with_lora_support()
        assert "flux-krea" in lora_models
        assert "qwen" in lora_models
        assert "wan-22" in lora_models
        assert "flux-dev" not in lora_models  # flux-dev doesn't support LoRA

    def test_model_has_required_fields(self):
        for name, config in FAL_MODELS.items():
            assert "endpoint" in config, f"{name} missing endpoint"
            assert "architecture" in config, f"{name} missing architecture"
            assert "default_params" in config, f"{name} missing default_params"


# ---------------------------------------------------------------------------
# Provider Registry Tests
# ---------------------------------------------------------------------------

class TestProviderRegistry:
    """Tests for provider registry functions."""

    def test_list_providers(self):
        providers = list_providers()
        assert "fal" in providers

    def test_get_provider_default(self):
        provider = get_provider()
        assert provider.name == "fal"

    def test_get_provider_by_name(self):
        provider = get_provider("fal")
        assert provider.name == "fal"

    def test_get_provider_invalid(self):
        with pytest.raises(ValueError) as exc:
            get_provider("nonexistent")
        assert "Unknown image provider" in str(exc.value)

    def test_provider_singleton(self):
        """Provider instances should be cached."""
        p1 = get_provider("fal")
        p2 = get_provider("fal")
        assert p1 is p2

    def test_list_all_models(self):
        all_models = list_all_models()
        assert "fal" in all_models
        assert "flux-dev" in all_models["fal"]


# ---------------------------------------------------------------------------
# FAL Provider Tests (Mocked)
# ---------------------------------------------------------------------------

class TestFALProvider:
    """Tests for FALImageProvider (mocked)."""

    def test_name(self):
        provider = get_provider("fal")
        assert provider.name == "fal"

    def test_list_models(self):
        provider = get_provider("fal")
        models = provider.list_models()
        assert "flux-dev" in models

    def test_get_model_info(self):
        provider = get_provider("fal")
        info = provider.get_model_info("flux-krea")
        assert info["supports_loras"] is True
        assert info["architecture"] == "flux"

    def test_get_model_info_invalid(self):
        provider = get_provider("fal")
        info = provider.get_model_info("nonexistent")
        assert info == {}

    def test_build_arguments(self):
        """Test that _build_arguments() builds correct arguments."""
        from semiautomatic.image.providers.fal import FALImageProvider
        from semiautomatic.image.providers.fal_models import get_model_config

        provider = FALImageProvider()
        config = get_model_config("flux-dev")

        args = provider._build_arguments(
            prompt="a cat",
            config=config,
            size="landscape_4_3",
            num_images=2,
            seed=12345,
            loras=None,
            steps=None,
            guidance=None,
            output_format="png",
        )

        assert args["prompt"] == "a cat"
        assert args["num_images"] == 2
        assert args["seed"] == 12345
        assert args["output_format"] == "png"
        assert "image_size" in args

    def test_build_arguments_with_overrides(self):
        """Test that _build_arguments() respects overrides."""
        from semiautomatic.image.providers.fal import FALImageProvider
        from semiautomatic.image.providers.fal_models import get_model_config

        provider = FALImageProvider()
        config = get_model_config("flux-dev")

        args = provider._build_arguments(
            prompt="a cat",
            config=config,
            size="1920x1080",
            num_images=1,
            seed=None,
            loras=None,
            steps=50,
            guidance=7.5,
            output_format="jpeg",
        )

        assert args["num_inference_steps"] == 50
        assert args["guidance_scale"] == 7.5
        assert args["output_format"] == "jpeg"
        assert isinstance(args["image_size"], dict)
        assert args["image_size"]["width"] == 1920
        assert args["image_size"]["height"] == 1080

    def test_parse_result(self):
        """Test that _parse_result() correctly parses FAL response."""
        from semiautomatic.image.providers.fal import FALImageProvider

        provider = FALImageProvider()
        result = provider._parse_result(
            result={
                "images": [
                    {"url": "https://example.com/1.png", "width": 1024, "height": 768},
                    {"url": "https://example.com/2.png", "width": 1024, "height": 768},
                ],
                "seed": 12345,
            },
            model="flux-dev",
            prompt="a cat",
        )

        assert len(result.images) == 2
        assert result.images[0].url == "https://example.com/1.png"
        assert result.images[0].width == 1024
        assert result.model == "flux-dev"
        assert result.provider == "fal"
        assert result.seed == 12345

    def test_parse_result_single_image_format(self):
        """Test that _parse_result() handles {image: {...}} format."""
        from semiautomatic.image.providers.fal import FALImageProvider

        provider = FALImageProvider()
        result = provider._parse_result(
            result={
                "image": {"url": "https://example.com/img.png", "width": 512, "height": 512}
            },
            model="flux-dev",
            prompt="a cat",
        )

        assert len(result.images) == 1
        assert result.images[0].url == "https://example.com/img.png"

    def test_num_images_clamped(self):
        """Test that num_images is clamped to 1-4."""
        from semiautomatic.image.providers.fal import FALImageProvider
        from semiautomatic.image.providers.fal_models import get_model_config

        provider = FALImageProvider()
        config = get_model_config("flux-dev")

        args = provider._build_arguments(
            prompt="a cat",
            config=config,
            size="square",
            num_images=10,  # Should be clamped to 4
            seed=None,
            loras=None,
            steps=None,
            guidance=None,
            output_format="png",
        )

        assert args["num_images"] == 4


# ---------------------------------------------------------------------------
# generate_image Orchestration Tests
# ---------------------------------------------------------------------------

class TestGenerateImageOrchestration:
    """Tests for generate_image() orchestration function."""

    @patch("semiautomatic.image.generate.get_provider")
    @patch("semiautomatic.image.generate.download_file")
    def test_generate_image_basic(self, mock_download, mock_get_provider):
        """Test basic generate_image call."""
        from semiautomatic.image.generate import generate_image

        # Setup mocks
        mock_provider = MagicMock()
        mock_provider.generate.return_value = GenerationResult(
            images=[ImageResult(url="https://example.com/img.png", width=1024, height=768)],
            model="flux-dev",
            provider="fal",
            prompt="a cat",
        )
        mock_get_provider.return_value = mock_provider
        mock_download.return_value = True

        result = generate_image("a cat", output_dir=Path("/tmp/test"))

        mock_provider.generate.assert_called_once()
        assert len(result.images) == 1

    @patch("semiautomatic.image.generate.get_provider")
    def test_generate_image_no_download(self, mock_get_provider):
        """Test generate_image with download=False."""
        from semiautomatic.image.generate import generate_image

        mock_provider = MagicMock()
        mock_provider.generate.return_value = GenerationResult(
            images=[ImageResult(url="https://example.com/img.png", width=1024, height=768)],
            model="flux-dev",
            provider="fal",
            prompt="a cat",
        )
        mock_get_provider.return_value = mock_provider

        result = generate_image("a cat", download=False)

        # Should not have set path on images
        assert result.images[0].path is None

    @patch("semiautomatic.image.generate.get_provider")
    def test_generate_image_with_loras(self, mock_get_provider):
        """Test generate_image with LoRA specifications."""
        from semiautomatic.image.generate import generate_image

        mock_provider = MagicMock()
        mock_provider.generate.return_value = GenerationResult(
            images=[ImageResult(url="https://example.com/img.png", width=1024, height=768)],
            model="flux-krea",
            provider="fal",
            prompt="a cat",
        )
        mock_get_provider.return_value = mock_provider

        result = generate_image(
            "a cat",
            model="flux-krea",
            loras=["path/to/lora.safetensors:0.8"],
            download=False,
        )

        call_args = mock_provider.generate.call_args
        assert call_args.kwargs["loras"] is not None
        assert len(call_args.kwargs["loras"]) == 1
        assert call_args.kwargs["loras"][0].scale == 0.8


# ---------------------------------------------------------------------------
# CLI Handler Tests
# ---------------------------------------------------------------------------

class TestCLIHandler:
    """Tests for run_generate_image CLI handler."""

    def test_list_models_flag(self, capsys):
        """Test --list-models flag."""
        from semiautomatic.image.generate import run_generate_image
        from argparse import Namespace

        args = Namespace(list_models=True)
        result = run_generate_image(args)

        assert result is True
        captured = capsys.readouterr()
        assert "flux-dev" in captured.out

    def test_missing_prompt_fails(self):
        """Test that missing prompt returns False."""
        from semiautomatic.image.generate import run_generate_image
        from argparse import Namespace

        args = Namespace(
            list_models=False,
            prompt=None,
        )
        result = run_generate_image(args)

        assert result is False

    @patch("semiautomatic.image.generate.generate_image")
    def test_successful_generation(self, mock_generate):
        """Test successful generation via CLI handler."""
        from semiautomatic.image.generate import run_generate_image
        from argparse import Namespace

        mock_generate.return_value = GenerationResult(
            images=[ImageResult(url="https://example.com/img.png", width=1024, height=768)],
            model="flux-dev",
            provider="fal",
            prompt="a cat",
        )

        args = Namespace(
            list_models=False,
            prompt="a cat",
            model="flux-dev",
            size="landscape_4_3",
            num_images=1,
            seed=None,
            lora=None,
            output_dir="./output",
            steps=None,
            guidance=None,
            format="png",
        )
        result = run_generate_image(args)

        assert result is True
        mock_generate.assert_called_once()


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFALProviderIntegration:
    """Integration tests for FAL provider (requires FAL_KEY)."""

    @pytest.fixture(autouse=True)
    def check_dependencies(self):
        """Skip if fal_client not installed or FAL_KEY not set."""
        try:
            import fal_client
        except ImportError:
            pytest.skip("fal_client not installed")

        import os
        if not os.environ.get("FAL_KEY"):
            pytest.skip("FAL_KEY not set")

    def test_generate_single_image(self, integration_output_dir):
        """Test generating a single image."""
        from semiautomatic.image import generate_image

        result = generate_image(
            "a simple test image of a red circle on white background",
            model="flux-schnell",  # Use schnell for speed
            size="square",
            num_images=1,
            output_dir=integration_output_dir,
            output_prefix="fal_image",
        )

        assert len(result.images) == 1
        assert result.images[0].path is not None
        assert result.images[0].path.exists()
        assert result.images[0].path.name == "fal_image.png"
