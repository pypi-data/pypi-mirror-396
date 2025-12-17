"""Unit tests for the virgo.actions.protocols module."""

from virgo.actions.protocols import ArticleGenerator
from virgo.agent.schemas import MarkdownArticle


class DescribeArticleGeneratorProtocol:
    """Tests for the ArticleGenerator protocol."""

    def it_defines_generate_method(self):
        """Verify protocol defines generate method signature."""
        # The protocol should have a generate method
        assert hasattr(ArticleGenerator, "generate")

    def it_accepts_conforming_implementation(self):
        """Verify a conforming class is accepted as ArticleGenerator."""

        class MockGenerator:
            def generate(self, question: str) -> MarkdownArticle | None:
                return MarkdownArticle(
                    title="Test",
                    summary="Summary",
                    content="Content",
                )

        # This should not raise - the mock conforms to the protocol
        generator: ArticleGenerator = MockGenerator()
        result = generator.generate("test question")

        assert result is not None
        assert isinstance(result, MarkdownArticle)
        assert result.title == "Test"

    def it_accepts_none_return_value(self):
        """Verify protocol accepts None as valid return value."""

        class FailingGenerator:
            def generate(self, question: str) -> MarkdownArticle | None:
                return None

        generator: ArticleGenerator = FailingGenerator()
        result = generator.generate("test")

        assert result is None
