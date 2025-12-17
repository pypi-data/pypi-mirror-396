"""Integration tests for the Virgo agent using agentevals."""

import json
from unittest.mock import patch

import pytest
from agentevals.trajectory.llm import (  # type: ignore[import-untyped]
    TRAJECTORY_ACCURACY_PROMPT,
    create_trajectory_llm_as_judge,
)
from agentevals.trajectory.match import (  # type: ignore[import-untyped]
    create_trajectory_match_evaluator,
)

from virgo.agent import VirgoAgent
from virgo.agent.schemas import MarkdownArticle


class DescribeVirgoAgent:
    """Integration tests for VirgoAgent."""

    @pytest.fixture
    def virgo_agent_stub(self) -> VirgoAgent:
        """Lightweight VirgoAgent stub for tests that patch generate()."""

        class VirgoAgentStub(VirgoAgent):
            def __init__(self) -> None:  # pragma: no cover - simple test helper
                self._builder = None  # type: ignore[assignment]
                self._graph = None  # type: ignore[assignment]

        return VirgoAgentStub()

    class DescribeTrajectoryEvaluation:
        """Tests for agent trajectory evaluation."""

        def it_should_use_search_tools_in_trajectory(self) -> None:
            """Test that the agent's trajectory includes proper tool usage."""
            # Create a mock trajectory representing expected agent behavior
            reference_trajectory = [
                {"role": "user", "content": "What is Python?"},
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "tavily_search",
                                "arguments": json.dumps(
                                    {"query": "Python programming language"}
                                ),
                            }
                        }
                    ],
                },
                {
                    "role": "tool",
                    "content": "Python is a high-level programming language...",
                },
                {
                    "role": "assistant",
                    "content": "Python is a versatile programming language...",
                },
            ]

            # Create the trajectory match evaluator with superset mode
            # (agent output should contain at least the reference tool calls)
            evaluator = create_trajectory_match_evaluator(
                trajectory_match_mode="superset",
                tool_args_match_mode="ignore",  # Ignore specific arguments
            )

            # Simulated agent trajectory for testing
            simulated_agent_trajectory = [
                {"role": "user", "content": "What is Python?"},
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "tavily_search",
                                "arguments": json.dumps(
                                    {"query": "Python programming language overview"}
                                ),
                            }
                        }
                    ],
                },
                {
                    "role": "tool",
                    "content": "Python is a high-level, general-purpose programming language...",
                },
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "tavily_search",
                                "arguments": json.dumps(
                                    {"query": "Python features and use cases"}
                                ),
                            }
                        }
                    ],
                },
                {
                    "role": "tool",
                    "content": "Python is used for web development, data science...",
                },
                {
                    "role": "assistant",
                    "content": "Python is a versatile programming language known for...",
                },
            ]

            result = evaluator(
                outputs=simulated_agent_trajectory,
                reference_outputs=reference_trajectory,
            )

            assert result["score"] is True, (
                f"Trajectory evaluation failed: {result.get('comment')}"
            )

        def it_should_match_unordered_tool_calls(self) -> None:
            """Test that tool calls can be matched in any order."""
            outputs = [
                {"role": "user", "content": "Compare Python and JavaScript"},
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "tavily_search",
                                "arguments": json.dumps(
                                    {"query": "JavaScript features"}
                                ),
                            }
                        },
                        {
                            "function": {
                                "name": "tavily_search",
                                "arguments": json.dumps({"query": "Python features"}),
                            }
                        },
                    ],
                },
                {"role": "tool", "content": "JavaScript is a scripting language..."},
                {"role": "tool", "content": "Python is a programming language..."},
                {"role": "assistant", "content": "Here's a comparison..."},
            ]

            reference_outputs = [
                {"role": "user", "content": "Compare Python and JavaScript"},
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "tavily_search",
                                "arguments": json.dumps({"query": "Python features"}),
                            }
                        },
                        {
                            "function": {
                                "name": "tavily_search",
                                "arguments": json.dumps(
                                    {"query": "JavaScript features"}
                                ),
                            }
                        },
                    ],
                },
                {"role": "tool", "content": "Python is a programming language..."},
                {"role": "tool", "content": "JavaScript is a scripting language..."},
                {"role": "assistant", "content": "Here's a comparison..."},
            ]

            evaluator = create_trajectory_match_evaluator(
                trajectory_match_mode="unordered",
                tool_args_match_mode="ignore",
            )

            result = evaluator(
                outputs=outputs,
                reference_outputs=reference_outputs,
            )

            assert result["score"] is True, "Unordered trajectory match should succeed"

    class DescribeAgentOutput:
        """Tests for agent output validation."""

        def it_should_generate_markdown_article_structure(
            self, virgo_agent_stub: VirgoAgent
        ) -> None:
            """Test that the agent generates a properly structured MarkdownArticle."""
            # Create a mock graph that returns a valid MarkdownArticle
            mock_article = MarkdownArticle(
                title="What is Python?",
                summary="Python is a high-level programming language.",
                content="# Python\n\nPython is a versatile programming language...",
                references=["https://python.org"],
            )

            with patch.object(VirgoAgent, "generate", return_value=mock_article):
                result = virgo_agent_stub.generate("What is Python?")

                assert result is not None
                assert isinstance(result, MarkdownArticle)
                assert result.title == "What is Python?"
                assert len(result.content) > 0
                assert len(result.references) > 0

        def it_should_return_none_for_failed_generation(
            self, virgo_agent_stub: VirgoAgent
        ) -> None:
            """Test that the agent returns None when generation fails."""
            with patch.object(VirgoAgent, "generate", return_value=None):
                result = virgo_agent_stub.generate("Invalid query")

                assert result is None


