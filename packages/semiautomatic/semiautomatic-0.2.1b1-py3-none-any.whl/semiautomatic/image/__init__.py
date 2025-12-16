"""
semiautomatic.image - Image processing, generation, and upscaling utilities.

Processing API:
    compress_for_api    Compress image for size-limited APIs (e.g., Claude Vision)
    compress_to_size    Progressive compression with full control
    process_single_image    Resize, convert, or compress a single image

Generation API:
    generate_image      Generate images from text prompts
    image_to_image      Transform images with AI

Upscaling API:
    upscale_image       Upscale images with AI (2x/4x)

Data classes:
    CompressionResult   Result of compression operation
    SizeSpec           Parsed size specification
    GenerationResult   Result of image generation
    ImageResult        Single generated image
    ImageSize          Image dimensions
    LoRASpec           LoRA specification
    UpscaleResult      Result of upscale operation
    UpscaleSettings    Settings for upscaling

Providers:
    get_provider        Get an image generation provider
    list_providers      List available providers
    list_all_models     List all models across providers
"""

from semiautomatic.image.process import (
    # Main functions
    compress_for_api,
    compress_to_size,
    process_single_image,
    # Utilities
    parse_size,
    calculate_dimensions,
    find_images,
    get_unique_path,
    # Data classes
    CompressionResult,
    SizeSpec,
    # Constants
    DEFAULT_MAX_SIZE_BYTES,
    IMAGE_EXTENSIONS,
)

from semiautomatic.image.generate import generate_image, image_to_image

from semiautomatic.image.upscale import upscale_image

from semiautomatic.image.providers.freepik import (
    UpscaleResult,
    UpscaleSettings,
    ScaleFactor,
    UpscaleEngine,
    OptimizedFor,
)

from semiautomatic.image.providers import (
    get_provider,
    list_providers,
    list_all_models,
    GenerationResult,
    ImageResult,
    ImageSize,
    LoRASpec,
    IMAGE_SIZE_PRESETS,
    RecraftControls,
)

__all__ = [
    # Processing
    'compress_for_api',
    'compress_to_size',
    'process_single_image',
    'parse_size',
    'calculate_dimensions',
    'find_images',
    'get_unique_path',
    'CompressionResult',
    'SizeSpec',
    'DEFAULT_MAX_SIZE_BYTES',
    'IMAGE_EXTENSIONS',
    # Generation
    'generate_image',
    'image_to_image',
    'get_provider',
    'list_providers',
    'list_all_models',
    'GenerationResult',
    'ImageResult',
    'ImageSize',
    'LoRASpec',
    'IMAGE_SIZE_PRESETS',
    'RecraftControls',
    # Upscaling
    'upscale_image',
    'UpscaleResult',
    'UpscaleSettings',
    'ScaleFactor',
    'UpscaleEngine',
    'OptimizedFor',
]
