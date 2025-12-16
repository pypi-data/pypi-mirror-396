"""
Video processing library for semiautomatic.

Provides functions for speed adjustment, zoom effects, resize, trim, and frame extraction.
Supports easing curves for smooth speed ramping effects.

Library usage:
    from semiautomatic.video import process_video
    output_path = process_video(Path('input.mp4'), Path('./output'), speed=1.5)

CLI usage:
    semiautomatic process-video --speed 1.25
    semiautomatic process-video --zoom 100:150
    semiautomatic process-video --extract-frame last
"""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional

from semiautomatic.lib.logging import log_info, log_error
from semiautomatic.video.easing import EASING_CURVES
from semiautomatic.video.info import (
    get_video_info, get_unique_output_path, find_videos,
    parse_size, parse_zoom, ZoomSpec
)
from semiautomatic.video.frames import (
    extract_frame_from_video, extract_frames,
    process_frames_with_zoom, create_speed_ramped_frames,
    FitMode, CropAlign
)
from semiautomatic.video.ffmpeg import (
    assemble_video, process_video_simple
)

# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class ProcessingResult:
    """Result of video processing operation."""
    output_path: Path
    input_duration: float
    output_duration: float


# ---------------------------------------------------------------------------
# Main Processing
# ---------------------------------------------------------------------------


def process_video(
    video_path: Path,
    output_dir: Path,
    speed: float = 1.0,
    zoom_h: Tuple[int, int] = (100, 100),
    zoom_v: Tuple[int, int] = (100, 100),
    target_size: Optional[Tuple[int, int]] = None,
    fit_mode: FitMode = "stretch",
    crop_align: CropAlign = "center",
    target_fps: Optional[int] = None,
    trim_start: float = 0.0,
    trim_end: float = 0.0,
    speed_ramp: Optional[str] = None,
    output_path: Optional[Path] = None
) -> Path:
    """
    Process a single video with all effects.

    Args:
        video_path: Source video file
        output_dir: Directory for output
        speed: Playback speed multiplier (default: 1.0)
        zoom_h: (start_percent, end_percent) for horizontal zoom
        zoom_v: (start_percent, end_percent) for vertical zoom
        target_size: Optional (width, height) target dimensions
        fit_mode: How to fit to target size (stretch, crop, crop-max, pad)
        crop_align: Alignment when cropping
        target_fps: Target frame rate (None to preserve)
        trim_start: Seconds to trim from start
        trim_end: Seconds to trim from end
        speed_ramp: Easing curve name for speed ramping
        output_path: Explicit output path (overrides output_dir)

    Returns:
        Path to the output file
    """
    video_name = video_path.stem

    log_info(f"[{video_name}] Starting processing...")

    # Get video info
    info = get_video_info(video_path)
    log_info(
        f"[{video_name}] Input: {info.width}x{info.height} @ {info.fps}fps, "
        f"duration: {info.duration:.2f}s, audio: {info.has_audio}"
    )

    # Validate trim parameters
    if trim_start < 0:
        raise ValueError(f"trim_start must be >= 0, got {trim_start}")
    if trim_end < 0:
        raise ValueError(f"trim_end must be >= 0, got {trim_end}")

    # Calculate output duration
    if trim_start + trim_end >= info.duration:
        raise ValueError(
            f"Combined trim ({trim_start + trim_end:.2f}s) must be less than "
            f"video duration ({info.duration:.2f}s)"
        )

    output_duration = (
        info.duration - trim_start - trim_end
        if (trim_start > 0 or trim_end > 0) else None
    )

    if output_duration is not None:
        log_info(
            f"[{video_name}] Trimming: start={trim_start}s, end={trim_end}s, "
            f"output duration={output_duration:.2f}s"
        )

    # Determine output fps
    fps = target_fps if target_fps else info.fps

    # Determine if we need frame-by-frame processing
    needs_zoom = (
        (zoom_h[0] != 100 or zoom_h[1] != 100) or
        (zoom_v[0] != 100 or zoom_v[1] != 100)
    )
    needs_frame_processing = needs_zoom or speed_ramp is not None

    # Set target size
    final_size = target_size if target_size else (info.width, info.height)

    # Generate output path
    if output_path:
        final_output_path = Path(output_path)
        final_output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        final_output_path = output_dir / f"{video_name}_processed.mp4"
        final_output_path = get_unique_output_path(final_output_path)

    try:
        if needs_frame_processing:
            _process_with_frames(
                video_path, final_output_path, video_name,
                info, fps, speed, zoom_h, zoom_v,
                final_size, fit_mode, crop_align,
                speed_ramp, trim_start, output_duration
            )
        else:
            log_info(f"[{video_name}] Using FFmpeg direct processing")
            process_video_simple(
                video_path, final_output_path, speed, target_size, fit_mode,
                crop_align, target_fps, info.has_audio,
                (info.width, info.height), info.fps, trim_start, output_duration
            )

        log_info(f"[{video_name}] Complete! Output: {final_output_path.name}")
        return final_output_path

    except Exception as e:
        raise RuntimeError(f"Processing failed for {video_name}: {e}")


