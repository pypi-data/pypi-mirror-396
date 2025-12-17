"""Schemas for the Virgo assistant's answers and reflections."""

from pydantic import BaseModel, Field


class Reflection(BaseModel):
    """Reflection model representing the assistant's reflection on a given content."""

    missing: str = Field(description="Critique of what is missing from the content.")
    superfluous: str = Field(
        description="Critique of what is superfluous in the content."
    )


class Answer(BaseModel):
    """Answer model representing the assistant's answer to a question."""

    value: str = Field(description="~250 word detailed answer to the question.")
    reflection: Reflection = Field(
        description="Reflection on the content of the answer."
    )
    search_queries: list[str] = Field(
        default_factory=list,
        description="1-3 search queries for researching improvements to address the critique of your current answer.",
    )


class Revised(Answer):
    """Revised answer model representing the assistant's revised answer to a question."""

    references: list[str] = Field(
        default_factory=list,
        description="List of full citations for each of the numerical citations in your revised answer.",
    )


class MarkdownArticle(BaseModel):
    """A well-formatted Markdown article."""

    title: str = Field(
        description="Article title (without # prefix, will be added during rendering)."
    )
    summary: str = Field(description="A brief 1-2 sentence summary of the article.")
    content: str = Field(
        description="The main article content formatted in Markdown with proper headings (##, ###), "
        "**bold** for key terms, bullet points, and numbered lists where appropriate."
    )
    references: list[str] = Field(
        default_factory=list,
        description="List of references formatted as Markdown links: [1] [Title](URL) - Description",
    )

    def to_markdown(self) -> str:
        """Convert the article to a complete Markdown string.

        Returns:
            str: The full Markdown-formatted article.
        """
        parts = [
            f"# {self.title}",
            "",
            f"*{self.summary}*",
            "",
            self.content,
        ]
        if self.references:
            parts.extend(["", "## References", ""])
            parts.extend(self.references)
        return "\n".join(parts)


__all__ = [
    "Answer",
    "MarkdownArticle",
    "Reflection",
    "Revised",
]
