"""
API utilities for semiautomatic.

Provides polling, retry logic, and common HTTP patterns used across providers.

Library usage:
    from semiautomatic.lib.api import poll_for_result, download_file

    # Poll an async API endpoint
    result = poll_for_result(
        check_fn=lambda: api.get_status(task_id),
        is_complete=lambda r: r["status"] == "completed",
        is_failed=lambda r: r["status"] == "failed",
        get_error=lambda r: r.get("error"),
        interval=5.0,
        timeout=300.0,
    )

    # Download a file from URL
    download_file("https://example.com/file.mp4", Path("output.mp4"))
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar

from semiautomatic.lib.logging import log_info, log_error


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_POLL_INTERVAL = 5.0  # seconds
DEFAULT_POLL_TIMEOUT = 300.0  # 5 minutes
DEFAULT_DOWNLOAD_TIMEOUT = 60  # seconds


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class PollResult:
    """Result from a polling operation."""

    success: bool
    result: Any = None
    error: Optional[str] = None
    elapsed: float = 0.0
    attempts: int = 0


T = TypeVar("T")


# ---------------------------------------------------------------------------
# Polling Utilities
# ---------------------------------------------------------------------------

def poll_for_result(
    check_fn: Callable[[], T],
    is_complete: Callable[[T], bool],
    is_failed: Optional[Callable[[T], bool]] = None,
    get_error: Optional[Callable[[T], Optional[str]]] = None,
    *,
    interval: float = DEFAULT_POLL_INTERVAL,
    timeout: float = DEFAULT_POLL_TIMEOUT,
    on_status: Optional[Callable[[T, int], None]] = None,
) -> PollResult:
    """
    Poll an async operation until completion.

    Args:
        check_fn: Function that checks status (called each poll).
        is_complete: Function that returns True when operation is complete.
        is_failed: Function that returns True when operation has failed.
        get_error: Function that extracts error message from result.
        interval: Seconds between polls.
        timeout: Maximum seconds to poll before timing out.
        on_status: Optional callback for status updates (result, attempt).

    Returns:
        PollResult with success status, result, and metadata.

    Example:
        result = poll_for_result(
            check_fn=lambda: requests.get(f"{API}/tasks/{id}").json(),
            is_complete=lambda r: r["status"] == "completed",
            is_failed=lambda r: r["status"] == "failed",
            get_error=lambda r: r.get("error_message"),
        )
    """
    start_time = time.time()
    attempts = 0
    last_result = None

    while True:
        elapsed = time.time() - start_time
        attempts += 1

        # Check timeout
        if elapsed >= timeout:
            return PollResult(
                success=False,
                result=last_result,
                error=f"Polling timeout after {timeout:.0f}s ({attempts} attempts)",
                elapsed=elapsed,
                attempts=attempts,
            )

        try:
            last_result = check_fn()

            # Notify status callback
            if on_status:
                on_status(last_result, attempts)

            # Check completion
            if is_complete(last_result):
                return PollResult(
                    success=True,
                    result=last_result,
                    elapsed=elapsed,
                    attempts=attempts,
                )

            # Check failure
            if is_failed and is_failed(last_result):
                error_msg = None
                if get_error:
                    error_msg = get_error(last_result)
                return PollResult(
                    success=False,
                    result=last_result,
                    error=error_msg or "Operation failed",
                    elapsed=elapsed,
                    attempts=attempts,
                )

        except Exception as e:
            # Log but continue polling on transient errors
            log_error(f"Poll attempt {attempts} failed: {e}")

        # Wait before next poll
        time.sleep(interval)


# ---------------------------------------------------------------------------
# Download Utilities
# ---------------------------------------------------------------------------

def download_file(
    url: str,
    output_path: Path,
    *,
    timeout: int = DEFAULT_DOWNLOAD_TIMEOUT,
    chunk_size: int = 8192,
) -> bool:
    """
    Download a file from URL.

    Args:
        url: URL to download from.
        output_path: Local path to save file.
        timeout: Request timeout in seconds.
        chunk_size: Bytes per chunk when streaming.

    Returns:
        True if successful, False otherwise.
    """
    try:
        import requests
    except ImportError:
        raise ImportError(
            "requests package not found. Install with: pip install requests"
        )

    try:
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Stream to file
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

        return True

    except Exception as e:
        log_error(f"Download failed: {e}")
        return False


def download_to_bytes(
    url: str,
    *,
    timeout: int = DEFAULT_DOWNLOAD_TIMEOUT,
) -> Optional[bytes]:
    """
    Download content from URL to bytes.

    Args:
        url: URL to download from.
        timeout: Request timeout in seconds.

    Returns:
        File content as bytes, or None on failure.
    """
    try:
        import requests
    except ImportError:
        raise ImportError(
            "requests package not found. Install with: pip install requests"
        )

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content

    except Exception as e:
        log_error(f"Download failed: {e}")
        return None


# ---------------------------------------------------------------------------
# HTTP Utilities
# ---------------------------------------------------------------------------

def post_json(
    url: str,
    payload: dict,
    *,
    headers: Optional[dict] = None,
    timeout: int = 120,
) -> Optional[dict]:
    """
    POST JSON to an API endpoint.

    Args:
        url: API endpoint URL.
        payload: JSON payload to send.
        headers: Optional HTTP headers.
        timeout: Request timeout in seconds.

    Returns:
        JSON response as dict, or None on failure.
    """
    try:
        import requests
    except ImportError:
        raise ImportError(
            "requests package not found. Install with: pip install requests"
        )

    try:
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)

        response = requests.post(
            url,
            json=payload,
            headers=default_headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        log_error(f"POST request failed: {e}")
        return None


def get_json(
    url: str,
    *,
    headers: Optional[dict] = None,
    timeout: int = 30,
) -> Optional[dict]:
    """
    GET JSON from an API endpoint.

    Args:
        url: API endpoint URL.
        headers: Optional HTTP headers.
        timeout: Request timeout in seconds.

    Returns:
        JSON response as dict, or None on failure.
    """
    try:
        import requests
    except ImportError:
        raise ImportError(
            "requests package not found. Install with: pip install requests"
        )

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        log_error(f"GET request failed: {e}")
        return None
