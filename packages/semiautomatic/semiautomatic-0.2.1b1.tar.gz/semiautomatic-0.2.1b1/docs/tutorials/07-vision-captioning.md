# Vision & Captioning

Understand images using AI vision models. Generate captions, descriptions, and answers to questions about images.

## Prerequisites

Set up your API key in `.env`:

```bash
FAL_KEY=your-fal-key
```

For captioning without an API key, install `gradio_client` to use Joy Caption Beta One:

```bash
pip install gradio_client
```

## Providers

| Provider | Model | Best For |
|----------|-------|----------|
| `fal` | Moondream 3 (default) | Captions + Q&A |
| `huggingface` | Joy Caption Beta One | Detailed captions (requires gradio_client) |

## Image Captioning

```python
from semiautomatic.lib.vision import get_caption

# Default (FAL + Moondream)
caption = get_caption("photo.jpg")
print(caption)

# Short caption
caption = get_caption("photo.jpg", length="short")

# Long, detailed caption
caption = get_caption("photo.jpg", length="long")
```

### Caption Lengths

| Length | Words | Use Case |
|--------|-------|----------|
| `short` | ~50 | Quick descriptions, prompts |
| `normal` | ~150 | Balanced detail (default) |
| `long` | ~300 | Full scene description |

### Using FAL/Moondream

```python
from semiautomatic.lib.vision import get_caption

# Specify provider
caption = get_caption("photo.jpg", provider="fal")

# With model
caption = get_caption("photo.jpg", provider="fal", model="moondream3")
```

## Quick Prompts

Get a short caption suitable for use as an image generation prompt:

```python
from semiautomatic.lib.vision import get_prompt

# Returns short caption, truncated if needed
prompt = get_prompt("photo.jpg")
print(prompt)  # "woman in red dress standing on beach at sunset"

# With max length
prompt = get_prompt("photo.jpg", max_length=100)
```

## Question Answering

Ask questions about an image (works best with FAL/Moondream):

```python
from semiautomatic.lib.vision import describe_image

# Ask a question
answer = describe_image("photo.jpg", "What colors are in this image?")
print(answer)

answer = describe_image("photo.jpg", "How many people are in the photo?")
print(answer)

answer = describe_image("photo.jpg", "What is the mood of this image?")
print(answer)
```

## Use with Upscaling

Auto-generate prompts for upscaling:

```bash
# CLI with --auto-prompt
sa upscale-image -i photo.jpg --auto-prompt
```

This uses the vision model to describe the image, then passes that description to guide the upscaling.

## Provider Comparison

### Moondream (FAL) - Default

- **Pros**: Fast, supports Q&A, good for short prompts
- **Cons**: Requires FAL_KEY
- **Best for**: Quick captions, answering questions, auto-prompt

### Joy Caption Beta One (HuggingFace)

- **Pros**: No API key needed, excellent detailed captions
- **Cons**: Requires `gradio_client` install, no Q&A support, slower, rate limited
- **Best for**: Generating detailed image descriptions

## Library Reference

```python
from semiautomatic.lib.vision import (
    get_caption,      # Generate caption
    get_prompt,       # Short caption for prompts
    describe_image,   # Q&A about image
    get_provider,     # Get provider instance
    list_providers,   # List available providers
)

# List providers
print(list_providers())  # ['fal', 'huggingface']

# Get provider directly
provider = get_provider("huggingface")
print(provider.list_models())  # ['joycaption']
```

## Workflow Examples

### Caption → Image Generation

```python
from semiautomatic.lib.vision import get_prompt
from semiautomatic.image import generate_image

# Describe existing image
prompt = get_prompt("reference.jpg")

# Generate similar image
result = generate_image(prompt + ", oil painting style")
```

### Caption → Video Motion

```python
from semiautomatic.lib.vision import get_caption
from semiautomatic.prompt import generate_video_prompt

# Get description of scene
caption = get_caption("scene.jpg", length="short")

# Generate motion prompt
motion = generate_video_prompt("scene.jpg")
```

### Batch Captioning

```python
from pathlib import Path
from semiautomatic.lib.vision import get_caption

images = Path("./images").glob("*.jpg")
for img in images:
    caption = get_caption(img, length="short")
    print(f"{img.name}: {caption}")
```

## Tips

1. **Use Joy Caption for detail** - Better at describing nuanced scenes
2. **Use Moondream for Q&A** - Can answer specific questions
3. **Short for prompts** - Use `length="short"` when generating prompts
4. **Batch with care** - HuggingFace Spaces have rate limits

## Start Over

- [Getting Started](01-getting-started.md) - Back to the beginning
