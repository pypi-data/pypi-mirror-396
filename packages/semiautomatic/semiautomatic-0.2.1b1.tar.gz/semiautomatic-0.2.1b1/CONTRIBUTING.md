# Contributing

## Development Setup

```bash
git clone https://github.com/drpolygon/semiautomatic.git
cd semiautomatic
uv sync
```

## Running Tests

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=semiautomatic

# Run integration tests (requires API keys)
uv run pytest -m integration
```

Integration tests output to `tests/output/` for manual inspection.

## Project Structure

```
src/semiautomatic/
    __init__.py          # Package init
    cli.py               # CLI entry point
    defaults.py          # Centralized defaults
    lib/                 # Shared utilities
        env.py           # Project root detection, .env loading
        storage.py       # Storage backend abstraction
        api.py           # HTTP utilities, polling
        vision/          # Vision providers (Moondream)
    image/               # Image processing and generation
        process.py       # Resize, compress, convert
        generate.py      # Image generation orchestration
        upscale.py       # Image upscaling
        providers/       # FAL, Recraft, Freepik
    video/               # Video processing and generation
        process.py       # Speed, zoom, trim, frames
        generate.py      # Video generation orchestration
        providers/       # FAL, Wavespeed, Higgsfield
tests/
    conftest.py          # Shared fixtures
    test_*.py            # Unit tests
    output/              # Integration test outputs
```

## Code Style

See `CLAUDE.md` for project conventions including:
- Module structure and imports
- Type hints and docstrings
- Git commit style
- Testing patterns

## Adding a New Provider

1. Create provider in `image/providers/` or `video/providers/`
2. Implement the base class (`ImageProvider` or `VideoProvider`)
3. Register in the provider's `__init__.py`
4. Add unit tests with mocked API calls
5. Add integration test marked with `@pytest.mark.integration`
