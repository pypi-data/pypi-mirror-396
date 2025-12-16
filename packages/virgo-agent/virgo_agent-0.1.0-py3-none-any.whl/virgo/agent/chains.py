"""Chains for the Virgo assistant, including first responder and revisor agents."""

from datetime import datetime

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_openai import ChatOpenAI

from virgo.agent.schemas import Answer, MarkdownArticle, Revised

_llm = ChatOpenAI(
    model="gpt-4-turbo",
)
"""The LLM used for generating answers and reflections."""


_markdown_formatter_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert technical writer and Markdown formatter.

Your task is to take an article and format it as a well-structured Markdown document.

Formatting guidelines:
- Create a clear, descriptive title
- Write a brief 1-2 sentence summary
- Use ## for main section headings and ### for subsections
- Use **bold** for key terms and important concepts
- Use bullet points (-) for unordered lists
- Use numbered lists (1. 2. 3.) for sequential steps or rankings
- Use > for important quotes or callouts
- Format references as numbered Markdown links: [1] [Title](URL) - Brief description
- Ensure proper spacing between sections
- Keep the content faithful to the original - do not add or remove information
""",
        ),
        (
            "human",
            """Please format the following article as Markdown:

{article}

References (if any):
{references}""",
        ),
    ]
)
"""The prompt template for the Markdown formatter."""


markdown_formatter = _markdown_formatter_prompt | _llm.bind_tools(
    tools=[MarkdownArticle], tool_choice="MarkdownArticle"
)
"""The Markdown formatter chain that converts articles to well-formatted Markdown."""


actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an expert researcher.

            Current time: {current_time}

            1. {first_instruction}
            2. Reflect and critique your answer. Be severe, to maximize improvement.
            3. Recommend search queries ro get information and improve your answer.
            """,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ],
).partial(current_time=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
"""The prompt template for the actor agent to generate answers and reflections."""


_revise_instructions = """
Revise your previous answer using the new information.
    - You should use the previous critique to add important information to your answer;
    - You MUST include numerical citations in your revised answer, to ensure it can be verified;
    - Add a "References" section at the end of your answer (which does not count towards the word limit), listing the full citations for each of the numerical citations in your answer. For example:
        [1] Author Name, "Title of the Article", Source, Year. URL
        [2] "Title of the Article", Source, Year. URL
    - You should use the previous critique to remove any superfluous information from your answer, and make sure it does not contain more than ~250 words.
"""


_json_parser = JsonOutputToolsParser(return_id=True)
"""Parser for the JSON output of the actor agent's response."""

_pydantic_parser = PydanticToolsParser(tools=[Answer])
"""Parser for the Pydantic output of the actor agent's response."""


_first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction="Answer the question in detail, with ~250 words.",
)
"""The prompt template for the first responder agent to generate answers."""


first_responder = _first_responder_prompt_template | _llm.bind_tools(
    tools=[Answer], tool_choice="Answer"
)
"""The first responder agent that generates detailed answers to questions."""


revisor = actor_prompt_template.partial(
    first_instruction=_revise_instructions,
) | _llm.bind_tools(tools=[Revised], tool_choice="Revised")
"""The revisor agent that revises previous answers based on reflections and new information."""


__all__ = [
    "first_responder",
    "markdown_formatter",
    "revisor",
]


if __name__ == "__main__":
    _human_message = HumanMessage(
        content="Write about AI-Powered SOC / autonomous SOC problem domains, list startups that to that and raised capital."
    )

    _chain = (
        _first_responder_prompt_template
        | _llm.bind_tools(tools=[Answer], tool_choice="Answer")
        | _pydantic_parser
    )

    _res = _chain.invoke({"messages": [_human_message]})
    print(_res)
