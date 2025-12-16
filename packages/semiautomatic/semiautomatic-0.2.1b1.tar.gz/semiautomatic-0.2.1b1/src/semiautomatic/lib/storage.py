"""
Storage backends for semiautomatic.

Provides abstract storage interface and implementations for cloud storage.
Used for LoRA uploads, image hosting, and other file operations.

Library usage:
    from semiautomatic.lib.storage import R2Backend, get_storage_backend

    # Get configured backend from environment
    storage = get_storage_backend()
    url = storage.upload(Path("lora.safetensors"), "loras/my-lora.safetensors")

    # Or configure explicitly
    storage = R2Backend(
        endpoint="https://...",
        access_key="...",
        secret_key="...",
        bucket="my-bucket",
        public_url="https://pub-..."
    )
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Storage Protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class StorageBackend(Protocol):
    """Protocol for storage backends.

    Implement this protocol to create custom storage backends.
    """

    def upload(self, local_path: Path, key: str) -> str:
        """
        Upload a file to storage.

        Args:
            local_path: Path to local file.
            key: Storage key (path within bucket/container).

        Returns:
            Public URL to the uploaded file.
        """
        ...

    def upload_image(self, image_path: Path, prefix: str = "images") -> str:
        """
        Upload an image file.

        Args:
            image_path: Path to image file.
            prefix: Key prefix for organization.

        Returns:
            Public URL to the uploaded image.
        """
        ...

    def upload_lora(self, lora_path: Path) -> str:
        """
        Upload a LoRA file.

        Args:
            lora_path: Path to .safetensors file.

        Returns:
            Public URL to the uploaded LoRA.
        """
        ...


# ---------------------------------------------------------------------------
# R2 Backend
# ---------------------------------------------------------------------------

@dataclass
class R2Config:
    """Configuration for Cloudflare R2 storage."""

    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    public_url: str

    @classmethod
    def from_env(cls) -> "R2Config":
        """
        Create R2Config from environment variables.

        Required environment variables:
            EU_ENDPOINT: R2 endpoint URL
            CLOUDFLARE_S3_ACCESS_KEY: Access key
            CLOUDFLARE_S3_SECRET_ACCESS: Secret key
            R2_BUCKET_NAME: Bucket name
            R2_PUBLIC_URL: Public URL prefix

        Raises:
            EnvironmentError: If required variables are missing.
        """
        from semiautomatic.lib.env import require_env

        return cls(
            endpoint=require_env("EU_ENDPOINT", "R2 endpoint URL"),
            access_key=require_env("CLOUDFLARE_S3_ACCESS_KEY", "R2 access key"),
            secret_key=require_env("CLOUDFLARE_S3_SECRET_ACCESS", "R2 secret key"),
            bucket=require_env("R2_BUCKET_NAME", "R2 bucket name"),
            public_url=require_env("R2_PUBLIC_URL", "R2 public URL prefix"),
        )


class R2Backend:
    """Cloudflare R2 storage backend."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket: Optional[str] = None,
        public_url: Optional[str] = None,
        config: Optional[R2Config] = None,
    ):
        """
        Initialize R2 backend.

        Args:
            endpoint: R2 endpoint URL.
            access_key: S3 access key.
            secret_key: S3 secret key.
            bucket: Bucket name.
            public_url: Public URL prefix for uploaded files.
            config: R2Config object (alternative to individual params).

        If no arguments provided, loads from environment variables.
        """
        if config:
            self._config = config
        elif all([endpoint, access_key, secret_key, bucket, public_url]):
            self._config = R2Config(
                endpoint=endpoint,
                access_key=access_key,
                secret_key=secret_key,
                bucket=bucket,
                public_url=public_url,
            )
        else:
            self._config = R2Config.from_env()

    def upload(self, local_path: Path, key: str) -> str:
        """
        Upload a file to R2.

        Args:
            local_path: Path to local file.
            key: Storage key (path within bucket).

        Returns:
            Public URL to the uploaded file.
        """
        from semiautomatic.lib.s3 import put_object

        put_object(
            endpoint=self._config.endpoint,
            bucket=self._config.bucket,
            key=key,
            file_path=local_path,
            access_key=self._config.access_key,
            secret_key=self._config.secret_key,
        )

        return f"{self._config.public_url}/{key}"

    def upload_image(self, image_path: Path, prefix: str = "images") -> str:
        """
        Upload an image file.

        Args:
            image_path: Path to image file.
            prefix: Key prefix for organization.

        Returns:
            Public URL to the uploaded image.
        """
        key = f"{prefix}/{image_path.name}"
        return self.upload(image_path, key)

    def upload_lora(self, lora_path: Path) -> str:
        """
        Upload a LoRA file.

        Args:
            lora_path: Path to .safetensors file.

        Returns:
            Public URL to the uploaded LoRA.
        """
        key = f"loras/{lora_path.name}"
        return self.upload(lora_path, key)


# ---------------------------------------------------------------------------
# Backend Factory
# ---------------------------------------------------------------------------

_default_backend: Optional[StorageBackend] = None


def get_storage_backend(backend_type: str = "r2") -> StorageBackend:
    """
    Get a storage backend instance.

    Args:
        backend_type: Type of backend ("r2" currently supported).

    Returns:
        Configured storage backend.

    Raises:
        ValueError: If backend_type is not supported.
    """
    global _default_backend

    if backend_type == "r2":
        if _default_backend is None:
            _default_backend = R2Backend()
        return _default_backend
    else:
        raise ValueError(
            f"Unknown storage backend: {backend_type}. Supported: r2"
        )


def set_storage_backend(backend: StorageBackend) -> None:
    """
    Set the default storage backend.

    Useful for testing or custom storage implementations.

    Args:
        backend: Storage backend instance.
    """
    global _default_backend
    _default_backend = backend
