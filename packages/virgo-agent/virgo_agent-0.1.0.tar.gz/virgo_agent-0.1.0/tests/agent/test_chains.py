"""Unit tests for the Virgo agent chains module."""

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

from virgo.agent.chains import (
    _first_responder_prompt_template,
    _markdown_formatter_prompt,
    _revise_instructions,
    actor_prompt_template,
)


class DescribeActorPromptTemplate:
    """Tests for the actor prompt template."""

    def it_formats_with_messages_placeholder(self):
        """Verify the template accepts messages and first_instruction."""
        prompt = actor_prompt_template.partial(first_instruction="Test instruction")
        result = prompt.invoke({"messages": [HumanMessage(content="Hello")]})

        assert len(result.messages) == 2
        assert "expert researcher" in result.messages[0].content.lower()
        assert "Test instruction" in result.messages[0].content
        assert result.messages[1].content == "Hello"

    def it_includes_current_time_in_system_message(self):
        """Verify the template includes the current time."""
        prompt = actor_prompt_template.partial(first_instruction="Test instruction")
        result = prompt.invoke({"messages": [HumanMessage(content="Test")]})

        # Should contain a timestamp pattern like "2025-12-11"
        assert "current time:" in result.messages[0].content.lower()


class DescribeFirstResponderPromptTemplate:
    """Tests for the first responder prompt template."""

    def it_includes_word_count_instruction(self):
        """Verify the first responder has ~250 words instruction."""
        result = _first_responder_prompt_template.invoke(
            {"messages": [HumanMessage(content="Test")]}
        )

        assert "250 words" in result.messages[0].content


class DescribeMarkdownFormatterPrompt:
    """Tests for the markdown formatter prompt template."""

    def it_formats_article_and_references(self):
        """Verify the markdown formatter prompt accepts article and references."""
        result = _markdown_formatter_prompt.invoke(
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
        result = _markdown_formatter_prompt.invoke(
            {
                "article": "Test",
                "references": "None",
            }
        )

        system_content = result.messages[0].content.lower()
        assert "##" in system_content or "heading" in system_content
        assert "bold" in system_content
        assert "bullet" in system_content


class DescribeFirstResponderChain:
    """Tests for the first responder chain."""

    def it_returns_answer_tool_call(self):
        """Verify the chain returns an AIMessage with Answer tool call."""
        mock_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_1",
                    "name": "Answer",
                    "args": {
                        "value": "Test answer about AI in cybersecurity.",
                        "reflection": {
                            "missing": "More details needed",
                            "superfluous": "None",
                        },
                        "search_queries": ["AI cybersecurity trends"],
                    },
                }
            ],
        )

        fake_llm = GenericFakeChatModel(messages=iter([mock_response]))

        # Build a test chain with the fake LLM
        test_chain = _first_responder_prompt_template | fake_llm

        result = test_chain.invoke(
            {"messages": [HumanMessage(content="Test question")]}
        )

        assert result is not None
        assert isinstance(result, AIMessage)
        assert len(result.tool_calls) > 0
        assert result.tool_calls[0]["name"] == "Answer"
        assert "value" in result.tool_calls[0]["args"]
        assert "reflection" in result.tool_calls[0]["args"]


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

        fake_llm = GenericFakeChatModel(messages=iter([mock_response]))

        test_chain = (
            actor_prompt_template.partial(
                first_instruction=_revise_instructions,
            )
            | fake_llm
        )

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
        """Verify the chain returns an AIMessage with MarkdownArticle tool call."""
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

        fake_llm = GenericFakeChatModel(messages=iter([mock_response]))

        test_chain = _markdown_formatter_prompt | fake_llm

        result = test_chain.invoke(
            {
                "article": "Test article",
                "references": "None",
            }
        )

        assert result is not None
        assert isinstance(result, AIMessage)
        assert len(result.tool_calls) > 0
        assert result.tool_calls[0]["name"] == "MarkdownArticle"
        assert "title" in result.tool_calls[0]["args"]
        assert "content" in result.tool_calls[0]["args"]
        assert "summary" in result.tool_calls[0]["args"]
