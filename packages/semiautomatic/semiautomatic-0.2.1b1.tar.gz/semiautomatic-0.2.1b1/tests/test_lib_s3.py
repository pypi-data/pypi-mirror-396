"""
Tests for semiautomatic.lib.s3 module.

Tests cover:
- AWS4-HMAC-SHA256 signing components
- put_object operation (mocked)
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from semiautomatic.lib.s3 import (
    _sha256_hex,
    _hmac_sha256,
    _get_signing_key,
    _create_canonical_request,
    _sign_request,
    put_object,
)


class TestHashFunctions:
    """Tests for hash helper functions."""

    def test_sha256_hex(self):
        """Should return correct SHA256 hex digest."""
        result = _sha256_hex(b"test")
        expected = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        assert result == expected

    def test_sha256_hex_empty(self):
        """Should handle empty input."""
        result = _sha256_hex(b"")
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert result == expected

    def test_hmac_sha256(self):
        """Should return correct HMAC-SHA256."""
        result = _hmac_sha256(b"key", "message")
        assert len(result) == 32  # SHA256 produces 32 bytes


class TestSigningKey:
    """Tests for signing key derivation."""

    def test_get_signing_key(self):
        """Should derive signing key correctly."""
        key = _get_signing_key(
            secret_key="wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY",
            date_stamp="20230101",
            region="auto",
        )
        # Signing key should be 32 bytes
        assert len(key) == 32
        assert isinstance(key, bytes)


class TestCanonicalRequest:
    """Tests for canonical request creation."""

    def test_create_canonical_request(self):
        """Should create properly formatted canonical request."""
        headers = {
            "host": "example.com",
            "x-amz-date": "20230101T000000Z",
        }

        result = _create_canonical_request(
            method="PUT",
            path="/bucket/key",
            query_string="",
            headers=headers,
            signed_headers="host;x-amz-date",
            payload_hash="abc123",
        )

        lines = result.split("\n")
        assert lines[0] == "PUT"
        assert lines[1] == "/bucket/key"
        assert lines[2] == ""  # empty query string
        assert "host:example.com" in result
        assert "x-amz-date:20230101T000000Z" in result


class TestSignRequest:
    """Tests for request signing."""

    def test_sign_request_adds_authorization(self):
        """Should add Authorization header."""
        headers = {
            "Host": "test.r2.cloudflarestorage.com",
            "Content-Type": "text/plain",
        }

        with patch("semiautomatic.lib.s3.datetime") as mock_datetime:
            mock_now = MagicMock()
            mock_now.strftime.side_effect = lambda f: (
                "20230101T120000Z" if "T" in f else "20230101"
            )
            mock_datetime.now.return_value = mock_now
            mock_datetime.timezone = timezone

            result = _sign_request(
                method="PUT",
                url="https://test.r2.cloudflarestorage.com/bucket/key",
                headers=headers,
                access_key="AKIAIOSFODNN7EXAMPLE",
                secret_key="wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY",
                region="auto",
                payload_hash="abc123",
            )

        assert "Authorization" in result
        assert "AWS4-HMAC-SHA256" in result["Authorization"]
        assert "AKIAIOSFODNN7EXAMPLE" in result["Authorization"]
        assert "x-amz-date" in result
        assert "x-amz-content-sha256" in result


class TestPutObject:
    """Tests for put_object operation."""

    def test_put_object_success(self, temp_dir):
        """Should upload file successfully."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("hello world")

        with patch("semiautomatic.lib.s3.requests.put") as mock_put:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_put.return_value = mock_response

            put_object(
                endpoint="https://account.r2.cloudflarestorage.com",
                bucket="my-bucket",
                key="uploads/test.txt",
                file_path=test_file,
                access_key="access",
                secret_key="secret",
            )

        mock_put.assert_called_once()
        call_args = mock_put.call_args
        assert "https://account.r2.cloudflarestorage.com/my-bucket/uploads/test.txt" == call_args[0][0]
        assert "Authorization" in call_args[1]["headers"]

    def test_put_object_file_not_found(self, temp_dir):
        """Should raise FileNotFoundError for missing file."""
        missing_file = temp_dir / "missing.txt"

        with pytest.raises(FileNotFoundError):
            put_object(
                endpoint="https://test.endpoint",
                bucket="bucket",
                key="key",
                file_path=missing_file,
                access_key="access",
                secret_key="secret",
            )

    def test_put_object_http_error(self, temp_dir):
        """Should raise on HTTP error."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        with patch("semiautomatic.lib.s3.requests.put") as mock_put:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = Exception("403 Forbidden")
            mock_put.return_value = mock_response

            with pytest.raises(Exception, match="403 Forbidden"):
                put_object(
                    endpoint="https://test.endpoint",
                    bucket="bucket",
                    key="key",
                    file_path=test_file,
                    access_key="access",
                    secret_key="secret",
                )

    def test_put_object_content_type_detection(self, temp_dir):
        """Should detect content type from file extension."""
        test_file = temp_dir / "image.jpg"
        test_file.write_bytes(b"fake image")

        with patch("semiautomatic.lib.s3.requests.put") as mock_put:
            mock_response = MagicMock()
            mock_put.return_value = mock_response

            put_object(
                endpoint="https://test.endpoint",
                bucket="bucket",
                key="image.jpg",
                file_path=test_file,
                access_key="access",
                secret_key="secret",
            )

        call_args = mock_put.call_args
        assert call_args[1]["headers"]["Content-Type"] == "image/jpeg"
