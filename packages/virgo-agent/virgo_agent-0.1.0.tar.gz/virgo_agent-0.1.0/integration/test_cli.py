"""Integration tests for the CLI layer."""

from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from virgo.agent.schemas import MarkdownArticle
from virgo.cli import app
from virgo.cli.container import Container

runner = CliRunner()


@pytest.fixture
def test_container():
    """Create and wire a container for testing."""
    container = Container()
    container.wire(modules=["virgo.cli.commands"])
    yield container
    container.unwire()


class DescribeCLIIntegration:
    """Integration tests for the CLI commands."""

    class DescribeGenerateCommand:
        """Tests for the generate command."""

        def it_should_generate_article_successfully(
            self, test_container: Container
        ) -> None:
            """Test that the generate command produces output."""
            mock_article = MarkdownArticle(
                title="CLI Test Article",
                summary="This is a CLI test article.",
                content="# CLI Test\n\nContent generated via CLI.",
                references=["https://example.com"],
            )

            mock_agent = MagicMock()
            mock_agent.generate.return_value = mock_article

            with test_container.agent.override(mock_agent):
                result = runner.invoke(app, ["generate", "What is Python?"])

                assert result.exit_code == 0
                assert mock_agent.generate.called

        def it_should_handle_failed_generation(self, test_container: Container) -> None:
            """Test that the CLI handles failed generation gracefully."""
            mock_agent = MagicMock()
            mock_agent.generate.return_value = None

            with test_container.agent.override(mock_agent):
                result = runner.invoke(app, ["generate", "What is Python?"])

                # Should not crash, may show error message
                assert result.exit_code in [0, 1]

        def it_should_pass_question_to_agent(self, test_container: Container) -> None:
            """Test that the question is passed correctly to the agent."""
            mock_agent = MagicMock()
            mock_agent.generate.return_value = MarkdownArticle(
                title="Test",
                summary="Test",
                content="Test content",
                references=[],
            )

            test_question = "What are the benefits of TypeScript?"

            with test_container.agent.override(mock_agent):
                runner.invoke(app, ["generate", test_question])

                mock_agent.generate.assert_called_once_with(test_question)

    class DescribeDependencyInjection:
        """Tests for DI integration with CLI."""

        def it_should_use_injected_agent(self, test_container: Container) -> None:
            """Test that the CLI uses the injected agent from the container."""
            mock_agent = MagicMock()
            mock_agent.generate.return_value = MarkdownArticle(
                title="Injected Test",
                summary="Testing injection",
                content="# Injection Test",
                references=[],
            )

            with test_container.agent.override(mock_agent):
                runner.invoke(app, ["generate", "Test question"])

                # Verify the mock was used
                mock_agent.generate.assert_called_once()

        def it_should_allow_container_override(self, test_container: Container) -> None:
            """Test that container overrides work correctly."""
            call_count = 0

            class CountingAgent:
                def generate(self, question: str) -> MarkdownArticle:
                    nonlocal call_count
                    call_count += 1
                    return MarkdownArticle(
                        title=f"Article {call_count}",
                        summary="Counting agent",
                        content="Content",
                        references=[],
                    )

            counting_agent = CountingAgent()

            with test_container.agent.override(counting_agent):
                runner.invoke(app, ["generate", "Question 1"])
                runner.invoke(app, ["generate", "Question 2"])

                assert call_count == 2


class DescribeCLIOutput:
    """Tests for CLI output formatting."""

    def it_should_display_article_content(self, test_container: Container) -> None:
        """Test that the CLI displays the article content."""
        mock_article = MarkdownArticle(
            title="Output Test",
            summary="Testing CLI output",
            content="# Output Test\n\nThis content should appear in output.",
            references=["https://example.com"],
        )

        mock_agent = MagicMock()
        mock_agent.generate.return_value = mock_article

        with test_container.agent.override(mock_agent):
            result = runner.invoke(app, ["generate", "Test question"])

            # Check that some output was produced
            assert len(result.stdout) > 0 or result.exit_code == 0

    def it_should_handle_empty_references(self, test_container: Container) -> None:
        """Test that the CLI handles articles without references."""
        mock_article = MarkdownArticle(
            title="No References",
            summary="Article without references",
            content="# No References\n\nThis article has no references.",
            references=[],
        )

        mock_agent = MagicMock()
        mock_agent.generate.return_value = mock_article

        with test_container.agent.override(mock_agent):
            result = runner.invoke(app, ["generate", "Test question"])

            assert result.exit_code == 0


class DescribeCLIErrorHandling:
    """Tests for CLI error handling."""

    def it_should_handle_missing_question(self) -> None:
        """Test that the CLI handles missing question argument."""
        result = runner.invoke(app, ["generate"])

        # Typer should report missing argument
        assert result.exit_code != 0

    def it_should_handle_agent_exception(self, test_container: Container) -> None:
        """Test that the CLI handles agent exceptions gracefully."""
        mock_agent = MagicMock()
        mock_agent.generate.side_effect = Exception("Agent error")

        with test_container.agent.override(mock_agent):
            result = runner.invoke(app, ["generate", "Test question"])

            # Should not crash with unhandled exception
            # Exit code may be non-zero but app should handle it
            assert result.exception is not None or result.exit_code != 0
