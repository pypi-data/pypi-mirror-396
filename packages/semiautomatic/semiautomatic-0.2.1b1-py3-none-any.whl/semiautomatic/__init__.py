"""Automation tools for creative AI workflows."""
import sys

# Auto-configure UTF-8 on Windows at import time
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("semiautomatic")
except PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback for development without install
