"""
semiautomatic CLI - Main entry point for all commands.

Usage:
    semiautomatic <command> [options]
    sa <command> [options]  # alias

Commands:
    generate-image         Generate images with AI models (FLUX, Qwen, WAN, Recraft)
    generate-video         Generate videos with AI models (Kling, Seedance, Hailuo)
    generate-image-prompt  Generate platform-specific image prompts
    generate-video-prompt  Generate motion prompts from images
    upscale-image          Upscale images with AI (Freepik)
    process-image          Batch resize, convert, and compress images
    process-video          Video speed, zoom, resize, trim, and frame extraction
"""

import sys
import argparse
from importlib.metadata import version

import semiautomatic  # triggers UTF-8 setup on Windows


def cmd_generate_image(args):
    """Handler for 'generate-image' command."""
    from semiautomatic.image.generate import run_generate_image
    return run_generate_image(args)


def cmd_upscale_image(args):
    """Handler for 'upscale-image' command."""
    from semiautomatic.image.upscale import run_upscale_image
    return run_upscale_image(args)


def cmd_process_image(args):
    """Handler for 'process-image' command."""
    from semiautomatic.image.process import run_process_image
    return run_process_image(args)


def cmd_process_video(args):
    """Handler for 'process-video' command."""
    from semiautomatic.video.process import run_process_video
    return run_process_video(args)


def cmd_generate_video(args):
    """Handler for 'generate-video' command."""
    from semiautomatic.video.generate import run_generate_video
    return run_generate_video(args)


def cmd_generate_image_prompt(args):
    """Handler for 'generate-image-prompt' command."""
    from semiautomatic.prompt import run_generate_image_prompt
    return run_generate_image_prompt(args)


def cmd_generate_video_prompt(args):
    """Handler for 'generate-video-prompt' command."""
    from semiautomatic.prompt import run_generate_video_prompt
    return run_generate_video_prompt(args)


