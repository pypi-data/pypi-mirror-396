# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-14

### Added

- Optional `ollama` dependency group for installing Ollama provider support (`virgo-agent[ollama]`).
- Environment-driven settings for GenAI provider, model name, and max iterations (`VIRGO_GENAI_PROVIDER`, `VIRGO_MODEL_NAME`, `VIRGO_MAX_ITERATIONS`).
- Tests covering the CLI container and settings model, including env var loading.

### Changed

- README updated with provider selection, optional Ollama install instructions, and new environment variables.

## [1.0.0] - 2025-12-12

### Added

- Initial project structure with CLI, agent, and actions modules
- LangGraph-based agent implementation for article generation
- Integration with OpenAI and Tavily for research capabilities
- GitHub Actions CI/CD pipeline with automated testing and PyPI releases
- Codecov integration for coverage reporting

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.0] - 2025-12-12

### Added

- Initial release
- Article generation assistant using LangChain and LangGraph
- CLI interface with Typer
- Support for generating, reviewing, and improving articles
