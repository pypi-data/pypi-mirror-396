"""
Subprocess wrapper with UTF-8 defaults for Windows compatibility.

Usage:
    from semiautomatic.lib.subprocess import run
    result = run(["ffmpeg", "-i", "input.mp4", ...])
"""
import subprocess as _subprocess
from typing import Any

def run(*args, encoding: str = "utf-8", errors: str = "replace", **kwargs) -> _subprocess.CompletedProcess:
    """subprocess.run() with UTF-8 defaults."""
    return _subprocess.run(*args, encoding=encoding, errors=errors, **kwargs)

# Re-export commonly used items for convenience
CalledProcessError = _subprocess.CalledProcessError
PIPE = _subprocess.PIPE
DEVNULL = _subprocess.DEVNULL
