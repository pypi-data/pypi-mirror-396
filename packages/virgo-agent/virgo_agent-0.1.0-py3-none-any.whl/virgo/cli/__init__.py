"""CLI module for Virgo command-line interface."""

from virgo.cli.commands import app
from virgo.cli.container import Container

# Initialize the container (auto-wires to commands module via wiring_config)
container = Container()

__all__ = [
    "app",
    "container",
]
