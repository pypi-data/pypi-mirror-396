# Video Processing

Process videos with speed adjustments, zoom effects, resizing, trimming, and frame extraction. All processing uses FFmpeg under the hood.

## Prerequisites

FFmpeg must be installed on your system:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Speed Adjustment

```bash
# Speed up 1.5x
sa process-video -i video.mp4 --speed 1.5

# Slow motion (0.5x)
sa process-video -i video.mp4 --speed 0.5

# Fast forward (10x)
sa process-video -i video.mp4 --speed 10
```

### Speed with Easing Curves

Apply smooth acceleration/deceleration:

```bash
# Ease in-out (slow start and end)
sa process-video -i video.mp4 --speed 2 --speed-ramp ease-in-out

# Whip effect (fast middle, slow ends)
sa process-video -i video.mp4 --speed 10 --speed-ramp ease-out-in

# Accelerate
sa process-video -i video.mp4 --speed 3 --speed-ramp ease-in

# Decelerate
sa process-video -i video.mp4 --speed 3 --speed-ramp ease-out
```

| Curve | Effect |
|-------|--------|
| `ease-in` | Starts slow, accelerates |
| `ease-out` | Starts fast, decelerates |
| `ease-in-out` | Slow start and end |
| `ease-out-in` | Whip effect (fast middle) |
| `ease-in-cubic` | Stronger ease-in |
| `ease-in-quartic` | Even stronger ease-in |
| `ease-in-quintic` | Strongest ease-in |

## Zoom Effects

```bash
# Zoom from 100% to 150%
sa process-video -i video.mp4 --zoom 100:150

# Zoom out (150% to 100%)
sa process-video -i video.mp4 --zoom 150:100
```

### Independent Horizontal/Vertical Zoom

```bash
# Horizontal zoom only
sa process-video -i video.mp4 --zoomh 100:120

# Vertical zoom only
sa process-video -i video.mp4 --zoomv 100:110

# Combined (different H/V)
sa process-video -i video.mp4 --zoomh 100:120 --zoomv 95:105
```

## Resizing

```bash
# Resize to exact dimensions
sa process-video -i video.mp4 --size 1920x1080

# Square (stretches to fit)
sa process-video -i video.mp4 --size 1080x1080
```

### Fit Modes

Control how the video fits the target dimensions:

```bash
# Stretch to fill (may distort)
sa process-video -i video.mp4 --size 1080x1080 --fit stretch

# Scale and crop (no distortion, clips edges)
sa process-video -i video.mp4 --size 1080x1080 --fit crop

# Scale and letterbox (no distortion, adds black bars)
sa process-video -i video.mp4 --size 1080x1080 --fit pad
```

| Mode | Description |
|------|-------------|
| `stretch` | Stretch to fill (default) |
| `crop` | Scale and crop to fill |
| `crop-max` | Maximum crop |
| `pad` | Scale and add letterbox/pillarbox |

### Crop Alignment

When using `--fit crop`, control which part is kept:

```bash
# Keep center (default)
sa process-video -i video.mp4 --size 1080x1080 --fit crop --crop-align center

# Keep top
sa process-video -i video.mp4 --size 1080x1080 --fit crop --crop-align top

# Keep bottom-right
sa process-video -i video.mp4 --size 1080x1080 --fit crop --crop-align bottomright
```

Options: `center`, `left`, `right`, `top`, `bottom`, `topleft`, `topright`, `bottomleft`, `bottomright`

## Trimming

```bash
# Remove first 2.5 seconds
sa process-video -i video.mp4 --trim-start 2.5

# Remove last 3 seconds
sa process-video -i video.mp4 --trim-end 3.0

# Both
sa process-video -i video.mp4 --trim-start 1.0 --trim-end 2.0
```

## Frame Rate

```bash
# Convert to 30fps
sa process-video -i video.mp4 --fps 30

# High frame rate
sa process-video -i video.mp4 --fps 60
```

## Frame Extraction

Extract single frames as images:

```bash
# First frame
sa process-video -i video.mp4 --extract-frame first

# Last frame
sa process-video -i video.mp4 --extract-frame last

# Middle frame
sa process-video -i video.mp4 --extract-frame middle

# Specific frame number
sa process-video -i video.mp4 --extract-frame 10

# Negative index (from end)
sa process-video -i video.mp4 --extract-frame -5

# Extract at timestamp (seconds)
sa process-video -i video.mp4 --extract-time 5.5
```

## Combining Effects

Apply multiple effects in one command:

```bash
sa process-video -i video.mp4 \
  --speed 1.5 \
  --speed-ramp ease-in-out \
  --zoom 100:120 \
  --trim-start 1.0 \
  --size 1080x1080 \
  --fit crop
```

## Batch Processing

Process all videos in a directory:

```bash
sa process-video --input-dir ./videos --speed 2
```

## Library Usage

```python
from pathlib import Path
from semiautomatic.video import process_video, extract_frame_from_video

# Basic processing
output = process_video(
    Path("input.mp4"),
    Path("./output"),
    speed=1.5
)

# With effects
output = process_video(
    Path("input.mp4"),
    Path("./output"),
    speed=2.0,
    speed_ramp="ease-in-out",
    zoom_start=100,
    zoom_end=150,
    size=(1080, 1080),
    fit="crop"
)

# Extract frame
frame = extract_frame_from_video(
    Path("video.mp4"),
    Path("./output"),
    frame_position="last"
)
```

## Tips

1. **Whip effect** - Use `--speed 10 --speed-ramp ease-out-in` for dramatic transitions
2. **Subtle zoom** - 100:110 or 100:105 for Ken Burns effect
3. **Frame extraction** - Use `--extract-frame last` to get the final frame of AI-generated videos

## Next Steps

- [Prompt Generation](06-prompt-generation.md) - Generate AI-optimized prompts
