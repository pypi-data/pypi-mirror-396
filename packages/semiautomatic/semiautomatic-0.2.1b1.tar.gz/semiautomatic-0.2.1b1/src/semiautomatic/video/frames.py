"""
Frame extraction and zoom processing for video.

Library usage:
    from semiautomatic.video.frames import extract_frame_from_video
    output_path = extract_frame_from_video(video_path, output_dir, "last")
"""

from __future__ import annotations

import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional, List, Literal

from PIL import Image

from semiautomatic.lib import subprocess
from semiautomatic.lib.logging import log_info
from semiautomatic.video.info import (
    get_video_info, get_unique_output_path, ZoomSpec, VideoInfo
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FitMode = Literal["stretch", "crop", "crop-max", "pad"]
CropAlign = Literal[
    "center", "left", "right", "top", "bottom",
    "topleft", "topright", "bottomleft", "bottomright"
]

# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class FrameExtractionResult:
    """Result of frame extraction operation."""
    output_path: Path
    timestamp: float
    position_desc: str


# ---------------------------------------------------------------------------
# Single Frame Extraction
# ---------------------------------------------------------------------------


def extract_single_frame(
    video_path: Path,
    output_path: Path,
    timestamp: float,
    target_size: Optional[Tuple[int, int]] = None,
    fit_mode: FitMode = "stretch",
    crop_align: CropAlign = "center"
) -> None:
    """
    Extract a single frame at specified timestamp.

    Args:
        video_path: Source video file
        output_path: Output image path
        timestamp: Time in seconds
        target_size: Optional (width, height) for resize
        fit_mode: How to fit to target size
        crop_align: Alignment when cropping
    """
    log_info(f"    Extracting frame at {timestamp:.2f}s...")

    # Create temp file for initial extraction
    temp_frame = output_path.with_suffix('.temp.png')

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp),
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "1",
        str(temp_frame)
    ]

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg frame extraction failed: {result.stderr}")

    # Apply resize/crop if needed
    if target_size:
        _resize_frame(temp_frame, output_path, target_size, fit_mode, crop_align)
        temp_frame.unlink()
    else:
        temp_frame.rename(output_path)

    log_info(f"    Frame extracted: {output_path.name}")


def _resize_frame(
    input_path: Path,
    output_path: Path,
    target_size: Tuple[int, int],
    fit_mode: FitMode,
    crop_align: CropAlign
) -> None:
    """Resize a single frame image."""
    with Image.open(input_path) as img:
        orig_w, orig_h = img.size
        target_w, target_h = target_size

        if fit_mode == "stretch":
            resized = img.resize((target_w, target_h), Image.LANCZOS)
            resized.save(output_path)

        elif fit_mode == "crop":
            resized = _crop_to_fill(img, target_w, target_h, crop_align)
            resized.save(output_path)

        elif fit_mode == "pad":
            padded = _pad_to_fit(img, target_w, target_h)
            padded.save(output_path)


def _crop_to_fill(
    img: Image.Image,
    target_w: int,
    target_h: int,
    crop_align: CropAlign
) -> Image.Image:
    """Scale image to fill target size, then crop."""
    orig_w, orig_h = img.size

    # Calculate scale to fill
    scale_w = target_w / orig_w
    scale_h = target_h / orig_h
    scale = max(scale_w, scale_h)

    scaled_w = int(orig_w * scale)
    scaled_h = int(orig_h * scale)
    scaled_img = img.resize((scaled_w, scaled_h), Image.LANCZOS)

    # Calculate crop position
    crop_x, crop_y = _calculate_crop_position(
        scaled_w, scaled_h, target_w, target_h, crop_align
    )

    return scaled_img.crop((crop_x, crop_y, crop_x + target_w, crop_y + target_h))


