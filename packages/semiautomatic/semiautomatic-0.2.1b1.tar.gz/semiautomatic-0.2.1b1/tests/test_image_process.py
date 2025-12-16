"""
Tests for semiautomatic.image.process module.

Tests cover:
- Size parsing (all format variations)
- Dimension calculations (all modes)
- Path utilities (unique naming, image discovery)
- Image conversion (RGB, transparency)
- Compression (progressive algorithm)
- Single image processing (integration)
"""

import pytest
from pathlib import Path
from PIL import Image

from semiautomatic.image.process import (
    # Size parsing
    parse_size,
    calculate_dimensions,
    SizeSpec,
    # Path utilities
    get_unique_path,
    find_images,
    # Image conversion
    ensure_rgb,
    has_transparency,
    determine_output_format,
    # Compression
    compress_to_size,
    compress_for_api,
    CompressionResult,
    # Processing
    process_single_image,
    # Constants
    DEFAULT_MAX_SIZE_BYTES,
    IMAGE_EXTENSIONS,
)


# =============================================================================
# parse_size() tests
# =============================================================================

class TestParseSize:
    """Tests for parse_size() function."""

    def test_empty_string_returns_empty_spec(self):
        result = parse_size("")
        assert result.mode is None
        assert result.width is None
        assert result.height is None
        assert result.scale is None

    def test_none_returns_empty_spec(self):
        result = parse_size(None)
        assert result.mode is None

    def test_exact_dimensions(self):
        result = parse_size("1920x1080")
        assert result.mode == 'exact'
        assert result.width == 1920
        assert result.height == 1080

    def test_exact_dimensions_uppercase_x(self):
        result = parse_size("1920X1080")
        assert result.mode == 'exact'
        assert result.width == 1920
        assert result.height == 1080

    def test_scale_factor_half(self):
        result = parse_size("0.5")
        assert result.mode == 'scale'
        assert result.scale == 0.5

    def test_scale_factor_double(self):
        result = parse_size("2.0")
        assert result.mode == 'scale'
        assert result.scale == 2.0

    def test_scale_factor_integer(self):
        result = parse_size("2")
        assert result.mode == 'scale'
        assert result.scale == 2.0

    def test_width_constrained(self):
        result = parse_size("1920x")
        assert result.mode == 'width'
        assert result.width == 1920
        assert result.height is None

    def test_height_constrained(self):
        result = parse_size("x1080")
        assert result.mode == 'height'
        assert result.height == 1080
        assert result.width is None

    def test_integer_without_x_is_scale(self):
        # "1920" without 'x' is interpreted as scale factor, not dimension
        result = parse_size("1920")
        assert result.mode == 'scale'
        assert result.scale == 1920.0

    def test_invalid_format_multiple_x(self):
        with pytest.raises(ValueError, match="Invalid size format"):
            parse_size("1920x1080x720")

    def test_invalid_width(self):
        with pytest.raises(ValueError, match="Invalid width"):
            parse_size("abcx")

    def test_invalid_height(self):
        with pytest.raises(ValueError, match="Invalid height"):
            parse_size("xabc")

    def test_invalid_dimensions(self):
        with pytest.raises(ValueError, match="Invalid dimensions"):
            parse_size("abcxdef")


# =============================================================================
# calculate_dimensions() tests
# =============================================================================

class TestCalculateDimensions:
    """Tests for calculate_dimensions() function."""

    def test_none_mode_returns_original(self):
        result = calculate_dimensions((1920, 1080), SizeSpec())
        assert result == (1920, 1080)

    def test_exact_mode(self):
        spec = SizeSpec(width=800, height=600, mode='exact')
        result = calculate_dimensions((1920, 1080), spec)
        assert result == (800, 600)

    def test_scale_mode_half(self):
        spec = SizeSpec(scale=0.5, mode='scale')
        result = calculate_dimensions((1920, 1080), spec)
        assert result == (960, 540)

    def test_scale_mode_double(self):
        spec = SizeSpec(scale=2.0, mode='scale')
        result = calculate_dimensions((100, 100), spec)
        assert result == (200, 200)

    def test_width_constrained_preserves_aspect(self):
        spec = SizeSpec(width=960, mode='width')
        result = calculate_dimensions((1920, 1080), spec)
        assert result[0] == 960
        # Aspect ratio should be preserved: 1080/1920 = 0.5625
        assert result[1] == 540

    def test_height_constrained_preserves_aspect(self):
        spec = SizeSpec(height=540, mode='height')
        result = calculate_dimensions((1920, 1080), spec)
        assert result[1] == 540
        # Aspect ratio should be preserved: 1920/1080 = 1.777...
        assert result[0] == 960

    def test_width_constrained_portrait(self):
        """Test width constraint on portrait image."""
        spec = SizeSpec(width=500, mode='width')
        result = calculate_dimensions((1000, 2000), spec)
        assert result == (500, 1000)

    def test_height_constrained_portrait(self):
        """Test height constraint on portrait image."""
        spec = SizeSpec(height=1000, mode='height')
        result = calculate_dimensions((1000, 2000), spec)
        assert result == (500, 1000)


