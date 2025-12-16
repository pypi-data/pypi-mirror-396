"""
Image prompt generation.

Generates platform-specific image prompts from user intent, optionally styled
by a schema (aesthetic JSON file).

Library usage:
    from semiautomatic.prompt import generate_image_prompt

    # Basic usage (no schema)
    result = generate_image_prompt("person dancing at a rave")

    # With schema for styling
    result = generate_image_prompt(
        "person dancing",
        schema_path="path/to/aesthetic.json",
        platform="flux"
    )

CLI usage:
    semiautomatic generate-image-prompt "person dancing"
    semiautomatic generate-image-prompt "person dancing" --schema aesthetic.json
    semiautomatic generate-image-prompt "person dancing" --schema aesthetic.json --platform flux
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from semiautomatic.lib.llm import complete
from semiautomatic.prompt.models import (
    IMAGE_PLATFORM_CONFIGS,
    BANNED_WORDS,
)


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class ImagePromptResult:
    """Result from image prompt generation."""

    prompt: str
    descriptive_only: str
    platform: str
    schema_name: Optional[str] = None
    schema_version: Optional[str] = None
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# System Prompt Builders
# ---------------------------------------------------------------------------

def _build_generic_system_prompt(platform: str) -> str:
    """Build a generic system prompt when no schema is provided."""
    config = IMAGE_PLATFORM_CONFIGS.get(platform, IMAGE_PLATFORM_CONFIGS["flux"])
    max_words = config["max_words"]

    return f"""You generate concise, direct image prompts for {config['name']}.

CRITICAL RULES:

1. **BE DIRECT AND CONCISE**
   - Maximum {max_words} words total
   - Natural, descriptive language
   - Focus on visual details

2. **STRUCTURE**
   - Start with subject: describe the main subject clearly
   - Add key visual details: clothing, accessories, features
   - Include mood/expression if relevant
   - End with lighting/atmosphere

3. **OUTPUT FORMAT**
   - Simple, direct description
   - NO technical jargon or parameters
   - Just describe the scene naturally
   - {max_words} words maximum

Generate a prompt for the user's request."""