def _pad_to_fit(
    img: Image.Image,
    target_w: int,
    target_h: int
) -> Image.Image:
    """Scale image to fit within target size, then pad with black."""
    orig_w, orig_h = img.size

    # Calculate scale to fit
    scale_w = target_w / orig_w
    scale_h = target_h / orig_h
    scale = min(scale_w, scale_h)

    scaled_w = int(orig_w * scale)
    scaled_h = int(orig_h * scale)
    scaled_img = img.resize((scaled_w, scaled_h), Image.LANCZOS)

    # Create canvas and paste centered
    canvas = Image.new('RGB', (target_w, target_h), (0, 0, 0))
    paste_x = (target_w - scaled_w) // 2
    paste_y = (target_h - scaled_h) // 2
    canvas.paste(scaled_img, (paste_x, paste_y))

    return canvas


def _calculate_crop_position(
    src_w: int,
    src_h: int,
    target_w: int,
    target_h: int,
    crop_align: CropAlign
) -> Tuple[int, int]:
    """Calculate crop position based on alignment."""
    excess_w = src_w - target_w
    excess_h = src_h - target_h

    # Horizontal alignment
    if 'left' in crop_align:
        crop_x = 0
    elif 'right' in crop_align:
        crop_x = excess_w
    else:
        crop_x = excess_w // 2

    # Vertical alignment
    if 'top' in crop_align:
        crop_y = 0
    elif 'bottom' in crop_align:
        crop_y = excess_h
    else:
        crop_y = excess_h // 2

    return crop_x, crop_y


# ---------------------------------------------------------------------------
# Frame Position Extraction
# ---------------------------------------------------------------------------


def extract_frame_from_video(
    video_path: Path,
    output_dir: Path,
    frame_position: Optional[str] = None,
    frame_time: Optional[float] = None,
    target_size: Optional[Tuple[int, int]] = None,
    fit_mode: FitMode = "stretch",
    crop_align: CropAlign = "center"
) -> Path:
    """
    Extract a frame from video based on position or time.

    Args:
        video_path: Source video file
        output_dir: Directory for output
        frame_position: Position specifier (first, last, middle, or frame number)
        frame_time: Specific timestamp in seconds
        target_size: Optional (width, height) for resize
        fit_mode: How to fit to target size
        crop_align: Alignment when cropping

    Returns:
        Path to extracted frame
    """
    video_name = video_path.stem
    log_info(f"[{video_name}] Extracting frame...")

    # Get video info
    info = get_video_info(video_path)
    log_info(
        f"[{video_name}] Input: {info.width}x{info.height} @ {info.fps}fps, "
        f"duration: {info.duration:.2f}s"
    )

    # Calculate total frames
    total_frames = int(info.duration * info.fps)

    # Calculate timestamp
    timestamp, position_desc = _calculate_frame_timestamp(
        frame_position, frame_time, info.duration, info.fps, total_frames, video_name
    )

    # Generate output path
    output_path = output_dir / f"{video_name}_{position_desc}_frame.png"
    output_path = get_unique_output_path(output_path)

    try:
        extract_single_frame(
            video_path, output_path, timestamp,
            target_size, fit_mode, crop_align
        )
        log_info(f"[{video_name}] Complete! Output: {output_path.name}")
        return output_path

    except Exception as e:
        raise RuntimeError(f"Frame extraction failed for {video_name}: {e}")


