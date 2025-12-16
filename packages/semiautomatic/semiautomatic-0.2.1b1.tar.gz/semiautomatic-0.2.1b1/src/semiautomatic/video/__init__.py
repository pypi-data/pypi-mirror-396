"""
Video processing and generation module for semiautomatic.

Processing:
    Provides video manipulation tools including speed adjustment, zoom effects,
    resize, trim, and frame extraction operations.

Generation:
    Generate videos from text prompts using AI models (Kling, Seedance, Hailuo).

Library usage:
    from semiautomatic.video import process_video, generate_video

    # Process video with speed and zoom
    output = process_video(
        Path('input.mp4'),
        Path('./output'),
        speed=1.5,
        zoom_h=(100, 150)
    )

    # Generate video from prompt
    result = generate_video("a cat walking", model="kling2.1")
    print(result.video.path)

CLI usage:
    semiautomatic process-video --speed 1.25
    semiautomatic generate-video --prompt "a cat walking"
"""

from semiautomatic.video.process import (
    process_video,
    run_process_video,
    ProcessingResult,
)
from semiautomatic.video.frames import (
    extract_frame_from_video,
    extract_single_frame,
    extract_frames,
    process_frames_with_zoom,
    create_speed_ramped_frames,
    FrameExtractionResult,
)
from semiautomatic.video.info import (
    get_video_info,
    get_unique_output_path,
    find_videos,
    parse_size,
    parse_zoom,
    VideoInfo,
    ZoomSpec,
)
from semiautomatic.video.easing import (
    apply_easing_curve,
    EASING_CURVES,
)
from semiautomatic.video.ffmpeg import (
    build_ffmpeg_filter,
    assemble_video,
    process_video_simple,
)

from semiautomatic.video.generate import generate_video, run_generate_video

from semiautomatic.video.providers import (
    get_provider as get_video_provider,
    list_providers as list_video_providers,
    list_all_models as list_video_models,
    VideoProvider,
    VideoResult,
    VideoGenerationResult,
)

__all__ = [
    # Main processing
    "process_video",
    "run_process_video",
    "ProcessingResult",
    # Frame operations
    "extract_frame_from_video",
    "extract_single_frame",
    "extract_frames",
    "process_frames_with_zoom",
    "create_speed_ramped_frames",
    "FrameExtractionResult",
    # Video info
    "get_video_info",
    "get_unique_output_path",
    "find_videos",
    "parse_size",
    "parse_zoom",
    "VideoInfo",
    "ZoomSpec",
    # Easing
    "apply_easing_curve",
    "EASING_CURVES",
    # FFmpeg
    "build_ffmpeg_filter",
    "assemble_video",
    "process_video_simple",
    # Generation
    "generate_video",
    "run_generate_video",
    "get_video_provider",
    "list_video_providers",
    "list_video_models",
    "VideoProvider",
    "VideoResult",
    "VideoGenerationResult",
]
