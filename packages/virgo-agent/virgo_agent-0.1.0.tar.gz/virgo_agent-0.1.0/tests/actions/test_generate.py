"""Unit tests for the virgo.actions.generate module."""

from unittest.mock import Mock

from virgo.actions.generate import GenerateArticleAction
from virgo.actions.protocols import ArticleGenerator
from virgo.agent.schemas import MarkdownArticle


class DescribeGenerateArticleAction:
    """Tests for the GenerateArticleAction class."""

    def it_initializes_with_generator(self):
        """Verify action can be initialized with a generator."""
        mock_generator = Mock(spec=ArticleGenerator)
        action = GenerateArticleAction(generator=mock_generator)

        assert action.generator is mock_generator

    def it_executes_generation_via_generator(self):
        """Verify execute calls generator.generate with question."""
        mock_generator = Mock(spec=ArticleGenerator)
        expected_article = MarkdownArticle(
            title="Test Article",
            summary="A summary.",
            content="Content here.",
        )
        mock_generator.generate.return_value = expected_article

        action = GenerateArticleAction(generator=mock_generator)
        result = action.execute("What is AI?")

        mock_generator.generate.assert_called_once_with("What is AI?")
        assert result == expected_article

    def it_returns_none_when_generator_fails(self):
        """Verify execute returns None when generator returns None."""
        mock_generator = Mock(spec=ArticleGenerator)
        mock_generator.generate.return_value = None

        action = GenerateArticleAction(generator=mock_generator)
        result = action.execute("some question")

        assert result is None

    def it_passes_question_to_generator(self):
        """Verify the question is passed correctly to the generator."""
        mock_generator = Mock(spec=ArticleGenerator)
        mock_generator.generate.return_value = None

        action = GenerateArticleAction(generator=mock_generator)
        action.execute("Complex question about cybersecurity?")

        mock_generator.generate.assert_called_once_with(
            "Complex question about cybersecurity?"
        )

    def it_is_a_dataclass(self):
        """Verify GenerateArticleAction is a dataclass."""
        import dataclasses

        assert dataclasses.is_dataclass(GenerateArticleAction)

    def it_supports_dependency_injection(self):
        """Verify action works with different generator implementations."""

        class CustomGenerator:
            def __init__(self, prefix: str):
                self.prefix = prefix

            def generate(self, question: str) -> MarkdownArticle | None:
                return MarkdownArticle(
                    title=f"{self.prefix}: {question}",
                    summary="Generated summary.",
                    content="Generated content.",
                )

        generator = CustomGenerator(prefix="Article")
        action = GenerateArticleAction(generator=generator)
        result = action.execute("Test Question")

        assert result is not None
        assert result.title == "Article: Test Question"
