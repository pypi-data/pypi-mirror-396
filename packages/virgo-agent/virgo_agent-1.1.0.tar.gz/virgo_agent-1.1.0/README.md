# Virgo

[![pypi](https://img.shields.io/pypi/v/virgo-agent.svg)](https://pypi.org/project/virgo-agent/)
[![python](https://img.shields.io/pypi/pyversions/virgo-agent.svg)](https://pypi.org/project/virgo-agent/)
[![Build Status](https://github.com/William-Fernandes252/virgo/actions/workflows/ci.yaml/badge.svg)](https://github.com/William-Fernandes252/virgo/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/William-Fernandes252/virgo/branch/master/graph/badge.svg?token=bcPzCjDnSk)](https://codecov.io/gh/William-Fernandes252/virgo)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Virgo is a command-line assistant that helps you generate, review, and improve articles. It blends retrieval (Tavily), reasoning (LangChain + LangGraph), and drafting (OpenAI) into a guided flow so you can go from idea to polished copy quickly.

## Quickstart

1) Install (from PyPI):

```bash
pip install virgo-agent

# Optional: add Ollama provider support
pip install "virgo-agent[ollama]"
```

1) Configure your environment (see next section), then run:

```bash
virgo --help
```

## Environment

Set these variables before running Virgo:

| Variable | Required | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | Drafting, rewrites, and reviews via OpenAI models |
| `TAVILY_API_KEY` | Yes | Web research to gather facts and sources |
| `LANGSMITH_API_KEY` | Optional | Observability and tracing via LangSmith |
| `LANGSMITH_TRACING` | Optional | Enable LangSmith tracing (`true`/`false`) |
| `LANGSMITH_ENDPOINT` | Optional | Override LangSmith endpoint |
| `LANGSMITH_PROJECT` | Optional | LangSmith project name |
| `VIRGO_GENAI_PROVIDER` | Optional | `openai` (default) or `ollama` |
| `VIRGO_MODEL_NAME` | Optional | Model name for the chosen provider (default `gpt-4-turbo`) |
| `VIRGO_MAX_ITERATIONS` | Optional | Max tool iterations the agent will run (default `5`) |
| `OLLAMA_MODEL` | Optional | Model name for local integration tests (e.g., `llama3.2:1b`) |
| `OLLAMA_BASE_URL` | Optional | Ollama base URL (e.g., `http://localhost:11434`) |

Tips:

- Put secrets in a local `.env` (not committed) or manage them via `mise`.
- Python requirement: 3.14 (pre-release builds are fine).

## How It Works (High-Level)

- **LangChain** orchestrates LLM calls and tool usage for drafting and review steps.
- **LangGraph** wires these steps into a controllable graph: gather context → draft → critique → refine.
- **Tavily** performs targeted web searches to pull fresh facts and references.
- **OpenAI** provides the language model for generation and editing.
- **Ollama** can be used as an alternative model provider when installed (`virgo-agent[ollama]`) and selected via `VIRGO_GENAI_PROVIDER=ollama`.
- **Rich** and **Typer** power the CLI experience (progress, prompts, commands).

Workflow overview:

1) You provide a topic and intent via the CLI.
2) Virgo runs Tavily searches to collect supporting context.
3) LangGraph coordinates drafting with OpenAI, then runs critique/refinement passes.
4) The final article is returned with suggested improvements and sources.

## Common Commands

- Show help: `virgo --help`
- Generate/review (example): `virgo generate "AI safety"`

## For Contributors

Developer tooling uses `uv` for fast installs:

- Install deps: `uv sync --group dev`
- Lint: `uv run task lint:ci`
- Format check: `uv run task format:ci`
- Type check: `uv run task type-check`
- Tests with coverage: `uv run pytest tests --cov=virgo --cov-report=term-missing`
- Integration tests (needs Docker + Ollama):

  ```bash
  docker compose -f docker-compose.development.yaml up -d --build
  uv run task integration
  docker compose -f docker-compose.development.yaml down
  ```
