from langchain_core.language_models import BaseChatModel

from virgo.agent import VirgoAgent
from virgo.agent.chains import (
    create_first_responder_chain,
    create_markdown_formatter_chain,
    create_revisor_chain,
)
from virgo.agent.graph import create_graph_builder


def create_virgo_agent(llm: BaseChatModel) -> VirgoAgent:
    """Create and configure a VirgoAgent instance.

    Args:
        llm (BaseChatModel): The language model to be used by the agent.
    Returns:
        VirgoAgent: A configured instance of VirgoAgent.
    """
    graph_builder = create_graph_builder(
        first_responder_chain=create_first_responder_chain(llm),
        revisor_chain=create_revisor_chain(llm),
        formatter_chain=create_markdown_formatter_chain(llm),
    )
    agent = VirgoAgent(graph_builder=graph_builder)
    return agent
