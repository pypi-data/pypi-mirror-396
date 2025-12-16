"""
Shared logging utilities for semiautomatic tools.
Provides consistent timestamped log output across all tools.
"""

import sys
import time


def log_info(message):
    """Log general information with timestamp to stdout."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def log_error(message):
    """Log error message with timestamp to stderr."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] ERROR: {message}", file=sys.stderr)