def _process_with_frames(
    video_path: Path,
    output_path: Path,
    video_name: str,
    info,
    fps: float,
    speed: float,
    zoom_h: Tuple[int, int],
    zoom_v: Tuple[int, int],
    final_size: Tuple[int, int],
    fit_mode: FitMode,
    crop_align: CropAlign,
    speed_ramp: Optional[str],
    trim_start: float,
    output_duration: Optional[float]
) -> None:
    """Process video using frame-by-frame method (for zoom/speed ramp)."""
    needs_zoom = (zoom_h[0] != 100 or zoom_h[1] != 100) or (zoom_v[0] != 100 or zoom_v[1] != 100)

    if needs_zoom and speed_ramp:
        log_info(f"[{video_name}] Using frame-by-frame processing (zoom + speed ramp)")
    elif needs_zoom:
        log_info(f"[{video_name}] Using frame-by-frame zoom processing")
    else:
        log_info(f"[{video_name}] Using frame-by-frame speed ramp processing")

    temp_dir = Path(tempfile.mkdtemp(prefix=f"vp_{video_name}_"))
    input_frames_dir = temp_dir / "input_frames"
    output_frames_dir = temp_dir / "output_frames"
    speed_ramp_dir = temp_dir / "speed_ramp_frames" if speed_ramp else None

    try:
        # Extract frames
        frame_files = extract_frames(
            video_path, input_frames_dir, fps, trim_start, output_duration
        )

        # Process frames with zoom (or just copy if no zoom)
        if needs_zoom:
            process_frames_with_zoom(
                frame_files, output_frames_dir, video_name,
                zoom_h, zoom_v, final_size, crop_align, fit_mode
            )
        else:
            output_frames_dir.mkdir(parents=True, exist_ok=True)
            for frame_file in frame_files:
                shutil.copy2(frame_file, output_frames_dir / frame_file.name)

        # Apply speed ramping if requested
        if speed_ramp:
            create_speed_ramped_frames(
                output_frames_dir, speed_ramp_dir, fps, speed, speed_ramp
            )
            final_frames_dir = speed_ramp_dir
            assemble_speed = 1.0
            audio_speed = speed
        else:
            final_frames_dir = output_frames_dir
            assemble_speed = speed
            audio_speed = speed

        # Assemble video
        assemble_video(
            final_frames_dir, video_path, output_path, fps,
            assemble_speed, info.has_audio, speed_ramp, audio_speed,
            trim_start, output_duration
        )

    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------


