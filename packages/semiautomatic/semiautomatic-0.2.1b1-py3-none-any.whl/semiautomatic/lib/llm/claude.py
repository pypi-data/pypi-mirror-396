"""
Claude (Anthropic) LLM provider.

Uses Anthropic API directly via requests (no SDK).
"""

from __future__ import annotations

import os
from typing import Optional

import requests

from semiautomatic.lib.llm.base import LLMProvider


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"

AVAILABLE_MODELS = [
    "claude-opus-4-5-20251101",
    "claude-sonnet-4-5-20250929",
    "claude-haiku-3-5-20241022",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
    "claude-3-opus-20240229",
]


# ---------------------------------------------------------------------------
# Provider Implementation
# ---------------------------------------------------------------------------

class ClaudeProvider(LLMProvider):
    """
    Claude LLM provider via Anthropic API.

    Requires ANTHROPIC_API_KEY environment variable.
    """

    def __init__(self):
        self._api_key = None

    @property
    def name(self) -> str:
        return "claude"

    @property
    def default_model(self) -> str:
        return DEFAULT_MODEL

    def list_models(self) -> list[str]:
        return AVAILABLE_MODELS.copy()

    @property
    def _key(self) -> str:
        """Lazy-load API key."""
        if self._api_key is None:
            key = os.environ.get("ANTHROPIC_API_KEY")
            if not key:
                raise EnvironmentError(
                    "ANTHROPIC_API_KEY environment variable not set. "
                    "Add ANTHROPIC_API_KEY=... to your .env file."
                )
            # Strip quotes that dotenv might not handle
            self._api_key = key.strip().strip('"').strip("'")
        return self._api_key

    def _make_request(
        self,
        messages: list[dict],
        *,
        model: Optional[str] = None,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> str:
        """Make a request to the Anthropic API."""
        model = model or self.default_model

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self._key,
            "anthropic-version": ANTHROPIC_API_VERSION,
        }

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        if system:
            payload["system"] = system

        response = requests.post(
            ANTHROPIC_API_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )

        if response.status_code != 200:
            error_msg = response.text
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", error_msg)
            except Exception:
                pass
            raise RuntimeError(
                f"Anthropic API error ({response.status_code}): {error_msg}"
            )

        data = response.json()
        return data["content"][0]["text"]

    def complete(
        self,
        messages: list[dict],
        *,
        model: Optional[str] = None,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        **kwargs,
    ) -> str:
        """
        Generate a completion from messages.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: Model to use (default: claude-sonnet-4-5-20250929).
            system: System prompt to use.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.

        Returns:
            Generated text content.
        """
        return self._make_request(
            messages,
            model=model,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def complete_with_vision(
        self,
        messages: list[dict],
        *,
        model: Optional[str] = None,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        **kwargs,
    ) -> str:
        """
        Generate a completion from messages that may include images.

        Messages can include image content blocks:
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}},
                    {"type": "text", "text": "What's in this image?"}
                ]
            }

        Args:
            messages: List of message dicts with image content.
            model: Model to use (default: claude-sonnet-4-5-20250929).
            system: System prompt to use.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.

        Returns:
            Generated text content.
        """
        return self._make_request(
            messages,
            model=model,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
        )
