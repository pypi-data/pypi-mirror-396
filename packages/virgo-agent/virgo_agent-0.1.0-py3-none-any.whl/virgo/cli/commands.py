"""CLI commands for Virgo."""

from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from rich.markdown import Markdown

from virgo.actions import GenerateArticleAction
from virgo.cli.container import Container

app = typer.Typer(
    name="virgo",
    help="Virgo - Assistant to generate, review and improve articles.",
)
console = Console()


@inject
def _execute_generate(
    question: str,
    action: GenerateArticleAction = Provide[Container.generate_action],
) -> None:
    """Execute article generation with injected action."""
    with console.status("[bold green]Generating article...[/bold green]"):
        article = action.execute(question)

    if article:
        markdown_content = article.to_markdown()
        console.print(Markdown(markdown_content))
    else:
        typer.secho(
            "Failed to generate article. Please try again.",
            fg=typer.colors.RED,
        )


@app.command()
def generate(
    question: Annotated[
        str, typer.Argument(..., help="The input question to generate an article for.")
    ],
) -> None:
    """Generate an article using the Virgo assistant."""
    _execute_generate(question)


@app.callback()
def main() -> None:
    """Virgo - Assistant to generate, review and improve articles."""
    pass


__all__ = [
    "app",
    "generate",
]