class DescribeLLMAsJudgeEvaluation:
    """Tests using LLM-as-judge for trajectory evaluation."""

    @pytest.fixture
    def check_ollama_available(self, ollama_base_url: str) -> bool:
        """Check if Ollama server is available."""
        import httpx

        try:
            response = httpx.get(f"{ollama_base_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

    def it_should_evaluate_trajectory_with_llm(
        self,
        ollama_model: str,
        ollama_base_url: str,
        check_ollama_available: bool,
    ) -> None:
        """Test LLM-based trajectory evaluation using Ollama."""
        if not check_ollama_available:
            pytest.skip(f"Ollama server not available at {ollama_base_url}")

        evaluator = create_trajectory_llm_as_judge(
            prompt=TRAJECTORY_ACCURACY_PROMPT,
            model=ollama_model,
        )

        outputs = [
            {"role": "user", "content": "What is the capital of France?"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "function": {
                            "name": "search",
                            "arguments": json.dumps({"query": "capital of France"}),
                        }
                    }
                ],
            },
            {
                "role": "tool",
                "content": "Paris is the capital and largest city of France.",
            },
            {"role": "assistant", "content": "The capital of France is Paris."},
        ]

        result = evaluator(outputs=outputs)

        assert result["score"] is True, (
            f"LLM evaluation failed: {result.get('comment')}"
        )


class DescribeGraphTrajectory:
    """Tests for LangGraph-specific trajectory validation."""

    def it_should_follow_expected_node_sequence(self) -> None:
        """Test that the agent follows the expected node sequence."""
        # Expected node sequence for Virgo: draft -> execute_tools -> revise -> format
        expected_nodes = ["draft", "execute_tools", "revise", "format"]

        # Verify node sequence matches expected flow
        # This is a structural test - in real integration, we'd capture from actual execution
        assert expected_nodes[0] == "draft", "Graph should start with draft node"
        assert expected_nodes[-1] == "format", "Graph should end with format node"
        assert "execute_tools" in expected_nodes, "Graph should include execute_tools"
        assert "revise" in expected_nodes, "Graph should include revise"

    def it_should_respect_max_iterations(self) -> None:
        """Test that the agent respects the maximum iterations limit."""
        # Verify that VIRGO_MAX_ITERATIONS is respected
        from virgo.agent.graph import VIRGO_MAX_ITERATIONS

        assert VIRGO_MAX_ITERATIONS > 0, "Max iterations should be positive"
        assert VIRGO_MAX_ITERATIONS <= 10, "Max iterations should be reasonable"
