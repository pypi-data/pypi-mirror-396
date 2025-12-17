# Virgo AI Coding Instructions

You are an expert Python developer working on **Virgo**, a CLI assistant for generating and reviewing articles. This project uses a modern stack including **LangChain**, **LangGraph**, **Typer**, and **Rich**.

## 🏗 Project Architecture

- **Core Logic (`virgo/agent/`)**: Built on **LangGraph**. The agent flows through nodes defined in `_VirgoNodes` (DRAFT, EXECUTE_TOOLS, REVISE, FORMAT).
  - **State**: `AnswerState` (`TypedDict`) tracks `messages` and `formatted_article`.
  - **Graph**: Defined in `virgo/agent/graph.py`.
  - **Chains**: LangChain runnables are in `virgo/agent/chains.py`.
- **CLI (`virgo/cli/`)**: Uses **Typer** for commands and **Rich** for output.
  - **Dependency Injection**: `dependency-injector` is used for wiring components (see `virgo/cli/container.py`).
- **Actions (`virgo/actions/`)**: High-level business logic invoked by the CLI (e.g., `GenerateArticleAction`).

## 🛠 Development Workflow

Use `uv` for all dependency management and task execution.

- **Install Dependencies**: `uv sync --group dev`
- **Run Tests**: `uv run task test`
- **Watch Tests (TDD)**: `uv run task test:watch` (Preferred for active development)
- **Lint & Fix**: `uv run task lint`
- **Format**: `uv run task format`
- **Type Check**: `uv run task type-check`

## 🧪 Testing Strategy

- **Unit Tests**: Located in `tests/`. Mock external LLM calls and tools.
- **Integration Tests**: Located in `integration/`. Require Docker (Ollama).
  - Run with: `docker compose -f docker-compose.development.yaml up -d --build && uv run task integration`
- **Conventions**:
  - Use `pytest` fixtures.
  - Mock `langchain_core.runnables.RunnableSerializable` for chain testing.

## 📝 Coding Conventions

- **Type Hints**: Strictly typed. Use `typing.Annotated`, `typing.TypedDict`, and `collections.abc.Sequence`.
- **Docstrings**: Google-style docstrings for all functions and classes.
- **Imports**: Sorted by `ruff`.
- **Environment**: Configuration via environment variables (see `README.md` and `virgo/config.py` if applicable).

## 🚀 Key Patterns

- **Graph Construction**: When modifying the agent, update `virgo/agent/graph.py`. Ensure state transitions are valid.
- **Dependency Injection**: When adding new services, register them in `virgo/cli/container.py` and inject them into commands using `@inject` and `Provide`.
- **Rich Output**: Use `rich.console.Console` for user-facing output. Avoid `print()`.

## ⚠️ Common Pitfalls

- **State Immutability**: LangGraph state updates should be handled carefully.
- **Async vs Sync**: Be mindful of async contexts, though the current CLI entry points are synchronous.
- **Ollama vs OpenAI**: The system supports both. Ensure changes are compatible with both providers where possible.
