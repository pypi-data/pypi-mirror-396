"""Tools for the Virgo assistant.

Currently includes a web search tool using Tavily.
"""

from langchain_core.tools import StructuredTool
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode

from virgo.agent.schemas import Answer, Revised

_tavily_tool = TavilySearch(max_results=5)
"""The Tavily search tool for retrieving relevant documents from the web."""


def _run_queries(search_queries: list[str]) -> list[str]:
    """Run the search queries.

    Args:
        search_queries (list[str]): The list of search queries to run.

    Returns:
        list[str]: The list of search results.
    """
    return _tavily_tool.batch([{"query": query} for query in search_queries])


execute_tools = ToolNode(
    [
        StructuredTool.from_function(
            _run_queries, name=Answer.__name__, description=Answer.__doc__
        ),
        StructuredTool.from_function(
            _run_queries,
            name=Revised.__name__,
            description=Revised.__doc__,
        ),
    ]
)
"""The tool node for executing the search queries.

This node executes the search queries, using the Tavily search tool, depending on the tool name:
- If the tool name is "Answer", it returns search results for the initial answer.
- If the tool name is "Revised", it returns search results made to revise the previous answer.
"""
