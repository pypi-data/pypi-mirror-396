"""
Video prompt generation.

Generates motion prompts for video generation from an image, optionally styled
by a schema (aesthetic JSON file).

Library usage:
    from semiautomatic.prompt import generate_video_prompt

    # Basic usage (no schema)
    result = generate_video_prompt("image.jpg")

    # With schema for motion styling
    result = generate_video_prompt(
        "image.jpg",
        schema_path="path/to/aesthetic.json",
        video_model="higgsfield"
    )

CLI usage:
    semiautomatic generate-video-prompt --input image.jpg
    semiautomatic generate-video-prompt --input image.jpg --schema aesthetic.json
    semiautomatic generate-video-prompt --input image.jpg --schema aesthetic.json --video-model kling
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from semiautomatic.lib.llm import complete_with_vision
from semiautomatic.prompt.models import VIDEO_MODEL_CONFIGS


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class VideoPromptResult:
    """Result from video prompt generation."""

    prompt: str
    video_model: str
    input_image: str
    schema_name: Optional[str] = None
    motion_preset: Optional[str] = None
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# System Prompt Builders
# ---------------------------------------------------------------------------

def _build_generic_system_prompt(video_model: str) -> str:
    """Build a generic system prompt when no schema is provided."""
    config = VIDEO_MODEL_CONFIGS.get(video_model, VIDEO_MODEL_CONFIGS["generic"])
    max_words = config["max_words"]

    return f"""You write SHORT video prompts that describe simple human movements and emotions.

RULES:
- {max_words} words maximum
- Use simple, direct language
- Focus on what the person DOES and FEELS
- No aesthetic jargon (no "neon trails," "UV glow," "stroboscopic")
- Natural, casual tone

STRUCTURE:
The [person] [action]. [unexpected detail or emotion shift].

GOOD EXAMPLES:
- "The woman taps her fingers on her face and widens her gaze. Her mouth chomps."
- "The woman dances erratically, while the screen strobes behind her."
- "The man makes jittery robotic dance movements while nodding his head in intense pain."
- "They look at each other and become suddenly horrified, then scream."

BAD EXAMPLES (too flowery):
- "The raver bounces with euphoric smile frozen at peak intensity as neon trails follow movements"
- "Kandi bracelets multiply up their arms in waves with UV glow intensifying"

YOUR TASK:
Write ONE simple prompt ({max_words} words max) describing movement and emotion. Be direct and concrete."""


def _build_schema_system_prompt(schema: dict, video_model: str) -> str:
    """Build a system prompt based on schema (aesthetic) data."""
    config = VIDEO_MODEL_CONFIGS.get(video_model, VIDEO_MODEL_CONFIGS["generic"])
    max_words = config["max_words"]

    schema_name = schema.get('name', 'Custom')
    mood = ', '.join(schema.get('mood', []))

    # Motion philosophy
    motion = schema.get('motion_philosophy', {})
    motion_speed = motion.get('speed', 'natural paced')
    motion_quality = motion.get('quality', 'smooth natural movement')
    camera_behavior = motion.get('camera_behavior', 'static framing')
    preferred_movements = ', '.join(motion.get('preferred_movements', []))

    # Video canonical examples
    video_examples = schema.get('video_canonical_examples', [])
    examples_text = ""
    if video_examples:
        examples_list = '\n'.join([f'- "{ex}"' for ex in video_examples])
        examples_text = f"\n\nGOOD EXAMPLES (from this style):\n{examples_list}"
    else:
        examples_text = "\n\nNOTE: No video examples defined. Use motion_philosophy to guide prompts."

    if video_model == "higgsfield":
        return f"""You generate concise motion prompts for Higgsfield video generation using the {schema_name} style.

STYLE OVERVIEW:
- Mood: {mood}
- Motion speed: {motion_speed}
- Motion quality: {motion_quality}
- Camera behavior: {camera_behavior}
- Preferred movements: {preferred_movements}{examples_text}

CRITICAL RULES:

1. **BE EXTREMELY CONCISE**
   - Maximum {max_words} words total
   - Focus on PRIMARY motion action only
   - Describe what moves and how
   - Natural, direct language

2. **STRUCTURE**
   - Start with subject: who/what is moving
   - Add primary motion: the main action/movement
   - Optional: brief motion quality
   - DO NOT describe static details

3. **MOTION FOCUS**
   - Describe movement, not composition
   - Use active verbs: walks, turns, tilts, glides, struts
   - Capture energy and pace: fast, slow, smooth, sharp

GOOD EXAMPLES:
- "character walks toward camera with confident stride"
- "figure turns head sharply, lips pursed"
- "subject struts down path like a runway model"

OUTPUT: Simple motion description, {max_words} words max."""

    elif video_model == "kling":
        return f"""You generate natural motion prompts for Kling video generation using the {schema_name} style.

