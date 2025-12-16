"""Dependency injection container for Virgo CLI."""

from dependency_injector import containers, providers

from virgo.actions import GenerateArticleAction
from virgo.agent import VirgoAgent


class Container(containers.DeclarativeContainer):
    """DI container for Virgo application.

    This container manages the dependencies for the Virgo CLI,
    providing configured instances of agents and actions.

    Example usage:
        ```python
        from virgo.cli import container

        # Override for testing
        with container.generate_action.override(mock_action):
            result = runner.invoke(app, ["generate", "question"])
        ```
    """

    wiring_config = containers.WiringConfiguration(
        modules=["virgo.cli.commands"],
    )

    # Agent provider - singleton since it's stateless
    agent = providers.Singleton(VirgoAgent)

    # Action providers - factory creates new instance per invocation
    generate_action = providers.Factory(
        GenerateArticleAction,
        generator=agent,
    )


__all__ = [
    "Container",
]
