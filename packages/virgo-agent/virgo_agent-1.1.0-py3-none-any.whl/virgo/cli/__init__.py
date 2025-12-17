"""CLI module for Virgo command-line interface."""

from virgo.cli.commands import app
from virgo.cli.container import Container, VirgoSettings

# Initialize the container (auto-wires to commands module via wiring_config)
container = Container()
container.config.from_pydantic(VirgoSettings())

__all__ = [
    "app",
    "container",
]
