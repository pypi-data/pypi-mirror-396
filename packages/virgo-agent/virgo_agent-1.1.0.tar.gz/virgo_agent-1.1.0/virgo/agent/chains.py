"""Chains for the Virgo assistant, including first responder and revisor agents."""

from collections.abc import Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers.openai_tools import (
    PydanticToolsParser,
)
from langchain_core.runnables import RunnableSerializable
from langchain_openai import ChatOpenAI

from virgo.agent.prompts import ACTOR_PROMPT, MARKDOWN_FORMATTER_PROMPT
from virgo.agent.schemas import Answer, MarkdownArticle, Revised


def create_markdown_formatter_chain(
    llm: BaseChatModel,
) -> RunnableSerializable[dict, Sequence[MarkdownArticle]]:
    """Create a chain that formats articles into Markdown.

    Args:
        llm (BaseChatModel): The language model to use. It must support tool usage.
    """
    return (
        MARKDOWN_FORMATTER_PROMPT
        | llm.bind_tools(  # type: ignore
            tools=[MarkdownArticle],
            tool_choice="MarkdownArticle",
        )
        | PydanticToolsParser(tools=[MarkdownArticle])
    )


def create_first_responder_chain(
    llm: BaseChatModel,
) -> RunnableSerializable[dict, AIMessage]:
    """Create a chain that generates detailed answers to questions.

    Args:
        llm (BaseChatModel): The language model to use. It must support tool usage.
    """
    return ACTOR_PROMPT.partial(
        first_instruction="Answer the question in detail, with ~250 words."
    ) | llm.bind_tools(tools=[Answer], tool_choice="Answer")


def create_revisor_chain(
    llm: BaseChatModel,
) -> RunnableSerializable[dict, AIMessage]:
    """Create a chain that revises previous answers based on reflections and new information.

    Args:
        llm (BaseChatModel): The language model to use. It must support tool usage.
    """
    return ACTOR_PROMPT.partial(
        first_instruction="""
        Revise your previous answer using the new information.
            - You should use the previous critique to add important information to your answer;
            - You MUST include numerical citations in your revised answer, to ensure it can be verified;
            - Add a "References" section at the end of your answer (which does not count towards the word limit), listing the full citations for each of the numerical citations in your answer. For example:
                [1] Author Name, "Title of the Article", Source, Year. URL
                [2] "Title of the Article", Source, Year. URL
            - You should use the previous critique to remove any superfluous information from your answer, and make sure it does not contain more than ~250 words.
        """,
    ) | llm.bind_tools(tools=[Revised], tool_choice="Revised")


__all__ = [
    "create_markdown_formatter_chain",
    "create_first_responder_chain",
    "create_revisor_chain",
]


if __name__ == "__main__":
    _pydantic_parser = PydanticToolsParser(tools=[Answer])

    _human_message = HumanMessage(
        content="Write about AI-Powered SOC / autonomous SOC problem domains, list startups that to that and raised capital."
    )

    _chain = (
        ACTOR_PROMPT.partial(
            first_instruction="Answer the question in detail, with ~250 words."
        )
        | ChatOpenAI(model="gpt-4-turbo").bind_tools(
            tools=[Answer], tool_choice="Answer"
        )
        | _pydantic_parser
    )

    _res = _chain.invoke({"messages": [_human_message]})
    print(_res)
