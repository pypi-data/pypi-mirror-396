# Prompt Generation

Generate detailed prompts for image and video generation using AI. Transform simple descriptions into rich, descriptive prompts.

## Prerequisites

Set up your API key in `.env`:

```bash
ANTHROPIC_API_KEY=your-anthropic-key
```

## Image Prompt Generation

Transform a simple idea into a detailed image prompt:

```bash
# Basic usage
sa generate-image-prompt "person dancing at a rave"

# Output: "figure moving through crowded dance floor, neon lights casting
# colorful shadows, arms raised, euphoric expression, fog machine haze,
# dynamic motion blur"
```

### Schema-Based Styling

Use a JSON schema to apply consistent aesthetic styling:

```bash
sa generate-image-prompt "person dancing" --schema aesthetic.json
```

Example `aesthetic.json`:

```json
{
  "name": "Neon Rave",
  "description": "High-energy rave aesthetic with neon colors",
  "mood": ["euphoric", "energetic", "intense"],
  "elements": {
    "lighting": ["neon", "strobes", "UV blacklight"]
  },
  "props": {
    "examples": ["glow sticks", "LED accessories", "fog machine"]
  }
}
```

The schema guides the AI to incorporate specific visual elements, mood, and style.

### Output to File

```bash
# Save as JSON
sa generate-image-prompt "portrait photo" -o prompt.json
```

Output format:

```json
{
  "prompt": "the generated prompt text",
  "schema_name": "Neon Rave"
}
```

## Video Prompt Generation

Generate motion prompts from an image:

```bash
# Basic usage - analyzes image and generates motion prompt
sa generate-video-prompt -i portrait.jpg

# Output: "figure turns head slowly toward camera, subtle smile forming"
```

### With Motion Preset

Pair with Higgsfield motion presets:

```bash
sa generate-video-prompt -i portrait.jpg --motion catwalk
```

### Schema-Based Motion

Use a schema to define motion philosophy:

```bash
sa generate-video-prompt -i photo.jpg --schema aesthetic.json
```

Example schema with motion:

```json
{
  "name": "Cinematic",
  "motion_philosophy": {
    "speed": "slow and deliberate",
    "quality": "smooth, controlled",
    "camera_behavior": "subtle push-in",
    "preferred_movements": ["head turns", "eye contact", "subtle gestures"]
  }
}
```

## Library Usage

```python
from semiautomatic.prompt import generate_image_prompt, generate_video_prompt

# Image prompt
result = generate_image_prompt("person dancing at a rave")
print(result.prompt)

# With schema
result = generate_image_prompt(
    "portrait in style",
    schema_path="aesthetic.json"
)

# Video prompt from image
result = generate_video_prompt("portrait.jpg")
print(result.prompt)

# With schema and motion preset
result = generate_video_prompt(
    "portrait.jpg",
    schema_path="aesthetic.json",
    motion_preset="catwalk"
)
```

## Workflow Example

Generate an image, then create a video prompt for it:

```bash
# 1. Generate image prompt
sa generate-image-prompt "woman at neon rave" -o prompt.json

# 2. Generate image using the prompt (copy from prompt.json)
sa generate-image --prompt "figure dancing under neon lights..."

# 3. Generate video motion prompt from the image
sa generate-video-prompt -i output/generated_image.png

# 4. Generate video using the motion prompt
sa generate-video --prompt "figure sways to music, head turns..." \
  --image output/generated_image.png
```

## Tips

1. **Keep input simple** - Let the AI expand "cat on windowsill" into a detailed prompt
2. **Use schemas** - Consistent style across multiple generations
3. **Video prompts** - Focus on motion, not scene description (the image already has the scene)

## Next Steps

- [Vision & Captioning](07-vision-captioning.md) - Understand and describe images with AI
