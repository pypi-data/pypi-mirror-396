"""
Tests for semiautomatic.image upscale functionality.

Tests cover:
- UpscaleSettings dataclass
- UpscaleResult dataclass
- FreepikUpscaleProvider (mocked)
- upscale_image orchestration function
- CLI handler
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import base64

from semiautomatic.image.providers.freepik import (
    FreepikUpscaleProvider,
    UpscaleSettings,
    UpscaleResult,
    ScaleFactor,
    UpscaleEngine,
    OptimizedFor,
)
from semiautomatic.image.upscale import (
    upscale_image,
    find_images,
    get_upscale_provider,
    run_upscale_image,
)


# ---------------------------------------------------------------------------
# UpscaleSettings Tests
# ---------------------------------------------------------------------------

class TestUpscaleSettings:
    """Tests for UpscaleSettings dataclass."""

    def test_defaults(self):
        settings = UpscaleSettings()
        assert settings.scale == "2x"
        assert settings.engine == "automatic"
        assert settings.optimized_for == "standard"
        assert settings.creativity == 0
        assert settings.hdr == 0
        assert settings.resemblance == 0
        assert settings.fractality == 0
        assert settings.prompt is None

    def test_custom_values(self):
        settings = UpscaleSettings(
            scale="4x",
            engine="magnific_sharpy",
            optimized_for="soft_portraits",
            creativity=5,
            hdr=3,
            resemblance=7,
            fractality=2,
            prompt="enhance details",
        )
        assert settings.scale == "4x"
        assert settings.engine == "magnific_sharpy"
        assert settings.optimized_for == "soft_portraits"
        assert settings.creativity == 5
        assert settings.hdr == 3
        assert settings.resemblance == 7
        assert settings.fractality == 2
        assert settings.prompt == "enhance details"

    def test_to_dict_basic(self):
        settings = UpscaleSettings()
        result = settings.to_dict()
        assert result["scale_factor"] == "2x"
        assert result["engine"] == "automatic"
        assert result["optimized_for"] == "standard"
        assert "prompt" not in result

    def test_to_dict_with_prompt(self):
        settings = UpscaleSettings(prompt="enhance details")
        result = settings.to_dict()
        assert result["prompt"] == "enhance details"

    def test_to_dict_all_params(self):
        settings = UpscaleSettings(
            scale="4x",
            engine="magnific_illusio",
            optimized_for="nature_n_landscapes",
            creativity=8,
            hdr=5,
            resemblance=3,
            fractality=6,
            prompt="test prompt",
        )
        result = settings.to_dict()
        assert result["scale_factor"] == "4x"
        assert result["engine"] == "magnific_illusio"
        assert result["optimized_for"] == "nature_n_landscapes"
        assert result["creativity"] == 8
        assert result["hdr"] == 5
        assert result["resemblance"] == 3
        assert result["fractality"] == 6
        assert result["prompt"] == "test prompt"


# ---------------------------------------------------------------------------
# UpscaleResult Tests
# ---------------------------------------------------------------------------

class TestUpscaleResult:
    """Tests for UpscaleResult dataclass."""

    def test_basic_result(self):
        result = UpscaleResult(url="https://example.com/image.png")
        assert result.url == "https://example.com/image.png"
        assert result.width is None
        assert result.height is None
        assert result.path is None
        assert result.task_id is None
        assert result.original_path is None

    def test_full_result(self):
        result = UpscaleResult(
            url="https://example.com/image.png",
            width=2048,
            height=2048,
            path=Path("./output/image_2x.png"),
            task_id="task-123",
            original_path=Path("./input/image.png"),
        )
        assert result.url == "https://example.com/image.png"
        assert result.width == 2048
        assert result.height == 2048
        assert result.path == Path("./output/image_2x.png")
        assert result.task_id == "task-123"
        assert result.original_path == Path("./input/image.png")


# ---------------------------------------------------------------------------
# FreepikUpscaleProvider Tests
# ---------------------------------------------------------------------------

class TestFreepikUpscaleProvider:
    """Tests for FreepikUpscaleProvider."""

    def test_provider_name(self):
        provider = FreepikUpscaleProvider()
        assert provider.name == "freepik"

    def test_get_engines(self):
        provider = FreepikUpscaleProvider()
        engines = provider.get_engines()
        assert "automatic" in engines
        assert "magnific_illusio" in engines
        assert "magnific_sharpy" in engines
        assert "magnific_sparkle" in engines

    def test_get_optimization_presets(self):
        provider = FreepikUpscaleProvider()
        presets = provider.get_optimization_presets()
        assert "standard" in presets
        assert "soft_portraits" in presets
        assert "hard_portraits" in presets
        assert "art_n_illustration" in presets
        assert "videogame_assets" in presets
        assert "nature_n_landscapes" in presets
        assert "films_n_photography" in presets
        assert "3d_renders" in presets
        assert "science_fiction_n_horror" in presets

    def test_api_key_not_set(self):
        provider = FreepikUpscaleProvider()
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError) as exc:
                _ = provider._freepik_api_key
            assert "FREEPIK_API_KEY" in str(exc.value)

    def test_api_key_from_env(self):
        provider = FreepikUpscaleProvider()
        with patch.dict("os.environ", {"FREEPIK_API_KEY": "test-key"}):
            provider._api_key = None  # Reset cached key
            assert provider._freepik_api_key == "test-key"

    def test_encode_image_bytes(self):
        provider = FreepikUpscaleProvider()
        test_bytes = b"test image data"
        encoded, path = provider._encode_image(test_bytes)
        expected = base64.b64encode(test_bytes).decode('utf-8')
        assert encoded == expected
        assert path is None

    def test_encode_image_file_not_found(self):
        provider = FreepikUpscaleProvider()
        with pytest.raises(FileNotFoundError):
            provider._encode_image(Path("/nonexistent/image.png"))

    @patch("builtins.open", mock_open(read_data=b"test image content"))
    def test_encode_image_from_path(self):
        provider = FreepikUpscaleProvider()
        with patch.object(Path, "exists", return_value=True):
            encoded, path = provider._encode_image(Path("test.png"))
            expected = base64.b64encode(b"test image content").decode('utf-8')
            assert encoded == expected
            assert path == Path("test.png")

    @patch("requests.post")
    def test_submit_task(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"task_id": "test-task-123"}}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        provider = FreepikUpscaleProvider()
        provider._api_key = "test-key"

        settings = UpscaleSettings(scale="2x")
        task_id = provider._submit_task("base64data", settings)

        assert task_id == "test-task-123"
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_submit_task_no_task_id(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        provider = FreepikUpscaleProvider()
        provider._api_key = "test-key"

        settings = UpscaleSettings()
        with pytest.raises(ValueError) as exc:
            provider._submit_task("base64data", settings)
        assert "No task ID" in str(exc.value)

    def test_find_download_url_direct(self):
        provider = FreepikUpscaleProvider()
        data = {
            "data": {
                "generated": ["https://example.com/result.png"]
            }
        }
        url = provider._find_download_url(data)
        assert url == "https://example.com/result.png"

    def test_find_download_url_nested(self):
        provider = FreepikUpscaleProvider()
        data = {
            "data": {
                "result": {
                    "download_url": "https://example.com/result.png"
                }
            }
        }
        url = provider._find_download_url(data)
        assert url == "https://example.com/result.png"

    def test_find_download_url_not_found(self):
        provider = FreepikUpscaleProvider()
        data = {"data": {"status": "completed"}}
        url = provider._find_download_url(data)
        assert url is None

    @patch("requests.get")
    def test_poll_for_result_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "status": "succeeded",
                "generated": ["https://example.com/result.png"]
            }
        }
        mock_get.return_value = mock_response

        provider = FreepikUpscaleProvider()
        provider._api_key = "test-key"

        url = provider._poll_for_result(
            task_id="test-123",
            poll_interval=0.01,
            poll_timeout=1,
            on_progress=None,
        )
        assert url == "https://example.com/result.png"

    @patch("requests.get")
    def test_poll_for_result_failed(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "status": "failed",
                "error": "Image too small"
            }
        }
        mock_get.return_value = mock_response

        provider = FreepikUpscaleProvider()
        provider._api_key = "test-key"

        with pytest.raises(RuntimeError) as exc:
            provider._poll_for_result(
                task_id="test-123",
                poll_interval=0.01,
                poll_timeout=1,
                on_progress=None,
            )
        assert "Image too small" in str(exc.value)

    @patch("requests.get")
    def test_poll_for_result_timeout(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"status": "processing"}
        }
        mock_get.return_value = mock_response

        provider = FreepikUpscaleProvider()
        provider._api_key = "test-key"

        with pytest.raises(TimeoutError):
            provider._poll_for_result(
                task_id="test-123",
                poll_interval=0.01,
                poll_timeout=0.05,
                on_progress=None,
            )


# ---------------------------------------------------------------------------
# Upscale Orchestration Tests
# ---------------------------------------------------------------------------

class TestUpscaleOrchestration:
    """Tests for upscale_image orchestration function."""

    def test_get_upscale_provider_default(self):
        provider = get_upscale_provider()
        assert isinstance(provider, FreepikUpscaleProvider)

    def test_get_upscale_provider_freepik(self):
        provider = get_upscale_provider("freepik")
        assert isinstance(provider, FreepikUpscaleProvider)

    def test_get_upscale_provider_invalid(self):
        with pytest.raises(ValueError) as exc:
            get_upscale_provider("nonexistent")
        assert "Unknown upscale provider" in str(exc.value)

    def test_upscale_image_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            upscale_image("/nonexistent/image.png")

    @patch("semiautomatic.image.upscale.get_upscale_provider")
    @patch("semiautomatic.image.upscale.download_file")
    def test_upscale_image_basic(self, mock_download, mock_get_provider, tmp_path):
        # Create test image
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"test image data")

        # Mock provider
        mock_provider = MagicMock()
        mock_provider.upscale.return_value = UpscaleResult(
            url="https://example.com/upscaled.jpg",
            task_id="test-123",
        )
        mock_get_provider.return_value = mock_provider

        # Mock download
        mock_download.return_value = True

        result = upscale_image(test_image, output_dir=tmp_path)

        assert result.url == "https://example.com/upscaled.jpg"
        mock_provider.upscale.assert_called_once()

    @patch("semiautomatic.image.upscale.get_upscale_provider")
    def test_upscale_image_no_download(self, mock_get_provider, tmp_path):
        # Create test image
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"test image data")

        # Mock provider
        mock_provider = MagicMock()
        mock_provider.upscale.return_value = UpscaleResult(
            url="https://example.com/upscaled.jpg",
        )
        mock_get_provider.return_value = mock_provider

        result = upscale_image(test_image, download=False)

        assert result.url == "https://example.com/upscaled.jpg"
        assert result.path is None


# ---------------------------------------------------------------------------
# Find Images Tests
# ---------------------------------------------------------------------------

class TestFindImages:
    """Tests for find_images utility."""

    def test_find_images_empty_folder(self, tmp_path):
        result = find_images(tmp_path)
        assert result == []

    def test_find_images_nonexistent_folder(self):
        result = find_images("/nonexistent/folder")
        assert result == []

    def test_find_images_with_images(self, tmp_path):
        # Create test images
        (tmp_path / "image1.jpg").write_bytes(b"test")
        (tmp_path / "image2.png").write_bytes(b"test")
        (tmp_path / "image3.webp").write_bytes(b"test")
        (tmp_path / "not_an_image.txt").write_text("test")

        result = find_images(tmp_path)
        assert len(result) == 3
        assert all(p.suffix.lower() in {".jpg", ".png", ".webp"} for p in result)

    def test_find_images_sorted(self, tmp_path):
        # Create test images in non-alphabetical order
        (tmp_path / "zebra.jpg").write_bytes(b"test")
        (tmp_path / "apple.jpg").write_bytes(b"test")
        (tmp_path / "mango.png").write_bytes(b"test")

        result = find_images(tmp_path)
        names = [p.name for p in result]
        assert names == sorted(names)


# ---------------------------------------------------------------------------
# CLI Handler Tests
# ---------------------------------------------------------------------------

class TestCLIHandler:
    """Tests for run_upscale_image CLI handler."""

    @patch("semiautomatic.image.upscale.upscale_image")
    def test_cli_single_file(self, mock_upscale, tmp_path):
        # Create test image
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"test")

        # Create output directory and result file (so exists() check passes)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        result_file = output_dir / "test_2x.jpg"
        result_file.write_bytes(b"result")

        mock_upscale.return_value = UpscaleResult(
            url="https://example.com/result.jpg",
            path=result_file,
        )

        args = MagicMock()
        args.input = str(test_image)
        args.input_dir = None
        args.output = None
        args.output_dir = str(output_dir)
        args.scale = "2x"
        args.engine = "automatic"
        args.optimized_for = "standard"
        args.prompt = None
        args.auto_prompt = False
        args.creativity = 0
        args.hdr = 0
        args.resemblance = 0
        args.fractality = 0

        result = run_upscale_image(args)
        assert result is True
        mock_upscale.assert_called_once()

    @patch("semiautomatic.image.upscale.upscale_image")
    @patch("semiautomatic.image.upscale.find_images")
    def test_cli_input_dir(self, mock_find, mock_upscale, tmp_path):
        mock_find.return_value = [
            tmp_path / "img1.jpg",
            tmp_path / "img2.png",
        ]

        # Create output directory and result files (so exists() checks pass)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        result_file = output_dir / "result_4x.jpg"
        result_file.write_bytes(b"result")

        mock_upscale.return_value = UpscaleResult(
            url="https://example.com/result.jpg",
            path=result_file,
        )

        args = MagicMock()
        args.input = None
        args.input_dir = str(tmp_path)
        args.output = None
        args.output_dir = str(output_dir)
        args.scale = "4x"
        args.engine = "magnific_sharpy"
        args.optimized_for = "soft_portraits"
        args.prompt = None
        args.auto_prompt = False
        args.creativity = 0
        args.hdr = 0
        args.resemblance = 0
        args.fractality = 0

        result = run_upscale_image(args)
        assert result is True
        assert mock_upscale.call_count == 2

    def test_cli_no_images(self, tmp_path):
        args = MagicMock()
        args.input = None
        args.input_dir = str(tmp_path)
        args.output = None
        args.output_dir = str(tmp_path / "output")

        result = run_upscale_image(args)
        assert result is False

    @patch("semiautomatic.image.upscale.upscale_image")
    def test_cli_handles_exception(self, mock_upscale, tmp_path):
        # Create test image
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"test")

        mock_upscale.side_effect = RuntimeError("API error")

        args = MagicMock()
        args.input = str(test_image)
        args.input_dir = None
        args.output = None
        args.output_dir = str(tmp_path / "output")
        args.scale = "2x"
        args.engine = "automatic"
        args.optimized_for = "standard"
        args.prompt = None
        args.auto_prompt = False
        args.creativity = 0
        args.hdr = 0
        args.resemblance = 0
        args.fractality = 0

        result = run_upscale_image(args)
        assert result is False


# ---------------------------------------------------------------------------
# Type Literal Tests
# ---------------------------------------------------------------------------

class TestTypeLiterals:
    """Tests for type literal definitions."""

    def test_scale_factor_values(self):
        # These should be valid scale factors
        settings_2x = UpscaleSettings(scale="2x")
        settings_4x = UpscaleSettings(scale="4x")
        assert settings_2x.scale == "2x"
        assert settings_4x.scale == "4x"

    def test_engine_values(self):
        for engine in ["automatic", "magnific_illusio", "magnific_sharpy", "magnific_sparkle"]:
            settings = UpscaleSettings(engine=engine)
            assert settings.engine == engine

    def test_optimized_for_values(self):
        valid_values = [
            "standard",
            "soft_portraits",
            "hard_portraits",
            "art_n_illustration",
            "videogame_assets",
            "nature_n_landscapes",
            "films_n_photography",
            "3d_renders",
            "science_fiction_n_horror",
        ]
        for value in valid_values:
            settings = UpscaleSettings(optimized_for=value)
            assert settings.optimized_for == value


# ---------------------------------------------------------------------------
# Regression Tests
# ---------------------------------------------------------------------------

class TestFreepikAPICompatibility:
    """Regression tests to ensure engine/scale values match Freepik API.

    These tests prevent bugs where we use invalid values that the API rejects.
    See: https://docs.freepik.com/api-reference/image-upscaler-creative/post-image-upscaler
    """

    def test_engine_values_match_freepik_api(self):
        """Engine values must match Freepik API exactly."""
        provider = FreepikUpscaleProvider()
        engines = provider.get_engines()

        # These are the ONLY valid values per Freepik API docs
        valid_api_engines = {"automatic", "magnific_illusio", "magnific_sharpy", "magnific_sparkle"}

        assert set(engines) == valid_api_engines, (
            f"Engine values don't match Freepik API. "
            f"Got: {set(engines)}, Expected: {valid_api_engines}"
        )

    def test_scale_factors_match_freepik_api(self):
        """Scale factors must match Freepik API exactly."""
        # These are the valid values per Freepik API docs
        valid_api_scales = {"2x", "4x", "8x", "16x"}

        for scale in valid_api_scales:
            settings = UpscaleSettings(scale=scale)
            assert settings.scale == scale

    def test_settings_to_dict_uses_correct_engine_key(self):
        """The API payload must use 'engine' key with valid value."""
        settings = UpscaleSettings(engine="magnific_sharpy")
        payload = settings.to_dict()

        assert "engine" in payload
        assert payload["engine"] == "magnific_sharpy"

    def test_invalid_engines_not_accepted(self):
        """Old invalid engine names should not be in the provider."""
        provider = FreepikUpscaleProvider()
        engines = provider.get_engines()

        # These were the OLD invalid values
        invalid_engines = ["clarity", "magnific"]
        for invalid in invalid_engines:
            assert invalid not in engines, f"Invalid engine '{invalid}' should not be in provider"


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFreepikUpscaleIntegration:
    """Integration tests for Freepik upscaler (requires FREEPIK_API_KEY)."""

    @pytest.fixture(autouse=True)
    def check_dependencies(self):
        """Skip if FREEPIK_API_KEY not set."""
        import os
        if not os.environ.get("FREEPIK_API_KEY"):
            pytest.skip("FREEPIK_API_KEY not set")

    def test_upscale_2x(self, small_image_path, integration_output_dir):
        """Test 2x upscaling with Freepik."""
        result = upscale_image(
            small_image_path,
            scale="2x",
            output_dir=integration_output_dir,
            output_suffix="_freepik_2x",
        )

        assert result is not None
        assert result.path is not None
        assert result.path.exists()
        assert "_freepik_2x" in result.path.name

        # Verify dimensions doubled
        from PIL import Image
        original = Image.open(small_image_path)
        upscaled = Image.open(result.path)
        assert upscaled.width == original.width * 2
        assert upscaled.height == original.height * 2