def _calculate_frame_timestamp(
    frame_position: Optional[str],
    frame_time: Optional[float],
    duration: float,
    fps: float,
    total_frames: int,
    video_name: str
) -> Tuple[float, str]:
    """Calculate timestamp and description for frame extraction."""
    if frame_time is not None:
        if frame_time < 0 or frame_time > duration:
            raise ValueError(
                f"Frame time {frame_time}s is outside video duration (0-{duration:.2f}s)"
            )
        return frame_time, f"{frame_time:.2f}s"

    if frame_position == "first":
        return 0.0, "first"

    if frame_position == "last":
        return max(0, duration - 0.1), "last"

    if frame_position == "middle":
        return duration / 2, "middle"

    # Try to parse as numeric frame index
    try:
        frame_index = int(frame_position)

        # Handle negative indices (count from end)
        if frame_index < 0:
            frame_index = total_frames + frame_index
            if frame_index < 0:
                raise ValueError(
                    f"Negative frame index {int(frame_position)} exceeds "
                    f"video length ({total_frames} frames)"
                )
        elif frame_index >= total_frames:
            raise ValueError(
                f"Frame index {frame_index} exceeds video length ({total_frames} frames)"
            )

        # Calculate timestamp from frame number
        timestamp = frame_index / fps
        log_info(f"[{video_name}] Frame {frame_index}/{total_frames} at {timestamp:.2f}s")
        return timestamp, f"frame{frame_index}"

    except ValueError as e:
        if "exceeds" in str(e):
            raise
        raise ValueError(f"Invalid frame position: {frame_position}")


# ---------------------------------------------------------------------------
# Batch Frame Extraction
# ---------------------------------------------------------------------------


