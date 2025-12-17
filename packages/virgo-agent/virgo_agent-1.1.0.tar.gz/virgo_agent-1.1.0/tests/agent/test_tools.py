"""Unit tests for the Virgo agent tools module."""

from unittest.mock import patch

from langgraph.prebuilt import ToolNode

from virgo.agent.tools import _run_queries, execute_tools


class DescribeRunQueries:
    """Tests for the _run_queries function."""

    def it_calls_tavily_batch_with_formatted_queries(self):
        """Verify _run_queries formats queries correctly for Tavily batch."""
        mock_results = [
            [{"content": "Result 1"}],
            [{"content": "Result 2"}],
        ]

        with patch("virgo.agent.tools._tavily_tool") as mock_tavily:
            mock_tavily.batch.return_value = mock_results

            queries = ["query 1", "query 2"]
            result = _run_queries(queries)

            mock_tavily.batch.assert_called_once_with(
                [
                    {"query": "query 1"},
                    {"query": "query 2"},
                ]
            )
            assert result == mock_results

    def it_handles_single_query(self):
        """Verify _run_queries handles a single query."""
        mock_results = [[{"content": "Single result"}]]

        with patch("virgo.agent.tools._tavily_tool") as mock_tavily:
            mock_tavily.batch.return_value = mock_results

            result = _run_queries(["single query"])

            mock_tavily.batch.assert_called_once_with([{"query": "single query"}])
            assert result == mock_results

    def it_handles_empty_query_list(self):
        """Verify _run_queries handles empty query list."""
        with patch("virgo.agent.tools._tavily_tool") as mock_tavily:
            mock_tavily.batch.return_value = []

            result = _run_queries([])

            mock_tavily.batch.assert_called_once_with([])
            assert result == []

    def it_returns_batch_results(self):
        """Verify _run_queries returns the batch results directly."""
        expected_results = [
            [{"url": "https://example.com", "content": "Content 1"}],
            [{"url": "https://test.com", "content": "Content 2"}],
            [{"url": "https://demo.com", "content": "Content 3"}],
        ]

        with patch("virgo.agent.tools._tavily_tool") as mock_tavily:
            mock_tavily.batch.return_value = expected_results

            result = _run_queries(["q1", "q2", "q3"])

            assert result == expected_results
            assert len(result) == 3


class DescribeExecuteTools:
    """Tests for the execute_tools ToolNode."""

    def it_is_a_tool_node(self):
        """Verify execute_tools is a ToolNode instance."""
        assert isinstance(execute_tools, ToolNode)

    def it_has_answer_tool(self):
        """Verify execute_tools contains an Answer tool."""
        tool_names = [tool.name for tool in execute_tools.tools_by_name.values()]
        assert "Answer" in tool_names

    def it_has_revised_tool(self):
        """Verify execute_tools contains a Revised tool."""
        tool_names = [tool.name for tool in execute_tools.tools_by_name.values()]
        assert "Revised" in tool_names

    def it_has_two_tools(self):
        """Verify execute_tools has exactly two tools."""
        assert len(execute_tools.tools_by_name) == 2

    def it_answer_tool_accepts_search_queries(self):
        """Verify Answer tool has search_queries parameter."""
        answer_tool = execute_tools.tools_by_name.get("Answer")
        assert answer_tool is not None
        # Check the tool's input schema
        schema = answer_tool.args_schema
        assert schema is not None
        assert "search_queries" in schema.model_fields

    def it_revised_tool_accepts_search_queries(self):
        """Verify Revised tool has search_queries parameter."""
        revised_tool = execute_tools.tools_by_name.get("Revised")
        assert revised_tool is not None
        schema = revised_tool.args_schema
        assert schema is not None
        assert "search_queries" in schema.model_fields


class DescribeToolDescriptions:
    """Tests for tool descriptions."""

    def it_answer_tool_has_description(self):
        """Verify Answer tool has a description from the schema."""
        answer_tool = execute_tools.tools_by_name.get("Answer")
        assert answer_tool is not None
        assert answer_tool.description is not None
        assert len(answer_tool.description) > 0

    def it_revised_tool_has_description(self):
        """Verify Revised tool has a description from the schema."""
        revised_tool = execute_tools.tools_by_name.get("Revised")
        assert revised_tool is not None
        assert revised_tool.description is not None
        assert len(revised_tool.description) > 0
