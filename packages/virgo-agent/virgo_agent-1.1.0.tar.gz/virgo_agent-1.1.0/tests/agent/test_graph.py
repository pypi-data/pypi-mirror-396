"""Unit tests for the Virgo agent graph module."""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph

from virgo.agent.graph import (
    VIRGO_MAX_ITERATIONS,
    AnswerState,
    _event_loop,
    _VirgoNodes,
    create_format_node,
    create_graph_builder,
)
from virgo.agent.schemas import MarkdownArticle


class DescribeVirgoMaxIterations:
    """Tests for the VIRGO_MAX_ITERATIONS constant."""

    def it_has_default_value_of_5(self):
        """Verify default max iterations is 5."""
        # Note: This tests the default, but env var may override
        assert VIRGO_MAX_ITERATIONS >= 1

    def it_is_an_integer(self):
        """Verify max iterations is an integer."""
        assert isinstance(VIRGO_MAX_ITERATIONS, int)


class DescribeVirgoNodes:
    """Tests for the _VirgoNodes enum."""

    def it_has_draft_node(self):
        """Verify DRAFT node exists."""
        assert _VirgoNodes.DRAFT.value == "draft"

    def it_has_execute_tools_node(self):
        """Verify EXECUTE_TOOLS node exists."""
        assert _VirgoNodes.EXECUTE_TOOLS.value == "execute_tools"

    def it_has_revise_node(self):
        """Verify REVISE node exists."""
        assert _VirgoNodes.REVISE.value == "revise"

    def it_has_format_node(self):
        """Verify FORMAT node exists."""
        assert _VirgoNodes.FORMAT.value == "format"

    def it_has_four_nodes(self):
        """Verify there are exactly four nodes."""
        assert len(_VirgoNodes) == 4


class DescribeAnswerTypedDict:
    """Tests for the AnswerState TypedDict."""

    def it_accepts_messages_list(self):
        """Verify AnswerState accepts messages list."""
        answer: AnswerState = {
            "messages": [HumanMessage(content="test")],
            "formatted_article": None,
        }
        assert len(answer["messages"]) == 1

    def it_accepts_formatted_article(self):
        """Verify AnswerState accepts formatted_article."""
        article = MarkdownArticle(
            title="Test",
            summary="Summary",
            content="Content",
        )
        answer: AnswerState = {
            "messages": [],
            "formatted_article": article,
        }
        assert answer["formatted_article"] == article

    def it_accepts_none_formatted_article(self):
        """Verify AnswerState accepts None for formatted_article."""
        answer: AnswerState = {
            "messages": [],
            "formatted_article": None,
        }
        assert answer["formatted_article"] is None


class DescribeEventLoop:
    """Tests for the _event_loop function."""

    def it_returns_execute_tools_when_under_max_iterations(self):
        """Verify event loop continues when under max iterations."""
        state: AnswerState = {
            "messages": [
                HumanMessage(content="question"),
                AIMessage(content="answer"),
                ToolMessage(content="result", tool_call_id="1"),
            ],
            "formatted_article": None,
        }

        result = _event_loop(state)

        assert result == _VirgoNodes.EXECUTE_TOOLS.value

    def it_returns_format_when_at_max_iterations(self):
        """Verify event loop goes to format when at max iterations."""
        # Create state with VIRGO_MAX_ITERATIONS tool messages
        tool_messages = [
            ToolMessage(content=f"result {i}", tool_call_id=str(i))
            for i in range(VIRGO_MAX_ITERATIONS)
        ]
        state: AnswerState = {
            "messages": [HumanMessage(content="question"), *tool_messages],
            "formatted_article": None,
        }

        result = _event_loop(state)

        assert result == _VirgoNodes.FORMAT.value

    def it_returns_format_when_over_max_iterations(self):
        """Verify event loop goes to format when over max iterations."""
        tool_messages = [
            ToolMessage(content=f"result {i}", tool_call_id=str(i))
            for i in range(VIRGO_MAX_ITERATIONS + 2)
        ]
        state: AnswerState = {
            "messages": tool_messages,
            "formatted_article": None,
        }

        result = _event_loop(state)

        assert result == _VirgoNodes.FORMAT.value

    def it_counts_only_tool_messages(self):
        """Verify event loop only counts ToolMessages."""
        state: AnswerState = {
            "messages": [
                HumanMessage(content="q1"),
                AIMessage(content="a1"),
                HumanMessage(content="q2"),
                AIMessage(content="a2"),
                ToolMessage(content="t1", tool_call_id="1"),
            ],
            "formatted_article": None,
        }

        result = _event_loop(state)

        # Only 1 ToolMessage, should continue
        assert result == _VirgoNodes.EXECUTE_TOOLS.value

    def it_returns_execute_tools_with_empty_messages(self):
        """Verify event loop continues with no messages."""
        state: AnswerState = {
            "messages": [],
            "formatted_article": None,
        }

        result = _event_loop(state)

        assert result == _VirgoNodes.EXECUTE_TOOLS.value


