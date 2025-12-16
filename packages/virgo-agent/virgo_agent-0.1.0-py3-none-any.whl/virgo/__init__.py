"""Virgo - Assistant to generate, review and improve articles.

This package is organized into three main subpackages:
- agent: LangGraph implementation (chains, tools, graph)
- actions: Use cases/application layer (protocols and actions)
- cli: Command-line interface
"""

# Re-export main classes for convenience
from virgo.actions import ArticleGenerator, GenerateArticleAction
from virgo.agent import VirgoAgent
from virgo.agent.schemas import MarkdownArticle

__all__ = [
    "ArticleGenerator",
    "GenerateArticleAction",
    "MarkdownArticle",
    "VirgoAgent",
]
