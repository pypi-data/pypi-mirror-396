"""
Tests for semiautomatic.video module.

Tests cover:
- Easing curve functions (all curve types)
- Size and zoom parsing
- Zoom scale calculations
- FFmpeg filter building
- Path utilities
"""

import pytest
from pathlib import Path

from semiautomatic.video.easing import (
    ease_in, ease_out, ease_in_out, ease_out_in,
    ease_in_cubic, ease_in_quartic, ease_in_quintic,
    apply_easing_curve, EASING_CURVES
)
from semiautomatic.video.info import (
    parse_size, parse_zoom, get_unique_output_path, find_videos,
    ZoomSpec, VIDEO_EXTENSIONS
)
from semiautomatic.video.frames import (
    calculate_zoom_scale, _calculate_crop_position,
    _calculate_crop_position_float
)
from semiautomatic.video.ffmpeg import (
    build_ffmpeg_filter, _build_audio_speed_filter,
    _calculate_crop_offset
)


# =============================================================================
# Easing Function Tests
# =============================================================================

class TestEasingFunctions:
    """Tests for easing curve functions."""

    def test_ease_in_at_zero(self):
        assert ease_in(0) == 0

    def test_ease_in_at_one(self):
        assert ease_in(1) == 1

    def test_ease_in_at_half(self):
        assert ease_in(0.5) == 0.25  # 0.5^2

    def test_ease_out_at_zero(self):
        assert ease_out(0) == 0

    def test_ease_out_at_one(self):
        assert ease_out(1) == 1

    def test_ease_out_at_half(self):
        # 1 - (1-0.5)^2 = 1 - 0.25 = 0.75
        assert ease_out(0.5) == 0.75

    def test_ease_in_out_at_zero(self):
        assert ease_in_out(0) == 0

    def test_ease_in_out_at_one(self):
        assert ease_in_out(1) == 1

    def test_ease_in_out_at_half(self):
        assert ease_in_out(0.5) == 0.5

    def test_ease_in_out_first_quarter(self):
        # t < 0.5: 2 * t^2 = 2 * 0.25^2 = 0.125
        assert ease_in_out(0.25) == 0.125

    def test_ease_in_out_third_quarter(self):
        # t >= 0.5: 1 - 2*(1-t)^2 = 1 - 2*0.25^2 = 0.875
        assert ease_in_out(0.75) == 0.875

    def test_ease_out_in_at_zero(self):
        assert ease_out_in(0) == 0

    def test_ease_out_in_at_one(self):
        assert ease_out_in(1) == 1

    def test_ease_out_in_at_half(self):
        assert ease_out_in(0.5) == 0.5

    def test_ease_in_cubic_at_half(self):
        assert ease_in_cubic(0.5) == 0.125  # 0.5^3

    def test_ease_in_quartic_at_half(self):
        assert ease_in_quartic(0.5) == 0.0625  # 0.5^4

    def test_ease_in_quintic_at_half(self):
        assert ease_in_quintic(0.5) == 0.03125  # 0.5^5


class TestApplyEasingCurve:
    """Tests for apply_easing_curve() dispatcher."""

    def test_linear_returns_unchanged(self):
        assert apply_easing_curve(0.5, "linear") == 0.5

    def test_unknown_curve_returns_linear(self):
        assert apply_easing_curve(0.5, "unknown") == 0.5

    def test_ease_in_dispatched(self):
        assert apply_easing_curve(0.5, "ease-in") == ease_in(0.5)

    def test_ease_out_dispatched(self):
        assert apply_easing_curve(0.5, "ease-out") == ease_out(0.5)

    def test_ease_in_out_dispatched(self):
        assert apply_easing_curve(0.5, "ease-in-out") == ease_in_out(0.5)

    def test_ease_out_in_dispatched(self):
        assert apply_easing_curve(0.5, "ease-out-in") == ease_out_in(0.5)

    def test_ease_in_cubic_dispatched(self):
        assert apply_easing_curve(0.5, "ease-in-cubic") == ease_in_cubic(0.5)

    def test_ease_in_quartic_dispatched(self):
        assert apply_easing_curve(0.5, "ease-in-quartic") == ease_in_quartic(0.5)

    def test_ease_in_quintic_dispatched(self):
        assert apply_easing_curve(0.5, "ease-in-quintic") == ease_in_quintic(0.5)


class TestEasingCurvesConstant:
    """Tests for EASING_CURVES constant."""

    def test_contains_expected_curves(self):
        expected = [
            "ease-in", "ease-in-cubic", "ease-in-quartic",
            "ease-in-quintic", "ease-out", "ease-in-out", "ease-out-in"
        ]
        for curve in expected:
            assert curve in EASING_CURVES

    def test_all_curves_are_dispatchable(self):
        for curve in EASING_CURVES:
            result = apply_easing_curve(0.5, curve)
            assert 0 <= result <= 1


# =============================================================================
# Parse Functions Tests
# =============================================================================

