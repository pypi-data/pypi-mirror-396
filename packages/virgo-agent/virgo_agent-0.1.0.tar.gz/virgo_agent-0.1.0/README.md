# Virgo

Virgo is a command-line assistant that helps you generate, review, and improve articles. It blends retrieval (Tavily), reasoning (LangChain + LangGraph), and drafting (OpenAI) into a guided flow so you can go from idea to polished copy quickly.

## Quickstart

1) Install (from PyPI):

```bash
pip install virgo-agent
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
