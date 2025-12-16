"""
Tests for semiautomatic.video generation functionality.

Tests cover:
- VideoResult and VideoGenerationResult dataclasses
- FAL video models configuration
- FAL video provider (mocked)
- Video generation orchestration
- CLI handler
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from semiautomatic.video.providers.base import (
    VideoResult,
    VideoGenerationResult,
)
from semiautomatic.video.providers.fal_models import (
    FAL_VIDEO_MODELS,
    DEFAULT_MODEL,
    list_models,
    get_model_config,
    get_model_info,
    normalize_duration,
)
from semiautomatic.video.providers.fal import FALVideoProvider
from semiautomatic.video.providers import (
    get_provider,
    list_providers,
    list_all_models,
)
from semiautomatic.video.generate import (
    generate_video,
    run_generate_video,
    _slugify,
)


# ---------------------------------------------------------------------------
# VideoResult Tests
# ---------------------------------------------------------------------------

class TestVideoResult:
    """Tests for VideoResult dataclass."""

    def test_basic_result(self):
        result = VideoResult(url="https://example.com/video.mp4")
        assert result.url == "https://example.com/video.mp4"
        assert result.path is None
        assert result.duration is None
        assert result.width is None
        assert result.height is None

    def test_full_result(self):
        result = VideoResult(
            url="https://example.com/video.mp4",
            path=Path("./output/video.mp4"),
            duration=5.0,
            width=1920,
            height=1080,
            task_id="task-123",
            content_type="video/mp4",
        )
        assert result.url == "https://example.com/video.mp4"
        assert result.path == Path("./output/video.mp4")
        assert result.duration == 5.0
        assert result.width == 1920
        assert result.height == 1080
        assert result.task_id == "task-123"
        assert result.content_type == "video/mp4"


class TestVideoGenerationResult:
    """Tests for VideoGenerationResult dataclass."""

    def test_basic_result(self):
        video = VideoResult(url="https://example.com/video.mp4")
        result = VideoGenerationResult(
            video=video,
            model="kling2.1",
            provider="fal",
            prompt="a cat walking",
        )
        assert result.video == video
        assert result.model == "kling2.1"
        assert result.provider == "fal"
        assert result.prompt == "a cat walking"
        assert result.seed is None
        assert result.input_image is None

    def test_full_result(self):
        video = VideoResult(url="https://example.com/video.mp4")
        result = VideoGenerationResult(
            video=video,
            model="kling2.1",
            provider="fal",
            prompt="a cat walking",
            seed=12345,
            input_image=Path("./input/cat.jpg"),
            metadata={"duration": 5},
        )
        assert result.seed == 12345
        assert result.input_image == Path("./input/cat.jpg")
        assert result.metadata["duration"] == 5


# ---------------------------------------------------------------------------
# FAL Models Tests
# ---------------------------------------------------------------------------

class TestFALModels:
    """Tests for FAL video model configurations."""

    def test_default_model(self):
        assert DEFAULT_MODEL == "kling2.1"

    def test_list_models(self):
        models = list_models()
        assert "kling1.5" in models
        assert "kling1.6" in models
        assert "kling2.0" in models
        assert "kling2.1" in models
        assert "kling2.5" in models
        assert "kling2.6" in models
        assert "klingo1" in models
        assert "seedance1.0" in models
        assert "hailuo2.0" in models

    def test_get_model_config_valid(self):
        config = get_model_config("kling2.1")
        assert config is not None
        assert "endpoint" in config
        assert "default_params" in config

    def test_get_model_config_invalid(self):
        config = get_model_config("nonexistent")
        assert config is None

    def test_get_model_info(self):
        info = get_model_info("kling2.1")
        assert info["name"] == "kling2.1"
        assert "description" in info
        assert "supports_tail_image" in info
        assert info["supports_tail_image"] is True

    def test_model_supports_tail_image(self):
        # Models that support tail images
        assert get_model_config("kling1.5")["supports_tail_image"] is True
        assert get_model_config("kling1.6")["supports_tail_image"] is True
        assert get_model_config("kling2.1")["supports_tail_image"] is True
        assert get_model_config("klingo1")["supports_tail_image"] is True
        assert get_model_config("seedance1.0")["supports_tail_image"] is True

        # kling2.5 supports tail images
        assert get_model_config("kling2.5")["supports_tail_image"] is True

        # Models that don't support tail images
        assert get_model_config("kling2.0")["supports_tail_image"] is False
        assert get_model_config("hailuo2.0")["supports_tail_image"] is False

    def test_normalize_duration_valid(self):
        assert normalize_duration("kling2.1", 5) == 5
        assert normalize_duration("kling2.1", 10) == 10

    def test_normalize_duration_hailuo(self):
        # Hailuo uses 6s instead of 5s
        assert normalize_duration("hailuo2.0", 5) == 6
        assert normalize_duration("hailuo2.0", 10) == 10


# ---------------------------------------------------------------------------
# Provider Registry Tests
# ---------------------------------------------------------------------------

class TestProviderRegistry:
    """Tests for video provider registry."""

    def test_list_providers(self):
        providers = list_providers()
        assert "fal" in providers

    def test_get_provider_default(self):
        provider = get_provider()
        assert isinstance(provider, FALVideoProvider)

    def test_get_provider_fal(self):
        provider = get_provider("fal")
        assert isinstance(provider, FALVideoProvider)

    def test_get_provider_invalid(self):
        with pytest.raises(ValueError) as exc:
            get_provider("nonexistent")
        assert "Unknown video provider" in str(exc.value)

    def test_list_all_models(self):
        all_models = list_all_models()
        assert "fal" in all_models
        assert "kling2.1" in all_models["fal"]


# ---------------------------------------------------------------------------
# FAL Provider Tests
# ---------------------------------------------------------------------------

class TestFALProvider:
    """Tests for FALVideoProvider."""

    def test_name(self):
        provider = FALVideoProvider()
        assert provider.name == "fal"

    def test_list_models(self):
        provider = FALVideoProvider()
        models = provider.list_models()
        assert "kling2.1" in models
        assert len(models) >= 9

    def test_get_model_info(self):
        provider = FALVideoProvider()
        info = provider.get_model_info("kling2.1")
        assert info["name"] == "kling2.1"
        assert "description" in info

    def test_get_model_info_invalid(self):
        provider = FALVideoProvider()
        info = provider.get_model_info("nonexistent")
        assert info == {}

    def test_supports_tail_image(self):
        provider = FALVideoProvider()
        assert provider.supports_tail_image("kling2.1") is True
        assert provider.supports_tail_image("kling2.0") is False

    def test_resolve_image_url_already_url(self):
        provider = FALVideoProvider()
        url = provider._resolve_image_url("https://example.com/image.jpg")
        assert url == "https://example.com/image.jpg"

    def test_resolve_image_url_local_raises(self):
        provider = FALVideoProvider()
        with pytest.raises(FileNotFoundError) as exc:
            provider._resolve_image_url("/path/to/local/image.jpg")
        assert "Image file not found" in str(exc.value)

    def test_build_arguments_basic(self):
        provider = FALVideoProvider()
        config = get_model_config("kling2.1")
        args = provider._build_arguments(
            model="kling2.1",
            config=config,
            prompt="a cat walking",
            image="https://example.com/cat.jpg",
            tail_image=None,
            duration=5,
            aspect_ratio="16:9",
            negative_prompt=None,
            seed=None,
            cfg_scale=None,
            loop=False,
        )
        assert args["prompt"] == "a cat walking"
        assert args["image_url"] == "https://example.com/cat.jpg"
        assert args["duration"] == 5
        assert args["aspect_ratio"] == "16:9"

    def test_build_arguments_with_loop(self):
        provider = FALVideoProvider()
        config = get_model_config("kling2.1")
        args = provider._build_arguments(
            model="kling2.1",
            config=config,
            prompt="breathing",
            image="https://example.com/portrait.jpg",
            tail_image=None,
            duration=5,
            aspect_ratio="16:9",
            negative_prompt=None,
            seed=None,
            cfg_scale=None,
            loop=True,
        )
        assert args["image_url"] == "https://example.com/portrait.jpg"
        assert args["tail_image_url"] == "https://example.com/portrait.jpg"

    def test_build_arguments_with_tail_image(self):
        provider = FALVideoProvider()
        config = get_model_config("kling2.1")
        args = provider._build_arguments(
            model="kling2.1",
            config=config,
            prompt="morphing",
            image="https://example.com/start.jpg",
            tail_image="https://example.com/end.jpg",
            duration=5,
            aspect_ratio="16:9",
            negative_prompt=None,
            seed=None,
            cfg_scale=None,
            loop=False,
        )
        assert args["image_url"] == "https://example.com/start.jpg"
        assert args["tail_image_url"] == "https://example.com/end.jpg"


# ---------------------------------------------------------------------------
# Orchestration Tests
# ---------------------------------------------------------------------------

class TestOrchestration:
    """Tests for generate_video orchestration."""

    @patch("semiautomatic.video.generate.get_provider")
    @patch("semiautomatic.video.generate.download_file")
    def test_generate_video_basic(self, mock_download, mock_get_provider, tmp_path):
        mock_provider = MagicMock()
        mock_provider.generate.return_value = VideoGenerationResult(
            video=VideoResult(url="https://example.com/video.mp4"),
            model="kling2.1",
            provider="fal",
            prompt="a cat walking",
        )
        mock_get_provider.return_value = mock_provider
        mock_download.return_value = True

        result = generate_video(
            "a cat walking",
            image="https://example.com/cat.jpg",
            output_dir=tmp_path,
        )

        assert result.video.url == "https://example.com/video.mp4"
        mock_provider.generate.assert_called_once()

    @patch("semiautomatic.video.generate.get_provider")
    def test_generate_video_no_download(self, mock_get_provider, tmp_path):
        # Create test image
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake image data")

        mock_provider = MagicMock()
        mock_provider.generate.return_value = VideoGenerationResult(
            video=VideoResult(url="https://example.com/video.mp4"),
            model="kling2.1",
            provider="fal",
            prompt="a cat walking",
        )
        mock_get_provider.return_value = mock_provider

        result = generate_video(
            "a cat walking",
            image=test_image,
            download=False,
        )

        assert result.video.url == "https://example.com/video.mp4"
        assert result.video.path is None


class TestSlugify:
    """Tests for _slugify helper."""

    def test_basic_text(self):
        assert _slugify("a cat walking") == "a_cat_walking"

    def test_with_special_chars(self):
        assert _slugify("hello, world!") == "hello_world"

    def test_with_multiple_spaces(self):
        assert _slugify("hello   world") == "hello_world"

    def test_uppercase(self):
        assert _slugify("Hello World") == "hello_world"


# ---------------------------------------------------------------------------
# CLI Handler Tests
# ---------------------------------------------------------------------------

class TestCLIHandler:
    """Tests for run_generate_video CLI handler."""

    @patch("semiautomatic.video.generate.list_all_models")
    @patch("semiautomatic.video.generate.get_provider")
    def test_list_models_flag(self, mock_get_provider, mock_list_models, capsys):
        mock_list_models.return_value = {"fal": ["kling2.1", "kling2.0"]}
        mock_provider = MagicMock()
        mock_provider.get_model_info.return_value = {
            "description": "Test model",
            "supports_tail_image": True,
        }
        mock_get_provider.return_value = mock_provider

        args = MagicMock()
        args.list_models = True

        result = run_generate_video(args)
        assert result is True

        captured = capsys.readouterr()
        assert "fal" in captured.out

    def test_missing_prompt_fails(self):
        args = MagicMock()
        args.list_models = False
        args.list_motions = False
        args.prompt = None

        result = run_generate_video(args)
        assert result is False

    @patch("semiautomatic.video.generate.generate_video")
    def test_successful_generation(self, mock_generate, tmp_path):
        output_file = tmp_path / "video.mp4"
        output_file.write_bytes(b"video data")

        mock_generate.return_value = VideoGenerationResult(
            video=VideoResult(
                url="https://example.com/video.mp4",
                path=output_file,
            ),
            model="kling2.1",
            provider="fal",
            prompt="a cat walking",
        )

        args = MagicMock()
        args.list_models = False
        args.list_motions = False
        args.prompt = "a cat walking"
        args.provider = None
        args.model = None
        args.image = "https://example.com/cat.jpg"
        args.tail_image = None
        args.duration = 5
        args.aspect_ratio = "16:9"
        args.negative_prompt = None
        args.seed = None
        args.loop = False
        args.motion = None
        args.motion_strength = None
        args.output = None
        args.output_dir = str(tmp_path)

        result = run_generate_video(args)
        assert result is True

    @patch("semiautomatic.video.generate.generate_video")
    def test_handles_exception(self, mock_generate):
        mock_generate.side_effect = RuntimeError("API error")

        args = MagicMock()
        args.list_models = False
        args.list_motions = False
        args.prompt = "a cat walking"
        args.provider = None
        args.model = None
        args.image = "https://example.com/cat.jpg"
        args.tail_image = None
        args.duration = 5
        args.aspect_ratio = "16:9"
        args.negative_prompt = None
        args.seed = None
        args.loop = False
        args.motion = None
        args.motion_strength = None
        args.output = None
        args.output_dir = "./output"

        result = run_generate_video(args)
        assert result is False


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFALVideoIntegration:
    """Integration tests for FAL video provider (requires FAL_KEY)."""

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
            output_prefix="kling26_source",
        )
        return result.images[0].url

    def test_generate_video_kling26(self, generated_image_url, integration_output_dir):
        """Test video generation with Kling 2.6."""
        result = generate_video(
            prompt="kling26 test",
            image=generated_image_url,
            model="kling2.6",
            duration=5,
            aspect_ratio="16:9",
            output_dir=integration_output_dir,
        )

        assert result is not None
        assert result.video is not None
        assert result.video.path is not None
        assert result.video.path.exists()
        assert result.video.path.suffix == ".mp4"
        assert "kling2.6" in result.video.path.name
