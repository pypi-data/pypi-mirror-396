"""Dependency injection container for Virgo CLI."""

from typing import Annotated, Literal

from dependency_injector import containers, providers
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from virgo.actions import GenerateArticleAction
from virgo.agent.factories import create_virgo_agent
from virgo.agent.llms import (
    LanguageModelProvider,
    OllamaLanguageModelProvider,
    OpenAILanguageModelProvider,
)

type _GenAIProvider = Literal["openai", "ollama"]
"""Supported GenAI providers."""


class VirgoSettings(BaseSettings):
    """Settings for the Virgo application."""

    model_config = SettingsConfigDict(env_prefix="virgo_")

    genai_provider: Annotated[
        _GenAIProvider,
        Field(
            help="The GenAI provider to use for language model interactions.",
        ),
    ] = "openai"
    model_name: Annotated[
        str,
        Field(
            help="""
            The name of the model to use from the GenAI provider.
                                
            It should correspond to a valid model name for the selected provider. Also, ensure that the model supports tool usage.
                                    
            It is recommended to use models with reliable reasoning capabilities.
            """,
        ),
    ] = "gpt-4-turbo"
    max_iterations: Annotated[
        int,
        Field(
            help="The maximum number of iterations for the Virgo agent's reasoning process.",
        ),
    ] = 5


class Container(containers.DeclarativeContainer):
    """DI container for Virgo application.

    This container manages the dependencies for the Virgo CLI,
    providing configured instances of agents and actions.

    Example usage:
        ```python
        from virgo.cli import container

        # Override for testing
        with container.generate_action.override(mock_action):
            result = runner.invoke(app, ["generate", "question"])
        ```
    """

    wiring_config = containers.WiringConfiguration(
        modules=["virgo.cli.commands"],
    )

    config = providers.Configuration(strict=True)
    """The configuration provider for Virgo settings."""

    _language_model_provider = providers.Selector[LanguageModelProvider](
        config.genai_provider,
        openai=providers.Singleton(OpenAILanguageModelProvider),
        ollama=providers.Singleton(OllamaLanguageModelProvider),
    )

    _chat_model = providers.Callable(
        lambda provider, model_name: provider.get_chat_model(model_name),
        provider=_language_model_provider,
        model_name=config.model_name,
    )

    _agent = providers.Singleton(
        create_virgo_agent,
        llm=_chat_model,
    )
    """The Virgo agent singleton provider."""

    generate_action = providers.Factory(
        GenerateArticleAction,
        generator=_agent,
    )
    """The action provider for generating articles."""


__all__ = [
    "Container",
    "VirgoSettings",
]
