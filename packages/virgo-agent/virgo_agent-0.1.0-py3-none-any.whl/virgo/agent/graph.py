"""The graph definitions for Virgo."""

import operator
import os
from enum import Enum
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langgraph.graph import END, StateGraph

from virgo.agent.chains import first_responder, markdown_formatter, revisor
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


class AnswerState(TypedDict):
    """The answer graph that produces detailed answers to questions."""

    messages: Annotated[list[BaseMessage], operator.add]
    formatted_article: MarkdownArticle | None


def _first_responder_node(state: AnswerState) -> AnswerState:
    """The first responder node that generates detailed answers to questions.

    Args:
        state (AnswerState): The current state of the graph.

    Returns:
        AnswerState: The updated state of the graph with the first response.
    """
    return AnswerState(
        messages=[first_responder.invoke({"messages": state["messages"]})],
        formatted_article=None,
    )


def _revisor_node(state: AnswerState) -> AnswerState:
    """The revisor node that revises previous answers based on reflections and new information.

    Args:
        state (AnswerState): The current state of the graph.
    Returns:
        AnswerState: The updated state of the graph with the revised answer.
    """
    return AnswerState(
        messages=[revisor.invoke({"messages": state["messages"]})],
        formatted_article=None,
    )


def _format_node(state: AnswerState) -> AnswerState:
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
    formatter_chain = markdown_formatter | PydanticToolsParser(tools=[MarkdownArticle])
    result = formatter_chain.invoke(
        {
            "article": article_content,
            "references": "\n".join(references) if references else "None",
        }
    )

    formatted_article = result[0] if result else None
    return AnswerState(messages=[], formatted_article=formatted_article)


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


def create_graph_builder() -> StateGraph:
    """Create the state graph builder for Virgo.

    Returns:
        StateGraph: The state graph builder for Virgo.
    """
    builder = StateGraph(state_schema=AnswerState)

    # Add the nodes to the graph
    builder.add_node(_VirgoNodes.DRAFT.value, _first_responder_node)
    builder.add_node(_VirgoNodes.EXECUTE_TOOLS.value, execute_tools)
    builder.add_node(_VirgoNodes.REVISE.value, _revisor_node)
    builder.add_node(_VirgoNodes.FORMAT.value, _format_node)

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


class VirgoAgent:
    """The Virgo agent that wraps the LangGraph implementation."""

    def __init__(self, graph_builder: StateGraph | None = None):
        """Initialize the Virgo agent.

        Args:
            graph_builder: Optional StateGraph builder. If not provided,
                          creates a new one using create_graph_builder().
        """
        self._builder = graph_builder or create_graph_builder()
        self._graph = self._builder.compile()

    def generate(self, question: str) -> MarkdownArticle | None:
        """Generate an article based on the input question.

        Args:
            question: The question to generate an article for.

        Returns:
            MarkdownArticle if generation succeeded, None otherwise.
        """
        message = HumanMessage(content=question)
        result = self._graph.invoke({"messages": [message]})  # type: ignore[arg-type]
        return result.get("formatted_article")


# Define the state graph for Virgo (for backwards compatibility)
builder = create_graph_builder()
"""The state graph builder for Virgo."""

__all__ = [
    "AnswerState",
    "VirgoAgent",
    "builder",
    "create_graph_builder",
]
