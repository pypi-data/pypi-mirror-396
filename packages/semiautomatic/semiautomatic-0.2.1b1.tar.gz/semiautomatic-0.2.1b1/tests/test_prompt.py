"""
Tests for semiautomatic.prompt module.

Tests cover:
- Image prompt generation
- Video prompt generation
- Schema handling
- Platform-specific formatting
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from semiautomatic.prompt import (
    generate_image_prompt,
    generate_video_prompt,
    ImagePromptResult,
    VideoPromptResult,
    IMAGE_PLATFORM_CONFIGS,
    VIDEO_MODEL_CONFIGS,
)


class TestImagePlatformConfigs:
    """Tests for image platform configurations."""

    def test_flux_config_exists(self):
        """Should have flux platform config."""
        assert "flux" in IMAGE_PLATFORM_CONFIGS

    def test_midjourney_config_exists(self):
        """Should have midjourney platform config."""
        assert "midjourney" in IMAGE_PLATFORM_CONFIGS

    def test_configs_have_required_fields(self):
        """Each config should have required fields."""
        for name, config in IMAGE_PLATFORM_CONFIGS.items():
            assert "name" in config
            assert "max_words" in config
            assert "style" in config


class TestVideoModelConfigs:
    """Tests for video model configurations."""

    def test_higgsfield_config_exists(self):
        """Should have higgsfield model config."""
        assert "higgsfield" in VIDEO_MODEL_CONFIGS

    def test_kling_config_exists(self):
        """Should have kling model config."""
        assert "kling" in VIDEO_MODEL_CONFIGS

    def test_generic_config_exists(self):
        """Should have generic model config."""
        assert "generic" in VIDEO_MODEL_CONFIGS

    def test_configs_have_required_fields(self):
        """Each config should have required fields."""
        for name, config in VIDEO_MODEL_CONFIGS.items():
            assert "name" in config
            assert "max_words" in config
            assert "style" in config


class TestGenerateImagePrompt:
    """Tests for generate_image_prompt()."""

    def test_returns_image_prompt_result(self):
        """Should return ImagePromptResult."""
        with patch("semiautomatic.prompt.image.complete", return_value="test prompt"):
            result = generate_image_prompt("a cat")

            assert isinstance(result, ImagePromptResult)

    def test_result_has_prompt(self):
        """Result should contain the generated prompt."""
        with patch("semiautomatic.prompt.image.complete", return_value="a fluffy cat"):
            result = generate_image_prompt("a cat")

            assert result.prompt == "a fluffy cat"

    def test_result_has_platform(self):
        """Result should include the platform."""
        with patch("semiautomatic.prompt.image.complete", return_value="test"):
            result = generate_image_prompt("a cat", platform="flux")

            assert result.platform == "flux"

    def test_default_platform_is_flux(self):
        """Default platform should be flux."""
        with patch("semiautomatic.prompt.image.complete", return_value="test"):
            result = generate_image_prompt("a cat")

            assert result.platform == "flux"

    def test_raises_for_missing_schema(self, temp_dir):
        """Should raise FileNotFoundError for missing schema."""
        missing_schema = temp_dir / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            generate_image_prompt("a cat", schema_path=missing_schema)

    def test_loads_schema_file(self, temp_dir):
        """Should load and use schema file."""
        schema = {
            "name": "Test Aesthetic",
            "mood": ["happy", "bright"],
            "description": "A test aesthetic"
        }
        schema_path = temp_dir / "test_schema.json"
        schema_path.write_text(json.dumps(schema))

        with patch("semiautomatic.prompt.image.complete", return_value="styled prompt"):
            result = generate_image_prompt("a cat", schema_path=schema_path)

            assert result.schema_name == "Test Aesthetic"

    def test_passes_intent_to_llm(self):
        """Should pass user intent to LLM."""
        with patch("semiautomatic.prompt.image.complete", return_value="test") as mock:
            generate_image_prompt("dancing person at rave")

            call_args = mock.call_args[0]
            messages = call_args[0]
            assert any("dancing person at rave" in str(m) for m in messages)


class TestGenerateVideoPrompt:
    """Tests for generate_video_prompt()."""

    def test_returns_video_prompt_result(self, small_image_path):
        """Should return VideoPromptResult."""
        with patch("semiautomatic.prompt.video.complete_with_vision", return_value="walk"):
            result = generate_video_prompt(small_image_path)

            assert isinstance(result, VideoPromptResult)

    def test_result_has_prompt(self, small_image_path):
        """Result should contain the generated prompt."""
        with patch("semiautomatic.prompt.video.complete_with_vision", return_value="person walks"):
            result = generate_video_prompt(small_image_path)

            assert result.prompt == "person walks"

    def test_result_has_video_model(self, small_image_path):
        """Result should include the video model."""
        with patch("semiautomatic.prompt.video.complete_with_vision", return_value="test"):
            result = generate_video_prompt(small_image_path, video_model="kling")

            assert result.video_model == "kling"

    def test_default_video_model_is_higgsfield(self, small_image_path):
        """Default video model should be higgsfield."""
        with patch("semiautomatic.prompt.video.complete_with_vision", return_value="test"):
            result = generate_video_prompt(small_image_path)

            assert result.video_model == "higgsfield"

    def test_raises_for_missing_image(self, temp_dir):
        """Should raise FileNotFoundError for missing image."""
        missing_image = temp_dir / "nonexistent.jpg"

        with pytest.raises(FileNotFoundError):
            generate_video_prompt(missing_image)

    def test_raises_for_missing_schema(self, temp_dir, small_image_path):
        """Should raise FileNotFoundError for missing schema."""
        missing_schema = temp_dir / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            generate_video_prompt(small_image_path, schema_path=missing_schema)

    def test_loads_schema_file(self, temp_dir, small_image_path):
        """Should load and use schema file."""
        schema = {
            "name": "Test Motion",
            "motion_philosophy": {
                "speed": "slow",
                "quality": "smooth"
            }
        }
        schema_path = temp_dir / "test_motion.json"
        schema_path.write_text(json.dumps(schema))

        with patch("semiautomatic.prompt.video.complete_with_vision", return_value="motion"):
            result = generate_video_prompt(small_image_path, schema_path=schema_path)

            assert result.schema_name == "Test Motion"

    def test_includes_motion_preset(self, small_image_path):
        """Should include motion preset in result."""
        with patch("semiautomatic.prompt.video.complete_with_vision", return_value="test"):
            result = generate_video_prompt(
                small_image_path,
                motion_preset="catwalk"
            )

            assert result.motion_preset == "catwalk"


class TestImagePromptResult:
    """Tests for ImagePromptResult dataclass."""

    def test_has_required_fields(self):
        """Should have all required fields."""
        result = ImagePromptResult(
            prompt="test prompt",
            descriptive_only="test prompt",
            platform="flux"
        )

        assert result.prompt == "test prompt"
        assert result.descriptive_only == "test prompt"
        assert result.platform == "flux"

    def test_optional_fields_default_to_none(self):
        """Optional fields should default to None."""
        result = ImagePromptResult(
            prompt="test",
            descriptive_only="test",
            platform="flux"
        )

        assert result.schema_name is None
        assert result.schema_version is None


class TestVideoPromptResult:
    """Tests for VideoPromptResult dataclass."""

    def test_has_required_fields(self):
        """Should have all required fields."""
        result = VideoPromptResult(
            prompt="walk forward",
            video_model="higgsfield",
            input_image="test.jpg"
        )

        assert result.prompt == "walk forward"
        assert result.video_model == "higgsfield"
        assert result.input_image == "test.jpg"

    def test_optional_fields_default_to_none(self):
        """Optional fields should default to None."""
        result = VideoPromptResult(
            prompt="test",
            video_model="higgsfield",
            input_image="test.jpg"
        )

        assert result.schema_name is None
        assert result.motion_preset is None


@pytest.mark.integration
class TestPromptIntegration:
    """Integration tests for prompt generation.

    These tests require ANTHROPIC_API_KEY to be set and make real API calls.
    Run with: pytest -m integration
    """

    def test_generate_image_prompt(self, integration_output_dir):
        """Should generate an image prompt."""
        import os

        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        result = generate_image_prompt("person dancing at a rave")

        assert isinstance(result.prompt, str)
        assert len(result.prompt) > 0

        output_file = integration_output_dir / "image_prompt.txt"
        output_file.write_text(f"Intent: person dancing at a rave\nPrompt: {result.prompt}")

    def test_generate_video_prompt(self, small_image_path, integration_output_dir):
        """Should generate a video prompt from image."""
        import os

        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        result = generate_video_prompt(small_image_path)

        assert isinstance(result.prompt, str)
        assert len(result.prompt) > 0

        output_file = integration_output_dir / "video_prompt.txt"
        output_file.write_text(f"Image: {small_image_path}\nPrompt: {result.prompt}")