def _build_schema_system_prompt(schema: dict, platform: str) -> str:
    """Build a system prompt based on schema (aesthetic) data."""
    config = IMAGE_PLATFORM_CONFIGS.get(platform, IMAGE_PLATFORM_CONFIGS["flux"])
    max_words = config["max_words"]

    schema_name = schema.get('name', 'Custom')
    description = schema.get('description', '')
    mood = schema.get('mood', [])
    style_treatment = schema.get('style_treatment', {})

    # Extract props and actions
    props_section = schema.get('props', {})
    actions_section = schema.get('actions', {})
    props_examples = props_section.get('examples', []) if isinstance(props_section, dict) else []
    actions_examples = actions_section.get('examples', []) if isinstance(actions_section, dict) else []

    # Expression rules
    expression_rules = schema.get('expression_rules', {})
    default_expressions = expression_rules.get('default', 'natural expressions')
    allowed_horror = expression_rules.get('allowed_horror', [])

    # Lighting
    elements = schema.get('elements', {})
    lighting = elements.get('lighting', style_treatment.get('lighting', 'natural lighting'))
    if isinstance(lighting, list):
        lighting = ', '.join(lighting[:5])

    # Canonical examples
    canonical_examples = schema.get('canonical_examples', [])
    examples_text = ""
    if canonical_examples:
        examples_list = '\n'.join([f"- {ex}" for ex in canonical_examples[:5]])
        examples_text = f"\n\nCANONICAL EXAMPLES:\n{examples_list}\n\nUse these to understand typical subjects, settings, and details."

    if platform == "flux":
        return f"""You generate concise, direct image prompts for FLUX models using the {schema_name} style.

STYLE OVERVIEW:
{description}

- Mood: {', '.join(mood[:8]) if isinstance(mood, list) else str(mood)}
- Lighting: {lighting}
- Props: {', '.join(props_examples[:10]) if props_examples else 'N/A'}
- Actions: {', '.join(actions_examples[:10]) if actions_examples else 'N/A'}
- Expressions: {default_expressions}
- Horror expressions: {', '.join(allowed_horror[:8]) if allowed_horror else 'N/A'}{examples_text}

CRITICAL RULES FOR FLUX PROMPTS:

1. **BE DIRECT AND CONCISE**
   - No framing like "album cover" or "poster art"
   - Just describe what you see directly
   - Maximum {max_words} words total

2. **STRUCTURE**
   - Start with subject
   - Add key visual details
   - Include mood/expression
   - End with lighting/atmosphere

3. **APPLY STYLE**
   - Use the mood and lighting from this style
   - Include relevant props and actions
   - Match the tone and feel

OUTPUT FORMAT:
- Simple, direct description
- NO technical jargon or parameters
- {max_words} words maximum

Generate a FLUX prompt for the user's request using {schema_name} styling."""

    else:  # midjourney
        when_figures = schema.get('when_figures_present', {})
        colors = schema.get('color_palette', schema.get('colors', []))
        must_include = schema.get('must_include', schema.get('constraints', {}).get('must_include', []))
        must_avoid = schema.get('must_avoid', schema.get('constraints', {}).get('must_avoid', []))

        # Prompt framing
        prompt_framing = schema.get('prompt_framing', {})
        default_context = prompt_framing.get('default_context', '')
        framing_usage = prompt_framing.get('usage', 'optional')

        framing_instruction = ""
        if default_context:
            if framing_usage == "required":
                framing_instruction = f'\nPROMPT FRAMING (REQUIRED): Always start with "{default_context}"'
            elif framing_usage == "preferred":
                framing_instruction = f'\nPROMPT FRAMING (PREFERRED): Default to "{default_context}" unless user specifies otherwise'

        return f"""You generate Midjourney image prompts for the {schema_name} style.

STYLE OVERVIEW:
{description}
{framing_instruction}

VISUAL CHARACTERISTICS:
- Mood: {', '.join(mood) if isinstance(mood, list) else mood}
- Colors: {', '.join(colors) if isinstance(colors, list) else 'See style context'}
- Lighting: {style_treatment.get('lighting', 'N/A')}
- Atmosphere: {style_treatment.get('atmosphere', 'N/A')}

WHEN FIGURES ARE PRESENT:
{json.dumps(when_figures, indent=2) if when_figures else 'No specific guidelines'}

CONSTRAINTS:
- Must include: {', '.join(must_include) if isinstance(must_include, list) else must_include}
- Must avoid: {', '.join(must_avoid) if isinstance(must_avoid, list) else must_avoid}

PROMPT STYLE:
- Conversational narrative format
- Use connecting words: "with", "featuring", "in"
- Target {max_words} words
- NO technical parameters (added automatically)

Generate a prompt for the user's request using {schema_name} styling."""


# ---------------------------------------------------------------------------
# Prompt Sanitization
# ---------------------------------------------------------------------------

def _sanitize_prompt(prompt: str) -> str:
    """Replace banned words with acceptable alternatives."""
    sanitized = prompt
    for pattern, replacement in BANNED_WORDS.items():
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    return sanitized


def _inject_trigger_word(prompt: str, schema: dict) -> str:
    """Inject trigger word at the beginning of the prompt if specified."""
    trigger_word_config = schema.get('trigger_word')
    if trigger_word_config and isinstance(trigger_word_config, dict):
        trigger_word = trigger_word_config.get('word', '').strip()
        if trigger_word:
            return f"{trigger_word}, {prompt}"
    return prompt


