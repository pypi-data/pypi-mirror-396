"""Unit tests for the Virgo GenAI provider abstractions."""

from __future__ import annotations

import sys
import types

import pytest

from virgo.agent.llms import (
    OllamaLanguageModelProvider,
    OpenAILanguageModelProvider,
    ProviderError,
)


class DescribeOpenAIProvider:
    def it_creates_a_chat_model_instance(self):
        provider = OpenAILanguageModelProvider()
        model = provider.get_chat_model("gpt-4-turbo")

        assert model.__class__.__name__ == "ChatOpenAI"
        # Be tolerant across langchain-openai versions.
        assert (
            getattr(model, "model", None) == "gpt-4-turbo"
            or getattr(model, "model_name", None) == "gpt-4-turbo"
        )


class DescribeOllamaProvider:
    def it_raises_provider_error_when_cannot_connect(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """Avoid real network calls by faking the imported modules."""

        class FakeClient:
            def _request_raw(self):
                raise ConnectionError("no server")

        fake_langchain_ollama = types.SimpleNamespace(
            ChatOllama=lambda **_kwargs: object()
        )
        fake_ollama = types.SimpleNamespace(Client=FakeClient)

        monkeypatch.setitem(sys.modules, "langchain_ollama", fake_langchain_ollama)
        monkeypatch.setitem(sys.modules, "ollama", fake_ollama)

        provider = OllamaLanguageModelProvider()

        with pytest.raises(ProviderError):
            provider.get_chat_model("llama3")