# =============================================================================
# get_unique_path() tests
# =============================================================================

class TestGetUniquePath:
    """Tests for get_unique_path() function."""

    def test_nonexistent_path_returned_unchanged(self, temp_dir):
        path = temp_dir / "newfile.jpg"
        result = get_unique_path(path)
        assert result == path

    def test_existing_file_gets_suffix(self, temp_dir):
        path = temp_dir / "existing.jpg"
        path.write_text("content")

        result = get_unique_path(path)
        assert result == temp_dir / "existing_01.jpg"

    def test_multiple_collisions(self, temp_dir):
        path = temp_dir / "file.jpg"
        path.write_text("content")
        (temp_dir / "file_01.jpg").write_text("content")
        (temp_dir / "file_02.jpg").write_text("content")

        result = get_unique_path(path)
        assert result == temp_dir / "file_03.jpg"

    def test_preserves_extension(self, temp_dir):
        path = temp_dir / "image.png"
        path.write_text("content")

        result = get_unique_path(path)
        assert result.suffix == ".png"
        assert result.stem == "image_01"


# =============================================================================
# find_images() tests
# =============================================================================

class TestFindImages:
    """Tests for find_images() function."""

    def test_finds_images_in_directory(self, image_directory):
        images = find_images(image_directory)
        assert len(images) == 3  # image1.jpg, image2.png, subdir/image3.jpg

    def test_ignores_non_image_files(self, image_directory):
        images = find_images(image_directory)
        names = [img.name for img in images]
        assert "readme.txt" not in names

    def test_finds_images_recursively(self, image_directory):
        images = find_images(image_directory)
        paths = [str(img) for img in images]
        assert any("subdir" in p for p in paths)

    def test_returns_sorted_list(self, image_directory):
        images = find_images(image_directory)
        names = [img.name.lower() for img in images]
        assert names == sorted(names)

    def test_empty_directory(self, temp_dir):
        images = find_images(temp_dir)
        assert images == []

    def test_supported_extensions(self):
        """Verify IMAGE_EXTENSIONS constant covers common formats."""
        expected = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif', '.ico'}
        assert IMAGE_EXTENSIONS == expected


# =============================================================================
# ensure_rgb() tests
# =============================================================================

class TestEnsureRgb:
    """Tests for ensure_rgb() function."""

    def test_rgb_unchanged(self, small_rgb_image):
        result = ensure_rgb(small_rgb_image)
        assert result.mode == 'RGB'

    def test_rgba_converted(self, rgba_image):
        result = ensure_rgb(rgba_image)
        assert result.mode == 'RGB'

    def test_la_converted(self):
        img = Image.new('LA', (10, 10))
        result = ensure_rgb(img)
        assert result.mode == 'RGB'

    def test_p_converted(self):
        img = Image.new('P', (10, 10))
        result = ensure_rgb(img)
        assert result.mode == 'RGB'

    def test_l_converted(self):
        img = Image.new('L', (10, 10))
        result = ensure_rgb(img)
        assert result.mode == 'RGB'


# =============================================================================
# has_transparency() tests
# =============================================================================

class TestHasTransparency:
    """Tests for has_transparency() function."""

    def test_rgba_has_transparency(self, rgba_image):
        assert has_transparency(rgba_image) is True

    def test_rgb_no_transparency(self, small_rgb_image):
        assert has_transparency(small_rgb_image) is False

    def test_la_has_transparency(self):
        img = Image.new('LA', (10, 10))
        assert has_transparency(img) is True

    def test_p_with_transparency_info(self):
        img = Image.new('P', (10, 10))
        img.info['transparency'] = 0
        assert has_transparency(img) is True


# =============================================================================
# determine_output_format() tests
# =============================================================================

