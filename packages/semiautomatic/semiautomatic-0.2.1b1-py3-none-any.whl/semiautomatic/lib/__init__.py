"""
semiautomatic.lib - Shared utilities.

Provides common functionality used across semiautomatic modules:

- env: Project root detection and .env loading
- logging: Timestamped log output
- subprocess: UTF-8 subprocess wrapper
- storage: Cloud storage backends (R2, etc.)
- vision: Image captioning and understanding
- api: HTTP utilities, polling, downloads
"""

from semiautomatic.lib import logging
from semiautomatic.lib import subprocess
from semiautomatic.lib import env
from semiautomatic.lib import storage
from semiautomatic.lib import api

__all__ = [
    "logging",
    "subprocess",
    "env",
    "storage",
    "api",
]