def _add_midjourney_parameters(prompt: str, schema: dict, config: Optional[dict] = None) -> str:
    """Add Midjourney technical parameters to the prompt."""
    specs = schema.get("technical_specs", schema.get("model_specs", {}).get("midjourney", {}))

    # Aspect ratio
    aspect_ratios = specs.get("aspect_ratios", ["5:4"])
    ar = random.choice(aspect_ratios)

    # Get sref URLs
    global_srefs = (config or {}).get("global_sref_urls", [])
    aesthetic_srefs = specs.get("sref_urls", [])

    # Combine srefs
    selected_aesthetic_srefs = aesthetic_srefs if aesthetic_srefs else []
    global_sref_range = specs.get("global_sref_range", [1, 3])
    min_global, max_global = global_sref_range[0], global_sref_range[1]

    selected_global_srefs = []
    if global_srefs and max_global > 0:
        num_global = random.randint(min_global, min(max_global, len(global_srefs)))
        if num_global > 0:
            selected_global_srefs = random.sample(global_srefs, num_global)

    all_srefs = selected_aesthetic_srefs + selected_global_srefs
    random.shuffle(all_srefs)
    all_srefs = all_srefs[:8]

    # Style weight
    sw = specs.get("style_weight", "500")
    if isinstance(sw, str) and "-" in sw:
        parts = sw.split("-")
        sw = str((int(parts[0]) + int(parts[1])) // 2)

    # Version
    version = specs.get("version", "6.1")

    # Build full prompt
    full_prompt = prompt
    full_prompt += f" --ar {ar}"
    if all_srefs:
        full_prompt += f" --sref {' '.join(all_srefs)}"
    full_prompt += f" --sw {sw}"
    full_prompt += f" --v {version}"
    full_prompt += " --p"

    return full_prompt


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_image_prompt(
    intent: str,
    *,
    schema_path: Optional[str | Path] = None,
    platform: str = "flux",
    config_path: Optional[str | Path] = None,
    model: Optional[str] = None,
) -> ImagePromptResult:
    """
    Generate a platform-specific image prompt from user intent.

    Args:
        intent: Description of what to generate (e.g., "person dancing at rave").
        schema_path: Optional path to schema JSON (e.g., aesthetic.json).
        platform: Target platform - "flux" or "midjourney" (default: flux).
        config_path: Optional path to config JSON with global settings.
        model: LLM model to use (default: provider default).

    Returns:
        ImagePromptResult with generated prompt and metadata.

    Examples:
        # Basic usage
        result = generate_image_prompt("person dancing at a rave")
        print(result.prompt)

        # With schema
        result = generate_image_prompt(
            "person dancing",
            schema_path="aesthetic.json",
            platform="flux"
        )
    """
    # Load schema if provided
    schema = None
    if schema_path:
        schema_path = Path(schema_path)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)

    # Load config if provided
    config = None
    if config_path:
        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

    # Build system prompt
    if schema:
        system_prompt = _build_schema_system_prompt(schema, platform)
    else:
        system_prompt = _build_generic_system_prompt(platform)

    # Generate prompt via LLM
    response = complete(
        [{"role": "user", "content": intent}],
        system=system_prompt,
        model=model,
        max_tokens=1024,
    )

    descriptive_prompt = response.strip()

    # Post-processing
    descriptive_prompt = _sanitize_prompt(descriptive_prompt)

    if schema:
        descriptive_prompt = _inject_trigger_word(descriptive_prompt, schema)

    # Add technical parameters for Midjourney
    if platform == "midjourney" and schema:
        full_prompt = _add_midjourney_parameters(descriptive_prompt, schema, config)
    else:
        full_prompt = descriptive_prompt

    return ImagePromptResult(
        prompt=full_prompt,
        descriptive_only=descriptive_prompt,
        platform=platform,
        schema_name=schema.get('name') if schema else None,
        schema_version=schema.get('version') if schema else None,
        metadata={
            "intent": intent,
            "has_schema": schema is not None,
        }
    )


# ---------------------------------------------------------------------------
# CLI Handler
# ---------------------------------------------------------------------------

def run_generate_image_prompt(args) -> bool:
    """CLI handler for generate-image-prompt command."""
    from semiautomatic.lib.logging import log_info, log_error

    if not args.intent:
        log_error("Intent is required")
        return False

    try:
        result = generate_image_prompt(
            args.intent,
            schema_path=args.schema,
            platform=args.platform,
        )

        if args.output:
            # Write to JSON file
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "prompt": result.prompt,
                    "descriptive_only": result.descriptive_only,
                    "platform": result.platform,
                    "schema_name": result.schema_name,
                }, f, indent=2, ensure_ascii=False)
            log_info(f"Saved prompt to {output_path}")
        else:
            # Print to stdout
            print(result.prompt)

        return True

    except Exception as e:
        log_error(f"Failed to generate prompt: {e}")
        return False
