"""Pytest configuration for integration tests."""

import os

import pytest

# Default Ollama model for integration tests
# Can be overridden via OLLAMA_MODEL environment variable
DEFAULT_OLLAMA_MODEL = "llama3.2:1b"


@pytest.fixture
def ollama_model() -> str:
    """Provide the Ollama model name for LLM-based tests.

    The model can be configured via the OLLAMA_MODEL environment variable.
    Defaults to 'llama3.2:1b' for fast, cost-effective testing.

    Returns:
        str: The Ollama model identifier in LangChain format (e.g., 'ollama:llama3.2:1b')
    """
    model_name = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    return f"ollama:{model_name}"


@pytest.fixture
def ollama_base_url() -> str:
    """Provide the Ollama API base URL.

    Can be configured via the OLLAMA_BASE_URL environment variable.
    Defaults to 'http://localhost:11434' for local Docker setup.

    Returns:
        str: The Ollama API base URL
    """
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


@pytest.fixture
def sample_question() -> str:
    """Provide a sample question for testing the agent."""
    return "What are the main differences between Python and JavaScript?"


@pytest.fixture
def simple_question() -> str:
    """Provide a simple question for quick testing."""
    return "What is Python?"
