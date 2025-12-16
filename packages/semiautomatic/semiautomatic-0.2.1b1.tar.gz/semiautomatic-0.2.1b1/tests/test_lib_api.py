"""
Tests for semiautomatic.lib.api module.

Tests cover:
- Polling utilities
- Download functions
- HTTP helpers
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from semiautomatic.lib.api import (
    poll_for_result,
    download_file,
    download_to_bytes,
    PollResult,
)


class TestPollForResult:
    """Tests for poll_for_result()."""

    def test_returns_success_when_complete(self):
        """Should return success when is_complete returns True."""
        call_count = 0

        def check_fn():
            nonlocal call_count
            call_count += 1
            return {"status": "completed" if call_count >= 2 else "processing"}

        result = poll_for_result(
            check_fn=check_fn,
            is_complete=lambda r: r["status"] == "completed",
            interval=0.01,
            timeout=5.0,
        )

        assert result.success is True
        assert result.result["status"] == "completed"
        assert result.attempts == 2

    def test_returns_failure_when_failed(self):
        """Should return failure when is_failed returns True."""
        def check_fn():
            return {"status": "failed", "error": "Something went wrong"}

        result = poll_for_result(
            check_fn=check_fn,
            is_complete=lambda r: r["status"] == "completed",
            is_failed=lambda r: r["status"] == "failed",
            get_error=lambda r: r.get("error"),
            interval=0.01,
            timeout=5.0,
        )

        assert result.success is False
        assert result.error == "Something went wrong"

    def test_times_out_after_timeout(self):
        """Should return timeout error after timeout period."""
        def check_fn():
            return {"status": "processing"}

        result = poll_for_result(
            check_fn=check_fn,
            is_complete=lambda r: False,
            interval=0.01,
            timeout=0.05,
        )

        assert result.success is False
        assert "timeout" in result.error.lower()

    def test_calls_on_status_callback(self):
        """Should call on_status callback with result and attempt."""
        statuses = []

        def on_status(result, attempt):
            statuses.append((result["status"], attempt))

        call_count = 0

        def check_fn():
            nonlocal call_count
            call_count += 1
            return {"status": "completed" if call_count >= 3 else "processing"}

        poll_for_result(
            check_fn=check_fn,
            is_complete=lambda r: r["status"] == "completed",
            on_status=on_status,
            interval=0.01,
            timeout=5.0,
        )

        assert len(statuses) == 3
        assert statuses[0] == ("processing", 1)
        assert statuses[1] == ("processing", 2)
        assert statuses[2] == ("completed", 3)

    def test_continues_on_check_fn_exception(self):
        """Should continue polling if check_fn raises exception."""
        call_count = 0

        def check_fn():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Network error")
            return {"status": "completed"}

        result = poll_for_result(
            check_fn=check_fn,
            is_complete=lambda r: r["status"] == "completed",
            interval=0.01,
            timeout=5.0,
        )

        assert result.success is True
        assert result.attempts == 2


class TestDownloadFile:
    """Tests for download_file()."""

    def test_downloads_file_successfully(self, temp_dir):
        """Should download file to specified path."""
        output_path = temp_dir / "downloaded.txt"

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.iter_content.return_value = [b"test content"]
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = download_file("http://example.com/file.txt", output_path)

        assert result is True
        assert output_path.exists()
        assert output_path.read_bytes() == b"test content"

    def test_returns_false_on_error(self, temp_dir):
        """Should return False when download fails."""
        output_path = temp_dir / "failed.txt"

        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Connection failed")

            result = download_file("http://example.com/file.txt", output_path)

        assert result is False
        assert not output_path.exists()

    def test_creates_parent_directories(self, temp_dir):
        """Should create parent directories if they don't exist."""
        output_path = temp_dir / "nested" / "deep" / "file.txt"

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.iter_content.return_value = [b"content"]
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = download_file("http://example.com/file.txt", output_path)

        assert result is True
        assert output_path.exists()


class TestDownloadToBytes:
    """Tests for download_to_bytes()."""

    def test_returns_bytes_on_success(self):
        """Should return bytes content on success."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"file bytes"
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = download_to_bytes("http://example.com/file.bin")

        assert result == b"file bytes"

    def test_returns_none_on_error(self):
        """Should return None when download fails."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Network error")

            result = download_to_bytes("http://example.com/file.bin")

        assert result is None
