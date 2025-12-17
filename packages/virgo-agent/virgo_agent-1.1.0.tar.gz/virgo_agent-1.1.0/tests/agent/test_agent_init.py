"""Tests for VirgoAgent.from_llm integration wiring."""

from __future__ import annotations

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableLambda

from virgo.agent import VirgoAgent
from virgo.agent.schemas import MarkdownArticle


class DescribeVirgoAgentFromLLM:
    def it_builds_agent_and_generates_markdown(self, monkeypatch):
        """Smoke test: from_llm wires chains/graph and returns formatted article."""

        def _first_responder_chain(_llm):
            return RunnableLambda(
                lambda _input: AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "id": "call_answer",
                            "name": "Answer",
                            "args": {
                                "value": "Draft answer",
                                "reflection": {"missing": "", "superfluous": ""},
                                "search_queries": [],
                            },
                        }
                    ],
                )
            )

        def _revisor_chain(_llm):
            return RunnableLambda(
                lambda _input: AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "id": "call_revised",
                            "name": "Revised",
                            "args": {
                                "value": "Final content with refs",
                                "reflection": {"missing": "", "superfluous": ""},
                                "search_queries": [],
                                "references": ["[1] Source"],
                            },
                        }
                    ],
                )
            )

        def _formatter_chain(_llm):
            return RunnableLambda(
                lambda _input: [
                    MarkdownArticle(
                        title="Generated Article",
                        summary="Summary",
                        content="## Section\n\nFinal content with refs",
                        references=["[1] Source"],
                    )
                ]
            )

        def _execute_tools(state):
            messages = state.get("messages", [])
            tool_messages: list[ToolMessage] = []
            for msg in messages:
                if isinstance(msg, AIMessage) and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_messages.append(
                            ToolMessage(
                                content="tool result",
                                tool_call_id=tool_call["id"],
                            )
                        )
            return {"messages": tool_messages}

        monkeypatch.setattr(
            "virgo.agent.chains.create_first_responder_chain", _first_responder_chain
        )
        monkeypatch.setattr("virgo.agent.chains.create_revisor_chain", _revisor_chain)
        monkeypatch.setattr(
            "virgo.agent.chains.create_markdown_formatter_chain", _formatter_chain
        )
        # Also patch symbols imported into virgo.agent module namespace so from_llm uses stubs
        monkeypatch.setattr(
            "virgo.agent.create_first_responder_chain", _first_responder_chain
        )
        monkeypatch.setattr("virgo.agent.create_revisor_chain", _revisor_chain)
        monkeypatch.setattr(
            "virgo.agent.create_markdown_formatter_chain", _formatter_chain
        )
        monkeypatch.setattr(
            "virgo.agent.graph.execute_tools", RunnableLambda(_execute_tools)
        )

        agent = VirgoAgent.from_llm(object())

        article = agent.generate("What is AI?")

        assert isinstance(article, MarkdownArticle)
        assert article.title == "Generated Article"
        assert "Final content" in article.content
        assert article.references == ["[1] Source"]
