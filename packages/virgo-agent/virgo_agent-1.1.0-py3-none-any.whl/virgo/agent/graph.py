"""The graph definitions for Virgo."""

import operator
import os
from collections.abc import Sequence
from enum import Enum
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.runnables import RunnableSerializable
from langgraph.graph import END, StateGraph
from langgraph.graph.state import StateNode

from virgo.agent.schemas import MarkdownArticle
from virgo.agent.tools import execute_tools

VIRGO_MAX_ITERATIONS = int(os.getenv("VIRGO_MAX_ITERATIONS", 5))
"""The maximum number of iterations for the Virgo graph."""


class _VirgoNodes(Enum):
    """The nodes in the Virgo graph."""

    DRAFT = "draft"
    EXECUTE_TOOLS = "execute_tools"
    REVISE = "revise"
    FORMAT = "format"


type VirgoStateGraph = StateGraph[AnswerState, None, AnswerState, AnswerState]
"""The type alias for the Virgo state graph.

In the current implementation, it starts with an list of messages (HumanMessage with the question),
and ends with an AnswerState containing the final formatted Markdown article.
"""


class AnswerState(TypedDict):
    """The answer graph that produces detailed answers to questions."""

    messages: Annotated[list[BaseMessage], operator.add]
    formatted_article: MarkdownArticle | None


def create_first_responder_node(
    chain: RunnableSerializable[dict, AIMessage],
) -> StateNode[AnswerState]:
    """Create the first responder node function.

    Args:
        chain: The first responder chain.

    Returns:
        callable: The first responder node function.
    """

    def first_responder_node(state: AnswerState) -> AnswerState:
        """The first responder node that generates detailed answers to questions.

        Args:
            state (AnswerState): The current state of the graph.

        Returns:
            AnswerState: The updated state of the graph with the first response.
        """
        return AnswerState(
            messages=[
                chain.invoke({"messages": state["messages"], "formatted_article": None})
            ],
            formatted_article=None,
        )

    return first_responder_node


def create_revisor_node(
    chain: RunnableSerializable[dict, AIMessage],
) -> StateNode[AnswerState]:
    """Create the revisor node function.

    Args:
        chain: The revisor chain.

    Returns:
        callable: The revisor node function.
    """

    def revisor_node(state: AnswerState) -> AnswerState:
        """The revisor node that revises previous answers based on reflections and new information.

        Args:
            state (AnswerState): The current state of the graph.
        Returns:
            AnswerState: The updated state of the graph with the revised answer.
        """
        return AnswerState(
            messages=[chain.invoke({"messages": state["messages"]})],
            formatted_article=None,
        )

    return revisor_node


def create_format_node(
    chain: RunnableSerializable[dict, Sequence[MarkdownArticle]],
) -> StateNode[AnswerState]:
    """Create the format node function.

    Args:
        chain: The markdown formatter chain.

    Returns:
        callable: The format node function.
    """

    def format_node(state: AnswerState) -> AnswerState:
        """The format node that converts the final answer to a well-formatted Markdown article.

        Args:
            state (AnswerState): The current state of the graph.
        Returns:
            AnswerState: The updated state with the formatted Markdown article.
        """
        # Extract the last AI message with tool calls (the final revised answer)
        last_revised_message: AIMessage | None = None
        for msg in reversed(state["messages"]):
            if isinstance(msg, AIMessage) and msg.tool_calls:
                last_revised_message = msg
                break

        if not last_revised_message or not last_revised_message.tool_calls:
            return AnswerState(messages=[], formatted_article=None)

        # Extract the answer content and references from the tool call
        tool_call = last_revised_message.tool_calls[0]
        article_content = tool_call["args"].get("value", "")
        references = tool_call["args"].get("references", [])

        # Format using the markdown formatter chain
        result = chain.invoke(
            {
                "article": article_content,
                "references": "\n".join(references) if references else "None",
            }
        )

        formatted_article = result[0] if result else None
        return AnswerState(messages=[], formatted_article=formatted_article)

    return format_node


# Define the event loop for the graph
def _event_loop(state: AnswerState) -> str:
    """The event loop that runs the graph until the final answer is produced, or the maximum number of iterations is reached.

    Args:
        state (AnswerState): The current state of the graph.
    Returns:
        str: The next node to execute.
    """
    count_tool_invocations = sum(
        isinstance(msg, ToolMessage) for msg in state["messages"]
    )
    if count_tool_invocations >= VIRGO_MAX_ITERATIONS:
        return _VirgoNodes.FORMAT.value
    return _VirgoNodes.EXECUTE_TOOLS.value


def create_graph_builder(
    first_responder_chain: RunnableSerializable[dict, AIMessage],
    revisor_chain: RunnableSerializable[dict, AIMessage],
    formatter_chain: RunnableSerializable[dict, Sequence[MarkdownArticle]],
) -> VirgoStateGraph:
    """Create the state graph builder for Virgo.

    Args:
        first_responder_chain: The first responder chain.
        revisor_chain: The revisor chain.
        formatter_chain: The markdown formatter chain.

    Returns:
        _VirgoStateGraph: The state graph builder for Virgo.
    """
    builder = StateGraph[AnswerState, None, AnswerState, AnswerState](
        state_schema=AnswerState
    )

    # Add the nodes to the graph
    builder.add_node(
        _VirgoNodes.DRAFT.value, create_first_responder_node(first_responder_chain)
    )
    builder.add_node(_VirgoNodes.EXECUTE_TOOLS.value, execute_tools)
    builder.add_node(_VirgoNodes.REVISE.value, create_revisor_node(revisor_chain))
    builder.add_node(_VirgoNodes.FORMAT.value, create_format_node(formatter_chain))

    # Define the edges between the nodes
    builder.add_edge(_VirgoNodes.DRAFT.value, _VirgoNodes.EXECUTE_TOOLS.value)
    builder.add_edge(_VirgoNodes.EXECUTE_TOOLS.value, _VirgoNodes.REVISE.value)

    # Define the entry point of the graph
    builder.set_entry_point(_VirgoNodes.DRAFT.value)

    builder.add_conditional_edges(
        _VirgoNodes.REVISE.value,
        _event_loop,
    )

    # Add edge from FORMAT to END
    builder.add_edge(_VirgoNodes.FORMAT.value, END)

    return builder


__all__ = [
    "AnswerState",
    "create_graph_builder",
]
