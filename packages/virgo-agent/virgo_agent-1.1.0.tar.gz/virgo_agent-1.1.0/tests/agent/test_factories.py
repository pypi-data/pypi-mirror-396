"""Unit tests for the Virgo agent factories module."""

from __future__ import annotations

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from virgo.agent.factories import create_virgo_agent


class _StubToolBindingLLM:
    def __init__(self, response: AIMessage):
        self._response = response

    def bind_tools(self, *_, **__) -> RunnableLambda:  # pragma: no cover
        return RunnableLambda(lambda _input: self._response)


class DescribeCreateVirgoAgent:
    def it_returns_a_virgo_agent_instance(self):
        """Smoke test: the factory returns a configured VirgoAgent."""
        llm = _StubToolBindingLLM(
            response=AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "Answer",
                        "args": {
                            "value": "",
                            "reflection": {"missing": "", "superfluous": ""},
                            "search_queries": [],
                        },
                    }
                ],
            )
        )

        agent = create_virgo_agent(llm)

        # Keep this intentionally lightweight: compiling the graph is enough here.
        assert agent is not None
        assert hasattr(agent, "generate")
