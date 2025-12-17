"""Module for managing GenAI providers and creating language model instances."""

from abc import ABC, abstractmethod
from typing import override

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI


class ProviderError(Exception):
    """Exception raised for errors in the GenAI provider selection."""

    pass


class LanguageModelProvider(ABC):
    """Abstract base class for language model providers."""

    @abstractmethod
    def get_chat_model(self, model_name: str) -> BaseChatModel:
        """Get the chat model instance for the given model name.

        Args:
            model_name (str): The name of the model to instantiate.
        Returns:
            BaseChatModel: An instance of the specified language model.
        Raises:
            ProviderError: If there is an error creating the model instance.
        """
        ...


class OpenAILanguageModelProvider(LanguageModelProvider):
    """Language model provider for OpenAI."""

    @override
    def get_chat_model(self, model_name: str) -> BaseChatModel:
        return ChatOpenAI(model=model_name)


class OllamaLanguageModelProvider(LanguageModelProvider):
    """Language model provider for Ollama."""

    @override
    def get_chat_model(self, model_name: str) -> BaseChatModel:
        try:
            from langchain_ollama import ChatOllama
            from ollama import Client

            client = Client()
            client._request_raw()  # Test connection
            return ChatOllama(
                model=model_name,
            )
        except ImportError as e:
            raise ProviderError(
                "langchain_ollama is not installed. Please install it to use the Ollama provider.",
            ) from e
        except ConnectionError as e:
            raise ProviderError(
                "Ollama client could not connect to the Ollama server. Please ensure the Ollama server is running, or the `OLLAMA_HOST` environment variable is set correctly."
            ) from e