def build_parser():
    """Build the argument parser with all subcommands."""
    ver = version("semiautomatic")
    parser = argparse.ArgumentParser(
        prog='semiautomatic',
        description=f'semiautomatic v{ver} - AI automation tools for creative workflows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run 'semiautomatic <command> --help' for details on a specific command.",
    )
    parser.add_argument(
        '--version', action='version',
        version=f'%(prog)s {version("semiautomatic")}'
    )

    subparsers = parser.add_subparsers(
        title='commands',
        dest='command',
        metavar='<command>',
    )

    # generate-image command
    generate_image_parser = subparsers.add_parser(
        'generate-image',
        help='Generate images with AI models (FLUX, Qwen, WAN, Recraft)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
FAL Size presets:
  square          1024x1024
  square_hd       1536x1536
  portrait_4_3    768x1024
  portrait_16_9   576x1024
  landscape_4_3   1024x768 (default)
  landscape_16_9  1024x576

Recraft Size presets:
  square          1024x1024
  square_hd       1536x1536
  landscape       1365x1024
  portrait        1024x1365

Recraft Styles:
  realistic_image, digital_illustration, vector_illustration, logo_raster, any

Examples:
  # FAL provider (default)
  semiautomatic generate-image --prompt "a cat on a windowsill"
  semiautomatic generate-image --prompt "portrait photo" --model flux-dev --size portrait_4_3
  semiautomatic generate-image --prompt "my style" --model flux-krea --lora path/to/lora.safetensors:0.8

  # Recraft provider
  semiautomatic generate-image --provider recraft --prompt "cyberpunk city" --style digital_illustration
  semiautomatic generate-image --provider recraft --prompt "product photo" --style realistic_image --size landscape

  # Recraft image-to-image
  semiautomatic generate-image --provider recraft --input-image photo.jpg --prompt "transform to illustration" --strength 0.7

  # List models
  semiautomatic generate-image --list-models
        """
    )
    generate_image_parser.add_argument(
        '--prompt', type=str,
        help='Text prompt describing the image to generate'
    )
    generate_image_parser.add_argument(
        '--provider', type=str, default=None,
        help='Provider to use: fal (default) or recraft'
    )
    generate_image_parser.add_argument(
        '--model', type=str, default=None,
        help='Model to use (default: flux-dev for FAL, recraftv3 for Recraft)'
    )
    generate_image_parser.add_argument(
        '--size', type=str, default=None,
        help='Image size: preset name or WxH (default varies by provider)'
    )
    generate_image_parser.add_argument(
        '--num-images', type=int, default=1,
        help='Number of images to generate (1-4 for FAL, 1-6 for Recraft)'
    )
    generate_image_parser.add_argument(
        '--seed', type=int, default=None,
        help='Random seed for reproducibility'
    )
    # FAL-specific options
    generate_image_parser.add_argument(
        '--lora', type=str, action='append',
        help='[FAL] LoRA file path (can specify multiple). Format: path or path:scale'
    )
    generate_image_parser.add_argument(
        '--steps', type=int, default=None,
        help='[FAL] Number of inference steps (overrides model default)'
    )
    generate_image_parser.add_argument(
        '--guidance', type=float, default=None,
        help='[FAL] Guidance scale (overrides model default)'
    )
    # Recraft-specific options
    generate_image_parser.add_argument(
        '--style', type=str, default=None,
        help='[Recraft] Style name or custom UUID (default: realistic_image)'
    )
    generate_image_parser.add_argument(
        '--input-image', type=str, default=None,
        help='[Recraft] Input image for image-to-image transformation'
    )
    generate_image_parser.add_argument(
        '--strength', type=float, default=None,
        help='[Recraft] Transformation strength 0-1 for i2i (default: 0.5)'
    )
    generate_image_parser.add_argument(
        '--artistic-level', type=int, default=None,
        help='[Recraft] Artistic tone 0-5 (0=static/clean, 5=dynamic/eccentric)'
    )
    generate_image_parser.add_argument(
        '--colors', type=str, nargs='+', default=None,
        help='[Recraft] Preferred colors as hex values (e.g., "#FF0000" "#00FF00")'
    )
    generate_image_parser.add_argument(
        '--background-color', type=str, default=None,
        help='[Recraft] Background color as hex (e.g., "#000000")'
    )
    generate_image_parser.add_argument(
        '--no-text', action='store_true',
        help='[Recraft] Do not embed text layouts in the image'
    )
    generate_image_parser.add_argument(
        '--negative-prompt', type=str, default=None,
        help='[Recraft] Text description of undesired elements (i2i only)'
    )
    # Common options
    generate_image_parser.add_argument(
        '--format', choices=['png', 'jpeg'], default='png',
        help='Output format (default: png)'
    )
    generate_image_parser.add_argument(
        '--output', '-o', type=str, default=None,
        help='Output filename (e.g., cat.png). Overrides --output-dir.'
    )
    generate_image_parser.add_argument(
        '--output-dir', type=str, default='./output',
        help='Output directory for auto-named files (default: ./output)'
    )
    generate_image_parser.add_argument(
        '--list-models', action='store_true',
        help='List available models and exit'
    )
    generate_image_parser.set_defaults(func=cmd_generate_image)

    # upscale-image command
    upscale_image_parser = subparsers.add_parser(
        'upscale-image',
        help='Upscale images with AI (Freepik)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Optimization presets:
  standard              General purpose (default)
  soft_portraits        Portrait photos with soft details
  hard_portraits        Portrait photos with sharp details
  art_n_illustration    Artwork and illustrations
  videogame_assets      Game textures and sprites
  nature_n_landscapes   Nature and landscape photos
  films_n_photography   Film stills and professional photos
  3d_renders            3D rendered images
  science_fiction_n_horror  Sci-fi and horror imagery

Examples:
  semiautomatic upscale-image --input photo.jpg
  semiautomatic upscale-image --input photo.jpg --scale 4x
  semiautomatic upscale-image --input photo.jpg --scale 2x --engine magnific_sharpy
  semiautomatic upscale-image --input-dir ./images --auto-prompt
  semiautomatic upscale-image --input portrait.jpg --optimized-for soft_portraits
        """
    )
    # Input options
    upscale_input = upscale_image_parser.add_mutually_exclusive_group()
    upscale_input.add_argument(
        '--input', '-i', type=str, default=None,
        help='Input image file to upscale'
    )
    upscale_input.add_argument(
        '--input-dir', type=str, default='./input',
        help='Input directory for batch processing (default: ./input)'
    )
    upscale_image_parser.add_argument(
        '--output', '-o', type=str, default=None,
        help='Output filename (e.g., upscaled.png). Overrides --output-dir.'
    )
    upscale_image_parser.add_argument(
        '--output-dir', type=str, default='./output',
        help='Output directory for auto-named files (default: ./output)'
    )
    # Upscale settings
    upscale_image_parser.add_argument(
        '--scale', type=str, default='2x', choices=['2x', '4x', '8x', '16x'],
        help='Scale factor (default: 2x)'
    )
    upscale_image_parser.add_argument(
        '--engine', type=str, default='automatic',
        choices=['automatic', 'magnific_illusio', 'magnific_sharpy', 'magnific_sparkle'],
        help='Upscaling engine (default: automatic)'
    )
    upscale_image_parser.add_argument(
        '--optimized-for', type=str, default='standard',
        choices=['standard', 'soft_portraits', 'hard_portraits',
                 'art_n_illustration', 'videogame_assets',
                 'nature_n_landscapes', 'films_n_photography',
                 '3d_renders', 'science_fiction_n_horror'],
        help='Optimization preset (default: standard)'
    )
    # Prompt options
    upscale_prompt = upscale_image_parser.add_mutually_exclusive_group()
    upscale_prompt.add_argument(
        '--prompt', type=str, default=None,
        help='Text prompt to guide upscaling'
    )
    upscale_prompt.add_argument(
        '--auto-prompt', action='store_true',
        help='Auto-generate prompt for each image using vision model'
    )
    # Fine-tuning options
    upscale_image_parser.add_argument(
        '--creativity', type=int, default=0,
        help='Creativity level 0-10 (default: 0)'
    )
    upscale_image_parser.add_argument(
        '--hdr', type=int, default=0,
        help='HDR enhancement 0-10 (default: 0)'
    )
    upscale_image_parser.add_argument(
        '--resemblance', type=int, default=0,
        help='Resemblance to original 0-10 (default: 0)'
    )
    upscale_image_parser.add_argument(
        '--fractality', type=int, default=0,
        help='Detail fractality 0-10 (default: 0)'
    )
    upscale_image_parser.set_defaults(func=cmd_upscale_image)

    # process-image command
    process_image_parser = subparsers.add_parser(
        'process-image',
        help='Batch resize, convert, and compress images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Size formats:
  1920x1080     Exact dimensions (width x height)
  0.5           Scale to 50% of original size
  2.0           Scale to 200% (upscale)
  1920x         Width-constrained (preserve aspect ratio)
  x1080         Height-constrained (preserve aspect ratio)

Examples:
  semiautomatic process-image --size 1920x1080
  semiautomatic process-image --size 0.5
  semiautomatic process-image --format png
  semiautomatic process-image --input photo.jpg --size 0.5
  semiautomatic process-image --max-size 5  # Compress for Claude Vision API
        """
    )
    process_image_parser.add_argument(
        '--size', type=str, default=None,
        help='Target size: WxH (1920x1080), scale (0.5), or constrained (1920x, x1080)'
    )
    process_image_parser.add_argument(
        '--format', choices=['auto', 'png', 'jpeg'], default='auto',
        help='Output format: auto (preserve source), png, or jpeg (default: auto)'
    )
    process_image_parser.add_argument(
        '--quality', type=int, default=85,
        help='JPEG quality 1-100 (default: 85)'
    )
    process_image_parser.add_argument(
        '--max-size', type=float, default=None,
        help='Maximum file size in MB (enables compression mode)'
    )
    process_image_parser.add_argument(
        '--input', '-i', type=str, default=None,
        help='Input image file (for single file processing)'
    )
    process_image_parser.add_argument(
        '--input-dir', type=str, default='./input',
        help='Input directory for batch processing (default: ./input)'
    )
    process_image_parser.add_argument(
        '--output', '-o', type=str, default=None,
        help='Output filename (e.g., resized.png). Overrides --output-dir.'
    )
    process_image_parser.add_argument(
        '--output-dir', type=str, default='./output',
        help='Output directory for auto-named files (default: ./output)'
    )
    process_image_parser.set_defaults(func=cmd_process_image)

    # process-video command
    process_video_parser = subparsers.add_parser(
        'process-video',
        help='Video speed, zoom, resize, trim, and frame extraction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Speed adjustment
  semiautomatic process-video --speed 1.25                    # 1.25x speed
  semiautomatic process-video --speed 0.5                     # Half speed (slow motion)
  semiautomatic process-video --speed 10 --speed-ramp ease-out-in  # 10x with whip effect

  # Zoom effects
  semiautomatic process-video --zoom 100:150                  # Zoom from 100% to 150%
  semiautomatic process-video --zoomh 100:110 --zoomv 95:105  # Independent H/V zoom

  # Resize
  semiautomatic process-video --size 1080x1080                # Resize to square
  semiautomatic process-video --size 1920x1080 --fit crop     # Crop to fit

  # Trimming
  semiautomatic process-video --trim-start 2.5                # Remove first 2.5 seconds
  semiautomatic process-video --trim-end 3.0                  # Remove last 3 seconds

  # Frame extraction
  semiautomatic process-video --input video.mp4 --extract-frame last
  semiautomatic process-video --input video.mp4 --extract-time 5.5
        """
    )
    # Input/output
    process_video_parser.add_argument(
        '--input', '-i', type=str, default=None,
        help='Input video file (for single file processing)'
    )
    process_video_parser.add_argument(
        '-o', '--output', type=str, default=None,
        help='Output video file path (for single file processing with --input)'
    )
    process_video_parser.add_argument(
        '--input-dir', type=str, default='./input',
        help='Input directory for batch processing (default: ./input)'
    )
    process_video_parser.add_argument(
        '--output-dir', type=str, default='./output',
        help='Output directory (default: ./output)'
    )
    # Frame extraction
    process_video_parser.add_argument(
        '--extract-frame', type=str, default=None,
        help='Extract single frame: first, last, middle, or frame number (e.g., 10, -5)'
    )
    process_video_parser.add_argument(
        '--extract-time', type=float, default=None,
        help='Extract frame at specific timestamp (seconds)'
    )
    # Effects
    process_video_parser.add_argument(
        '--speed', type=float, default=1.0,
        help='Playback speed multiplier (default: 1.0)'
    )
    process_video_parser.add_argument(
        '--speed-ramp', type=str,
        choices=['ease-in-out', 'ease-out-in', 'ease-in', 'ease-in-cubic',
                 'ease-in-quartic', 'ease-in-quintic', 'ease-out'],
        default=None,
        help='Apply easing curve to speed changes'
    )
    process_video_parser.add_argument(
        '--zoom', type=str, default=None,
        help='Zoom range as START:END percentages (e.g., 100:150)'
    )
    process_video_parser.add_argument(
        '--zoomh', type=str, default=None,
        help='Horizontal zoom range as START:END percentages'
    )
    process_video_parser.add_argument(
        '--zoomv', type=str, default=None,
        help='Vertical zoom range as START:END percentages'
    )
    # Trimming
    process_video_parser.add_argument(
        '--trim-start', type=float, default=0.0,
        help='Seconds to trim from the start (default: 0.0)'
    )
    process_video_parser.add_argument(
        '--trim-end', type=float, default=0.0,
        help='Seconds to trim from the end (default: 0.0)'
    )
    # Resize
    process_video_parser.add_argument(
        '--size', type=str, default=None,
        help='Output dimensions as WIDTHxHEIGHT (e.g., 1920x1080)'
    )
    process_video_parser.add_argument(
        '--fit', type=str, choices=['stretch', 'crop', 'crop-max', 'pad'],
        default='stretch',
        help='How to fit video to target size (default: stretch)'
    )
    process_video_parser.add_argument(
        '--crop-align', type=str,
        choices=['center', 'left', 'right', 'top', 'bottom',
                 'topleft', 'topright', 'bottomleft', 'bottomright'],
        default='center',
        help='Crop alignment when using --fit crop (default: center)'
    )
    process_video_parser.add_argument(
        '--fps', type=int, default=None,
        help='Target frame rate (e.g., 24, 30, 60)'
    )
    process_video_parser.set_defaults(func=cmd_process_video)

    # generate-video command
    generate_video_parser = subparsers.add_parser(
        'generate-video',
        help='Generate videos with AI models (Kling, Seedance, Hailuo, WAN, Sora)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Models:
  FAL provider (default):
    kling1.5, kling1.6, kling2.0, kling2.1 (default), kling2.5, kling2.6
    klingo1, seedance1.0, hailuo2.0

  Wavespeed provider (--provider wavespeed):
    kling2.5-wavespeed, wan2.2, wan2.5, sora2

  Higgsfield provider (--provider higgsfield):
    higgsfield, higgsfield_lite, higgsfield_preview, higgsfield_turbo
    (supports --motion and --motion-strength)

Motion presets (Higgsfield only):
  zoom_in, zoom_out, dolly_in, dolly_out, crane_up, crane_down
  handheld, static, 360_orbit, bullet_time, catwalk, and 100+ more
  Use --list-motions to see all available motion presets

Examples:
  # Basic image-to-video
  semiautomatic generate-video --prompt "walking" --image cat.jpg

  # With Wavespeed provider
  semiautomatic generate-video --prompt "dancing" --image person.jpg --provider wavespeed --model wan2.5

  # With Higgsfield motion preset
  semiautomatic generate-video --prompt "dramatic reveal" --image portrait.jpg --provider higgsfield --motion zoom_in

  # Loop mode (same start and end image)
  semiautomatic generate-video --prompt "breathing" --image portrait.jpg --loop

  # List models
  semiautomatic generate-video --list-models
        """
    )
    generate_video_parser.add_argument(
        '--prompt', type=str,
        help='Text prompt describing the video motion'
    )
    generate_video_parser.add_argument(
        '-i', '--input', '--image', type=str, default=None, dest='image',
        help='Input image for image-to-video generation'
    )
    generate_video_parser.add_argument(
        '--tail-image', type=str, default=None,
        help='End image URL for video transitions (models that support it)'
    )
    generate_video_parser.add_argument(
        '--provider', type=str, default=None,
        help='Provider to use (default: fal)'
    )
    generate_video_parser.add_argument(
        '--model', type=str, default=None,
        help='Model to use (default: kling2.1)'
    )
    generate_video_parser.add_argument(
        '--duration', type=int, default=5,
        help='Video duration in seconds: 5 or 10 (default: 5)'
    )
    generate_video_parser.add_argument(
        '--negative-prompt', type=str, default=None,
        help='Things to avoid in the video'
    )
    generate_video_parser.add_argument(
        '--seed', type=int, default=None,
        help='Random seed for reproducibility'
    )
    generate_video_parser.add_argument(
        '--loop', action='store_true',
        help='Use input image as both start and end for looping effect'
    )
    generate_video_parser.add_argument(
        '--output', '-o', type=str, default=None,
        help='Output filename (e.g., cat.mp4). Overrides --output-dir.'
    )
    generate_video_parser.add_argument(
        '--output-dir', type=str, default='./output',
        help='Output directory for auto-named files (default: ./output)'
    )
    generate_video_parser.add_argument(
        '--list-models', action='store_true',
        help='List available video models and exit'
    )
    generate_video_parser.add_argument(
        '--list-motions', action='store_true',
        help='List available motion presets (Higgsfield) and exit'
    )
    # Higgsfield-specific options
    generate_video_parser.add_argument(
        '--motion', type=str, default=None,
        help='Motion preset for Higgsfield (e.g., zoom_in, dolly_out)'
    )
    generate_video_parser.add_argument(
        '--motion-strength', type=float, default=0.5,
        help='Motion intensity 0.0-1.0 for Higgsfield (default: 0.5)'
    )
    generate_video_parser.set_defaults(func=cmd_generate_video)

    # generate-image-prompt command
    generate_image_prompt_parser = subparsers.add_parser(
        'generate-image-prompt',
        help='Generate platform-specific image prompts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Platforms:
  flux        Direct, concise prompts for FLUX models (default)
  midjourney  Narrative prompts with technical parameters

Examples:
  # Basic usage (no schema)
  semiautomatic generate-image-prompt "person dancing at a rave"

  # With schema for styling
  semiautomatic generate-image-prompt "person dancing" --schema aesthetic.json

  # For Midjourney
  semiautomatic generate-image-prompt "portrait" --schema aesthetic.json --platform midjourney

  # Output to file
  semiautomatic generate-image-prompt "cyberpunk city" --output prompt.json
        """
    )
    generate_image_prompt_parser.add_argument(
        'intent', type=str,
        help='Description of what to generate (e.g., "person dancing at rave")'
    )
    generate_image_prompt_parser.add_argument(
        '--schema', type=str, default=None,
        help='Path to schema JSON file (e.g., aesthetic.json) for styling'
    )
    generate_image_prompt_parser.add_argument(
        '--platform', type=str, default='flux',
        choices=['flux', 'midjourney'],
        help='Target platform (default: flux)'
    )
    generate_image_prompt_parser.add_argument(
        '--output', '-o', type=str, default=None,
        help='Output JSON file path (prints to stdout if not specified)'
    )
    generate_image_prompt_parser.set_defaults(func=cmd_generate_image_prompt)

    # generate-video-prompt command
    generate_video_prompt_parser = subparsers.add_parser(
        'generate-video-prompt',
        help='Generate motion prompts from images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Video models:
  higgsfield  Concise motion prompts for Higgsfield (default)
  kling       Natural motion prompts for Kling
  generic     General purpose motion prompts

Examples:
  # Basic usage (no schema)
  semiautomatic generate-video-prompt --input portrait.jpg

  # With schema for motion styling
  semiautomatic generate-video-prompt --input portrait.jpg --schema aesthetic.json

  # For Kling model
  semiautomatic generate-video-prompt --input image.jpg --video-model kling

  # With motion preset (for Higgsfield)
  semiautomatic generate-video-prompt --input image.jpg --motion catwalk

  # Output to file
  semiautomatic generate-video-prompt --input image.jpg --output prompt.json
        """
    )
    generate_video_prompt_parser.add_argument(
        '--input', '-i', type=str, required=True,
        help='Input image file path'
    )
    generate_video_prompt_parser.add_argument(
        '--schema', type=str, default=None,
        help='Path to schema JSON file (e.g., aesthetic.json) for motion styling'
    )
    generate_video_prompt_parser.add_argument(
        '--video-model', type=str, default='higgsfield',
        choices=['higgsfield', 'kling', 'generic'],
        help='Target video model (default: higgsfield)'
    )
    generate_video_prompt_parser.add_argument(
        '--motion', type=str, default=None,
        help='Motion preset (for Higgsfield)'
    )
    generate_video_prompt_parser.add_argument(
        '--output', '-o', type=str, default=None,
        help='Output JSON file path (prints to stdout if not specified)'
    )
    generate_video_prompt_parser.set_defaults(func=cmd_generate_video_prompt)

    return parser


def main():
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        result = args.func(args)
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
