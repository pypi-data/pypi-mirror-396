# CLAUDE.md

Project conventions for Claude Code sessions.

## Project Vision

**semiautomatic** is a general-purpose AI media workflow toolkit published to PyPI.

## Git

- **Commit style**: Lowercase, imperative mood, single line only
- **Format**: `verb: brief description` (no period)
- **No Claude attribution**: Don't include "Generated with Claude" or co-author lines
- **No multi-line commits**: Never use heredoc or multi-line strings for commit messages
- **Branches**: Work on `dev`, merge to `main` for releases

Examples:
```
add flux image generation tool
fix video prompt length validation
update compression algorithm defaults
```

## Documentation Updates

After completing any significant task:

1. **CHANGELOG.md** (backward-looking): Add entry under `[Unreleased]`
   - `Added` - new features
   - `Changed` - changes in existing functionality
   - `Deprecated` - soon-to-be removed features
   - `Removed` - now removed features
   - `Fixed` - bug fixes
   - `Security` - vulnerability fixes

2. **ROADMAP.md** (forward-looking): Remove completed items
   - Delete finished blockers entirely (don't check them off)
   - Remove completed release checklist items
   - Revise or remove items no longer planned

## Code Organization

### Architecture Philosophy

**Tools** (single focused task):
- Location: `src/semiautomatic/<domain>/`
- Naming: Module per domain (`image/`, `video/`, `prompt/`)
- Directly importable as library, callable via CLI

**Shared Utilities**:
- Location: `src/semiautomatic/lib/`
- Examples: `logging.py`, `subprocess.py`
- Cross-cutting concerns used by multiple tools

### Module Structure
```python
"""
Module docstring with usage examples.

Library usage:
    from semiautomatic.image import compress_for_api
    img_bytes = compress_for_api(Path('photo.jpg'))

CLI usage:
    semiautomatic process-image --size 1920x1080
"""

from __future__ import annotations

# stdlib imports
# third-party imports
# local imports

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UPPER_SNAKE_CASE = "for constants"

# ---------------------------------------------------------------------------
# Section Name
# ---------------------------------------------------------------------------

def function_name():
    """Docstring."""
    pass
```

### Patterns
- Type hints on function signatures
- Dataclasses for structured return values
- `Optional[T]` for nullable params (Python 3.9 compat)
- Docstrings: first line summary, then Args/Returns/Raises for complex functions
- Section separators: `# ---------------------------------------------------------------------------`

### Modularization Guidelines

When to modularize a tool:
- Exceeds 500-800 lines
- Multiple distinct feature domains
- Features could be tested independently
- Other tools might want to import specific functions

When NOT to modularize:
- Under 500 lines
- Logic is tightly coupled
- No reuse case for individual functions

Pattern when modularizing:
```
src/semiautomatic/video/
├── __init__.py          # Public API exports
├── process.py           # Main implementation
├── speed.py             # Speed/ramping logic
├── transform.py         # Zoom, resize, crop
└── ffmpeg.py            # FFmpeg command building
```

## Testing

- **Framework**: pytest with `-v` flag (configured in pyproject.toml)
- **Test files**: `tests/test_<module>.py`
- **Test classes**: `class TestFunctionName:` grouping related tests
- **Fixtures**: Programmatic test data in `conftest.py` (no binary fixtures committed)
- **Run tests**: `uv run pytest`

```python
"""
Tests for semiautomatic.module.

Tests cover:
- Feature A
- Feature B
"""

class TestFunctionName:
    """Tests for function_name()."""

    def test_basic_case(self):
        ...
```

## Project Structure

```
src/semiautomatic/
    __init__.py          # Package init, UTF-8 setup on Windows
    cli.py               # CLI entry point
    lib/                 # Shared utilities
        __init__.py
        logging.py       # log_info(), log_error()
        subprocess.py    # UTF-8 subprocess wrapper
    image/               # Image processing tools
        __init__.py
        process.py
    video/               # (planned)
    prompt/              # (planned)
tests/
    conftest.py          # Shared fixtures
    test_<module>.py
```

## Dependencies & Commands

- **Package manager**: uv
- **Build backend**: hatchling
- **Python**: >=3.9

```bash
# Development setup
uv sync

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=semiautomatic

# Install editable (for pip users)
pip install -e .
```

**CRITICAL**: Always use `uv run` to execute Python scripts, never `python` directly.

## CLI Conventions

- Main command: `semiautomatic` (alias: `sa`)
- Subcommands: `semiautomatic <command> [options]`
- Logging: Use `lib.logging.log_info()` and `log_error()` for timestamped output
- Exit codes: 0 success, 1 failure, 130 keyboard interrupt

## Windows Compatibility

- UTF-8 encoding auto-configured on package import (in `__init__.py`)
- Use `semiautomatic.lib.subprocess.run()` for subprocess calls (has UTF-8 defaults)
- No manual encoding fixes needed in individual tools
