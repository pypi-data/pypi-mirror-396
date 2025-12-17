"""Agent module containing LangGraph implementation for Virgo."""

from typing import Self

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage

from virgo.agent.chains import (
    create_first_responder_chain,
    create_markdown_formatter_chain,
    create_revisor_chain,
)
from virgo.agent.graph import VirgoStateGraph, create_graph_builder
from virgo.agent.schemas import MarkdownArticle


class VirgoAgent:
    """The Virgo agent that wraps the LangGraph implementation."""

    def __init__(self, graph_builder: VirgoStateGraph):
        """Initialize the Virgo agent.

        Args:
            graph_builder: The state graph builder for the Virgo agent.

        """
        self._builder = graph_builder
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

    @classmethod
    def from_llm(cls, llm: BaseChatModel) -> Self:
        """Create a VirgoAgent instance from a language model.

        Args:
            llm: The language model to be used by the agent.

        Returns:
            VirgoAgent: A configured instance of VirgoAgent.
        """
        graph_builder = create_graph_builder(
            first_responder_chain=create_first_responder_chain(llm),
            revisor_chain=create_revisor_chain(llm),
            formatter_chain=create_markdown_formatter_chain(llm),
        )
        agent = cls(graph_builder=graph_builder)
        return agent


__all__ = [
    "VirgoAgent",
    "create_graph_builder",
    "create_first_responder_chain",
    "create_markdown_formatter_chain",
    "create_revisor_chain",
]
