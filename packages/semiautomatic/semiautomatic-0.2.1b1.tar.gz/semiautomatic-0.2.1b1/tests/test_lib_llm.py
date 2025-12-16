"""
Tests for semiautomatic.lib.llm module.

Tests cover:
- LLM provider registry
- ClaudeProvider (mocked)
- OpenAIProvider (mocked)
- Public API functions
"""

import pytest
from unittest.mock import patch, MagicMock

from semiautomatic.lib.llm import (
    complete,
    complete_with_vision,
    get_provider,
    list_providers,
    register_provider,
    LLMProvider,
    ClaudeProvider,
    OpenAIProvider,
)


class TestProviderRegistry:
    """Tests for provider registry functions."""

    def test_list_providers_includes_claude(self):
        """Should include claude in available providers."""
        providers = list_providers()
        assert "claude" in providers

    def test_list_providers_includes_openai(self):
        """Should include openai in available providers."""
        providers = list_providers()
        assert "openai" in providers

    def test_get_provider_returns_claude(self):
        """Should return ClaudeProvider for 'claude'."""
        provider = get_provider("claude")
        assert isinstance(provider, ClaudeProvider)

    def test_get_provider_returns_openai(self):
        """Should return OpenAIProvider for 'openai'."""
        provider = get_provider("openai")
        assert isinstance(provider, OpenAIProvider)

    def test_get_provider_default_is_claude(self):
        """Should return claude when no name specified."""
        provider = get_provider()
        assert isinstance(provider, ClaudeProvider)

    def test_get_provider_raises_for_unknown(self):
        """Should raise ValueError for unknown provider."""
        with pytest.raises(ValueError) as exc_info:
            get_provider("nonexistent_provider")

        assert "nonexistent_provider" in str(exc_info.value)

    def test_register_provider_adds_new_provider(self):
        """Should be able to register custom providers."""

        class CustomLLMProvider(LLMProvider):
            @property
            def name(self):
                return "custom"

            def complete(self, messages, **kwargs):
                return "custom response"

            def complete_with_vision(self, messages, **kwargs):
                return "custom vision response"

            def list_models(self):
                return ["custom-model"]

        register_provider("custom_llm", CustomLLMProvider)

        providers = list_providers()
        assert "custom_llm" in providers


class TestClaudeProvider:
    """Tests for ClaudeProvider."""

    def test_name_is_claude(self):
        """Provider name should be 'claude'."""
        provider = ClaudeProvider()
        assert provider.name == "claude"

    def test_default_model(self):
        """Should have a default model set."""
        provider = ClaudeProvider()
        assert provider.default_model is not None
        assert "claude" in provider.default_model

    def test_list_models_returns_list(self):
        """Should return list of available models."""
        provider = ClaudeProvider()
        models = provider.list_models()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_raises_without_api_key(self):
        """Should raise EnvironmentError when ANTHROPIC_API_KEY not set."""
        provider = ClaudeProvider()

        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(EnvironmentError) as exc_info:
                provider._key

            assert "ANTHROPIC_API_KEY" in str(exc_info.value)


class TestOpenAIProvider:
    """Tests for OpenAIProvider."""

    def test_name_is_openai(self):
        """Provider name should be 'openai'."""
        provider = OpenAIProvider()
        assert provider.name == "openai"

    def test_default_model_is_gpt4o(self):
        """Default model should be gpt-4o."""
        provider = OpenAIProvider()
        assert provider.default_model == "gpt-4o"

    def test_list_models_includes_gpt4o(self):
        """Should list gpt-4o as available model."""
        provider = OpenAIProvider()
        models = provider.list_models()
        assert "gpt-4o" in models

    def test_raises_without_api_key(self):
        """Should raise EnvironmentError when OPENAI_API_KEY not set."""
        provider = OpenAIProvider()

        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(EnvironmentError) as exc_info:
                provider._key

            assert "OPENAI_API_KEY" in str(exc_info.value)


class TestComplete:
    """Tests for complete() public API."""

    def test_calls_provider_complete(self):
        """Should call provider's complete method."""
        with patch.object(ClaudeProvider, "complete", return_value="test response") as mock:
            result = complete([{"role": "user", "content": "Hello"}])

            mock.assert_called_once()
            assert result == "test response"

    def test_passes_messages_to_provider(self):
        """Should pass messages to provider."""
        messages = [{"role": "user", "content": "Test message"}]

        with patch.object(ClaudeProvider, "complete", return_value="response") as mock:
            complete(messages)

            call_args = mock.call_args[0]
            assert call_args[0] == messages

    def test_passes_system_prompt(self):
        """Should pass system prompt to provider."""
        with patch.object(ClaudeProvider, "complete", return_value="response") as mock:
            complete(
                [{"role": "user", "content": "Hi"}],
                system="You are helpful."
            )

            call_kwargs = mock.call_args[1]
            assert call_kwargs.get("system") == "You are helpful."

    def test_passes_temperature(self):
        """Should pass temperature to provider."""
        with patch.object(ClaudeProvider, "complete", return_value="response") as mock:
            complete(
                [{"role": "user", "content": "Hi"}],
                temperature=0.5
            )

            call_kwargs = mock.call_args[1]
            assert call_kwargs.get("temperature") == 0.5

    def test_uses_specified_provider(self):
        """Should use specified provider."""
        with patch.object(OpenAIProvider, "complete", return_value="openai response") as mock:
            result = complete(
                [{"role": "user", "content": "Hi"}],
                provider="openai"
            )

            mock.assert_called_once()
            assert result == "openai response"


class TestCompleteWithVision:
    """Tests for complete_with_vision() public API."""

    def test_calls_provider_complete_with_vision(self):
        """Should call provider's complete_with_vision method."""
        with patch.object(
            ClaudeProvider, "complete_with_vision", return_value="vision response"
        ) as mock:
            result = complete_with_vision([{"role": "user", "content": "Describe"}])

            mock.assert_called_once()
            assert result == "vision response"

    def test_passes_image_content(self):
        """Should pass image content blocks to provider."""
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "data": "..."}},
                {"type": "text", "text": "What is this?"}
            ]
        }]

        with patch.object(
            ClaudeProvider, "complete_with_vision", return_value="response"
        ) as mock:
            complete_with_vision(messages)

            call_args = mock.call_args[0]
            assert call_args[0] == messages


@pytest.mark.integration
class TestClaudeIntegration:
    """Integration tests for Claude provider.

    These tests require ANTHROPIC_API_KEY to be set and make real API calls.
    Run with: pytest -m integration
    """

    def test_complete_generates_response(self, integration_output_dir):
        """Should generate a response from Claude."""
        import os

        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        result = complete(
            [{"role": "user", "content": "Say 'hello' and nothing else."}],
            max_tokens=10
        )

        assert isinstance(result, str)
        assert len(result) > 0

        output_file = integration_output_dir / "claude_complete.txt"
        output_file.write_text(f"Response: {result}")


@pytest.mark.integration
class TestOpenAIIntegration:
    """Integration tests for OpenAI provider.

    These tests require OPENAI_API_KEY to be set and make real API calls.
    Run with: pytest -m integration
    """

    def test_complete_generates_response(self, integration_output_dir):
        """Should generate a response from OpenAI."""
        import os

        if not os.environ.get("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        result = complete(
            [{"role": "user", "content": "Say 'hello' and nothing else."}],
            provider="openai",
            max_tokens=10
        )

        assert isinstance(result, str)
        assert len(result) > 0

        output_file = integration_output_dir / "openai_complete.txt"
        output_file.write_text(f"Response: {result}")