def run_process_video(args) -> bool:
    """
    CLI handler for process-video command.

    Args:
        args: Parsed argparse namespace

    Returns:
        True on success, False on failure
    """
    # Validate --output usage
    if args.output and not args.input:
        log_error("--output can only be used with --input (single file mode)")
        return False

    # Check if we're in frame extraction mode
    is_extract_mode = args.extract_frame is not None or args.extract_time is not None

    # Validate conflicting arguments
    if is_extract_mode:
        if args.speed != 1.0:
            log_error("--speed cannot be used with frame extraction")
            return False
        if args.zoom or args.zoomh or args.zoomv:
            log_error("--zoom options cannot be used with frame extraction")
            return False
        if args.trim_start > 0 or args.trim_end > 0:
            log_error("--trim options cannot be used with frame extraction")
            return False
        if args.fps:
            log_error("--fps cannot be used with frame extraction")
            return False
        if args.extract_frame and args.extract_time is not None:
            log_error("Cannot specify both --extract-frame and --extract-time")
            return False

    # Validate speed
    if args.speed <= 0:
        log_error("Speed must be greater than 0")
        return False

    # Parse size
    target_size = None
    if args.size:
        try:
            target_size = parse_size(args.size)
        except ValueError as e:
            log_error(str(e))
            return False

    # Handle zoom arguments
    zoom_h = (100, 100)
    zoom_v = (100, 100)

    if args.zoomh:
        try:
            spec = parse_zoom(args.zoomh)
            zoom_h = (spec.start, spec.end)
        except ValueError as e:
            log_error(str(e))
            return False

    if args.zoomv:
        try:
            spec = parse_zoom(args.zoomv)
            zoom_v = (spec.start, spec.end)
        except ValueError as e:
            log_error(str(e))
            return False

    if args.zoom:
        try:
            spec = parse_zoom(args.zoom)
            if zoom_h == (100, 100):
                zoom_h = (spec.start, spec.end)
            if zoom_v == (100, 100):
                zoom_v = (spec.start, spec.end)
        except ValueError as e:
            log_error(str(e))
            return False

    # Set up output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Print header
    _print_header(args, is_extract_mode, zoom_h, zoom_v)

    # Process videos
    processed_count = 0
    failed_count = 0

    if args.input:
        # Single file mode
        input_path = Path(args.input)
        if not input_path.exists():
            log_error(f"Input file '{input_path}' not found")
            return False

        try:
            if is_extract_mode:
                extract_frame_from_video(
                    input_path, output_dir, args.extract_frame,
                    args.extract_time, target_size, args.fit, args.crop_align
                )
            else:
                process_video(
                    input_path, output_dir, args.speed, zoom_h, zoom_v,
                    target_size, args.fit, args.crop_align, args.fps,
                    args.trim_start, args.trim_end, args.speed_ramp,
                    output_path=Path(args.output) if args.output else None
                )
            processed_count = 1
        except Exception as e:
            log_error(f"Failed: {e}")
            failed_count = 1
    else:
        # Batch mode
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            log_error(f"Input directory '{input_dir}' not found")
            return False

        video_files = find_videos(input_dir)

        if not video_files:
            log_error("No video files found in input directory")
            return False

        log_info(f"Found {len(video_files)} video file(s) to process:")
        for video in video_files:
            print(f"  - {video.name}")
        log_info("")

        for i, video in enumerate(video_files, 1):
            log_info(f"--- Processing {i}/{len(video_files)}: {video.name} ---")
            try:
                if is_extract_mode:
                    extract_frame_from_video(
                        video, output_dir, args.extract_frame,
                        args.extract_time, target_size, args.fit, args.crop_align
                    )
                else:
                    process_video(
                        video, output_dir, args.speed, zoom_h, zoom_v,
                        target_size, args.fit, args.crop_align, args.fps,
                        args.trim_start, args.trim_end, args.speed_ramp
                    )
                processed_count += 1
            except Exception as e:
                log_error(f"Failed: {e}")
                failed_count += 1
                continue
            log_info("")

    # Summary
    log_info("=" * 60)
    if processed_count > 0:
        log_info(f"Successfully processed {processed_count} video(s)")
    if failed_count > 0:
        log_error(f"Failed to process {failed_count} video(s)")

    return processed_count > 0


def _print_header(args, is_extract_mode: bool, zoom_h: Tuple[int, int], zoom_v: Tuple[int, int]) -> None:
    """Print processing header with settings."""
    log_info("Video Processor")
    log_info("=" * 60)

    if is_extract_mode:
        log_info("Mode: Frame Extraction")
        if args.extract_frame:
            try:
                frame_idx = int(args.extract_frame)
                if frame_idx < 0:
                    log_info(f"  Position: Frame {args.extract_frame} (from end)")
                else:
                    log_info(f"  Position: Frame {frame_idx}")
            except ValueError:
                log_info(f"  Position: {args.extract_frame}")
        if args.extract_time is not None:
            log_info(f"  Time: {args.extract_time}s")
    else:
        log_info("Mode: Video Processing")
        if args.speed_ramp:
            log_info(f"  Speed: {args.speed}x with {args.speed_ramp} curve")
        else:
            log_info(f"  Speed: {args.speed}x")

        if zoom_h != (100, 100) or zoom_v != (100, 100):
            if zoom_h == zoom_v:
                log_info(f"  Zoom: {zoom_h[0]}% -> {zoom_h[1]}%")
            else:
                log_info(f"  Zoom H: {zoom_h[0]}% -> {zoom_h[1]}%")
                log_info(f"  Zoom V: {zoom_v[0]}% -> {zoom_v[1]}%")
        else:
            log_info(f"  Zoom: None")

        if args.trim_start > 0 or args.trim_end > 0:
            log_info(f"  Trim: start={args.trim_start}s, end={args.trim_end}s")
        else:
            log_info(f"  Trim: None")

    if args.size:
        log_info(f"  Resize: {args.size} ({args.fit}, align: {args.crop_align})")
    else:
        log_info(f"  Resize: None")

    if args.fps and not is_extract_mode:
        log_info(f"  Frame Rate: {args.fps}fps")
    elif not is_extract_mode:
        log_info(f"  Frame Rate: Original")

    log_info("")
