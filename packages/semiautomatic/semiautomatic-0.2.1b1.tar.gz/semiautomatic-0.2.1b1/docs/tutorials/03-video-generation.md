# Video Generation

Generate videos using Kling, Seedance, Hailuo (via FAL), WAN/Sora (via Wavespeed), or Higgsfield with motion presets.

## Prerequisites

Set up your API keys in `.env`:

```bash
FAL_KEY=your-fal-key              # For Kling, Seedance, Hailuo
WAVESPEED_API_KEY=your-wavespeed-key  # For WAN, Sora
HIGGSFIELD_API_KEY=your-higgsfield-key  # For Higgsfield
HIGGSFIELD_SECRET=your-higgsfield-secret
```

## Basic Video Generation

### Image-to-Video

```bash
# Basic i2v with Kling
sa generate-video --prompt "the cat turns its head" --image cat.jpg

# Specify model
sa generate-video --prompt "walking forward" --image person.jpg --model kling2.6

# Longer duration (5s or 10s)
sa generate-video --prompt "dancing" --image dancer.jpg --duration 10
```

## Providers and Models

### FAL Provider (default)

```bash
sa generate-video --prompt "motion" --image photo.jpg --provider fal --model kling2.6
```

| Model | Description |
|-------|-------------|
| `kling2.6` | Latest Kling (default) |
| `kling2.5` | Kling 2.5 |
| `kling2.1` | Kling 2.1 |
| `kling2.0` | Kling 2.0 |
| `klingo1` | Kling O1 |
| `seedance1.0` | Seedance |
| `hailuo2.0` | Hailuo/MiniMax |

### Wavespeed Provider

```bash
sa generate-video --prompt "dancing" --image person.jpg --provider wavespeed --model wan2.5
```

| Model | Description |
|-------|-------------|
| `kling2.5-wavespeed` | Kling via Wavespeed |
| `wan2.2` | WAN 2.2 |
| `wan2.5` | WAN 2.5 |
| `sora2` | Sora 2 |

### Higgsfield Provider

Higgsfield offers **120+ motion presets** for cinematic camera movements and effects.

```bash
# Basic with motion preset
sa generate-video --prompt "dramatic reveal" --image portrait.jpg \
  --provider higgsfield --motion zoom_in

# Adjust motion intensity (0.0-1.0)
sa generate-video --prompt "walking" --image person.jpg \
  --provider higgsfield --motion dolly_out --motion-strength 0.7
```

| Model | Description |
|-------|-------------|
| `higgsfield` | Standard quality |
| `higgsfield_lite` | Faster, lighter |
| `higgsfield_preview` | Quick preview |
| `higgsfield_turbo` | Fastest |

### Motion Presets

List all available presets:

```bash
sa generate-video --list-motions
```

Common presets:

| Category | Presets |
|----------|---------|
| **Camera** | `zoom_in`, `zoom_out`, `dolly_in`, `dolly_out`, `crane_up`, `crane_down` |
| **Movement** | `pan_left`, `pan_right`, `tilt_up`, `tilt_down`, `handheld`, `static` |
| **Cinematic** | `360_orbit`, `bullet_time`, `dramatic_zoom` |
| **Character** | `catwalk`, `head_turn`, `breathing` |

## Advanced Options

### Loop Mode

Creates seamless looping videos by using the input image as both start and end frame:

```bash
sa generate-video --prompt "breathing animation" --image portrait.jpg --loop
```

Requires tail image support. If your model doesn't support it (e.g., kling2.6), semiautomatic will auto-switch to kling2.5.

**Models with loop/tail support:** kling1.5, kling1.6, kling2.1, kling2.5, klingo1, seedance1.0

### Tail Image

Specify an end frame for transitions:

```bash
sa generate-video --prompt "morph between faces" \
  --image start.jpg --tail-image end.jpg --model kling2.5
```

Same model support as loop mode above.

### Negative Prompt

Exclude unwanted elements:

```bash
sa generate-video --prompt "person walking" --image photo.jpg \
  --negative-prompt "blur, distortion, artifacts"
```

## Library Usage

```python
from semiautomatic.video import generate_video

# Basic i2v
result = generate_video("cat turns head", input_image="cat.jpg")
print(result.videos[0].path)

# With Higgsfield motion
result = generate_video(
    "dramatic reveal",
    input_image="portrait.jpg",
    provider="higgsfield",
    motion="zoom_in",
    motion_strength=0.7
)

# Loop mode
result = generate_video(
    "breathing",
    input_image="portrait.jpg",
    loop=True
)

# Wavespeed with WAN
result = generate_video(
    "dancing",
    input_image="person.jpg",
    provider="wavespeed",
    model="wan2.5"
)
```

## Tips

1. **Start with kling2.6** - Best overall quality
2. **Use motion presets** - Higgsfield presets give cinematic results
3. **Keep prompts short** - Focus on the motion, not scene description
4. **5s duration first** - Test before committing to 10s (costs more)
5. **Loop mode** - Great for cinemagraphs and seamless animations

## Next Steps

- [Image Upscaling](04-image-upscaling.md) - Enhance image resolution with AI
