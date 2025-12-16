"""
FFmpeg command building and video assembly.

Library usage:
    from semiautomatic.video.ffmpeg import build_ffmpeg_filter, assemble_video
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Tuple, Optional

from semiautomatic.lib import subprocess
from semiautomatic.lib.logging import log_info
from semiautomatic.video.frames import FitMode, CropAlign

# ---------------------------------------------------------------------------
# Filter Building
# ---------------------------------------------------------------------------


def build_ffmpeg_filter(
    original_size: Tuple[int, int],
    target_size: Tuple[int, int],
    fit_mode: FitMode,
    crop_align: CropAlign
) -> Optional[str]:
    """
    Build FFmpeg filter string for resize operations without zoom.

    Args:
        original_size: (width, height) of source video
        target_size: (width, height) target dimensions
        fit_mode: How to fit video to target size
        crop_align: Alignment when cropping

    Returns:
        FFmpeg filter string or None if no filter needed
    """
    orig_w, orig_h = original_size
    target_w, target_h = target_size

    if fit_mode == "stretch":
        return f"scale={target_w}:{target_h}:flags=lanczos"

    elif fit_mode == "crop":
        return _build_crop_filter(orig_w, orig_h, target_w, target_h, crop_align)

    elif fit_mode == "crop-max":
        return _build_crop_max_filter(orig_w, orig_h, target_w, target_h, crop_align)

    elif fit_mode == "pad":
        return _build_pad_filter(orig_w, orig_h, target_w, target_h)

    return None


def _build_crop_filter(
    orig_w: int,
    orig_h: int,
    target_w: int,
    target_h: int,
    crop_align: CropAlign
) -> str:
    """Build scale-to-fill then crop filter."""
    scale_w = target_w / orig_w
    scale_h = target_h / orig_h
    scale = max(scale_w, scale_h)

    scaled_w = int(orig_w * scale)
    scaled_h = int(orig_h * scale)

    crop_x, crop_y = _calculate_crop_offset(
        scaled_w, scaled_h, target_w, target_h, crop_align
    )

    return (
        f"scale={scaled_w}:{scaled_h}:flags=lanczos,"
        f"crop={target_w}:{target_h}:{crop_x}:{crop_y}"
    )


def _build_crop_max_filter(
    orig_w: int,
    orig_h: int,
    target_w: int,
    target_h: int,
    crop_align: CropAlign
) -> str:
    """Build crop-at-max-resolution then scale filter."""
    target_aspect = target_w / target_h
    orig_aspect = orig_w / orig_h

    if orig_aspect > target_aspect:
        crop_height = orig_h
        crop_width = int(crop_height * target_aspect)
    else:
        crop_width = orig_w
        crop_height = int(crop_width / target_aspect)

    crop_x, crop_y = _calculate_crop_offset(
        orig_w, orig_h, crop_width, crop_height, crop_align
    )

    return (
        f"crop={crop_width}:{crop_height}:{crop_x}:{crop_y},"
        f"scale={target_w}:{target_h}:flags=lanczos"
    )


def _build_pad_filter(
    orig_w: int,
    orig_h: int,
    target_w: int,
    target_h: int
) -> str:
    """Build scale-to-fit then pad filter."""
    scale_w = target_w / orig_w
    scale_h = target_h / orig_h
    scale = min(scale_w, scale_h)

    scaled_w = int(orig_w * scale)
    scaled_h = int(orig_h * scale)

    return (
        f"scale={scaled_w}:{scaled_h}:flags=lanczos,"
        f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2"
    )


def _calculate_crop_offset(
    src_w: int,
    src_h: int,
    crop_w: int,
    crop_h: int,
    crop_align: CropAlign
) -> Tuple[int, int]:
    """Calculate crop offset based on alignment."""
    excess_w = src_w - crop_w
    excess_h = src_h - crop_h

    if 'left' in crop_align:
        crop_x = 0
    elif 'right' in crop_align:
        crop_x = excess_w
    else:
        crop_x = excess_w // 2

    if 'top' in crop_align:
        crop_y = 0
    elif 'bottom' in crop_align:
        crop_y = excess_h
    else:
        crop_y = excess_h // 2

    return crop_x, crop_y


# ---------------------------------------------------------------------------
# Video Assembly
# ---------------------------------------------------------------------------


def assemble_video(
    frames_dir: Path,
    original_video: Path,
    output_path: Path,
    fps: float,
    speed: float,
    has_audio: bool,
    speed_ramp: Optional[str] = None,
    audio_speed: Optional[float] = None,
    trim_start: float = 0.0,
    output_duration: Optional[float] = None
) -> None:
    """
    Assemble frames into video with optional speed adjustment and audio.

    Args:
        frames_dir: Directory containing frames
        original_video: Original video file (for audio extraction)
        output_path: Output video path
        fps: Frame rate
        speed: Speed multiplier for video PTS
        has_audio: Whether original video has audio
        speed_ramp: Speed ramp curve name (for logging)
        audio_speed: Speed multiplier for audio (defaults to speed if not provided)
        trim_start: Start time offset for audio extraction
        output_duration: Duration of trimmed video (before speed adjustment)
    """
    video_only = output_path.with_name(output_path.stem + "_vid.mp4")

    if audio_speed is None:
        audio_speed = speed

    if speed_ramp:
        log_info(
            f"    Encoding video at {fps}fps with {audio_speed}x speed "
            f"({speed_ramp} curve)..."
        )
    else:
        log_info(f"    Encoding video at {fps}fps with {speed}x speed...")

    # Use setpts to adjust playback speed
    pts_multiplier = 1.0 / speed

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-vf", f"setpts={pts_multiplier}*PTS",
        "-r", str(fps),
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        str(video_only)
    ]

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        if video_only.exists():
            video_only.unlink()
        raise RuntimeError(f"FFmpeg video encoding failed: {result.stderr}")

    # Handle audio
    if has_audio:
        _merge_audio(
            video_only, original_video, output_path,
            audio_speed, trim_start
        )
    else:
        log_info(f"    No audio track found, using video only...")
        shutil.copy2(video_only, output_path)

    # Clean up
    if video_only.exists():
        video_only.unlink()

    log_info(f"    Video assembly complete")


def _merge_audio(
    video_path: Path,
    original_video: Path,
    output_path: Path,
    audio_speed: float,
    trim_start: float
) -> None:
    """Merge audio from original video with processed video."""
    log_info(f"    Merging audio with speed adjustment...")

    # Build audio input args with trim offset
    audio_input_args = []
    if trim_start > 0:
        audio_input_args.extend(["-ss", str(trim_start)])
    audio_input_args.extend(["-i", str(original_video)])

    if audio_speed != 1.0:
        audio_filter = _build_audio_speed_filter(audio_speed)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            *audio_input_args,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy",
            "-af", audio_filter,
            "-c:a", "aac",
            "-shortest",
            str(output_path)
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            *audio_input_args,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac",
            "-shortest",
            str(output_path)
        ]

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        if video_path.exists():
            video_path.unlink()
        raise RuntimeError(f"FFmpeg audio merge failed: {result.stderr}")


def _build_audio_speed_filter(speed: float) -> str:
    """Build atempo filter chain for audio speed adjustment."""
    # atempo filter is limited to 0.5-2.0x, so chain for higher speeds
    if speed <= 2.0:
        return f"atempo={speed}"

    filters = []
    remaining_speed = speed
    while remaining_speed > 2.0:
        filters.append("atempo=2.0")
        remaining_speed /= 2.0
    if remaining_speed != 1.0:
        filters.append(f"atempo={remaining_speed}")

    return ",".join(filters)


# ---------------------------------------------------------------------------
# Simple Processing (No Zoom)
# ---------------------------------------------------------------------------


def process_video_simple(
    video_path: Path,
    output_path: Path,
    speed: float,
    target_size: Optional[Tuple[int, int]],
    fit_mode: FitMode,
    crop_align: CropAlign,
    target_fps: Optional[int],
    has_audio: bool,
    orig_size: Tuple[int, int],
    orig_fps: float,
    trim_start: float,
    output_duration: Optional[float]
) -> None:
    """
    Process video using pure FFmpeg (no zoom effect, faster).

    Args:
        video_path: Source video file
        output_path: Output video path
        speed: Speed multiplier
        target_size: Optional target dimensions
        fit_mode: How to fit to target size
        crop_align: Alignment when cropping
        target_fps: Target frame rate (None to preserve)
        has_audio: Whether video has audio
        orig_size: Original video dimensions
        orig_fps: Original frame rate
        trim_start: Seconds to skip from start
        output_duration: Duration to process (None for full)
    """
    orig_w, orig_h = orig_size

    # Build filter
    filters = []

    if target_size:
        scale_filter = build_ffmpeg_filter(
            (orig_w, orig_h), target_size, fit_mode, crop_align
        )
        if scale_filter:
            filters.append(scale_filter)

    # Build command
    cmd = ["ffmpeg", "-y"]

    if trim_start > 0:
        cmd.extend(["-ss", str(trim_start)])

    cmd.extend(["-i", str(video_path)])

    if output_duration is not None:
        cmd.extend(["-t", str(output_duration)])

    # Combine video filters
    video_filters = list(filters)

    if speed != 1.0:
        video_speed = 1.0 / speed
        video_filters.append(f"setpts={video_speed}*PTS")

    if video_filters:
        cmd.extend(["-vf", ",".join(video_filters)])

    # Frame rate
    output_fps = target_fps if target_fps else orig_fps
    cmd.extend(["-r", str(output_fps)])

    # Video codec
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17",
        "-pix_fmt", "yuv420p"
    ])

    # Audio handling
    if has_audio:
        if speed != 1.0:
            audio_filter = _build_audio_speed_filter(speed)
            cmd.extend(["-af", audio_filter, "-c:a", "aac"])
        else:
            cmd.extend(["-c:a", "copy"])
    else:
        cmd.extend(["-an"])

    cmd.append(str(output_path))

    log_info(f"    Processing with FFmpeg...")
    result = subprocess.run(cmd, capture_output=True)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg processing failed: {result.stderr}")

    log_info(f"    Processing complete")