class TestParseSize:
    """Tests for parse_size() function."""

    def test_none_returns_none(self):
        assert parse_size(None) is None

    def test_empty_string_returns_none(self):
        assert parse_size("") is None

    def test_valid_size(self):
        result = parse_size("1920x1080")
        assert result == (1920, 1080)

    def test_square_size(self):
        result = parse_size("1080x1080")
        assert result == (1080, 1080)

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="must be in format"):
            parse_size("1920")

    def test_invalid_width_raises(self):
        with pytest.raises(ValueError, match="must be in format"):
            parse_size("abcx1080")

    def test_invalid_height_raises(self):
        with pytest.raises(ValueError, match="must be in format"):
            parse_size("1920xabc")


class TestParseZoom:
    """Tests for parse_zoom() function."""

    def test_none_returns_none(self):
        assert parse_zoom(None) is None

    def test_empty_string_returns_none(self):
        assert parse_zoom("") is None

    def test_valid_zoom(self):
        result = parse_zoom("100:150")
        assert isinstance(result, ZoomSpec)
        assert result.start == 100
        assert result.end == 150

    def test_zoom_in(self):
        result = parse_zoom("100:200")
        assert result.start == 100
        assert result.end == 200

    def test_zoom_out(self):
        result = parse_zoom("150:100")
        assert result.start == 150
        assert result.end == 100

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="must be in format"):
            parse_zoom("100-150")

    def test_invalid_start_raises(self):
        with pytest.raises(ValueError, match="must be in format"):
            parse_zoom("abc:150")


# =============================================================================
# Zoom Scale Calculation Tests
# =============================================================================

class TestCalculateZoomScale:
    """Tests for calculate_zoom_scale() function."""

    def test_single_frame_returns_start(self):
        scale_h, scale_v = calculate_zoom_scale(0, 1, (100, 200), (100, 200))
        assert scale_h == 1.0  # 100 / 100
        assert scale_v == 1.0  # 100 / 100

    def test_first_frame_of_many(self):
        scale_h, scale_v = calculate_zoom_scale(0, 10, (100, 150), (100, 150))
        assert scale_h == 1.0  # 100%
        assert scale_v == 1.0  # 100%

    def test_last_frame_of_many(self):
        scale_h, scale_v = calculate_zoom_scale(9, 10, (100, 150), (100, 150))
        assert scale_h == 1.5  # 150%
        assert scale_v == 1.5  # 150%

    def test_middle_frame(self):
        # Frame 5 of 10 (index 4 with 0-indexing gives progress = 4/9)
        # Actually frame 4 of 10 gives progress = 4/9 ≈ 0.444
        # For 100:200 zoom: 100 + (200-100)*0.5 = 150% at middle
        scale_h, scale_v = calculate_zoom_scale(4, 9, (100, 200), (100, 200))
        assert scale_h == 1.5  # 150%
        assert scale_v == 1.5  # 150%

    def test_independent_h_v_zoom(self):
        scale_h, scale_v = calculate_zoom_scale(4, 9, (100, 200), (100, 100))
        assert scale_h == 1.5  # 150% horizontal
        assert scale_v == 1.0  # 100% vertical (no change)


# =============================================================================
# Crop Position Tests
# =============================================================================

class TestCalculateCropPosition:
    """Tests for crop position calculation functions."""

    def test_center_crop(self):
        x, y = _calculate_crop_position(200, 200, 100, 100, "center")
        assert x == 50  # (200-100) / 2
        assert y == 50

    def test_left_crop(self):
        x, y = _calculate_crop_position(200, 200, 100, 100, "left")
        assert x == 0
        assert y == 50

    def test_right_crop(self):
        x, y = _calculate_crop_position(200, 200, 100, 100, "right")
        assert x == 100  # 200 - 100
        assert y == 50

    def test_top_crop(self):
        x, y = _calculate_crop_position(200, 200, 100, 100, "top")
        assert x == 50
        assert y == 0

    def test_bottom_crop(self):
        x, y = _calculate_crop_position(200, 200, 100, 100, "bottom")
        assert x == 50
        assert y == 100

    def test_topleft_crop(self):
        x, y = _calculate_crop_position(200, 200, 100, 100, "topleft")
        assert x == 0
        assert y == 0

    def test_bottomright_crop(self):
        x, y = _calculate_crop_position(200, 200, 100, 100, "bottomright")
        assert x == 100
        assert y == 100


class TestCalculateCropPositionFloat:
    """Tests for floating-point crop position calculation."""

    def test_center_float(self):
        x, y = _calculate_crop_position_float(100.0, 100.0, "center")
        assert x == 50.0
        assert y == 50.0

    def test_negative_excess_clamps_to_zero(self):
        x, y = _calculate_crop_position_float(-50.0, -50.0, "center")
        assert x == 0.0
        assert y == 0.0


# =============================================================================
# FFmpeg Filter Building Tests
# =============================================================================