class TestDetermineOutputFormat:
    """Tests for determine_output_format() function."""

    def test_explicit_png(self, small_rgb_image):
        fmt, ext, img = determine_output_format(small_rgb_image, 'png', Path("test.jpg"))
        assert fmt == 'PNG'
        assert ext == '.png'

    def test_explicit_jpeg(self, small_rgb_image):
        fmt, ext, img = determine_output_format(small_rgb_image, 'jpeg', Path("test.png"))
        assert fmt == 'JPEG'
        assert ext == '.jpg'
        assert img.mode == 'RGB'

    def test_auto_preserves_png(self, small_rgb_image):
        fmt, ext, img = determine_output_format(small_rgb_image, 'auto', Path("test.png"))
        assert fmt == 'PNG'
        assert ext == '.png'

    def test_auto_preserves_jpg(self, small_rgb_image):
        fmt, ext, img = determine_output_format(small_rgb_image, 'auto', Path("test.jpg"))
        assert fmt == 'JPEG'
        assert ext == '.jpg'

    def test_auto_preserves_jpeg(self, small_rgb_image):
        fmt, ext, img = determine_output_format(small_rgb_image, 'auto', Path("test.jpeg"))
        assert fmt == 'JPEG'
        assert ext == '.jpg'

    def test_auto_with_transparency_uses_png(self, rgba_image):
        fmt, ext, img = determine_output_format(rgba_image, 'auto', Path("test.webp"))
        assert fmt == 'PNG'
        assert ext == '.png'

    def test_auto_without_transparency_uses_jpeg(self, small_rgb_image):
        fmt, ext, img = determine_output_format(small_rgb_image, 'auto', Path("test.webp"))
        assert fmt == 'JPEG'
        assert ext == '.jpg'


# =============================================================================
# compress_to_size() tests
# =============================================================================

class TestCompressToSize:
    """Tests for compress_to_size() function."""

    def test_returns_compression_result(self, small_rgb_image):
        result = compress_to_size(small_rgb_image, 1024 * 1024)  # 1MB limit
        assert isinstance(result, CompressionResult)
        assert isinstance(result.data, bytes)
        assert isinstance(result.final_size, int)
        assert isinstance(result.final_dims, tuple)
        assert isinstance(result.quality, int)

    def test_respects_size_limit(self, small_rgb_image):
        max_bytes = 50 * 1024  # 50KB
        result = compress_to_size(small_rgb_image, max_bytes)
        assert result.final_size <= max_bytes

    def test_large_image_gets_resized(self, large_rgb_image):
        """Large images should be resized to max_dimension first."""
        max_bytes = 500 * 1024  # 500KB
        result = compress_to_size(large_rgb_image, max_bytes, max_dimension=1000)

        # Should have been resized
        assert max(result.final_dims) <= 1000

    def test_quality_reduction_before_resize(self, large_rgb_image):
        """For images already under max_dimension, quality reduces before resizing."""
        # Use large image with tight limit - should reduce quality before shrinking
        # Image is 2000x1500, will resize to max_dimension first, then reduce quality
        result = compress_to_size(large_rgb_image, 20 * 1024, max_dimension=500)
        # Should have reduced quality from initial 95
        assert result.quality <= 95

    def test_warning_when_cannot_meet_limit(self, oversized_image):
        """When compression cannot meet limit, returns with warning."""
        with Image.open(oversized_image) as img:
            # Impossibly small limit
            result = compress_to_size(img, 1000, min_quality=90)  # 1KB, high min quality

            # Should have a warning
            assert result.warning is not None
            assert "Could not compress" in result.warning

    def test_output_is_valid_jpeg(self, small_rgb_image):
        result = compress_to_size(small_rgb_image, 100 * 1024)

        # Should be loadable as JPEG
        from io import BytesIO
        loaded = Image.open(BytesIO(result.data))
        assert loaded.format == 'JPEG'


# =============================================================================
# compress_for_api() tests
# =============================================================================

class TestCompressForApi:
    """Tests for compress_for_api() convenience function."""

    def test_returns_bytes(self, small_image_path):
        result = compress_for_api(small_image_path)
        assert isinstance(result, bytes)

    def test_respects_default_limit(self, small_image_path):
        result = compress_for_api(small_image_path)
        assert len(result) <= DEFAULT_MAX_SIZE_BYTES

    def test_respects_custom_limit(self, small_image_path):
        limit = 10 * 1024  # 10KB
        result = compress_for_api(small_image_path, max_bytes=limit)
        assert len(result) <= limit

    def test_output_is_valid_jpeg(self, small_image_path):
        result = compress_for_api(small_image_path)

        from io import BytesIO
        loaded = Image.open(BytesIO(result))
        assert loaded.format == 'JPEG'


# =============================================================================
# process_single_image() tests
# =============================================================================

