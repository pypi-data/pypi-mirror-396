"""
Minimal S3-compatible client with AWS4-HMAC-SHA256 signing.

Replaces boto3 (~80MB) with ~100 lines using only stdlib + requests.
Supports PUT operations for S3-compatible storage (AWS S3, Cloudflare R2, etc.).

Library usage:
    from semiautomatic.lib.s3 import put_object

    put_object(
        endpoint="https://account-id.r2.cloudflarestorage.com",
        bucket="my-bucket",
        key="path/to/file.jpg",
        file_path=Path("local/file.jpg"),
        access_key="access-key",
        secret_key="secret-key",
    )
"""

from __future__ import annotations

import hashlib
import hmac
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALGORITHM = "AWS4-HMAC-SHA256"
SERVICE = "s3"
UNSIGNED_PAYLOAD = "UNSIGNED-PAYLOAD"


# ---------------------------------------------------------------------------
# AWS4 Signing
# ---------------------------------------------------------------------------

def _sha256_hex(data: bytes) -> str:
    """Return SHA256 hash of data as hex string."""
    return hashlib.sha256(data).hexdigest()


def _hmac_sha256(key: bytes, msg: str) -> bytes:
    """Return HMAC-SHA256 of message with key."""
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _get_signing_key(secret_key: str, date_stamp: str, region: str) -> bytes:
    """
    Derive the signing key for AWS4 signature.

    Args:
        secret_key: AWS secret access key.
        date_stamp: Date in YYYYMMDD format.
        region: AWS region (use "auto" for R2).

    Returns:
        Derived signing key bytes.
    """
    k_date = _hmac_sha256(f"AWS4{secret_key}".encode("utf-8"), date_stamp)
    k_region = _hmac_sha256(k_date, region)
    k_service = _hmac_sha256(k_region, SERVICE)
    k_signing = _hmac_sha256(k_service, "aws4_request")
    return k_signing


def _create_canonical_request(
    method: str,
    path: str,
    query_string: str,
    headers: dict[str, str],
    signed_headers: str,
    payload_hash: str,
) -> str:
    """
    Create the canonical request string for AWS4 signing.

    Args:
        method: HTTP method (GET, PUT, etc.).
        path: URL path (e.g., /bucket/key).
        query_string: URL query string (empty string if none).
        headers: Request headers dict.
        signed_headers: Semicolon-separated list of signed header names.
        payload_hash: SHA256 hash of request payload.

    Returns:
        Canonical request string.
    """
    canonical_headers = "".join(
        f"{k.lower()}:{v.strip()}\n" for k, v in sorted(headers.items())
    )

    return "\n".join([
        method,
        path,
        query_string,
        canonical_headers,
        signed_headers,
        payload_hash,
    ])


def _create_string_to_sign(
    timestamp: str,
    date_stamp: str,
    region: str,
    canonical_request: str,
) -> str:
    """
    Create the string to sign for AWS4 signature.

    Args:
        timestamp: ISO 8601 timestamp (YYYYMMDDTHHMMSSZ).
        date_stamp: Date in YYYYMMDD format.
        region: AWS region.
        canonical_request: The canonical request string.

    Returns:
        String to sign.
    """
    credential_scope = f"{date_stamp}/{region}/{SERVICE}/aws4_request"
    return "\n".join([
        ALGORITHM,
        timestamp,
        credential_scope,
        _sha256_hex(canonical_request.encode("utf-8")),
    ])


def _sign_request(
    method: str,
    url: str,
    headers: dict[str, str],
    access_key: str,
    secret_key: str,
    region: str,
    payload_hash: str,
) -> dict[str, str]:
    """
    Sign a request using AWS4-HMAC-SHA256.

    Args:
        method: HTTP method.
        url: Full request URL.
        headers: Request headers (will be modified with auth headers).
        access_key: AWS access key ID.
        secret_key: AWS secret access key.
        region: AWS region (use "auto" for R2).
        payload_hash: SHA256 hash of request payload.

    Returns:
        Headers dict with Authorization header added.
    """
    parsed = urlparse(url)
    path = parsed.path or "/"

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")

    headers["x-amz-date"] = timestamp
    headers["x-amz-content-sha256"] = payload_hash

    signed_headers = ";".join(sorted(k.lower() for k in headers.keys()))

    canonical_request = _create_canonical_request(
        method=method,
        path=path,
        query_string="",
        headers=headers,
        signed_headers=signed_headers,
        payload_hash=payload_hash,
    )

    string_to_sign = _create_string_to_sign(
        timestamp=timestamp,
        date_stamp=date_stamp,
        region=region,
        canonical_request=canonical_request,
    )

    signing_key = _get_signing_key(secret_key, date_stamp, region)
    signature = hmac.new(
        signing_key,
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    credential_scope = f"{date_stamp}/{region}/{SERVICE}/aws4_request"
    headers["Authorization"] = (
        f"{ALGORITHM} "
        f"Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )

    return headers


# ---------------------------------------------------------------------------
# S3 Operations
# ---------------------------------------------------------------------------

def put_object(
    endpoint: str,
    bucket: str,
    key: str,
    file_path: Path,
    access_key: str,
    secret_key: str,
    region: str = "auto",
    content_type: Optional[str] = None,
) -> None:
    """
    Upload a file to S3-compatible storage.

    Args:
        endpoint: S3 endpoint URL (e.g., https://account.r2.cloudflarestorage.com).
        bucket: Bucket name.
        key: Object key (path within bucket).
        file_path: Path to local file to upload.
        access_key: S3 access key ID.
        secret_key: S3 secret access key.
        region: AWS region (default "auto" for R2).
        content_type: Optional content type (auto-detected if not provided).

    Raises:
        requests.HTTPError: If upload fails.
        FileNotFoundError: If file_path doesn't exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read file content
    data = file_path.read_bytes()
    payload_hash = _sha256_hex(data)

    # Determine content type
    if content_type is None:
        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or "application/octet-stream"

    # Build URL and headers
    url = f"{endpoint.rstrip('/')}/{bucket}/{key.lstrip('/')}"
    parsed = urlparse(endpoint)

    headers = {
        "Host": parsed.netloc,
        "Content-Type": content_type,
        "Content-Length": str(len(data)),
    }

    # Sign request
    headers = _sign_request(
        method="PUT",
        url=url,
        headers=headers,
        access_key=access_key,
        secret_key=secret_key,
        region=region,
        payload_hash=payload_hash,
    )

    # Upload
    response = requests.put(url, headers=headers, data=data, timeout=300)
    response.raise_for_status()
