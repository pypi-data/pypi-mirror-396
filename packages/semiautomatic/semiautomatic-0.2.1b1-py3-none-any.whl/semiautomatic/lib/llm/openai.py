"""
OpenAI LLM provider.

Uses OpenAI API directly via requests (no SDK).
"""

from __future__ import annotations

import os
from typing import Optional

import requests

from semiautomatic.lib.llm.base import LLMProvider


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

DEFAULT_MODEL = "gpt-4o"

AVAILABLE_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
    "o1",
    "o1-mini",
    "o1-preview",
]


# ---------------------------------------------------------------------------
# Provider Implementation
# ---------------------------------------------------------------------------

class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM provider.

    Requires OPENAI_API_KEY environment variable.
    """

    def __init__(self):
        self._api_key = None

    @property
    def name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return DEFAULT_MODEL

    def list_models(self) -> list[str]:
        return AVAILABLE_MODELS.copy()

    @property
    def _key(self) -> str:
        """Lazy-load API key."""
        if self._api_key is None:
            key = os.environ.get("OPENAI_API_KEY")
            if not key:
                raise EnvironmentError(
                    "OPENAI_API_KEY environment variable not set. "
                    "Add OPENAI_API_KEY=... to your .env file."
                )
            # Strip quotes that dotenv might not handle
            self._api_key = key.strip().strip('"').strip("'")
        return self._api_key

    def _convert_messages(
        self,
        messages: list[dict],
        system: Optional[str] = None,
    ) -> list[dict]:
        """Convert messages to OpenAI format, adding system message if needed."""
        result = []

        # Add system message if provided
        if system:
            result.append({"role": "system", "content": system})

        # Convert messages
        for msg in messages:
            result.append(msg)

        return result

    def _make_request(
        self,
        messages: list[dict],
        *,
        model: Optional[str] = None,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> str:
        """Make a request to the OpenAI API."""
        model = model or self.default_model

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._key}",
        }

        converted_messages = self._convert_messages(messages, system)

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": converted_messages,
        }

        response = requests.post(
            OPENAI_API_URL,
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
                f"OpenAI API error ({response.status_code}): {error_msg}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]

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
            model: Model to use (default: gpt-4o).
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

        Messages can include image content blocks in OpenAI format:
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}},
                    {"type": "text", "text": "What's in this image?"}
                ]
            }

        Args:
            messages: List of message dicts with image content.
            model: Model to use (default: gpt-4o).
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