STYLE OVERVIEW:
- Mood: {mood}
- Motion speed: {motion_speed}
- Motion quality: {motion_quality}
- Camera behavior: {camera_behavior}
- Preferred movements: {preferred_movements}{examples_text}

CRITICAL RULES:

1. **NATURAL AND DIRECT**
   - Maximum {max_words} words total
   - Describe motion naturally and clearly
   - Simple, conversational language

2. **STRUCTURE**
   - Start with subject: who/what is in motion
   - Describe the movement: action, direction, quality
   - Include motion characteristics: speed, smoothness

3. **MOTION DESCRIPTION**
   - Active verbs for movement
   - Capture pace and energy
   - Match style's motion philosophy

GOOD EXAMPLES:
- "woman walks briskly down beach, confident catwalk energy"
- "figure glides smoothly toward camera, turning head sharply"
- "character struts forward with swaying motion, fierce expression"

OUTPUT: Natural motion description, {max_words} words max."""

    else:  # generic
        return f"""You generate motion prompts for video generation using the {schema_name} style.

STYLE OVERVIEW:
- Mood: {mood}
- Motion speed: {motion_speed}
- Motion quality: {motion_quality}
- Preferred movements: {preferred_movements}{examples_text}

CRITICAL RULES:
- Maximum {max_words} words total
- Focus on motion and action
- Use the style's motion characteristics
- Be concise and direct

OUTPUT: Motion description, {max_words} words max."""


# ---------------------------------------------------------------------------
# Image Encoding
# ---------------------------------------------------------------------------

def _encode_image_for_vision(image_path: Path) -> tuple[str, str]:
    """Encode image for vision API. Returns (base64_data, media_type)."""
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    extension = image_path.suffix.lower().lstrip('.')
    media_type_map = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    media_type = media_type_map.get(extension, 'image/jpeg')

    return image_data, media_type


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_video_prompt(
    image_path: str | Path,
    *,
    schema_path: Optional[str | Path] = None,
    video_model: str = "higgsfield",
    motion_preset: Optional[str] = None,
    model: Optional[str] = None,
) -> VideoPromptResult:
    """
    Generate a motion prompt for video generation from an image.

    Args:
        image_path: Path to the input image.
        schema_path: Optional path to schema JSON (e.g., aesthetic.json).
        video_model: Target video model - "higgsfield", "kling", or "generic".
        motion_preset: Optional motion preset (for Higgsfield).
        model: LLM model to use (default: provider default).

    Returns:
        VideoPromptResult with generated prompt and metadata.

    Examples:
        # Basic usage
        result = generate_video_prompt("portrait.jpg")
        print(result.prompt)

        # With schema
        result = generate_video_prompt(
            "portrait.jpg",
            schema_path="aesthetic.json",
            video_model="higgsfield",
            motion_preset="catwalk"
        )
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Load schema if provided
    schema = None
    if schema_path:
        schema_path = Path(schema_path)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)

    # Build system prompt
    if schema:
        system_prompt = _build_schema_system_prompt(schema, video_model)
    else:
        system_prompt = _build_generic_system_prompt(video_model)

    # Encode image for vision
    image_data, media_type = _encode_image_for_vision(image_path)

    # Build vision message
    config = VIDEO_MODEL_CONFIGS.get(video_model, VIDEO_MODEL_CONFIGS["generic"])
    max_words = config["max_words"]

    messages = [{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_data,
                }
            },
            {
                "type": "text",
                "text": f"Write a short video prompt ({max_words} words max)."
            }
        ]
    }]

    # Generate prompt via LLM vision
    response = complete_with_vision(
        messages,
        system=system_prompt,
        model=model,
        max_tokens=256,
        temperature=1.0,
    )

    prompt = response.strip()

    return VideoPromptResult(
        prompt=prompt,
        video_model=video_model,
        input_image=str(image_path),
        schema_name=schema.get('name') if schema else None,
        motion_preset=motion_preset,
        metadata={
            "has_schema": schema is not None,
        }
    )


# ---------------------------------------------------------------------------
# CLI Handler
# ---------------------------------------------------------------------------

def run_generate_video_prompt(args) -> bool:
    """CLI handler for generate-video-prompt command."""
    from semiautomatic.lib.logging import log_info, log_error

    if not args.input:
        log_error("Input image is required (--input)")
        return False

    try:
        result = generate_video_prompt(
            args.input,
            schema_path=args.schema,
            video_model=args.video_model,
            motion_preset=args.motion,
        )

        if args.output:
            # Write to JSON file
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                output_data = {
                    "prompt": result.prompt,
                    "video_model": result.video_model,
                    "input_image": result.input_image,
                    "schema_name": result.schema_name,
                }
                if result.motion_preset:
                    output_data["motion_preset"] = result.motion_preset
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            log_info(f"Saved prompt to {output_path}")
        else:
            # Print to stdout
            print(result.prompt)

        return True

    except Exception as e:
        log_error(f"Failed to generate prompt: {e}")
        return False
