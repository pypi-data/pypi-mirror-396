"""Generate article action - use case for article generation."""

from dataclasses import dataclass

from virgo.actions.protocols import ArticleGenerator
from virgo.agent.schemas import MarkdownArticle


@dataclass
class GenerateArticleAction:
    """Action to generate an article from a question.

    This action encapsulates the use case of generating an article,
    depending on an ArticleGenerator protocol for the actual generation.
    This design facilitates dependency injection and testing.

    Example usage with dependency-injector:
        ```python
        from dependency_injector import containers, providers
        from virgo.actions import GenerateArticleAction
        from virgo.agent import VirgoAgent

        class Container(containers.DeclarativeContainer):
            agent = providers.Singleton(VirgoAgent)
            generate_action = providers.Factory(
                GenerateArticleAction,
                generator=agent,
            )
        ```
    """

    generator: ArticleGenerator

    def execute(self, question: str) -> MarkdownArticle | None:
        """Execute the article generation action.

        Args:
            question: The question to generate an article for.

        Returns:
            MarkdownArticle if generation succeeded, None otherwise.
        """
        return self.generator.generate(question)


__all__ = [
    "GenerateArticleAction",
]
