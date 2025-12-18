# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mistral Vibe is Mistral AI's open-source CLI coding assistant. It provides a conversational interface to codebases with tools for file manipulation, code searching, and command execution.

## Common Commands

```bash
# Install dependencies
uv sync --all-extras

# Run the CLI
uv run vibe

# Run all tests (uses pytest-xdist for parallel execution)
uv run pytest

# Run a specific test file
uv run pytest tests/test_agent_tool_call.py

# Run a specific test function
uv run pytest tests/test_agent_tool_call.py::test_function_name -k "test_name"

# Linting and formatting
uv run ruff check .              # Check for linting issues
uv run ruff check --fix .        # Auto-fix linting issues
uv run ruff format .             # Format code

# Type checking
uv run pyright

# Run all pre-commit hooks
uv run pre-commit run --all-files

# Version bumping
uv run scripts/bump_version.py patch  # or minor, major
```

## Architecture

### Entrypoints
- `vibe` → `vibe/cli/entrypoint.py` - Interactive CLI mode with Textual UI
- `vibe-acp` → `vibe/acp/entrypoint.py` - ACP (Agent Client Protocol) server mode

### Core Components (`vibe/core/`)
- `agent.py` - Main `Agent` class orchestrating LLM interactions and tool execution
- `config.py` - `VibeConfig` Pydantic settings model; loads from `~/.vibe/config.toml`
- `tools/` - Tool system with `BaseTool` abstract class, `ToolManager`, and MCP integration
- `llm/` - Backend abstraction layer supporting Mistral and generic OpenAI-compatible APIs
- `middleware.py` - Conversation middleware pipeline (auto-compact, context warnings, limits)
- `system_prompt.py` - System prompt generation from markdown templates in `prompts/`

### CLI Layer (`vibe/cli/`)
- `textual_ui/` - Textual-based terminal UI with widgets for chat, tool approval, completions
- `autocompletion/` - Path (`@`) and slash command (`/`) completion controllers
- `commands.py` - Slash command definitions and handlers
- `update_notifier/` - Version update checking with ports/adapters pattern

### ACP Mode (`vibe/acp/`)
- Alternative server mode implementing Agent Client Protocol
- Separate tool implementations optimized for ACP context

### Configuration
- Global config: `~/.vibe/config.toml`
- Project-specific: `.vibe/config.toml` (takes precedence)
- API keys: `~/.vibe/.env` or environment variables
- Custom prompts: `~/.vibe/prompts/*.md`
- Custom agents: `~/.vibe/agents/*.toml`

## Code Style Requirements

- Python 3.12+ with modern idioms (match-case, walrus operator, `list`/`dict` generics, `|` unions)
- All files must have `from __future__ import annotations` as first import
- Use Pydantic v2 for data models and validation
- Use `pathlib.Path` over `os.path`
- Avoid deep nesting - prefer early returns and guard clauses
- Never use `# type: ignore` or `# noqa` - fix the underlying type issue instead
- Always use `uv run` to execute Python commands, never bare `python` or `pip`

## Testing

Tests use pytest with pytest-asyncio and pytest-textual-snapshot for UI testing. Test configuration in `pyproject.toml` sets `-n auto` for parallel execution and 10-second timeout per test.