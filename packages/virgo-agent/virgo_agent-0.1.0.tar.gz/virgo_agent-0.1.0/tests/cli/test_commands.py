"""Unit tests for the virgo.cli.commands module."""

from unittest.mock import Mock

from typer.testing import CliRunner

from virgo.agent.schemas import MarkdownArticle
from virgo.cli import app, container

runner = CliRunner()


class DescribeGenerateCommand:
    """Tests for the generate CLI command."""

    def it_generates_article_successfully(self):
        """Verify generate command outputs article on success."""
        mock_article = MarkdownArticle(
            title="Test Article",
            summary="A test summary.",
            content="## Introduction\n\nTest content.",
            references=["[1] Reference"],
        )

        mock_action = Mock()
        mock_action.execute.return_value = mock_article

        with container.generate_action.override(mock_action):
            result = runner.invoke(app, ["generate", "What is AI?"])

        assert result.exit_code == 0
        mock_action.execute.assert_called_once_with("What is AI?")

    def it_shows_error_on_generation_failure(self):
        """Verify generate command shows error when generation fails."""
        mock_action = Mock()
        mock_action.execute.return_value = None

        with container.generate_action.override(mock_action):
            result = runner.invoke(app, ["generate", "Some question"])

        assert result.exit_code == 0  # Typer doesn't exit with error by default
        assert "Failed to generate article" in result.output

    def it_requires_question_argument(self):
        """Verify generate command requires a question argument."""
        # Use a mock to avoid actual API calls
        mock_action = Mock()
        mock_action.execute.return_value = None

        with container.generate_action.override(mock_action):
            result = runner.invoke(app, ["generate"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Usage" in result.output


class DescribeAppCallback:
    """Tests for the main app callback."""

    def it_shows_help_with_no_args(self):
        """Verify app shows help when invoked without commands."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "generate" in result.output.lower()
        assert "virgo" in result.output.lower() or "article" in result.output.lower()


class DescribeContainer:
    """Tests for the DI container."""

    def it_provides_generate_action(self):
        """Verify container provides GenerateArticleAction."""
        from virgo.actions import GenerateArticleAction

        action = container.generate_action()

        assert isinstance(action, GenerateArticleAction)

    def it_provides_singleton_agent(self):
        """Verify container provides same agent instance."""
        agent1 = container.agent()
        agent2 = container.agent()

        assert agent1 is agent2

    def it_provides_new_action_per_call(self):
        """Verify container creates new action instance per call."""
        action1 = container.generate_action()
        action2 = container.generate_action()

        assert action1 is not action2

    def it_injects_agent_into_action(self):
        """Verify action receives the agent as generator."""
        action = container.generate_action()
        agent = container.agent()

        assert action.generator is agent
