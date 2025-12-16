"""Unit tests for the Virgo agent schemas module."""

import pytest
from pydantic import ValidationError

from virgo.agent.schemas import Answer, MarkdownArticle, Reflection, Revised


class DescribeReflection:
    """Tests for the Reflection schema."""

    def it_creates_with_required_fields(self):
        """Verify Reflection can be created with required fields."""
        reflection = Reflection(
            missing="Missing some details",
            superfluous="Too much background info",
        )

        assert reflection.missing == "Missing some details"
        assert reflection.superfluous == "Too much background info"

    def it_requires_missing_field(self):
        """Verify missing field is required."""
        with pytest.raises(ValidationError):
            Reflection(superfluous="Some text")  # type: ignore[call-arg]

    def it_requires_superfluous_field(self):
        """Verify superfluous field is required."""
        with pytest.raises(ValidationError):
            Reflection(missing="Some text")  # type: ignore[call-arg]


class DescribeAnswer:
    """Tests for the Answer schema."""

    def it_creates_with_required_fields(self):
        """Verify Answer can be created with required fields."""
        reflection = Reflection(missing="None", superfluous="None")
        answer = Answer(
            value="This is a detailed answer about the topic.",
            reflection=reflection,
        )

        assert answer.value == "This is a detailed answer about the topic."
        assert answer.reflection == reflection
        assert answer.search_queries == []

    def it_defaults_search_queries_to_empty_list(self):
        """Verify search_queries defaults to empty list."""
        answer = Answer(
            value="Test answer",
            reflection=Reflection(missing="None", superfluous="None"),
        )

        assert answer.search_queries == []
        assert isinstance(answer.search_queries, list)

    def it_accepts_search_queries(self):
        """Verify search_queries can be provided."""
        queries = ["query 1", "query 2", "query 3"]
        answer = Answer(
            value="Test answer",
            reflection=Reflection(missing="None", superfluous="None"),
            search_queries=queries,
        )

        assert answer.search_queries == queries
        assert len(answer.search_queries) == 3

    def it_requires_value_field(self):
        """Verify value field is required."""
        with pytest.raises(ValidationError):
            Answer(
                reflection=Reflection(missing="None", superfluous="None"),
            )  # type: ignore[call-arg]

    def it_requires_reflection_field(self):
        """Verify reflection field is required."""
        with pytest.raises(ValidationError):
            Answer(value="Test answer")  # type: ignore[call-arg]


class DescribeRevised:
    """Tests for the Revised schema."""

    def it_extends_answer(self):
        """Verify Revised inherits from Answer."""
        assert issubclass(Revised, Answer)

    def it_creates_with_all_fields(self):
        """Verify Revised can be created with all fields."""
        reflection = Reflection(missing="None", superfluous="None")
        revised = Revised(
            value="Revised answer with citations [1].",
            reflection=reflection,
            search_queries=["additional query"],
            references=["[1] Source, 2024. https://example.com"],
        )

        assert revised.value == "Revised answer with citations [1]."
        assert revised.reflection == reflection
        assert revised.search_queries == ["additional query"]
        assert revised.references == ["[1] Source, 2024. https://example.com"]

    def it_defaults_references_to_empty_list(self):
        """Verify references defaults to empty list."""
        revised = Revised(
            value="Test answer",
            reflection=Reflection(missing="None", superfluous="None"),
        )

        assert revised.references == []
        assert isinstance(revised.references, list)

    def it_inherits_search_queries_default(self):
        """Verify Revised inherits search_queries default from Answer."""
        revised = Revised(
            value="Test answer",
            reflection=Reflection(missing="None", superfluous="None"),
        )

        assert revised.search_queries == []


class DescribeMarkdownArticle:
    """Tests for the MarkdownArticle schema."""

    def it_creates_with_required_fields(self):
        """Verify MarkdownArticle can be created with required fields."""
        article = MarkdownArticle(
            title="Test Article",
            summary="A brief summary.",
            content="## Section\n\nContent here.",
        )

        assert article.title == "Test Article"
        assert article.summary == "A brief summary."
        assert article.content == "## Section\n\nContent here."
        assert article.references == []

    def it_defaults_references_to_empty_list(self):
        """Verify references defaults to empty list."""
        article = MarkdownArticle(
            title="Test",
            summary="Summary",
            content="Content",
        )

        assert article.references == []
        assert isinstance(article.references, list)

    def it_accepts_references(self):
        """Verify references can be provided."""
        refs = [
            "[1] [Title](https://example.com) - Description",
            "[2] [Another](https://test.com) - More info",
        ]
        article = MarkdownArticle(
            title="Test",
            summary="Summary",
            content="Content",
            references=refs,
        )

        assert article.references == refs
        assert len(article.references) == 2


class DescribeMarkdownArticleToMarkdown:
    """Tests for the MarkdownArticle.to_markdown method."""

    def it_formats_basic_article(self):
        """Verify to_markdown formats a basic article correctly."""
        article = MarkdownArticle(
            title="My Article",
            summary="This is the summary.",
            content="## Introduction\n\nSome content here.",
        )

        result = article.to_markdown()

        assert result.startswith("# My Article")
        assert "*This is the summary.*" in result
        assert "## Introduction\n\nSome content here." in result

    def it_includes_references_section_when_present(self):
        """Verify to_markdown includes references when provided."""
        article = MarkdownArticle(
            title="Article With Refs",
            summary="Summary here.",
            content="Content here.",
            references=[
                "[1] [Source](https://example.com) - Description",
                "[2] [Another](https://test.com) - Info",
            ],
        )

        result = article.to_markdown()

        assert "## References" in result
        assert "[1] [Source](https://example.com) - Description" in result
        assert "[2] [Another](https://test.com) - Info" in result

    def it_excludes_references_section_when_empty(self):
        """Verify to_markdown excludes references section when no references."""
        article = MarkdownArticle(
            title="No Refs Article",
            summary="Summary.",
            content="Content.",
            references=[],
        )

        result = article.to_markdown()

        assert "## References" not in result

    def it_formats_with_correct_structure(self):
        """Verify the overall structure of the markdown output."""
        article = MarkdownArticle(
            title="Structured Article",
            summary="Brief summary.",
            content="Main content.",
            references=["[1] Ref one"],
        )

        result = article.to_markdown()
        lines = result.split("\n")

        # Check structure
        assert lines[0] == "# Structured Article"
        assert lines[1] == ""
        assert lines[2] == "*Brief summary.*"
        assert lines[3] == ""
        assert lines[4] == "Main content."
        assert lines[5] == ""
        assert lines[6] == "## References"
        assert lines[7] == ""
        assert lines[8] == "[1] Ref one"

    def it_returns_string(self):
        """Verify to_markdown returns a string."""
        article = MarkdownArticle(
            title="Test",
            summary="Summary",
            content="Content",
        )

        result = article.to_markdown()

        assert isinstance(result, str)
