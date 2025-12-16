# Getting Started

This tutorial walks you through installing semiautomatic and running your first commands.

## Installation

```bash
pip install semiautomatic
```

Verify the installation:

```bash
sa --version
```

(`sa` is the short alias for `semiautomatic`)

## System Requirements

**FFmpeg** (optional, for video processing):

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows - download from https://ffmpeg.org/download.html
```

Only needed if you'll use `process-video` for speed/zoom/trim effects. Not required for video generation.

## Environment Setup

Create a `.env` file in your project directory with API keys for the providers you want to use:

```bash
# Image generation (pick at least one)
FAL_KEY=your-fal-key              # FLUX, Qwen, WAN via FAL
RECRAFT_API_KEY=your-recraft-key  # Recraft v3 direct API

# Video generation (pick at least one)
FAL_KEY=your-fal-key              # Kling, Seedance, Hailuo via FAL
WAVESPEED_API_KEY=your-wavespeed-key
HIGGSFIELD_API_KEY=your-higgsfield-key
HIGGSFIELD_SECRET=your-higgsfield-secret

# Image upscaling (Magnific via Freepik)
FREEPIK_API_KEY=your-freepik-key

# Prompt generation (pick at least one)
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key

# Vision/captioning
OPENAI_API_KEY=your-openai-key
```

**Minimum setup**: FAL_KEY gives you both image and video generation with the default providers.

Get your API keys:
- **FAL**: https://fal.ai/dashboard/keys
- **Anthropic**: https://console.anthropic.com/
- **Recraft**: https://www.recraft.ai/
- **Freepik**: https://www.freepik.com/api
- **Wavespeed**: https://wavespeed.ai/
- **Higgsfield**: https://higgsfield.ai/
- **OpenAI**: https://platform.openai.com/api-keys

## Your First Workflow

Let's chain a few commands together to see how semiautomatic works.

> **Keys needed**: This workflow uses `FAL_KEY` (image/video generation) and `FREEPIK_API_KEY` (upscaling). Skip step 2 if you only have FAL set up.

**Step 1: Generate an image**

```bash
sa generate-image --prompt "a cat sitting on a windowsill, golden hour lighting" -o cat.png
```

The `-o` flag gives us a predictable filename: `cat.png`.

**Step 2: Upscale it**

The image looks great, but we want more detail. Let's upscale it 2x:

```bash
sa upscale-image -i cat.png -o cat_2x.png
```

Now we have `cat_2x.png` at twice the resolution.

**Step 3: Compress for API use**

Let's compress for faster uploads and smaller API payloads:

```bash
sa process-image -i cat_2x.png --max-size 1 -o cat_compressed.jpg
```

Note: `--max-size` outputs JPEG for best compression.

**Step 4: Generate a video**

Let's bring our cat to life:

```bash
sa generate-video --prompt "the cat turns its head and blinks slowly" --image cat_compressed.jpg -o cat.mp4
```

Done! From prompt to video in four commands - all with predictable filenames you control.

### Get Help

```bash
sa --help                    # List all commands
sa generate-image --help     # Details on a specific command
```

## Tips

When you don't specify `-i`, semiautomatic looks for input files in `input/`. When you don't specify `-o`, generated files save to `output/`. These directories fill up fast with media files, so consider adding them to your `.gitignore`:

```gitignore
input/
output/
```

## Using as a Library

```python
from semiautomatic.image import generate_image, compress_for_api
from semiautomatic.video import generate_video

# Generate an image
result = generate_image("a cat on a windowsill")
print(result.images[0].path)

# Compress for API
img_bytes = compress_for_api("photo.jpg")

# Generate a video
result = generate_video("camera zooms in", input_image="photo.jpg")
print(result.videos[0].path)
```

## Next Steps

- [Image Generation](02-image-generation.md) - FLUX, Recraft, LoRA support
- [Video Generation](03-video-generation.md) - Kling, WAN, Higgsfield motion presets
- [Image Upscaling](04-image-upscaling.md) - AI upscaling with Freepik
- [Video Processing](05-video-processing.md) - Speed, zoom, resize, trim
- [Prompt Generation](06-prompt-generation.md) - AI-powered prompt creation
- [Vision & Captioning](07-vision-captioning.md) - Image understanding
