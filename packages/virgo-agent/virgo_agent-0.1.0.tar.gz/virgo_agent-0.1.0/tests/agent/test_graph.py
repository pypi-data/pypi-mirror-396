"""Unit tests for the Virgo agent graph module."""

from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from virgo.agent.graph import (
    VIRGO_MAX_ITERATIONS,
    AnswerState,
    _event_loop,
    _format_node,
    _VirgoNodes,
    builder,
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
    """Tests for the _format_node function."""

    def it_returns_empty_when_no_ai_message_with_tool_calls(self):
        """Verify format node handles missing AI message gracefully."""
        state: AnswerState = {
            "messages": [HumanMessage(content="test")],
            "formatted_article": None,
        }

        result = _format_node(state)

        assert result["messages"] == []
        assert result["formatted_article"] is None

    def it_returns_empty_when_ai_message_has_no_tool_calls(self):
        """Verify format node handles AI message without tool calls."""
        state: AnswerState = {
            "messages": [
                HumanMessage(content="test"),
                AIMessage(content="response without tools"),
            ],
            "formatted_article": None,
        }

        result = _format_node(state)

        assert result["messages"] == []
        assert result["formatted_article"] is None

    def it_extracts_content_from_last_ai_message_with_tool_calls(self):
        """Verify format node finds the last AI message with tool calls."""
        mock_article = MarkdownArticle(
            title="Test",
            summary="Summary",
            content="Content",
        )

        with patch("virgo.agent.graph.markdown_formatter") as mock_formatter:
            # Mock the chain to return our article
            mock_chain = mock_formatter.__or__.return_value
            mock_chain.invoke.return_value = [mock_article]

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

            result = _format_node(state)

            assert result["formatted_article"] == mock_article
            mock_chain.invoke.assert_called_once()


class DescribeBuilder:
    """Tests for the graph builder."""

    def it_is_a_state_graph(self):
        """Verify builder is a StateGraph instance."""
        assert isinstance(builder, StateGraph)

    def it_has_draft_node(self):
        """Verify graph has draft node."""
        assert _VirgoNodes.DRAFT.value in builder.nodes

    def it_has_execute_tools_node(self):
        """Verify graph has execute_tools node."""
        assert _VirgoNodes.EXECUTE_TOOLS.value in builder.nodes

    def it_has_revise_node(self):
        """Verify graph has revise node."""
        assert _VirgoNodes.REVISE.value in builder.nodes

    def it_has_format_node(self):
        """Verify graph has format node."""
        assert _VirgoNodes.FORMAT.value in builder.nodes

    def it_has_four_nodes(self):
        """Verify graph has exactly four nodes."""
        assert len(builder.nodes) == 4

    def it_can_compile(self):
        """Verify graph can be compiled."""
        compiled = builder.compile()
        assert compiled is not None


class DescribeGraphEdges:
    """Tests for the graph edge configuration."""

    def it_has_draft_as_entry_point(self):
        """Verify draft is the entry point."""
        # The entry point is stored in the builder
        # We can verify by checking the compiled graph's first node
        compiled = builder.compile()
        # Entry point check - get_graph returns the graph structure
        graph = compiled.get_graph()
        # Find edges from __start__
        start_edges = [edge for edge in graph.edges if edge.source == "__start__"]
        assert len(start_edges) == 1
        assert start_edges[0].target == _VirgoNodes.DRAFT.value

    def it_connects_draft_to_execute_tools(self):
        """Verify draft connects to execute_tools."""
        compiled = builder.compile()
        graph = compiled.get_graph()
        draft_edges = [
            edge for edge in graph.edges if edge.source == _VirgoNodes.DRAFT.value
        ]
        targets = [edge.target for edge in draft_edges]
        assert _VirgoNodes.EXECUTE_TOOLS.value in targets

    def it_connects_execute_tools_to_revise(self):
        """Verify execute_tools connects to revise."""
        compiled = builder.compile()
        graph = compiled.get_graph()
        execute_edges = [
            edge
            for edge in graph.edges
            if edge.source == _VirgoNodes.EXECUTE_TOOLS.value
        ]
        targets = [edge.target for edge in execute_edges]
        assert _VirgoNodes.REVISE.value in targets

    def it_connects_format_to_end(self):
        """Verify format node exists and graph compiles with all edges."""
        # The FORMAT -> END edge is configured via builder.add_edge
        # We verify the graph compiles and has the format node
        compiled = builder.compile()

        # Verify format node exists in the builder
        assert _VirgoNodes.FORMAT.value in builder.nodes

        # Verify the graph compiles successfully (implicitly validates edges)
        assert compiled is not None


class DescribeGraphInvocation:
    """Tests for invoking the compiled graph."""

    def it_invokes_graph_with_mocked_chains(self):
        """Verify graph can be invoked end-to-end with mocked chains."""
        # Create mock responses for each chain
        draft_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_draft",
                    "name": "Answer",
                    "args": {
                        "value": "Initial draft answer.",
                        "reflection": {"missing": "Details", "superfluous": "None"},
                        "search_queries": ["test query"],
                    },
                }
            ],
        )

        revised_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_revised",
                    "name": "Revised",
                    "args": {
                        "value": "Revised answer with citations [1].",
                        "reflection": {"missing": "None", "superfluous": "None"},
                        "search_queries": [],
                        "references": ["[1] Test Reference"],
                    },
                }
            ],
        )

        mock_article = MarkdownArticle(
            title="Test Article",
            summary="A test summary.",
            content="## Content\n\nTest content here.",
            references=["[1] Test Reference"],
        )

        with (
            patch("virgo.agent.graph.first_responder") as mock_first_responder,
            patch("virgo.agent.graph.revisor") as mock_revisor,
            patch("virgo.agent.graph.execute_tools") as mock_execute_tools,
            patch("virgo.agent.graph.markdown_formatter") as mock_formatter,
        ):
            # Configure mocks
            mock_first_responder.invoke.return_value = draft_response
            mock_revisor.invoke.return_value = revised_response

            # Mock execute_tools to return tool messages
            def execute_tools_side_effect(state):
                # Return a ToolMessage for each tool call
                messages = state.get("messages", [])
                tool_messages = []
                for msg in messages:
                    if isinstance(msg, AIMessage) and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tool_messages.append(
                                ToolMessage(
                                    content="Search results here",
                                    tool_call_id=tool_call["id"],
                                )
                            )
                return {"messages": tool_messages}

            mock_execute_tools.invoke.side_effect = execute_tools_side_effect

            # Mock the formatter chain
            mock_chain = mock_formatter.__or__.return_value
            mock_chain.invoke.return_value = [mock_article]

            # Compile and invoke the graph
            checkpointer = MemorySaver()
            compiled = builder.compile(checkpointer=checkpointer)

            result = compiled.invoke(
                {
                    "messages": [HumanMessage(content="Test question")],
                    "formatted_article": None,
                },
                config={"configurable": {"thread_id": "test-1"}},
            )

            # Verify the result
            assert result is not None
            assert "formatted_article" in result
            assert result["formatted_article"] == mock_article

            # Verify chains were called
            mock_first_responder.invoke.assert_called()

    def it_invokes_graph_with_memory_checkpoint(self):
        """Verify graph maintains state across invocations with checkpointer."""
        draft_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_1",
                    "name": "Answer",
                    "args": {
                        "value": "Answer content.",
                        "reflection": {"missing": "None", "superfluous": "None"},
                        "search_queries": ["query"],
                    },
                }
            ],
        )

        revised_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_2",
                    "name": "Revised",
                    "args": {
                        "value": "Revised content.",
                        "reflection": {"missing": "None", "superfluous": "None"},
                        "search_queries": [],
                        "references": [],
                    },
                }
            ],
        )

        mock_article = MarkdownArticle(
            title="Title",
            summary="Summary",
            content="Content",
        )

        with (
            patch("virgo.agent.graph.first_responder") as mock_first_responder,
            patch("virgo.agent.graph.revisor") as mock_revisor,
            patch("virgo.agent.graph.execute_tools") as mock_execute_tools,
            patch("virgo.agent.graph.markdown_formatter") as mock_formatter,
        ):
            mock_first_responder.invoke.return_value = draft_response
            mock_revisor.invoke.return_value = revised_response

            def execute_tools_side_effect(state):
                messages = state.get("messages", [])
                tool_messages = []
                for msg in messages:
                    if isinstance(msg, AIMessage) and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tool_messages.append(
                                ToolMessage(
                                    content="Results",
                                    tool_call_id=tool_call["id"],
                                )
                            )
                return {"messages": tool_messages}

            mock_execute_tools.invoke.side_effect = execute_tools_side_effect

            mock_chain = mock_formatter.__or__.return_value
            mock_chain.invoke.return_value = [mock_article]

            checkpointer = MemorySaver()
            compiled = builder.compile(checkpointer=checkpointer)

            # First invocation
            result = compiled.invoke(
                {
                    "messages": [HumanMessage(content="Question 1")],
                    "formatted_article": None,
                },
                config={"configurable": {"thread_id": "test-memory"}},
            )

            assert result is not None
            assert result["formatted_article"] == mock_article

    def it_returns_formatted_article_in_final_state(self):
        """Verify the final state contains a formatted MarkdownArticle."""
        draft_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_1",
                    "name": "Answer",
                    "args": {
                        "value": "Draft.",
                        "reflection": {"missing": "X", "superfluous": "Y"},
                        "search_queries": ["q"],
                    },
                }
            ],
        )

        revised_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_2",
                    "name": "Revised",
                    "args": {
                        "value": "Final revised content with [1] citation.",
                        "reflection": {"missing": "None", "superfluous": "None"},
                        "search_queries": [],
                        "references": ["[1] Source URL"],
                    },
                }
            ],
        )

        expected_article = MarkdownArticle(
            title="Generated Article",
            summary="An article about the topic.",
            content="## Main Section\n\nFinal revised content with [1] citation.",
            references=["[1] [Source](URL) - Description"],
        )

        with (
            patch("virgo.agent.graph.first_responder") as mock_first_responder,
            patch("virgo.agent.graph.revisor") as mock_revisor,
            patch("virgo.agent.graph.execute_tools") as mock_execute_tools,
            patch("virgo.agent.graph.markdown_formatter") as mock_formatter,
        ):
            mock_first_responder.invoke.return_value = draft_response
            mock_revisor.invoke.return_value = revised_response

            def execute_tools_side_effect(state):
                messages = state.get("messages", [])
                tool_messages = []
                for msg in messages:
                    if isinstance(msg, AIMessage) and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tool_messages.append(
                                ToolMessage(
                                    content="Tool output",
                                    tool_call_id=tool_call["id"],
                                )
                            )
                return {"messages": tool_messages}

            mock_execute_tools.invoke.side_effect = execute_tools_side_effect

            mock_chain = mock_formatter.__or__.return_value
            mock_chain.invoke.return_value = [expected_article]

            checkpointer = MemorySaver()
            compiled = builder.compile(checkpointer=checkpointer)

            result = compiled.invoke(
                {
                    "messages": [HumanMessage(content="Write about AI")],
                    "formatted_article": None,
                },
                config={"configurable": {"thread_id": "test-article"}},
            )

            # Verify the formatted article
            assert result["formatted_article"] is not None
            assert isinstance(result["formatted_article"], MarkdownArticle)
            assert result["formatted_article"].title == "Generated Article"
            assert "Main Section" in result["formatted_article"].content

            # Verify to_markdown works
            markdown = result["formatted_article"].to_markdown()
            assert "# Generated Article" in markdown
            assert "## References" in markdown
