# Image Generation

Generate images using multiple AI models and providers. This tutorial covers text-to-image, image-to-image, LoRA support, and style controls.

## Prerequisites

Set up your API keys in `.env`:

```bash
FAL_KEY=your-fal-key           # For FLUX models
RECRAFT_API_KEY=your-recraft-key  # For Recraft
```

## Basic Image Generation

```bash
# Simple text-to-image (uses flux-dev by default)
sa generate-image --prompt "a cat sitting on a windowsill"

# Try different models - easily compare results
sa generate-image --prompt "portrait photo" --model flux-dev
sa generate-image --prompt "portrait photo" --model qwen
sa generate-image --prompt "portrait photo" --model wan-22

# Different sizes (presets)
sa generate-image --prompt "landscape" --size landscape_16_9
sa generate-image --prompt "portrait" --size portrait_4_3

# Custom dimensions
sa generate-image --prompt "cinematic" --size 1280x720
sa generate-image --prompt "social post" --size 1080x1080
```

### Available Models

| Model | Description | LoRA Support |
|-------|-------------|--------------|
| `flux-dev` | Balanced quality/speed (default) | No |
| `flux-schnell` | Ultra-fast | No |
| `flux-pro` | Highest quality | No |
| `flux-krea` | Krea variant | Yes |
| `qwen` | Qwen image model | Yes |
| `wan-22` | WAN 2.2 14B | Yes |

### Size Options

Use presets or custom `WIDTHxHEIGHT`:

| Preset | Dimensions |
|--------|------------|
| `square` | 1024x1024 |
| `square_hd` | 1536x1536 |
| `portrait_4_3` | 768x1024 |
| `portrait_16_9` | 576x1024 |
| `landscape_4_3` | 1024x768 (default) |
| `landscape_16_9` | 1024x576 |

Custom dimensions: `--size 1920x1080`, `--size 800x600`, etc.

## Using LoRA

LoRA (Low-Rank Adaptation) lets you apply custom trained models. Requires `flux-krea`, `qwen`, or `wan-22`.

```bash
# Single LoRA (local file)
sa generate-image --prompt "portrait" --model flux-krea --lora path/to/lora.safetensors

# LoRA with custom weight (0.0-1.0)
sa generate-image --prompt "portrait" --model flux-krea --lora path/to/lora.safetensors:0.8

# LoRA from URL
sa generate-image --prompt "portrait" --model flux-krea --lora https://example.com/lora.safetensors:0.8

# Multiple LoRAs
sa generate-image --prompt "portrait" --model flux-krea \
  --lora lora1.safetensors:0.7 \
  --lora lora2.safetensors:0.5
```

## Recraft Provider

Recraft offers different artistic styles and image-to-image transformation.

```bash
# Text-to-image with style
sa generate-image --provider recraft --prompt "cyberpunk city" --style digital_illustration

# Realistic photo
sa generate-image --provider recraft --prompt "product photo" --style realistic_image

# Vector illustration
sa generate-image --provider recraft --prompt "logo design" --style vector_illustration
```

### Recraft Styles

| Style | Description |
|-------|-------------|
| `realistic_image` | Photorealistic (default) |
| `digital_illustration` | Digital art style |
| `vector_illustration` | Vector graphics |
| `logo_raster` | Logo design |
| `any` | Auto-detect |

### Image-to-Image

Transform an existing image with Recraft:

```bash
# Basic i2i
sa generate-image --provider recraft \
  --input-image photo.jpg \
  --prompt "make it an illustration"

# Control transformation strength (0.0-1.0)
sa generate-image --provider recraft \
  --input-image photo.jpg \
  --prompt "watercolor style" \
  --strength 0.7
```

### Advanced Recraft Options

```bash
# Artistic level (0-5, higher = more stylized)
sa generate-image --provider recraft \
  --prompt "portrait" \
  --style digital_illustration \
  --artistic-level 3

# Color palette
sa generate-image --provider recraft \
  --prompt "abstract art" \
  --colors "#FF0000" "#00FF00" "#0000FF"

# Background color
sa generate-image --provider recraft \
  --prompt "product on background" \
  --background-color "#FFFFFF"
```

## Library Usage

```python
from semiautomatic.image import generate_image, image_to_image

# Basic generation
result = generate_image("a cat on a windowsill", model="flux-dev")
print(result.images[0].path)

# With LoRA
result = generate_image(
    "portrait in custom style",
    model="flux-krea",
    loras=["style.safetensors:0.8"]
)

# Recraft with style
result = generate_image(
    "cyberpunk city",
    provider="recraft",
    style="digital_illustration"
)

# Image-to-image
result = image_to_image(
    "photo.jpg",
    "make it a watercolor painting",
    strength=0.7
)
```

## Tips

1. **Start with flux-dev** - Good balance of quality and speed
2. **Use size presets** - Optimized for each model
3. **LoRA weights** - Start at 0.7-0.8, adjust based on results
4. **Recraft strength** - Lower values (0.3-0.5) for subtle changes, higher (0.7-0.9) for dramatic transformation

## Next Steps

- [Video Generation](03-video-generation.md) - Create videos from images
