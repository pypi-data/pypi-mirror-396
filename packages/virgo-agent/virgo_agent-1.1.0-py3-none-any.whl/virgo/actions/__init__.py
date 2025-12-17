"""Actions module containing use cases and protocols for Virgo."""

from virgo.actions.generate import GenerateArticleAction
from virgo.actions.protocols import ArticleGenerator

__all__ = [
    "ArticleGenerator",
    "GenerateArticleAction",
]
