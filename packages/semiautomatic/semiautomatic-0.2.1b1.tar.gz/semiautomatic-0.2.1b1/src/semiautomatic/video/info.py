"""
Video information and utility functions.

Library usage:
    from semiautomatic.video.info import get_video_info, VideoInfo
    info = get_video_info(Path("video.mp4"))
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional

from semiautomatic.lib import subprocess

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', '.webm'}

MAX_UNIQUE_FILENAME_ATTEMPTS = 1000

# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class VideoInfo:
    """Video metadata from ffprobe."""
    width: int
    height: int
    fps: float
    has_audio: bool
    duration: float


@dataclass
class ZoomSpec:
    """Zoom specification with start and end percentages."""
    start: int
    end: int


# ---------------------------------------------------------------------------
# Parsing Functions
# ---------------------------------------------------------------------------


def parse_size(size_str: Optional[str]) -> Optional[Tuple[int, int]]:
    """
    Parse size string like '1024x1024' into (width, height).

    Args:
        size_str: Size string in format 'WIDTHxHEIGHT'

    Returns:
        Tuple of (width, height) or None if size_str is empty

    Raises:
        ValueError: If size_str is not a valid format
    """
    if not size_str:
        return None
    try:
        width, height = size_str.split('x')
        return int(width), int(height)
    except ValueError:
        raise ValueError(f"Size must be in format 'WIDTHxHEIGHT', got: {size_str}")


def parse_zoom(zoom_str: Optional[str]) -> Optional[ZoomSpec]:
    """
    Parse zoom string like '100:150' into ZoomSpec.

    Args:
        zoom_str: Zoom string in format 'START:END'

    Returns:
        ZoomSpec or None if zoom_str is empty

    Raises:
        ValueError: If zoom_str is not a valid format
    """
    if not zoom_str:
        return None
    try:
        start, end = zoom_str.split(':')
        return ZoomSpec(start=int(start), end=int(end))
    except ValueError:
        raise ValueError(f"Zoom must be in format 'START:END', got: {zoom_str}")


# ---------------------------------------------------------------------------
# Video Info
# ---------------------------------------------------------------------------


def get_video_info(video_path: Path) -> VideoInfo:
    """
    Get video resolution, frame rate, and duration using ffprobe.

    Args:
        video_path: Path to video file

    Returns:
        VideoInfo with metadata

    Raises:
        RuntimeError: If ffprobe fails or video is invalid
    """
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_streams", "-show_format",
                str(video_path)
            ],
            capture_output=True,
            check=True
        )

        data = json.loads(result.stdout)
        video_stream = next(
            (s for s in data["streams"] if s["codec_type"] == "video"),
            None
        )

        if video_stream is None:
            raise RuntimeError(f"No video stream found in {video_path}")

        width = int(video_stream["width"])
        height = int(video_stream["height"])

        # Parse frame rate
        fps_str = video_stream.get("r_frame_rate", "30/1")
        if "/" in fps_str:
            num, den = map(int, fps_str.split("/"))
            fps = num / den if den != 0 else 30.0
        else:
            fps = float(fps_str)

        fps = round(fps, 2)

        # Check for audio
        has_audio = any(s["codec_type"] == "audio" for s in data["streams"])

        # Get duration
        duration = float(data["format"]["duration"])

        return VideoInfo(
            width=width,
            height=height,
            fps=fps,
            has_audio=has_audio,
            duration=duration
        )

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe failed for {video_path}: {e.stderr}")
    except (KeyError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to parse video info for {video_path}: {e}")


# ---------------------------------------------------------------------------
# Path Utilities
# ---------------------------------------------------------------------------


def get_unique_output_path(base_path: Path) -> Path:
    """
    Generate unique output filename if file exists.

    Args:
        base_path: Desired output path

    Returns:
        Path that doesn't exist (either base_path or with _01, _02, etc. suffix)

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


def find_videos(directory: Path) -> list[Path]:
    """
    Find all video files in directory (non-recursive).

    Args:
        directory: Directory to search

    Returns:
        Sorted list of video file paths
    """
    files = []
    for ext in VIDEO_EXTENSIONS:
        files.extend(directory.glob(f"*{ext}"))
        files.extend(directory.glob(f"*{ext.upper()}"))

    return sorted(set(files), key=lambda p: p.name.lower())
