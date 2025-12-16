"""
Image processing library for semiautomatic.

Provides functions for resizing, converting, and compressing images.
Includes intelligent compression to meet size constraints (e.g., 5MB for Claude Vision API).

Library usage:
    from semiautomatic.image import compress_for_api
    img_bytes = compress_for_api(Path('photo.jpg'))

CLI usage:
    semiautomatic process-image --size 1920x1080
    semiautomatic process-image --max-size 5
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional, List

from PIL import Image

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Compression defaults for API limits (e.g., Claude Vision API = 5MB)
DEFAULT_MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

# Quality floor - below this, artifacts become unacceptable
MIN_JPEG_QUALITY = 60

# Initial resize target when image exceeds size limit
DEFAULT_MAX_DIMENSION = 1920

# Minimum dimension before giving up on compression
# Below this, images become too small to be useful
MIN_DIMENSION = 512

# Scale factor when iteratively shrinking to meet size limit
SHRINK_FACTOR = 0.9

# Quality reset after resize (slightly lower than initial to converge faster)
QUALITY_AFTER_RESIZE = 85

# Quality decrement per iteration
QUALITY_STEP = 5

# Unique filename counter limit (prevents infinite loop on pathological cases)
MAX_UNIQUE_FILENAME_ATTEMPTS = 1000

# Supported image extensions (lowercase, will match case-insensitively)
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif', '.ico'}


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class CompressionResult:
    """Result of image compression operation."""
    data: bytes
    final_size: int
    final_dims: Tuple[int, int]
    quality: int
    warning: Optional[str] = None


@dataclass
class SizeSpec:
    """Parsed size specification."""
    width: Optional[int] = None
    height: Optional[int] = None
    scale: Optional[float] = None
    mode: Optional[str] = None  # 'exact', 'scale', 'width', 'height', or None


# ---------------------------------------------------------------------------
# Size Parsing
# ---------------------------------------------------------------------------

def parse_size(size_str: str) -> SizeSpec:
    """
    Parse size string into a SizeSpec.

    Formats:
        "1920x1080" -> exact dimensions
        "0.5"       -> scale factor
        "1920x"     -> width-constrained (preserve aspect)
        "x1080"     -> height-constrained (preserve aspect)

    Raises:
        ValueError: If size_str is not a valid format.
    """
    if not size_str:
        return SizeSpec()

    # Try scale factor first (0.5, 2.0, etc.)
    try:
        scale = float(size_str)
        if scale <= 0:
            raise ValueError(f"Scale factor must be positive: {size_str}")
        return SizeSpec(scale=scale, mode='scale')
    except ValueError as e:
        if "positive" in str(e):
            raise
        # Not a valid float, continue to dimension formats

    # Dimension formats with 'x'
    if 'x' not in size_str.lower():
        raise ValueError(f"Invalid size format: {size_str}")

    parts = size_str.lower().split('x')

    if len(parts) != 2:
        raise ValueError(f"Invalid size format: {size_str}")

    left, right = parts

    # Width-constrained: "1920x"
    if right == '':
        try:
            width = int(left)
            if width <= 0:
                raise ValueError(f"Width must be positive: {size_str}")
            return SizeSpec(width=width, mode='width')
        except ValueError as e:
            if "positive" in str(e):
                raise
            raise ValueError(f"Invalid width in size: {size_str}")

    # Height-constrained: "x1080"
    if left == '':
        try:
            height = int(right)
            if height <= 0:
                raise ValueError(f"Height must be positive: {size_str}")
            return SizeSpec(height=height, mode='height')
        except ValueError as e:
            if "positive" in str(e):
                raise
            raise ValueError(f"Invalid height in size: {size_str}")

    # Exact dimensions: "1920x1080"
    try:
        width = int(left)
        height = int(right)
        if width <= 0 or height <= 0:
            raise ValueError(f"Dimensions must be positive: {size_str}")
        return SizeSpec(width=width, height=height, mode='exact')
    except ValueError as e:
        if "positive" in str(e):
            raise
        raise ValueError(f"Invalid dimensions in size: {size_str}")


def calculate_dimensions(
    original_size: Tuple[int, int],
    spec: SizeSpec
) -> Tuple[int, int]:
    """
    Calculate final dimensions based on size specification.

    Args:
        original_size: (width, height) of original image
        spec: Parsed SizeSpec

    Returns:
        (new_width, new_height)

    Raises:
        ValueError: If original dimensions are zero (invalid image)
    """
    orig_width, orig_height = original_size

    if spec.mode is None:
        return orig_width, orig_height

    if spec.mode == 'scale':
        return int(orig_width * spec.scale), int(orig_height * spec.scale)

    if spec.mode == 'exact':
        return spec.width, spec.height

    if spec.mode == 'width':
        if orig_width == 0:
            raise ValueError("Cannot calculate aspect ratio: original width is zero")
        aspect = orig_height / orig_width
        return spec.width, int(spec.width * aspect)

    if spec.mode == 'height':
        if orig_height == 0:
            raise ValueError("Cannot calculate aspect ratio: original height is zero")
        aspect = orig_width / orig_height
        return int(spec.height * aspect), spec.height

    return orig_width, orig_height


# ---------------------------------------------------------------------------
# Path Utilities
# ---------------------------------------------------------------------------

def get_unique_path(base_path: Path) -> Path:
    """
    Generate unique output path by appending _01, _02, etc. if file exists.

    Args:
        base_path: Desired output path

    Returns:
        Path that doesn't exist (either base_path or base_path with suffix)

    Raises:
        RuntimeError: If unable to find unique name after MAX_UNIQUE_FILENAME_ATTEMPTS
    """
    if not base_path.exists():
        return base_path

    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent

    for counter in range(1, MAX_UNIQUE_FILENAME_ATTEMPTS + 1):
        new_path = parent / f"{stem}_{counter:02d}{suffix}"
        if not new_path.exists():
            return new_path

    raise RuntimeError(f"Could not generate unique filename for {base_path}")


def find_images(directory: Path) -> List[Path]:
    """
    Recursively find all image files in directory.

    Args:
        directory: Root directory to search

    Returns:
        Sorted list of image file paths
    """
    files = []
    for path in directory.rglob('*'):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            files.append(path)

    return sorted(files, key=lambda p: str(p).lower())


# ---------------------------------------------------------------------------
# Image Conversion
# ---------------------------------------------------------------------------

def ensure_rgb(img: Image.Image) -> Image.Image:
    """Convert image to RGB mode if needed (for JPEG output)."""
    if img.mode == 'RGB':
        return img
    return img.convert('RGB')


def has_transparency(img: Image.Image) -> bool:
    """Check if image has transparency that should be preserved."""
    if img.mode in ('RGBA', 'LA'):
        return True
    if hasattr(img, 'info') and 'transparency' in img.info:
        return True
    return False


def determine_output_format(
    img: Image.Image,
    format_choice: str,
    source_path: Path
) -> Tuple[str, str, Image.Image]:
    """
    Determine output format based on user choice and source.

    Args:
        img: PIL Image
        format_choice: 'auto', 'png', or 'jpeg'
        source_path: Original file path

    Returns:
        (format_name, file_extension, possibly_converted_image)
    """
    if format_choice == 'png':
        return 'PNG', '.png', img

    if format_choice == 'jpeg':
        return 'JPEG', '.jpg', ensure_rgb(img)

    # Auto: preserve source format where possible
    source_ext = source_path.suffix.lower()

    if source_ext == '.png':
        return 'PNG', '.png', img

    if source_ext in ('.jpg', '.jpeg'):
        return 'JPEG', '.jpg', ensure_rgb(img)

    # Other formats: choose based on transparency
    if has_transparency(img):
        return 'PNG', '.png', img

    return 'JPEG', '.jpg', ensure_rgb(img)


# ---------------------------------------------------------------------------
# Compression
# ---------------------------------------------------------------------------

def compress_to_size(
    img: Image.Image,
    max_bytes: int,
    max_dimension: int = DEFAULT_MAX_DIMENSION,
    min_quality: int = MIN_JPEG_QUALITY
) -> CompressionResult:
    """
    Progressively compress image to fit within size limit.

    Strategy:
      1. Start with original dimensions at high quality (95)
      2. If oversized and large, resize to max_dimension
      3. Progressively reduce JPEG quality
      4. If still oversized at min_quality, shrink dimensions by 10%
      5. Repeat until under limit or dimensions too small

    Args:
        img: PIL Image to compress
        max_bytes: Target maximum file size in bytes
        max_dimension: Maximum dimension for initial resize
        min_quality: Lowest acceptable JPEG quality

    Returns:
        CompressionResult with compressed bytes and metadata
    """
    original_dims = img.size
    working_img = ensure_rgb(img.copy())
    quality = 95

    while True:
        # Encode to JPEG
        buffer = io.BytesIO()
        working_img.save(buffer, format='JPEG', quality=quality, optimize=True)
        img_bytes = buffer.getvalue()
        current_size = len(img_bytes)

        # Success: under the limit
        if current_size <= max_bytes:
            return CompressionResult(
                data=img_bytes,
                final_size=current_size,
                final_dims=working_img.size,
                quality=quality
            )

        width, height = working_img.size

        # Strategy: Resize if still at original size and larger than max_dimension
        if working_img.size == original_dims:
            max_dim = max(width, height)
            if max_dim > max_dimension:
                if width > height:
                    new_width = max_dimension
                    new_height = int(height * (max_dimension / width))
                else:
                    new_height = max_dimension
                    new_width = int(width * (max_dimension / height))

                working_img = working_img.resize((new_width, new_height), Image.LANCZOS)
                quality = QUALITY_AFTER_RESIZE
                continue

        # Strategy: Reduce quality
        if quality > min_quality:
            quality -= QUALITY_STEP
            continue

        # Strategy: Shrink dimensions (at min quality)
        new_width = int(width * SHRINK_FACTOR)
        new_height = int(height * SHRINK_FACTOR)

        if new_width < MIN_DIMENSION or new_height < MIN_DIMENSION:
            # Can't compress further - return what we have with warning
            return CompressionResult(
                data=img_bytes,
                final_size=current_size,
                final_dims=working_img.size,
                quality=quality,
                warning=f"Could not compress below {current_size} bytes (limit: {max_bytes})"
            )

        working_img = working_img.resize((new_width, new_height), Image.LANCZOS)
        quality = QUALITY_AFTER_RESIZE
        continue


def compress_for_api(
    image_path: Path,
    max_bytes: int = DEFAULT_MAX_SIZE_BYTES
) -> bytes:
    """
    Compress image to fit within API size limit.

    Convenience function for other tools that need to send images to
    size-limited APIs (e.g., Claude Vision API's 5MB limit).

    Args:
        image_path: Path to image file
        max_bytes: Maximum size in bytes (default: 5MB)

    Returns:
        JPEG-compressed image bytes, typically under max_bytes.
        Note: In rare cases with highly complex images, the result may
        exceed max_bytes if compression cannot meet the target without
        reducing dimensions below the minimum threshold (512px).

    Example:
        from semiautomatic.image import compress_for_api
        img_bytes = compress_for_api(Path('photo.jpg'))
    """
    with Image.open(image_path) as img:
        result = compress_to_size(img, max_bytes)
        return result.data


# ---------------------------------------------------------------------------
# Main Processing
# ---------------------------------------------------------------------------

def process_single_image(
    image_path: Path,
    output_dir: Path,
    size_spec: Optional[SizeSpec] = None,
    format_choice: str = 'auto',
    jpeg_quality: int = 85,
    max_size_bytes: Optional[int] = None,
    preserve_structure: bool = False,
    input_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Process a single image: resize, convert, and/or compress.

    Args:
        image_path: Path to input image
        output_dir: Directory for output
        size_spec: Parsed size specification (optional)
        format_choice: 'auto', 'png', or 'jpeg'
        jpeg_quality: Quality for JPEG output (1-100)
        max_size_bytes: If set, compress to fit this limit
        preserve_structure: Maintain input directory structure in output
        input_dir: Base input directory (required if preserve_structure=True)
        output_path: Explicit output path (overrides output_dir/auto naming)

    Returns:
        Path to the output file

    Raises:
        Exception: If processing fails
    """
    from semiautomatic.lib.logging import log_info

    with Image.open(image_path) as img:
        original_size_bytes = image_path.stat().st_size
        original_dims = img.size

        # Determine output path
        if output_path:
            dest_path = output_path.with_suffix('')  # Extension set based on format
        elif preserve_structure and input_dir:
            rel_path = image_path.relative_to(input_dir)
            dest_path = output_dir / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path = dest_path.with_suffix('')
        else:
            dest_path = output_dir / image_path.stem  # Already without suffix

        # Compression mode
        if max_size_bytes:
            # Already under limit? Just copy.
            if original_size_bytes <= max_size_bytes:
                dest_path = dest_path.with_suffix(image_path.suffix)
                dest_path = get_unique_path(dest_path)
                dest_path.write_bytes(image_path.read_bytes())

                log_info(
                    f"[OK] {image_path.name} "
                    f"(already under {max_size_bytes / 1024 / 1024:.1f}MB)"
                )
                return dest_path

            # Warn if user requested non-JPEG output
            if output_path and output_path.suffix.lower() not in ('.jpg', '.jpeg'):
                log_info(
                    f"[WARN] --max-size requires JPEG output; "
                    f"ignoring {output_path.suffix} extension"
                )

            # Compress
            result = compress_to_size(img, max_size_bytes)

            dest_path = dest_path.with_suffix('.jpg')
            dest_path = get_unique_path(dest_path)
            dest_path.write_bytes(result.data)

            # Log result
            orig_mb = original_size_bytes / 1024 / 1024
            final_mb = result.final_size / 1024 / 1024
            savings = (1 - result.final_size / original_size_bytes) * 100

            dims_str = ""
            if result.final_dims != original_dims:
                dims_str = (
                    f" [{original_dims[0]}x{original_dims[1]} -> "
                    f"{result.final_dims[0]}x{result.final_dims[1]}]"
                )

            log_info(
                f"[OK] {image_path.name} -> {dest_path.name}{dims_str} "
                f"({orig_mb:.2f}MB -> {final_mb:.2f}MB, -{savings:.0f}%, Q{result.quality})"
            )

            if result.warning:
                log_info(f"  [WARN] {result.warning}")

            return dest_path

        # Normal resize/convert mode
        if size_spec and size_spec.mode:
            new_width, new_height = calculate_dimensions(img.size, size_spec)
            working_img = img.resize((new_width, new_height), Image.LANCZOS)
        else:
            working_img = img
            new_width, new_height = img.size

        # Determine format
        fmt, ext, output_img = determine_output_format(working_img, format_choice, image_path)

        dest_path = dest_path.with_suffix(ext)
        dest_path = get_unique_path(dest_path)

        # Save
        if fmt == 'PNG':
            output_img.save(dest_path, 'PNG', optimize=True, compress_level=9)
        else:
            output_img.save(dest_path, 'JPEG', quality=jpeg_quality, optimize=True)

        # Log result
        output_size_bytes = dest_path.stat().st_size
        orig_kb = original_size_bytes / 1024
        final_kb = output_size_bytes / 1024

        size_change = ""
        if size_spec and size_spec.mode:
            size_change = f" [{original_dims[0]}x{original_dims[1]} -> {new_width}x{new_height}]"

        log_info(
            f"[OK] {image_path.name} -> {dest_path.name}{size_change} "
            f"({orig_kb:.1f}KB -> {final_kb:.1f}KB)"
        )

        return dest_path


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def run_process_image(args) -> bool:
    """
    CLI handler for process-image command.

    Args:
        args: Parsed argparse namespace

    Returns:
        True on success, False on failure
    """
    from semiautomatic.lib.logging import log_info, log_error

    # Validate: need at least one operation
    if not args.size and args.format == 'auto' and not args.max_size:
        log_error("Must specify --size, --format (png/jpeg), or --max-size")
        return False

    # Validate quality
    if not (1 <= args.quality <= 100):
        log_error("Quality must be between 1 and 100")
        return False

    # Parse size spec
    size_spec = None
    if args.size:
        try:
            size_spec = parse_size(args.size)
        except ValueError as e:
            log_error(str(e))
            return False

    # Convert max_size MB to bytes
    max_size_bytes = int(args.max_size * 1024 * 1024) if args.max_size else None

    # Parse output path
    output_arg = getattr(args, "output", None)
    if output_arg:
        output_path = Path(output_arg)
        output_dir = output_path.parent or Path(".")
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_path = None
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Header
    log_info("Image Processor")
    log_info("=" * 60)
    log_info("Settings:")
    if args.size:
        log_info(f"  Size: {args.size}")
    if args.max_size:
        log_info(f"  Max size: {args.max_size}MB")
    log_info(f"  Format: {args.format}")
    if args.format in ('jpeg', 'auto'):
        log_info(f"  JPEG Quality: {args.quality}")
    log_info(f"  Output: {output_dir}")
    log_info("")

    processed = 0
    failed = 0

    if args.input:
        # Single file mode
        input_path = Path(args.input)
        if not input_path.exists():
            log_error(f"Input file not found: {input_path}")
            return False

        try:
            process_single_image(
                input_path, output_dir, size_spec,
                args.format, args.quality, max_size_bytes,
                output_path=output_path,
            )
            processed = 1
        except Exception as e:
            log_error(f"Failed to process {input_path.name}: {e}")
            failed = 1
    else:
        # Batch mode
        if output_path:
            log_error("--output cannot be used with batch processing. Use --output-dir instead.")
            return False
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            log_error(f"Input directory not found: {input_dir}")
            return False

        image_files = find_images(input_dir)

        if not image_files:
            log_error("No image files found in input directory")
            return False

        log_info(f"Found {len(image_files)} image(s)")
        log_info("")

        for i, img_path in enumerate(image_files, 1):
            log_info(f"[{i}/{len(image_files)}] {img_path.name}")
            try:
                process_single_image(
                    img_path, output_dir, size_spec,
                    args.format, args.quality, max_size_bytes,
                    preserve_structure=True, input_dir=input_dir
                )
                processed += 1
            except Exception as e:
                log_error(f"  Failed: {e}")
                failed += 1

    # Summary
    log_info("")
    log_info("=" * 60)
    if processed > 0:
        log_info(f"[OK] Processed {processed} image(s)")
    if failed > 0:
        log_error(f"[FAIL] Failed {failed} image(s)")

    return processed > 0