def extract_frames(
    video_path: Path,
    output_dir: Path,
    fps: float,
    trim_start: float = 0.0,
    output_duration: Optional[float] = None
) -> List[Path]:
    """
    Extract all frames from video with optional trimming.

    Args:
        video_path: Source video file
        output_dir: Directory for extracted frames
        fps: Target frame rate
        trim_start: Seconds to skip from start
        output_duration: Duration to extract (None for full video)

    Returns:
        Sorted list of frame file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    log_info(f"    Extracting frames at {fps}fps...")

    cmd = ["ffmpeg", "-y"]

    if trim_start > 0:
        cmd.extend(["-ss", str(trim_start)])

    cmd.extend(["-i", str(video_path)])

    if output_duration is not None:
        cmd.extend(["-t", str(output_duration)])

    cmd.extend([
        "-vf", f"fps={fps}",
        "-an",
        "-threads", "4",
        "-preset", "ultrafast",
        str(output_dir / "frame_%05d.png")
    ])

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg frame extraction failed: {result.stderr}")

    frame_files = sorted(output_dir.glob("frame_*.png"))
    log_info(f"    Extracted {len(frame_files)} frames")
    return frame_files


# ---------------------------------------------------------------------------
# Zoom Processing
# ---------------------------------------------------------------------------


def calculate_zoom_scale(
    frame_index: int,
    total_frames: int,
    zoom_h: Tuple[int, int],
    zoom_v: Tuple[int, int]
) -> Tuple[float, float]:
    """
    Calculate horizontal and vertical scale factors for a specific frame.

    Args:
        frame_index: Current frame number
        total_frames: Total number of frames
        zoom_h: (start_percent, end_percent) for horizontal zoom
        zoom_v: (start_percent, end_percent) for vertical zoom

    Returns:
        (scale_h, scale_v) scale factors
    """
    if total_frames <= 1:
        progress = 0.0
    else:
        progress = frame_index / (total_frames - 1)

    start_h, end_h = zoom_h
    start_v, end_v = zoom_v

    scale_h = (start_h + (end_h - start_h) * progress) / 100.0
    scale_v = (start_v + (end_v - start_v) * progress) / 100.0

    return scale_h, scale_v


def apply_zoom_to_frame(
    frame_path: Path,
    output_path: Path,
    scale_h: float,
    scale_v: float,
    target_size: Tuple[int, int],
    crop_align: CropAlign,
    fit_mode: FitMode = "stretch"
) -> None:
    """
    Apply zoom effect to a single frame with crop alignment.

    Args:
        frame_path: Input frame path
        output_path: Output frame path
        scale_h: Horizontal scale factor
        scale_v: Vertical scale factor
        target_size: Final output dimensions
        crop_align: Alignment when cropping
        fit_mode: How to fit to target size
    """
    with Image.open(frame_path) as img:
        original_width, original_height = img.size
        target_width, target_height = target_size

        # Apply scaling with floating-point precision
        scaled_width = original_width * scale_h
        scaled_height = original_height * scale_v
        scaled_img = img.resize(
            (int(scaled_width + 0.5), int(scaled_height + 0.5)),
            Image.LANCZOS
        )

        # Calculate crop positions
        excess_w = scaled_width - original_width
        excess_h = scaled_height - original_height

        crop_x, crop_y = _calculate_crop_position_float(
            excess_w, excess_h, crop_align
        )

        # Crop the scaled image
        crop_right = crop_x + original_width
        crop_bottom = crop_y + original_height
        cropped = scaled_img.crop((crop_x, crop_y, crop_right, crop_bottom))

        # Resize to target dimensions if needed
        if (target_width, target_height) != (original_width, original_height):
            final_img = _apply_final_resize(
                cropped, target_width, target_height, crop_align, fit_mode
            )
        else:
            final_img = cropped

        final_img.save(output_path)


def _calculate_crop_position_float(
    excess_w: float,
    excess_h: float,
    crop_align: CropAlign
) -> Tuple[float, float]:
    """Calculate crop position with floating-point precision."""
    if 'left' in crop_align:
        crop_x = 0.0
    elif 'right' in crop_align:
        crop_x = max(0.0, excess_w)
    else:
        crop_x = max(0.0, excess_w / 2.0)

    if 'top' in crop_align:
        crop_y = 0.0
    elif 'bottom' in crop_align:
        crop_y = max(0.0, excess_h)
    else:
        crop_y = max(0.0, excess_h / 2.0)

    return crop_x, crop_y


def _apply_final_resize(
    img: Image.Image,
    target_w: int,
    target_h: int,
    crop_align: CropAlign,
    fit_mode: FitMode
) -> Image.Image:
    """Apply final resize to target dimensions."""
    zoomed_w, zoomed_h = img.size

    if fit_mode == 'stretch':
        return img.resize((target_w, target_h), Image.LANCZOS)

    elif fit_mode == 'crop':
        return _crop_to_fill(img, target_w, target_h, crop_align)

    elif fit_mode == 'crop-max':
        return _crop_max_then_scale(img, target_w, target_h, crop_align)

    elif fit_mode == 'pad':
        return _pad_to_fit(img, target_w, target_h)

    return img


def _crop_max_then_scale(
    img: Image.Image,
    target_w: int,
    target_h: int,
    crop_align: CropAlign
) -> Image.Image:
    """Crop to target aspect ratio at max resolution, then scale down."""
    zoomed_w, zoomed_h = img.size
    target_aspect = target_w / target_h
    zoomed_aspect = zoomed_w / zoomed_h

    if zoomed_aspect > target_aspect:
        crop_height = zoomed_h
        crop_width = int(crop_height * target_aspect)
    else:
        crop_width = zoomed_w
        crop_height = int(crop_width / target_aspect)

    crop_x, crop_y = _calculate_crop_position(
        zoomed_w, zoomed_h, crop_width, crop_height, crop_align
    )

    max_crop = img.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))
    return max_crop.resize((target_w, target_h), Image.LANCZOS)


def process_frames_with_zoom(
    frame_files: List[Path],
    output_dir: Path,
    video_name: str,
    zoom_h: Tuple[int, int],
    zoom_v: Tuple[int, int],
    target_size: Tuple[int, int],
    crop_align: CropAlign,
    fit_mode: FitMode = "stretch"
) -> None:
    """
    Process all frames with zoom effect.

    Args:
        frame_files: List of input frame paths
        output_dir: Directory for output frames
        video_name: Name for logging
        zoom_h: (start_percent, end_percent) for horizontal zoom
        zoom_v: (start_percent, end_percent) for vertical zoom
        target_size: Final output dimensions
        crop_align: Alignment when cropping
        fit_mode: How to fit to target size
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    total_frames = len(frame_files)
    start_h, end_h = zoom_h
    start_v, end_v = zoom_v

    zoom_desc = []
    if start_h != 100 or end_h != 100:
        zoom_desc.append(f"H: {start_h}%->{end_h}%")
    if start_v != 100 or end_v != 100:
        zoom_desc.append(f"V: {start_v}%->{end_v}%")

    zoom_str = ", ".join(zoom_desc) if zoom_desc else "no zoom"

    log_info(
        f"[{video_name}] Processing {total_frames} frames "
        f"({zoom_str}, fit: {fit_mode}, align: {crop_align})"
    )

    start_time = time.time()

    for i, frame_path in enumerate(frame_files):
        scale_h, scale_v = calculate_zoom_scale(i, total_frames, zoom_h, zoom_v)
        output_path = output_dir / f"frame_{i:05d}.png"
        apply_zoom_to_frame(
            frame_path, output_path, scale_h, scale_v,
            target_size, crop_align, fit_mode
        )

        # Progress indicator
        if i % 10 == 0 or i == total_frames - 1:
            _print_progress(i, total_frames, start_time, video_name)

    print()  # New line after progress

    elapsed = time.time() - start_time
    log_info(f"[{video_name}] Frame processing complete! ({elapsed:.1f}s)")