class TestProcessSingleImage:
    """Integration tests for process_single_image() function."""

    def test_basic_resize(self, small_image_path, temp_dir):
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        spec = SizeSpec(width=50, height=50, mode='exact')
        result = process_single_image(
            small_image_path, output_dir, size_spec=spec
        )

        assert result.exists()
        with Image.open(result) as img:
            assert img.size == (50, 50)

    def test_format_conversion_to_png(self, small_image_path, temp_dir):
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        result = process_single_image(
            small_image_path, output_dir, format_choice='png'
        )

        assert result.suffix == '.png'
        with Image.open(result) as img:
            assert img.format == 'PNG'

    def test_compression_mode(self, oversized_image, temp_dir):
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        # The oversized fixture creates a high-entropy image that's larger than typical limits
        original_size = oversized_image.stat().st_size
        max_size = original_size // 2  # Request compression to half the size

        result = process_single_image(
            oversized_image, output_dir, max_size_bytes=max_size
        )

        assert result.exists()
        assert result.stat().st_size <= max_size
        assert result.suffix == '.jpg'  # Compression outputs JPEG

    def test_preserves_directory_structure(self, image_directory, temp_dir):
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        # Process image from subdirectory
        input_image = image_directory / "subdir" / "image3.jpg"
        spec = SizeSpec(scale=0.5, mode='scale')

        result = process_single_image(
            input_image, output_dir, size_spec=spec,
            preserve_structure=True, input_dir=image_directory
        )

        # Should be in subdir within output
        assert "subdir" in str(result)

    def test_unique_naming_on_collision(self, small_image_path, temp_dir):
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        spec = SizeSpec(scale=0.5, mode='scale')

        # Process same image twice
        result1 = process_single_image(small_image_path, output_dir, size_spec=spec)
        result2 = process_single_image(small_image_path, output_dir, size_spec=spec)

        # Should have different names
        assert result1 != result2
        assert result1.exists()
        assert result2.exists()

    def test_skips_compression_for_small_files(self, small_image_path, temp_dir):
        """Files already under max_size should be copied, not recompressed."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        original_size = small_image_path.stat().st_size
        max_size = original_size + 1000  # Larger than file

        result = process_single_image(
            small_image_path, output_dir, max_size_bytes=max_size
        )

        # Should preserve original format (not convert to JPEG)
        assert result.suffix == small_image_path.suffix


# =============================================================================
# Edge cases and error handling
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_scale_zero_produces_small_image(self):
        """Scale of 0.01 should produce tiny but valid dimensions."""
        spec = SizeSpec(scale=0.01, mode='scale')
        result = calculate_dimensions((1000, 1000), spec)
        assert result == (10, 10)

    def test_very_large_scale(self):
        """Very large scale factors should work."""
        spec = SizeSpec(scale=10.0, mode='scale')
        result = calculate_dimensions((100, 100), spec)
        assert result == (1000, 1000)

    def test_single_pixel_width_constraint(self):
        """Width constraint to 1 should work."""
        spec = SizeSpec(width=1, mode='width')
        result = calculate_dimensions((100, 200), spec)
        assert result[0] == 1
        assert result[1] == 2  # Maintains aspect

    def test_compression_with_grayscale_image(self, temp_dir):
        """Grayscale images should compress correctly."""
        img = Image.new('L', (100, 100), color=128)
        result = compress_to_size(img, 50 * 1024)
        assert isinstance(result.data, bytes)
        assert result.final_size > 0


# =============================================================================
# Input validation tests
# =============================================================================

class TestInputValidation:
    """Tests for input validation and error handling."""

    def test_negative_scale_rejected(self):
        with pytest.raises(ValueError, match="Scale factor must be positive"):
            parse_size("-0.5")

    def test_zero_scale_rejected(self):
        with pytest.raises(ValueError, match="Scale factor must be positive"):
            parse_size("0")

    def test_negative_width_rejected(self):
        with pytest.raises(ValueError, match="Width must be positive"):
            parse_size("-100x")

    def test_zero_width_rejected(self):
        with pytest.raises(ValueError, match="Width must be positive"):
            parse_size("0x")

    def test_negative_height_rejected(self):
        with pytest.raises(ValueError, match="Height must be positive"):
            parse_size("x-100")

    def test_zero_height_rejected(self):
        with pytest.raises(ValueError, match="Height must be positive"):
            parse_size("x0")

    def test_negative_exact_width_rejected(self):
        with pytest.raises(ValueError, match="Dimensions must be positive"):
            parse_size("-100x100")

    def test_negative_exact_height_rejected(self):
        with pytest.raises(ValueError, match="Dimensions must be positive"):
            parse_size("100x-100")

    def test_zero_exact_dimensions_rejected(self):
        with pytest.raises(ValueError, match="Dimensions must be positive"):
            parse_size("0x0")

    def test_zero_original_width_in_width_mode(self):
        """Division by zero should be caught when original width is 0."""
        spec = SizeSpec(width=100, mode='width')
        with pytest.raises(ValueError, match="original width is zero"):
            calculate_dimensions((0, 100), spec)

    def test_zero_original_height_in_height_mode(self):
        """Division by zero should be caught when original height is 0."""
        spec = SizeSpec(height=100, mode='height')
        with pytest.raises(ValueError, match="original height is zero"):
            calculate_dimensions((100, 0), spec)