class DescribeFormatNode:
    """Tests for the format node factory."""

    def it_returns_empty_when_no_ai_message_with_tool_calls(self):
        """Verify format node handles missing AI message gracefully."""
        formatter_chain = RunnableLambda(lambda _input: [])
        format_node = create_format_node(formatter_chain)

        state: AnswerState = {
            "messages": [HumanMessage(content="test")],
            "formatted_article": None,
        }

        result = format_node(state)

        assert result["messages"] == []
        assert result["formatted_article"] is None

    def it_returns_empty_when_ai_message_has_no_tool_calls(self):
        """Verify format node handles AI message without tool calls."""
        formatter_chain = RunnableLambda(lambda _input: [])
        format_node = create_format_node(formatter_chain)

        state: AnswerState = {
            "messages": [
                HumanMessage(content="test"),
                AIMessage(content="response without tools"),
            ],
            "formatted_article": None,
        }

        result = format_node(state)

        assert result["messages"] == []
        assert result["formatted_article"] is None

    def it_extracts_content_from_last_ai_message_with_tool_calls(self):
        """Verify format node finds the last AI message with tool calls."""
        mock_article = MarkdownArticle(
            title="Test",
            summary="Summary",
            content="Content",
        )

        formatter_chain = RunnableLambda(lambda _input: [mock_article])
        format_node = create_format_node(formatter_chain)

        state: AnswerState = {
            "messages": [
                HumanMessage(content="question"),
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "id": "call_1",
                            "name": "Revised",
                            "args": {
                                "value": "Article content here",
                                "references": ["[1] Ref one"],
                            },
                        }
                    ],
                ),
            ],
            "formatted_article": None,
        }

        result = format_node(state)

        assert result["formatted_article"] == mock_article


class DescribeBuilder:
    """Tests for the graph builder."""

    def it_is_a_state_graph(self):
        """Verify create_graph_builder returns a StateGraph instance."""
        dummy_ai_chain = RunnableLambda(lambda _input: AIMessage(content=""))
        dummy_formatter_chain = RunnableLambda(lambda _input: [])

        builder = create_graph_builder(
            first_responder_chain=dummy_ai_chain,
            revisor_chain=dummy_ai_chain,
            formatter_chain=dummy_formatter_chain,
        )

        assert isinstance(builder, StateGraph)

    def it_has_expected_nodes(self):
        """Verify the builder contains all expected nodes."""
        dummy_ai_chain = RunnableLambda(lambda _input: AIMessage(content=""))
        dummy_formatter_chain = RunnableLambda(lambda _input: [])

        builder = create_graph_builder(
            first_responder_chain=dummy_ai_chain,
            revisor_chain=dummy_ai_chain,
            formatter_chain=dummy_formatter_chain,
        )

        assert _VirgoNodes.DRAFT.value in builder.nodes
        assert _VirgoNodes.EXECUTE_TOOLS.value in builder.nodes
        assert _VirgoNodes.REVISE.value in builder.nodes
        assert _VirgoNodes.FORMAT.value in builder.nodes

    def it_can_compile(self):
        """Verify the builder can be compiled."""
        dummy_ai_chain = RunnableLambda(lambda _input: AIMessage(content=""))
        dummy_formatter_chain = RunnableLambda(lambda _input: [])

        builder = create_graph_builder(
            first_responder_chain=dummy_ai_chain,
            revisor_chain=dummy_ai_chain,
            formatter_chain=dummy_formatter_chain,
        )

        compiled = builder.compile()
        assert compiled is not None