def _print_progress(
    current: int,
    total: int,
    start_time: float,
    video_name: str
) -> None:
    """Print progress bar."""
    elapsed = time.time() - start_time
    progress_pct = (current + 1) / total
    fps_processing = (current + 1) / elapsed if elapsed > 0 else 0
    eta = (total - current - 1) / fps_processing if fps_processing > 0 else 0

    bar_filled = int(progress_pct * 20)
    progress_bar = "#" * bar_filled + "." * (20 - bar_filled)

    print(
        f"[{video_name}] [{progress_bar}] {current+1}/{total} ({progress_pct:.1%}) "
        f"| {fps_processing:.1f} fps | ETA: {eta:.1f}s",
        end="\r"
    )


# ---------------------------------------------------------------------------
# Speed Ramping
# ---------------------------------------------------------------------------


def create_speed_ramped_frames(
    input_frames_dir: Path,
    output_frames_dir: Path,
    fps: float,
    speed: float,
    speed_ramp: str
) -> List[Path]:
    """
    Create speed-ramped frame sequence by selecting frames with easing curve.

    Args:
        input_frames_dir: Directory with input frames
        output_frames_dir: Directory for output frames
        fps: Frame rate
        speed: Speed multiplier
        speed_ramp: Easing curve name

    Returns:
        Sorted list of output frame paths
    """
    from semiautomatic.video.easing import apply_easing_curve

    input_frames = sorted(input_frames_dir.glob("frame_*.png"))
    total_input_frames = len(input_frames)

    # Calculate output frame count based on speed
    total_output_frames = int(total_input_frames / speed)

    log_info(
        f"    Creating speed-ramped sequence: "
        f"{total_input_frames} -> {total_output_frames} frames"
    )
    log_info(f"    Using {speed_ramp} easing curve")

    output_frames_dir.mkdir(parents=True, exist_ok=True)

    for out_idx in range(total_output_frames):
        # Normalize output time (0-1)
        t_out = out_idx / max(1, total_output_frames - 1)

        # Apply easing curve to get remapped time
        t_remapped = apply_easing_curve(t_out, speed_ramp)

        # Map remapped time directly to input frame range
        in_idx = int(t_remapped * (total_input_frames - 1))
        in_idx = min(in_idx, total_input_frames - 1)

        # Copy frame
        input_frame = input_frames[in_idx]
        output_frame = output_frames_dir / f"frame_{out_idx:05d}.png"
        shutil.copy2(input_frame, output_frame)

    log_info(f"    Speed-ramped sequence created")
    return sorted(output_frames_dir.glob("frame_*.png"))
