"""Protocols (abstract interfaces) for dependency injection in Virgo actions."""

from typing import Protocol

from virgo.agent.schemas import MarkdownArticle


class ArticleGenerator(Protocol):
    """Protocol for article generation implementations.

    This protocol defines the interface for any article generator,
    allowing for dependency injection and easy testing/mocking.
    """

    def generate(self, question: str) -> MarkdownArticle | None:
        """Generate an article based on the input question.

        Args:
            question: The question to generate an article for.

        Returns:
            MarkdownArticle if generation succeeded, None otherwise.
        """
        ...


__all__ = [
    "ArticleGenerator",
]
