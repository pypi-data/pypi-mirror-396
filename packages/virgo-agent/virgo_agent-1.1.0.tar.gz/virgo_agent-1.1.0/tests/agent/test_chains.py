"""Unit tests for the Virgo agent chains module."""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda

from virgo.agent.chains import (
    create_first_responder_chain,
    create_markdown_formatter_chain,
    create_revisor_chain,
)
from virgo.agent.prompts import ACTOR_PROMPT, MARKDOWN_FORMATTER_PROMPT
from virgo.agent.schemas import MarkdownArticle


class _StubToolBindingLLM:
    """Small test double that emulates `llm.bind_tools(...).invoke(...)`."""

    def __init__(self, response: AIMessage):
        self._response = response

    def bind_tools(self, *_, **__) -> RunnableLambda:  # pragma: no cover
        return RunnableLambda(lambda _input: self._response)


class DescribeActorPrompt:
    """Tests for the actor prompt template."""

    def it_formats_with_messages_placeholder(self):
        """Verify the template accepts messages and first_instruction."""
        prompt = ACTOR_PROMPT.partial(first_instruction="Test instruction")
        result = prompt.invoke({"messages": [HumanMessage(content="Hello")]})

        assert len(result.messages) == 2
        assert "expert researcher" in result.messages[0].content.lower()
        assert "Test instruction" in result.messages[0].content
        assert result.messages[1].content == "Hello"

    def it_includes_current_time_in_system_message(self):
        """Verify the template includes the current time."""
        prompt = ACTOR_PROMPT.partial(first_instruction="Test instruction")
        result = prompt.invoke({"messages": [HumanMessage(content="Test")]})

        assert "current time:" in result.messages[0].content.lower()


class DescribeFirstResponderChain:
    """Tests for the first responder chain factory."""

    def it_returns_ai_message_with_tool_calls(self):
        """Verify chain invocation returns the LLM response."""
        mock_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_1",
                    "name": "Answer",
                    "args": {
                        "value": "Test answer.",
                        "reflection": {"missing": "", "superfluous": ""},
                        "search_queries": [],
                    },
                }
            ],
        )

        llm = _StubToolBindingLLM(response=mock_response)
        chain = create_first_responder_chain(llm)

        result = chain.invoke({"messages": [HumanMessage(content="Question")]})

        assert isinstance(result, AIMessage)
        assert result.tool_calls
        assert result.tool_calls[0]["name"] == "Answer"


class DescribeMarkdownFormatterPrompt:
    """Tests for the markdown formatter prompt template."""

    def it_formats_article_and_references(self):
        """Verify the markdown formatter prompt accepts article and references."""
        result = MARKDOWN_FORMATTER_PROMPT.invoke(
            {
                "article": "Test article content",
                "references": "[1] Test reference",
            }
        )

        assert len(result.messages) == 2
        assert "markdown" in result.messages[0].content.lower()
        assert "Test article content" in result.messages[1].content
        assert "[1] Test reference" in result.messages[1].content

    def it_includes_formatting_guidelines(self):
        """Verify the system message contains formatting guidelines."""
        result = MARKDOWN_FORMATTER_PROMPT.invoke(
            {
                "article": "Test",
                "references": "None",
            }
        )

        system_content = result.messages[0].content.lower()
        assert "##" in system_content or "heading" in system_content
        assert "bold" in system_content
        assert "bullet" in system_content


class DescribeRevisorChain:
    """Tests for the revisor chain."""

    def it_returns_revised_tool_call(self):
        """Verify the chain returns an AIMessage with Revised tool call."""
        mock_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_1",
                    "name": "Revised",
                    "args": {
                        "value": "Revised answer with citations [1].",
                        "reflection": {
                            "missing": "Could add more sources",
                            "superfluous": "None",
                        },
                        "search_queries": [],
                        "references": ["[1] Test Source, 2024. https://example.com"],
                    },
                }
            ],
        )

        llm = _StubToolBindingLLM(response=mock_response)
        test_chain = create_revisor_chain(llm)

        result = test_chain.invoke({"messages": [HumanMessage(content="Revise this")]})

        assert result is not None
        assert isinstance(result, AIMessage)
        assert len(result.tool_calls) > 0
        assert result.tool_calls[0]["name"] == "Revised"
        assert "references" in result.tool_calls[0]["args"]
        assert "value" in result.tool_calls[0]["args"]


class DescribeMarkdownFormatterChain:
    """Tests for the markdown formatter chain."""

    def it_returns_markdown_article_tool_call(self):
        """Verify the chain parses MarkdownArticle tool call into objects."""
        mock_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_1",
                    "name": "MarkdownArticle",
                    "args": {
                        "title": "AI in Cybersecurity",
                        "summary": "A brief overview of AI applications in security.",
                        "content": "## Introduction\n\n**Artificial Intelligence** is transforming cybersecurity.",
                        "references": [
                            "[1] [Source](https://example.com) - Description"
                        ],
                    },
                }
            ],
        )

        llm = _StubToolBindingLLM(response=mock_response)
        chain = create_markdown_formatter_chain(llm)

        result = chain.invoke({"article": "Test article", "references": "None"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], MarkdownArticle)
        assert result[0].title == "AI in Cybersecurity"
