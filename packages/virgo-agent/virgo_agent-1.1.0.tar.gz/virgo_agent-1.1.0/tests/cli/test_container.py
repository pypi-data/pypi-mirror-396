"""Unit tests for the Virgo DI container and settings."""

import pytest
from dependency_injector import providers

from virgo.agent.llms import OllamaLanguageModelProvider, OpenAILanguageModelProvider
from virgo.cli.container import Container, VirgoSettings


class DescribeVirgoSettings:
    """Tests for the settings model loading environment variables."""

    def it_uses_defaults_when_env_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("VIRGO_GENAI_PROVIDER", raising=False)
        monkeypatch.delenv("VIRGO_MODEL_NAME", raising=False)
        monkeypatch.delenv("VIRGO_MAX_ITERATIONS", raising=False)

        settings = VirgoSettings()

        assert settings.genai_provider == "openai"
        assert settings.model_name == "gpt-4-turbo"
        assert settings.max_iterations == 5

    def it_loads_values_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VIRGO_GENAI_PROVIDER", "ollama")
        monkeypatch.setenv("VIRGO_MODEL_NAME", "llama3")
        monkeypatch.setenv("VIRGO_MAX_ITERATIONS", "7")

        settings = VirgoSettings()

        assert settings.genai_provider == "ollama"
        assert settings.model_name == "llama3"
        assert settings.max_iterations == 7


class DescribeContainer:
    """Tests for container providers and wiring."""

    def it_loads_config_from_settings(self) -> None:
        settings = VirgoSettings()
        container = Container()
        container.config.from_pydantic(settings)

        assert container.config.genai_provider() == settings.genai_provider
        assert container.config.model_name() == settings.model_name

    def it_selects_openai_provider(self) -> None:
        settings = VirgoSettings(genai_provider="openai")
        container = Container()
        container.config.from_pydantic(settings)

        provider = container._language_model_provider()
        assert isinstance(provider, OpenAILanguageModelProvider)

    def it_selects_ollama_provider(self) -> None:
        settings = VirgoSettings(genai_provider="ollama")
        container = Container()
        container.config.from_pydantic(settings)

        provider = container._language_model_provider()
        assert isinstance(provider, OllamaLanguageModelProvider)

    def it_provides_generate_action_with_overridden_agent(self) -> None:
        container = Container()
        container.config.from_pydantic(VirgoSettings())

        dummy_agent = object()
        with container._agent.override(providers.Object(dummy_agent)):
            action = container.generate_action()

        assert action.generator is dummy_agent