class TestBuildFfmpegFilter:
    """Tests for build_ffmpeg_filter() function."""

    def test_stretch_filter(self):
        result = build_ffmpeg_filter((1920, 1080), (1080, 1080), "stretch", "center")
        assert result == "scale=1080:1080:flags=lanczos"

    def test_crop_filter_wider_source(self):
        result = build_ffmpeg_filter((1920, 1080), (1080, 1080), "crop", "center")
        # Should scale to fill height, then crop width
        assert "scale=" in result
        assert "crop=" in result
        assert "lanczos" in result

    def test_pad_filter(self):
        result = build_ffmpeg_filter((1920, 1080), (1080, 1080), "pad", "center")
        assert "scale=" in result
        assert "pad=" in result
        assert "lanczos" in result

    def test_crop_max_filter(self):
        result = build_ffmpeg_filter((1920, 1080), (1080, 1080), "crop-max", "center")
        # Should crop first, then scale
        assert "crop=" in result
        assert "scale=" in result


class TestBuildAudioSpeedFilter:
    """Tests for _build_audio_speed_filter() function."""

    def test_normal_speed(self):
        result = _build_audio_speed_filter(1.5)
        assert result == "atempo=1.5"

    def test_max_single_atempo(self):
        result = _build_audio_speed_filter(2.0)
        assert result == "atempo=2.0"

    def test_high_speed_chains_filters(self):
        result = _build_audio_speed_filter(4.0)
        # 4x = 2x * 2x
        assert "atempo=2.0" in result
        assert result.count("atempo") == 2

    def test_very_high_speed(self):
        result = _build_audio_speed_filter(8.0)
        # 8x = 2x * 2x * 2x
        assert result.count("atempo") == 3


class TestCalculateCropOffset:
    """Tests for _calculate_crop_offset() function."""

    def test_center_offset(self):
        x, y = _calculate_crop_offset(200, 200, 100, 100, "center")
        assert x == 50
        assert y == 50

    def test_left_offset(self):
        x, y = _calculate_crop_offset(200, 200, 100, 100, "left")
        assert x == 0

    def test_right_offset(self):
        x, y = _calculate_crop_offset(200, 200, 100, 100, "right")
        assert x == 100


# =============================================================================
# Path Utilities Tests
# =============================================================================

class TestGetUniqueOutputPath:
    """Tests for get_unique_output_path() function."""

    def test_nonexistent_path_unchanged(self, tmp_path):
        path = tmp_path / "newfile.mp4"
        result = get_unique_output_path(path)
        assert result == path

    def test_existing_file_gets_suffix(self, tmp_path):
        path = tmp_path / "existing.mp4"
        path.write_text("content")

        result = get_unique_output_path(path)
        assert result == tmp_path / "existing_01.mp4"

    def test_multiple_collisions(self, tmp_path):
        path = tmp_path / "file.mp4"
        path.write_text("content")
        (tmp_path / "file_01.mp4").write_text("content")
        (tmp_path / "file_02.mp4").write_text("content")

        result = get_unique_output_path(path)
        assert result == tmp_path / "file_03.mp4"


class TestFindVideos:
    """Tests for find_videos() function."""

    def test_finds_video_files(self, tmp_path):
        (tmp_path / "video1.mp4").write_text("content")
        (tmp_path / "video2.mov").write_text("content")
        (tmp_path / "readme.txt").write_text("content")

        result = find_videos(tmp_path)
        assert len(result) == 2
        assert all(p.suffix in VIDEO_EXTENSIONS for p in result)

    def test_empty_directory(self, tmp_path):
        result = find_videos(tmp_path)
        assert result == []

    def test_returns_sorted_list(self, tmp_path):
        (tmp_path / "c_video.mp4").write_text("content")
        (tmp_path / "a_video.mp4").write_text("content")
        (tmp_path / "b_video.mp4").write_text("content")

        result = find_videos(tmp_path)
        names = [p.name for p in result]
        assert names == sorted(names, key=str.lower)

    def test_supported_extensions(self):
        """Verify VIDEO_EXTENSIONS constant covers common formats."""
        expected = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', '.webm'}
        assert VIDEO_EXTENSIONS == expected


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_frame_zoom_returns_start(self):
        """When total_frames is 0 or 1, progress should be 0."""
        scale_h, scale_v = calculate_zoom_scale(0, 0, (100, 200), (100, 200))
        assert scale_h == 1.0
        assert scale_v == 1.0

    def test_easing_at_boundaries(self):
        """All easing functions should return 0 at t=0 and 1 at t=1."""
        for curve in EASING_CURVES:
            assert apply_easing_curve(0, curve) == 0
            assert apply_easing_curve(1, curve) == 1

    def test_easing_monotonic_for_ease_in(self):
        """Ease-in curves should be monotonically increasing."""
        prev = 0
        for i in range(11):
            t = i / 10
            val = apply_easing_curve(t, "ease-in")
            assert val >= prev
            prev = val

    def test_zoom_no_change(self):
        """100:100 zoom should produce scale of 1.0."""
        scale_h, scale_v = calculate_zoom_scale(5, 10, (100, 100), (100, 100))
        assert scale_h == 1.0
        assert scale_v == 1.0
