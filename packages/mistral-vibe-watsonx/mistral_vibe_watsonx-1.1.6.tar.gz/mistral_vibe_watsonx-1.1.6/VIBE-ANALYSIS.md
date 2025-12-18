# VIBE-ANALYSIS.md

*Generated: 2025-12-14 21:56*

This file provides comprehensive analysis of the codebase for AI coding assistants.

## Project Overview

Mistral Vibe delivers an interactive terminal‑based coding assistant that lets developers issue natural‑language prompts, have the VibeAgent orchestrate LLM responses, and automatically invoke file‑system tools (read, write, search‑replace, etc.) via the ACP protocol, with support for Mistral, WatsonX and other backends. It is packaged as a CLI/TUI (the VibeApp) for software engineers who need fast, context‑aware code generation, refactoring, and debugging directly from their shell without leaving their development workflow.

---

## Technology Stack

| Language | Version |
|----------|---------|
| Python   | ≥ 3.12 |

| Key Frameworks & Libraries | Primary Use |
|----------------------------|--------------|
| **Textual** (≥ 1.0.0) | Terminal‑based UI framework (TUI) |
| **Rich** (≥ 14.0.0) | Rich‑text rendering & styling (used by Textual) |
| **httpx** (≥ 0.28.1) | Async HTTP client for backend adapters |
| **aiofiles** (≥ 24.1.0) | Async file I/O |
| **pydantic** (≥ 2.12.4) | Data validation & settings models |
| **pydantic‑settings** (≥ 2.12.0) | Environment‑variable‑driven configuration |
| **tenacity** (≥ 8.2.0) | Retry logic with exponential back‑off |
| **textual‑speedups** (≥ 0.2.1) | Performance optimizations for Textual |
| **agent‑client‑protocol** (0.6.3) | Defines the ACP (Agent Communication Protocol) |
| **mcp** (≥ 1.14.0) | Mistral Control Protocol utilities |
| **mistralai** (1.9.11) | SDK for Mistral LLM API |
| **watchfiles** (≥ 1.1.1) | File‑system watching (e.g., config reload) |
| **pyperclip** (≥ 1.11.0) | Clipboard interaction (CLI copy/paste) |
| **python‑dotenv** (≥ 1.0.0) | Loading `.env` files for secrets |
| **packaging** (≥ 24.1) | Version parsing & requirement handling |
| **pexpect** (≥ 4.9.0) | Automating interactive processes (tests) |
| **tomli‑w** (≥ 1.2.0) | Writing TOML configuration files |
| **mistralai‑watsonx** (internal) | Adapter for IBM WatsonX LLM service |

| Build, Testing & Quality Tools | Category |
|--------------------------------|----------|
| **uv** (≥ 0.8.0) | Package manager & installer |
| **hatchling** / **hatch‑vcs** | Build backend (wheel creation) |
| **pyinstaller** (≥ 6.17.0) | Binary packaging |
| **pytest** (≥ 8.3.5) | Test runner |
| **pytest‑asyncio** (≥ 1.2.0) | Async test support |
| **pytest‑timeout** (≥ 2.4.0) | Test timeout enforcement |
| **pytest‑xdist** (≥ 3.8.0) | Parallel test execution |
| **pytest‑textual‑snapshot** (≥ 1.1.0) | Snapshot testing for Textual UI |
| **respx** (≥ 0.22.0) | HTTPX request mocking |
| **ruff** (≥ 0.14.5) | Linter & formatter |
| **pre‑commit** (≥ 4.2.0) | Git hook management |
| **pyright** (≥ 1.1.403) | Static type checking |
| **typos** (≥ 1.34.0) | Spell‑checking |
| **vulture** (≥ 2.14) | Dead code detection |
| **GitHub Actions** | CI/CD pipelines (build, test, release) |
| **twine** (≥ 5.0.0) | PyPI publishing |

| External Services & APIs | Role |
|--------------------------|------|
| **Mistral AI API** | LLM generation & tool usage |
| **IBM WatsonX API** | Alternative LLM backend |
| **Fireworks API** (used in test fixtures) | Mocked LLM service for tests |
| **Clipboard (system)** | Copy/paste support via `pyperclip` |
| **Environment variables** (`MISTRAL_API_KEY`, `WATSONX_API_KEY`, etc.) | Secure passing of credentials |
| **File system** | Config files, chat history, temporary files (no DB) |
| **Local HTTP services** (mock backends in tests) | Simulated backend endpoints |

---

## Development Commands

| Task | Command |
|------|---------|
| Install core dependencies | `uv sync` |
| Install **dev** dependencies (lint, tests, etc.) | `uv sync --group dev` |
| Run the Vibe CLI (defaults to the Textual UI) | `uv run vibe` |
| Run the Vibe ACP server | `uv run vibe-acp` |
| Run **all** tests (unit, integration, snapshot) | `uv run pytest -q` |
| Run tests with **coverage** report | `uv run pytest --cov=vibe --cov-report=term-missing` |
| Run a **specific test file** | `uv run pytest tests/acp/test_write_file.py -q` |
| Run a **specific test function** | `uv run pytest tests/acp/test_write_file.py::test_write_success -vv` |
| Run **snapshot** tests only | `uv run pytest -k snapshot -q` |
| Lint the codebase with **ruff** | `uv run ruff check .` |
| Auto‑fix lintable issues with **ruff** | `uv run ruff check . --fix` |
| Format code with **ruff** (PEP‑8, imports, etc.) | `uv run ruff format .` |
| Type‑check with **pyright** | `uv run pyright` |
| Run **pre‑commit** hooks locally | `uv run pre-commit run --all-files` |
| Build a **wheel** package | `uv build --wheel` |
| Build a **source distribution (sdist)** | `uv build --sdist` |
| Build both wheel and sdist (default) | `uv build` |
| Build a **stand‑alone executable** with PyInstaller (dev only) | `uv run pyinstaller --onefile --name vibe vibe/cli/entrypoint.py` |
| Clean build artefacts (`dist/`, `build/`, `*.egg-info/`) | `rm -rf dist build *.egg-info` |
| Upgrade all project dependencies to latest allowed versions | `uv lock --upgrade` |
| Re‑generate the lockfile after dependency changes | `uv lock` |
| Run the **interactive onboarding** flow (snapshot‑test mode) | `uv run pytest tests/onboarding/test_onboarding_flow.py -q` |
| Open the **documentation site** locally (if using MkDocs) | `uv run mkdocs serve` |

---

## Code Style Guidelines

**Naming Conventions**  
- **Classes & Exceptions** – PascalCase (e.g., `VibeApp`, `BackendFactory`, `AcpReadFileState`, `ConfigError`).  
- **Functions & Methods** – snake_case (e.g., `run_textual_ui`, `load_config`, `create_backend`).  
- **Variables & Attributes** – snake_case; constants are ALL_CAPS with underscores (e.g., `HISTORY_FILE`, `DEFAULT_TIMEOUT`).  
- **Modules & Packages** – all lower‑case, words separated by underscores when needed (e.g., `vibe/cli/commands.py`, `tests/acp/test_read_file.py`).  
- **Test Functions** – prefixed with `test_` and use snake_case for any helpers.  
- **Pydantic Models** – class name PascalCase, fields snake_case; field aliases follow the same naming style.

**Import Ordering & Organization**  
1. **Standard‑library imports** – alphabetically sorted.  
2. **Third‑party imports** – alphabetically sorted.  
3. **Project‑internal imports** – absolute imports only, alphabetically sorted.  

Each group is separated by a single blank line.  
Relative imports are forbidden (`ban-relative-imports = "all"`).  
Typical layout:  

```python
import asyncio
import json
import pathlib
from typing import Any, Callable

import aiofiles
import httpx
import pydantic
import rich
import textual

from vibe.core.agent import VibeAgent
from vibe.core.config import VibeConfig
from vibe.tools.base import BaseTool
```

**Type Hints & Annotations**  
- Every public function, method, and class attribute must have an explicit type annotation.  
- Use `typing` primitives (`str`, `int`, `list[str]`, `dict[str, Any]`, etc.) and modern syntax (`list[int]`, `dict[str, Any]`).  
- For async functions, annotate the return as `Awaitable[T]` or simply `Coroutine[Any, Any, T]` (e.g., `async def fetch() -> str:`).  
- Pydantic models use concrete field types and, where appropriate, `Annotated` for validators (e.g., `path: Annotated[Path, Field(...)]`).  
- Avoid bare `Any` unless the value truly cannot be typed; prefer `typing.Protocol` or concrete base classes.  
- Use forward‑referenced strings only when necessary to break circular imports.  

**Error Handling Patterns**  
- Raise specific, purpose‑built exception classes (e.g., `ConfigError`, `ToolExecutionError`).  
- When catching exceptions, log the error (using the project‑wide logger) and re‑raise if the caller cannot recover.  
- Wrap I/O‑heavy calls with the `@retry` decorator from **tenacity** to provide exponential back‑off and a sensible `stop` condition.  
- Use context managers for resource handling (`async with aiofiles.open(...) as f:`) and ensure cleanup via `__aexit__` / `finally`.  
- Validation errors from Pydantic are allowed to propagate; they are caught at the UI entry point to present a user‑friendly message.  

**Documentation Style**  
- Triple double‑quoted docstrings (`"""…"""`) for all modules, classes, public functions, and methods.  
- Begin with a concise one‑line summary, followed by a blank line and a more detailed description if needed.  
- Use the **Google style** sections for arguments, returns, and raises:

```python
def load_config(path: Path) -> VibeConfig:
    """Load and validate a Vibe configuration file.

    Args:
        path: Absolute path to a TOML configuration file.

    Returns:
        An instance of :class:`VibeConfig` populated with the file contents.

    Raises:
        ConfigError: If the file cannot be read or fails validation.
    """
```

- Inline comments should be brief, start with a capital letter, and end with a period.  
- Do not use commented‑out code; remove dead code instead.  

**Formatting Rules (as enforced by Ruff / pyproject.toml)**  
- Maximum line length: **88 characters**.  
- Use **single‑type imports** (`import pathlib`) unless multiple symbols are needed from the same module (`from typing import Any, Callable`).  
- Trailing commas are optional; the project disables the “magic trailing comma” check, but keep them where they improve diffs (e.g., multi‑line collections).  
- Blank lines: two before top‑level class or function definitions, one between methods inside a class.  
- No unused imports (`F401`): remove or prefix with `# noqa: F401` only when truly intentional.  
- No undefined names (`F821`).  
- Strict import sorting (`I001`) – use the order described above.  
- Docstring consistency (`D2xx`); missing docstrings on public objects are flagged.  
- Type annotation completeness (`ANN`).  
- Prefer modern syntax (`UP` – e.g., `list[str]` instead of `List[str]`).  

**Additional Conventions**  
- **Async‑first**: I/O, network, and file operations should be async where possible; synchronous fallbacks only for trivial, CPU‑bound utilities.  
- **Configuration**: All runtime configuration is accessed via the singleton‑like `VibeConfig`; never read environment variables directly outside this class.  
- **Logging**: Use the project‑wide logger (`logger = logging.getLogger(__name__)`) with level‑appropriate calls (`debug`, `info`, `warning`, `error`).  
- **Testing**: Tests must be fully typed, avoid `# type: ignore` unless absolutely required, and follow the same import ordering.  

Adhering to these conventions ensures consistency across the codebase, satisfies the Ruff‑based linting pipeline, and aligns with the project's architectural patterns.

---

## Architecture Overview

**Architecture Overview**

The Mistral Vibe application is organized as a layered, event‑driven system that separates concerns between configuration, core agent logic, tool execution, backend communication, and the Textual User Interface (TUI). The main layers are:

1. **Configuration Layer** – `VibeConfig` (singleton‑like) loads a TOML configuration file, merges environment‑variable overrides, and validates the result with **pydantic**. This layer is the single source of truth for API keys, model selection, backend choice, and UI defaults.

2. **Core Agent Layer** – `VibeAgent` (implemented in `vibe/core/agent.py`) owns an **AcpSession** that carries the chat history, **AcpToolState** objects, and any transient plan information. The agent receives user prompts, builds a plan, and invokes tools via the **ACP** (Agent Communication Protocol).  
   *Key abstractions*: `AcpToolState` (base), `AcpReadFileState`, `AcpWriteFileState`; `BackendFactory` (strategy for selecting a concrete LLM backend); `MiddlewarePipeline` (chain‑of‑responsibility for pre/post‑turn processing); `CommandRegistry` (maps slash commands to handlers).

3. **Tool Layer** – Each tool is a subclass of `BaseTool` (found under `vibe/core/tools/`). Tools implement a **Command**‑like `run` method, expose their own **AcpToolState** subclass, and register themselves in the **Renderer registry** so the UI can render results. The tool layer follows the **Template Method** pattern (common lifecycle in `BaseTool.run`) and the **Factory Method** for state creation (`_get_tool_state_class`).

4. **Backend Layer** – Adapters under `vibe/backend/` implement the **Adapter** pattern to translate the generic Vibe‑agent SDK calls into concrete HTTP requests using **httpx**. `BackendFactory` selects the appropriate adapter (e.g., Mistral, WatsonX) based on config, constituting a **Strategy** pattern. Each adapter incorporates **retry logic** via **tenacity** and uses **async context managers** to manage network sessions.

5. **Session & State Persistence** – `AcpSession` serialises the accumulated `AcpToolState` objects to disk, enabling multi‑session support (`tests/acp/test_multi_session.py`). The session objects are passed around via dependency injection (fixtures in tests) and are the contract between the agent and the UI.

6. **UI Layer (TUI)** – Implemented with **Textual** in `vibe/cli/textual_ui/app.py`. The `VibeApp` composes widgets (chat view, input box, tool panels) in a declarative `compose` method (Builder‑like). UI events (key presses, input changes) are turned into **messages** (`ToolResultMessage`, `LLMMessage`) that propagate through Textual’s **event‑driven UI** system. The UI observes the **AcpSession** for updates and posts messages back to the agent, thus closing the event loop.

7. **CLI Entrypoint** – `vibe/cli/entrypoint.py` (exposed as `vibe` console script) parses command‑line flags, instantiates `VibeConfig`, decides whether to launch the TUI (`run_textual_ui`) or execute a single‑shot command, and sets up the **middleware pipeline** for the chosen mode.

8. **Auxiliary Services** – Clipboard handling (`vibe/cli/clipboard`), init wizard (`vibe/cli/init`), autocompletion (`vibe/autocomplete`), and onboarding flow are separate modules that interact with the core through well‑defined interfaces (e.g., `PathCompleter`, `OnboardingController`). They rely on the **Observer** pattern via Textual messages or direct callbacks.

---

### Module Relationships & Contracts

| Module | Depends On | Provides / Contracts |
|--------|------------|----------------------|
| `vibe/cli/textual_ui/app.py` | `VibeConfig`, `VibeAgent`, `CommandRegistry`, `Clipboard`, `InitExecutor` | `VibeApp` (main UI), `run_textual_ui` entry point |
| `vibe/core/agent.py` | `BackendFactory`, `AcpSession`, `MiddlewarePipeline`, tool classes | `VibeAgent` (processes prompts, schedules tool calls) |
| `vibe/core/config.py` | `pydantic-settings`, environment variables | `VibeConfig` (global config singleton) |
| `vibe/core/tools/base.py` | `AcpToolState`, `Renderer registry` | Abstract `BaseTool` (template for concrete tools) |
| `vibe/backend/*` | `httpx`, `tenacity`, `VibeConfig` | Concrete backend adapters (Mistral, WatsonX) |
| `vibe/acp/entrypoint.py` | `AcpSession`, `VibeAgent` | `vibe-acp` CLI for direct ACP interaction |
| `vibe/cli/commands/CommandRegistry.py` | `vibe/cli/commands/*` | Mapping of slash commands (`/init`, `/set_mode`, …) to handlers |
| `vibe/autocomplete/*` | `vibe/core/config`, `vibe/core/tools` | Path and fuzzy completions used by the UI |
| Tests (`tests/**`) | All production modules | Fixture‑based dependency injection, mock backends, snapshot testing |

All cross‑module interactions respect **interface contracts** (e.g., a backend must implement `generate`, `stream`, and `close` methods defined by a protocol) and are mediated through factories or registries, ensuring loose coupling.

---

### Key Design Patterns

| Pattern | Where Used | Purpose |
|---------|------------|---------|
| **Factory / Strategy** | `BackendFactory`, `CommandRegistry`, `Renderer registry` | Choose concrete implementation at runtime based on config or tool type. |
| **Template Method** | `BaseTool.run`, `VibeApp.compose` | Define invariant steps while allowing subclasses to customise parts (tool execution, UI layout). |
| **Command** | Slash command handlers, tool invocation via ACP | Encapsulate user actions as objects that can be executed, logged, and undone. |
| **Observer / Event‑Driven** | Textual message system, `AcpSession` change notifications, middleware pipeline | Decouple producers (agent, backend) from consumers (UI, logger). |
| **Builder** | `IndexBuilder`, UI composition in `VibeApp.compose` | Incrementally assemble complex objects (index results, widget hierarchies). |
| **Chain of Responsibility** | `MiddlewarePipeline` (pre‑turn, post‑turn middlewares) | Allow extensible processing of messages without tight coupling. |
| **Adapter** | Backend adapters (`MistralBackend`, `WatsonXBackend`), tool UI adapters | Translate external SDK/API signatures to Vibe internal protocol. |
| **Singleton‑like** | `VibeConfig`, global logger | Provide a single, globally accessible configuration/state source. |
| **Retry (Decorator)** | Network calls in backends (`@retry` via tenacity) | Add resilience to flaky I/O. |
| **Snapshot Testing** | `tests/snapshots/*` | Guard against UI regressions by comparing rendered output to stored snapshots. |
| **Pilot Pattern** | Textual UI tests (`tests/*/test_ui_*`) | Programmatically drive the TUI to simulate user interaction. |

---

### Data Flow / Request Lifecycle

1. **User Input** – Keyboard event in the TUI is captured by `BottomApp` and emitted as a `UserMessage` event.  
2. **Command Dispatch** – If the message starts with a slash, `CommandRegistry` resolves the appropriate handler; otherwise the text is forwarded to `VibeAgent.act` via the ACP **async generator**.  
3. **Agent Planning** – `VibeAgent` analyses the prompt, optionally consults middleware, and decides whether to call a tool.  
4. **Tool Execution** – The agent creates (or loads) the corresponding `AcpToolState`, calls the concrete tool’s `run`. The tool may request file I/O, search/replace, etc., updating its state.  
5. **Result Rendering** – Tool returns a `ToolResult` which is handed to the **Renderer registry**; a `ToolResultMessage` containing a Rich/Textual widget is posted back to the UI.  
6. **Backend Interaction** – If the agent needs LLM completion, it asks the selected backend via `BackendFactory`. The backend issues an async HTTP request (httpx) with tenacity retry; streaming chunks are yielded back to the agent as an **async generator**.  
7. **Session Persistence** – After each turn, the updated `AcpSession` (including all tool states) is serialised to disk, enabling later retrieval and multi‑session continuity.  
8. **UI Update** – The UI receives the `ToolResultMessage` (or streaming `LLMMessage`), updates the chat view, and re‑enables the input box. If a tool requires approval, the UI shows a modal; the user’s decision is sent back through the ACP channel to the agent.

---

### Critical Files & Their Roles

| File | Role |
|------|------|
| `vibe/core/config.py` | Global configuration loader (`VibeConfig`). |
| `vibe/core/agent.py` | Core AI orchestration (`VibeAgent`). |
| `vibe/core/types.py` | Pydantic models for messages, tool arguments, and results. |
| `vibe/core/tools/base.py` | Abstract tool definition and state handling. |
| `vibe/backend/*` | Backend adapters; concrete LLM communication. |
| `vibe/acp/entrypoint.py` | CLI entry point for raw ACP sessions (`vibe‑acp`). |
| `vibe/cli/textual_ui/app.py` | Main TUI application (`VibeApp`), UI composition, event loop. |
| `vibe/cli/commands/CommandRegistry.py` | Registry mapping slash commands to handler callables. |
| `vibe/cli/clipboard/*` | Clipboard utilities used by the UI and tests. |
| `vibe/autocomplete/*` | Path/fuzzy completers that drive the autocompletion UI. |
| `vibe/cli/init/*` | Project‑initialisation flow (`/init` command). |
| `tests/**` | Comprehensive test suite exercising all layers, including snapshot and pilot UI tests. |

---

### Entry Points

* **`vibe` console script** (`vibe.cli.entrypoint:main`) – Parses CLI options, loads `VibeConfig`, and either launches the TUI (`run_textual_ui`) or executes a one‑off command.
* **`vibe-acp` console script** (`vibe.acp.entrypoint:main`) – Exposes the raw ACP protocol for external tools, creating an `AcpSession` and driving `VibeAgent` without the UI.
* **`vibe/cli/textual_ui/app.py`** – Defines `run_textual_ui()` which instantiates `VibeApp` and starts the Textual event loop; this is the primary user‑facing entry point when the CLI is invoked without sub‑commands.

---

### Summary

Mistral Vibe is a modular, test‑driven application built around a central **agent** that talks to LLM backends via a **strategy‑based factory**, coordinates tool execution through the **Agent Communication Protocol**, and presents a responsive **Textual UI** driven by an **event‑bus**. Configuration, state persistence, and extensibility are handled through well‑defined contracts (pydantic models, registries, and middleware), enabling clean separation between UI, business logic, and external services while supporting rich interactive features such as autocompletion, tool approval dialogs, and multi‑session management.

---

## File Contracts & Dependencies

*This section documents the relationships and contracts between files in the codebase.*


### Hub Files

*Files with the most connections (imports, dependencies, calls)*


| File | Connections |
|------|-------------|
| `vibe/cli/textual_ui/app.py` | 68 |
| `vibe/core/config.py` | 58 |
| `vibe/core/agent.py` | 49 |
| `vibe/core/types.py` | 49 |
| `vibe/core/tools/base.py` | 47 |
| `vibe/core/utils.py` | 43 |
| `tests/test_agent_observer_streaming.py` | 34 |
| `vibe/acp/acp_agent.py` | 34 |
| `tests/backend/test_backend.py` | 32 |
| `vibe/core/tools/manager.py` | 31 |


### Configuration Dependencies

*Config files and which source files depend on them*


**`.env`** used by:
- `vibe/core/config_path.py`
- `vibe/setup/onboarding/__init__.py`
- `vibe/setup/onboarding/screens/watsonx_setup.py`
- `vibe/setup/onboarding/screens/api_key.py`

**`.env (GLOBAL_ENV_FILE)`** used by:
- `vibe/core/config.py`

**`.gitignore`** used by:
- `vibe/core/autocompletion/file_indexer/ignore_rules.py`
- `vibe/cli/init/discovery.py`

**`.gitignore (read at runtime)`** used by:
- `vibe/core/system_prompt.py`

**`.ignore`** used by:
- `tests/tools/test_grep.py`

**`.pre-commit-config.yaml`** used by:
- `.github/workflows/ci.yml`

**`.python-version`** used by:
- `action.yml`

**`.vibe/config.toml`** used by:
- `tests/core/test_config_resolution.py`

**`.vibeignore`** used by:
- `tests/tools/test_grep.py`
- `vibe/core/tools/builtins/grep.py`

**`.vscode/launch.json`** used by:
- `scripts/bump_version.py`

**`CONFIG_FILE`** used by:
- `vibe/core/utils.py`

**`GLOBAL_CONFIG_FILE`** used by:
- `vibe/core/utils.py`

**`HISTORY_FILE (path to the chat history file)`** used by:
- `vibe/cli/textual_ui/app.py`

**`VIBE-ANALYSIS.json`** used by:
- `vibe/core/context_injector.py`

**`VIBE-ANALYSIS.md`** used by:
- `vibe/core/context_injector.py`

**`VibeConfig (loads user configuration, typically a .toml or .yaml file)`** used by:
- `vibe/cli/textual_ui/app.py`

**`agents/<agent_name>.toml (per‑agent configuration)`** used by:
- `vibe/core/config.py`

**`config.toml`** used by:
- `tests/conftest.py`
- `tests/core/test_config_migration.py`
- `tests/core/test_config_resolution.py`
- `tests/acp/test_acp.py`
- `vibe/core/config_path.py`

**`config.toml (CONFIG_FILE)`** used by:
- `vibe/core/config.py`

**`config.toml (represented by CONFIG_FILE)`** used by:
- `vibe/cli/entrypoint.py`

**`distribution/zed/extension.toml`** used by:
- `scripts/bump_version.py`

**`global configuration file (referenced via GLOBAL_CONFIG_FILE, TOML format)`** used by:
- `tests/onboarding/test_ui_onboarding.py`

**`global environment file (referenced via GLOBAL_ENV_FILE)`** used by:
- `tests/onboarding/test_ui_onboarding.py`

**`history.txt (represented by HISTORY_FILE)`** used by:
- `vibe/cli/entrypoint.py`

**`instructions.txt (represented by INSTRUCTIONS_FILE)`** used by:
- `vibe/cli/entrypoint.py`

**`pyproject.toml`** used by:
- `scripts/bump_version.py`

**`tests/acp/test_initialize.py`** used by:
- `scripts/bump_version.py`

**`uv.lock`** used by:
- `.github/workflows/ci.yml`

**`vibe/core/__init__.py`** used by:
- `scripts/bump_version.py`

**`vibe/core/config_path.py (INSTRUCTIONS_FILE definition)`** used by:
- `vibe/core/system_prompt.py`


### Resource Dependencies

*Templates, static files, and data files*


**`./icons/mistral_vibe.svg`** loaded by:
- `distribution/zed/extension.toml`

**`.vscode/launch.json`** loaded by:
- `scripts/bump_version.py`

**`LOG_DIR (directory for logs)`** loaded by:
- `vibe/core/utils.py`

**`LOG_FILE (log file path)`** loaded by:
- `vibe/core/utils.py`

**`UtilityPrompt.DANGEROUS_DIRECTORY template`** loaded by:
- `vibe/core/system_prompt.py`

**`UtilityPrompt.PROJECT_CONTEXT template`** loaded by:
- `vibe/core/system_prompt.py`

**`VIBE-ANALYSIS.json`** loaded by:
- `vibe/core/context_injector.py`

**`VIBE-ANALYSIS.md`** loaded by:
- `vibe/core/context_injector.py`

**`agents/`** loaded by:
- `vibe/core/config_path.py`

**`app.tcss (CSS styling for the Textual UI)`** loaded by:
- `vibe/cli/textual_ui/app.py`

**`core/prompts/*.md`** loaded by:
- `vibe/core/prompts/__init__.py`

**`core/tools/builtins/prompts/bash.md`** loaded by:
- `vibe/acp/tools/builtins/bash.py`

**`core/tools/builtins/prompts/read_file.md`** loaded by:
- `vibe/acp/tools/builtins/read_file.py`

**`core/tools/builtins/prompts/search_replace.md`** loaded by:
- `vibe/acp/tools/builtins/search_replace.py`

**`core/tools/builtins/prompts/todo.md`** loaded by:
- `vibe/acp/tools/builtins/todo.py`

**`core/tools/builtins/prompts/write_file.md`** loaded by:
- `vibe/acp/tools/builtins/write_file.py`

**`distribution/zed/extension.toml`** loaded by:
- `scripts/bump_version.py`

**`instructions.md`** loaded by:
- `vibe/core/config_path.py`

**`logs/`** loaded by:
- `vibe/core/config_path.py`

**`onboarding.tcss`** loaded by:
- `vibe/setup/onboarding/__init__.py`

**`prompts/`** loaded by:
- `vibe/core/config_path.py`

**`prompts/*.md (SystemPrompt markdown files)`** loaded by:
- `vibe/core/config.py`

**`prompts/<tool_name>.md (markdown prompt file corresponding to each concrete tool)`** loaded by:
- `vibe/core/tools/base.py`

**`prompts/utility/compact.md`** loaded by:
- `vibe/core/agent.py`

**`pyproject.toml`** loaded by:
- `scripts/bump_version.py`

**`snapshot_report.html`** loaded by:
- `.github/workflows/ci.yml`

**`tests/acp/test_initialize.py`** loaded by:
- `scripts/bump_version.py`

**`tools/`** loaded by:
- `vibe/core/config_path.py`

**`update_cache.json`** loaded by:
- `vibe/cli/update_notifier/adapters/filesystem_update_cache_repository.py`

**`vibe.log`** loaded by:
- `vibe/core/config_path.py`

**`vibe/core/__init__.py`** loaded by:
- `scripts/bump_version.py`

**`vibehistory`** loaded by:
- `vibe/core/config_path.py`


### Environment Variables

*Environment variables used across the codebase*


| Variable | Used By |
|----------|---------|
| `<provider.api_key_env_var> (dynamic name defined in ProviderConfig, e.g., 'WATSONX_API_KEY')` | `vibe/core/llm/backend/watsonx/backend.py` |
| `<provider>.api_key_env_var (e.g., MISTRAL_API_KEY)` | `vibe/setup/onboarding/screens/api_key.py` |
| `API_KEY` | `tests/backend/test_backend.py` |
| `Any provider‑specific api_key_env_var defined in the configuration` | `vibe/core/config.py` |
| `CI` | `vibe/core/tools/builtins/bash.py` |
| `COMSPEC` | `tests/test_system_prompt.py`, `vibe/core/system_prompt.py` |
| `DEBIAN_FRONTEND` | `vibe/core/tools/builtins/bash.py` |
| `GITHUB_OUTPUT` | `.github/workflows/build-and-upload.yml` |
| `GITHUB_REPOSITORY` | `.github/workflows/build-and-upload.yml` |
| `GIT_PAGER` | `vibe/core/tools/builtins/bash.py` |
| `HOME` | `scripts/install.sh` |
| `LC_ALL` | `vibe/core/tools/builtins/bash.py` |
| `LECHAT_API_KEY` | `tests/test_agent_stats.py` |
| `LESS` | `vibe/core/tools/builtins/bash.py` |
| `MISTRAL_API_KEY` | `tests/conftest.py`, `tests/acp/test_acp.py`, `tests/onboarding/test_ui_onboarding.py` (+2) |
| `NONINTERACTIVE` | `vibe/core/tools/builtins/bash.py` |
| `NO_COLOR` | `vibe/core/tools/builtins/bash.py` |
| `NO_TTY` | `vibe/core/tools/builtins/bash.py` |
| `PAGER` | `vibe/core/tools/builtins/bash.py` |
| `PATH` | `scripts/install.sh` |
| `PROMPT_INPUT` | `action.yml` |
| `PYTHON_VERSION` | `.github/workflows/ci.yml` |
| `SHELL` | `tests/conftest.py` |
| `TERM` | `vibe/core/tools/builtins/bash.py` |
| `TMUX` | `tests/cli/test_clipboard.py`, `vibe/cli/clipboard.py` |
| `VIBE_HOME` | `tests/core/test_config_resolution.py`, `tests/acp/test_acp.py`, `vibe/core/config_path.py` |
| `VIBE_MOCK_LLM_DATA` | `tests/mock/mock_entrypoint.py`, `tests/mock/utils.py` |
| `WATSONX_API_KEY` | `vibe/core/config.py`, `vibe/setup/onboarding/screens/watsonx_setup.py`, `vibe/setup/onboarding/screens/model_selection.py` |
| `WATSONX_ENDPOINT` | `vibe/core/llm/backend/watsonx/backend.py` |
| `WATSONX_PROJECT_ID` | `vibe/core/llm/backend/watsonx/backend.py`, `vibe/setup/onboarding/screens/watsonx_setup.py` |
| `WATSONX_REGION` | `vibe/core/llm/backend/watsonx/backend.py`, `vibe/setup/onboarding/screens/watsonx_setup.py`, `vibe/setup/onboarding/screens/model_selection.py` |
| `provider.api_key_env_var (accessed via os.getenv)` | `vibe/core/llm/backend/generic.py` |
| `provider.api_key_env_var (e.g., MISTRAL_API_KEY)` | `vibe/core/llm/backend/mistral.py` |


### Internal Import Graph

*How project files import from each other*

- `vibe/cli/textual_ui/app.py` → `vibe/cli/textual_ui/widgets/messages/UserCommandMessage.py`, `vibe/core/types/LLMMessage.py`, `vibe/core/types/ResumeSessionInfo.py`, `vibe/cli/init/execute_init.py`, `vibe/cli/textual_ui/handlers/event_handler/EventHandler.py` (+41)
- `tests/test_agent_observer_streaming.py` → `vibe/core/middleware/ResetReason.py`, `vibe/core/types/LLMMessage.py`, `vibe/core/utils/get_user_cancellation_message.py`, `vibe/core/types/Role.py`, `vibe/core/config/SessionLoggingConfig.py` (+20)
- `tests/backend/test_backend.py` → `tests/backend/data/JsonResponse.py`, `vibe/core/types/LLMMessage.py`, `tests/backend/data/mistral/TOOL_CONVERSATION_PARAMS.py`, `vibe/core/config/ProviderConfig.py`, `vibe/core/llm/exceptions/BackendError.py` (+20)
- `tests/acp/test_acp.py` → `tests/mock/utils/get_mocking_env.py`, `tests/TESTS_ROOT.py`, `tests/conftest/get_base_config.py`, `acp/RequestPermissionResponse.py`, `acp/ReadTextFileResponse.py` (+17)
- `tests/test_agent_tool_call.py` → `vibe/core/types/LLMMessage.py`, `tests/stubs/fake_tool/FakeTool.py`, `vibe/core/types/Role.py`, `vibe/core/config/SessionLoggingConfig.py`, `vibe/core/types/ApprovalResponse.py` (+14)
- `tests/test_agent_stats.py` → `vibe/core/config/SessionLoggingConfig.py`, `vibe/core/tools/base/ToolPermission.py`, `vibe/core/types/CompactEndEvent.py`, `vibe/core/types/LLMMessage.py`, `vibe/core/config/Backend.py` (+13)
- `tests/acp/test_content.py` → `acp/schema/TextContentBlock.py`, `tests/stubs/fake_connection/FakeAgentSideConnection.py`, `vibe/core/types/LLMMessage.py`, `tests/stubs/fake_backend/FakeBackend.py`, `acp/schema/TextResourceContents.py` (+10)
- `vibe/core/tools/manager.py` → `vibe/core/tools/mcp/list_tools_stdio.py`, `vibe/core/config/MCPStreamableHttp.py`, `vibe/core/utils/run_sync.py`, `vibe/core/config/MCPHttp.py`, `vibe/core/config_path/resolve_local_tools_dir.py` (+10)
- `tests/acp/test_new_session.py` → `vibe/acp/utils/VibeSessionMode.py`, `tests/stubs/fake_connection/FakeAgentSideConnection.py`, `acp/SetSessionModelRequest.py`, `vibe/core/types/LLMMessage.py`, `tests/stubs/fake_backend/FakeBackend.py` (+9)
- `vibe/cli/entrypoint.py` → `vibe/core/utils/ConversationLimitException.py`, `vibe/setup/onboarding/run_onboarding.py`, `vibe/core/config/VibeConfig.py`, `vibe/core/config/MissingAPIKeyError.py`, `vibe/core/config/MissingPromptFileError.py` (+9)
- `tests/acp/test_set_model.py` → `tests/stubs/fake_connection/FakeAgentSideConnection.py`, `acp/SetSessionModelRequest.py`, `vibe/core/types/LLMMessage.py`, `tests/stubs/fake_backend/FakeBackend.py`, `vibe/core/config/VibeConfig.py` (+8)
- `vibe/core/llm/backend/watsonx/backend.py` → `vibe/core/types/LLMMessage.py`, `vibe/core/types/LLMUsage.py`, `vibe/core/config/ProviderConfig.py`, `vibe/core/types/AvailableTool.py`, `vibe/core/types/LLMChunk.py` (+8)
- `tests/acp/test_set_mode.py` → `vibe/acp/utils/VibeSessionMode.py`, `tests/stubs/fake_connection/FakeAgentSideConnection.py`, `vibe/core/types/LLMMessage.py`, `tests/stubs/fake_backend/FakeBackend.py`, `vibe/core/types/LLMUsage.py` (+7)
- `vibe/core/agent.py` → `vibe/core/llm/backend/factory.py`, `vibe/core/tools/base.py`, `vibe/core/llm/format.py`, `vibe/core/prompts.py`, `vibe/core/interaction_logger.py` (+7)
- `vibe/core/llm/backend/mistral.py` → `vibe/core/types/LLMMessage.py`, `vibe/core/types/LLMUsage.py`, `vibe/core/config/ProviderConfig.py`, `vibe/core/types/AvailableTool.py`, `vibe/core/types/LLMChunk.py` (+7)


### Cross-File Calls

*Function calls, class instantiations, and inheritance across files*


**Accesses:**
- `tests/tools/test_ui_bash_execution.py` → `vibe/cli/textual_ui/widgets/chat_input/container.py` (Sets .value on ChatInputContainer to inject commands.)
- `tests/update_notifier/test_ui_version_update_notification.py` → `vibe/cli/update_notifier.py` (Tests inspect notifier.fetch_update_calls to ensure gateway interaction count.)

**Accesses_Attribute:**
- `tests/test_ui_input_history.py` → `vibe/cli/textual_ui/widgets/chat_input/body.py` (Sets the 'history' attribute on ChatInputBody.)
- `tests/test_ui_input_history.py` → `vibe/cli/textual_ui/widgets/chat_input/container.py` (Gets the underlying textarea widget via 'input_widget' for cursor checks.)

**Accesses_Property:**
- `tests/test_ui_input_history.py` → `vibe/cli/textual_ui/widgets/chat_input/container.py` (Reads the 'value' property of ChatInputContainer during assertions.)

**Calls:**
- `vibe/cli/textual_ui/app.py` → `vibe/cli/init.py` (Calls execute_init() to run the /init command.)
- `vibe/cli/textual_ui/app.py` → `vibe/cli/update_notifier.py` (Calls get_update_if_available() to check for newer versions.)
- `vibe/cli/textual_ui/app.py` → `vibe/core/utils.py` (Calls is_dangerous_directory() and logger for warnings.)
- `tests/test_history_manager.py` → `vibe/cli/history_manager.py` (Calls HistoryManager.add(), HistoryManager.get_previous(), and HistoryManager.get_next())
- `tests/test_ui_pending_user_message.py` → `vibe/cli/textual_ui/widgets/chat_input/container.py` (Accesses ChatInputContainer widget to set the input value)
- `tests/test_ui_pending_user_message.py` → `vibe/cli/textual_ui/app.py` (Uses VibeApp.run_test() context manager and VibeApp.query/query_one methods)
- `tests/test_agent_stats.py` → `tests/mock/utils.py` (uses mock_llm_chunk() to build fake LLM response chunks for the FakeBackend.)
- `tests/test_agent_stats.py` → `vibe/core/agent.py` (calls Agent.act(), Agent.reload_with_initial_messages(), Agent.compact(), Agent.clear_history().)
- `tests/test_agent_backend.py` → `tests/mock/utils.py` (calls mock_llm_chunk() to create fake LLM response chunks)
- `tests/test_system_prompt.py` → `vibe/core/system_prompt.py` (Calls get_universal_system_prompt(tool_manager, config) to generate the prompt.)
- *...and 146 more*

**Calls|Accesses:**
- `tests/autocompletion/test_ui_chat_autocompletion.py` → `vibe/cli/textual_ui/widgets/chat_input/completion_popup.py` (Queries CompletionPopup widget, calls .render(), reads .styles.display, iterates .spans)
- `tests/autocompletion/test_ui_chat_autocompletion.py` → `vibe/cli/textual_ui/widgets/chat_input/container.py` (Queries ChatInputContainer widget and reads/writes its .value attribute)

**Calls|Inherits:**
- `vibe/core/tools/ui.py` → `any tool implementation (e.g., vibe/core/tools/*.py)` (Checks if a tool class subclasses ToolUIData and, if so, calls its classmethods get_call_display, get_result_display, and get_status_text; also calls tool_class.get_name() to obtain a human readable name.)

**Checks Subclass Of:**
- `vibe/acp/tools/session_update.py` → `vibe/acp/tools/base.py` (uses issubclass(event.tool_class, ToolCallSessionUpdateProtocol) and ToolResultSessionUpdateProtocol)

**Checks/Invokes:**
- `vibe/acp/acp_agent.py` → `vibe/acp/tools/base.py` (Uses isinstance/issubclass to detect BaseAcpTool subclasses and calls BaseAcpTool.update_tool_state(...).)

**Checks_Instance:**
- `tests/onboarding/test_ui_onboarding.py` → `vibe/setup/onboarding/screens/api_key.py` (Uses isinstance(app.screen, ApiKeyScreen) to verify navigation)
- `tests/onboarding/test_ui_onboarding.py` → `vibe/setup/onboarding/screens/theme_selection.py` (Uses isinstance(app.screen, ThemeSelectionScreen) and accesses THEMES list)

**Executes:**
- `tests/acp/test_acp.py` → `tests/mock/mock_entrypoint.py` (The subprocess started by get_acp_agent_process runs this mock entrypoint script.)
- `.github/workflows/build-and-upload.yml` → `vibe-acp.spec` (PyInstaller is invoked on the spec file to produce the binary.)

**Imports:**
- `tests/acp/test_multi_session.py` → `vibe/core/types.py` (Uses Role enum for message role verification)
- `tests/acp/test_bash.py` → `acp/schema.py` (Imports TerminalOutputResponse and WaitForTerminalExitResponse for mock terminal handle return types)

**Imports_From:**
- `tests/test_cli_programmatic_preload.py` → `vibe/core/programmatic.py` (Monkeypatches create_formatter to return the SpyStreamingFormatter.)
- `tests/test_tagged_text.py` → `vibe/core/utils.py` (Imports constants CANCELLATION_TAG, KNOWN_TAGS and class TaggedText)
- `tests/stubs/fake_backend.py` → `vibe/core/types.py` (Imports LLMChunk and LLMMessage for type annotations.)
- `tests/stubs/fake_tool.py` → `vibe/core/tools/base.py` (Imports BaseToolConfig and BaseToolState from vibe.core.tools.base)
- `tests/tools/test_grep.py` → `vibe/core/tools/base.py` (Imports ToolError for exception handling.)
- `tests/core/test_config_migration.py` → `vibe/core/config.py` (Uses VibeConfig class and its dump_config attribute)
- `tests/core/test_config_migration.py` → `vibe/core/__init__.py` (Accesses config.CONFIG_FILE variable from vibe.core)
- `tests/core/test_config_resolution.py` → `vibe/core/config_path.py` (uses CONFIG_FILE, GLOBAL_CONFIG_FILE, and VIBE_HOME objects and their .path attribute)
- `tests/mock/mock_backend_factory.py` → `vibe/core/llm/backend/factory.py` (reads and writes entries in the BACKEND_FACTORY dict (original = BACKEND_FACTORY[backend_type]; BACKEND_FACTORY[backend_type] = factory_func; restored in finally block))
- `tests/mock/mock_backend_factory.py` → `vibe/core/config.py` (uses Backend enum/class for type hinting of backend_type)
- *...and 75 more*

**Imports|Uses:**
- `tests/acp/test_bash.py` → `vibe/core/tools/builtins/bash.py` (Imports BashArgs, BashResult, BashToolConfig to construct arguments and validate results)
- `tests/acp/test_bash.py` → `vibe/core/tools/base.py` (Imports ToolError for exception handling in test expectations)

**Inherits:**
- `tests/test_ui_pending_user_message.py` → `vibe/core/agent.py` (StubAgent inherits from Agent)
- `tests/stubs/fake_tool.py` → `vibe/core/tools/base.py` (FakeTool inherits from BaseTool defined in vibe.core.tools.base)
- `tests/stubs/fake_connection.py` → `acp/__init__.py (or wherever AgentSideConnection is defined)` (FakeAgentSideConnection inherits from AgentSideConnection)
- `tests/snapshots/base_snapshot_test_app.py` → `vibe/cli/textual_ui/app.py` (BaseSnapshotTestApp inherits from VibeApp.)
- `tests/snapshots/test_ui_snapshot_basic_conversation.py` → `tests/snapshots/base_snapshot_test_app.py` (Inherits from BaseSnapshotTestApp)
- `tests/snapshots/test_ui_snapshot_release_update_notification.py` → `tests/snapshots/base_snapshot_test_app.py` (SnapshotTestAppWithUpdate inherits BaseSnapshotTestApp)
- `tests/autocompletion/test_slash_command_controller.py` → `vibe/cli/autocompletion/base.py` (StubView inherits from CompletionView defined in this module.)
- `tests/acp/test_set_mode.py` → `vibe/core/agent.py` (PatchedAgent subclass inherits from Agent defined in vibe.core.agent.)
- `tests/acp/test_multi_session.py` → `vibe/core/agent.py` (PatchedAgent subclass inherits from Agent)
- `tests/acp/test_set_model.py` → `vibe/core/agent.py` (PatchedAgent subclass inherits from Agent.)
- *...and 37 more*

**Instantiates:**
- `vibe/cli/textual_ui/app.py` → `vibe/core/agent.py` (Creates an Agent instance to handle LLM interactions.)
- `vibe/cli/textual_ui/app.py` → `vibe/cli/textual_ui/widgets/loading.py` (Creates LoadingWidget objects to indicate progress.)
- `vibe/cli/textual_ui/app.py` → `vibe/cli/textual_ui/widgets/config_app.py` (Mounts ConfigApp in the bottom panel.)
- `vibe/cli/textual_ui/app.py` → `vibe/cli/textual_ui/widgets/approval_app.py` (Mounts ApprovalApp when a tool requires user approval.)
- `vibe/cli/textual_ui/app.py` → `vibe/cli/textual_ui/widgets/chat_input.py` (Creates ChatInputContainer for user message entry.)
- `tests/test_ui_input_history.py` → `vibe/cli/textual_ui/app.py` (Creates a VibeApp instance in the vibe_app fixture.)
- `tests/test_ui_input_history.py` → `vibe/cli/history_manager.py` (Creates a HistoryManager with the temporary history file in inject_history_file.)
- `tests/test_ui_input_history.py` → `vibe/core/config.py` (Creates a VibeConfig with a SessionLoggingConfig in the vibe_config fixture.)
- `tests/test_history_manager.py` → `vibe/cli/history_manager.py` (Creates HistoryManager instances with HistoryManager(history_file, ...))
- `tests/test_ui_pending_user_message.py` → `vibe/cli/textual_ui/app.py` (Creates VibeApp instance via fixture 'vibe_app')
- *...and 122 more*

**Instantiates & Uses:**
- `vibe/core/agent.py` → `vibe/core/middleware.py` (Agent._setup_middleware adds various Middleware objects to MiddlewarePipeline.)

**Instantiates/Validates:**
- `vibe/core/config.py` → `vibe/core/tools/base.py` (VibeConfig._normalize_tool_configs uses BaseToolConfig.model_validate to coerce raw dicts into BaseToolConfig objects.)

**Instantiates|Calls:**
- `tests/autocompletion/test_ui_chat_autocompletion.py` → `vibe/cli/textual_ui/app.py` (Creates VibeApp instance and calls its async run_test() method)
- `tests/autocompletion/test_file_indexer.py` → `vibe/core/autocompletion/file_indexer.py` (Creates a FileIndexer instance (fixture) and calls its methods get_index(), shutdown(), and accesses its stats attribute.)
- `tests/autocompletion/test_path_completer_recursive.py` → `vibe/core/autocompletion/completers.py` (Instantiates PathCompleter and calls its get_completions method to obtain completion suggestions.)
- `tests/acp/test_bash.py` → `vibe/acp/tools/builtins/bash.py` (Instantiates Bash in fixtures and tests; calls Bash.get_name(), Bash.get_summary(), Bash._parse_command(), Bash.run())
- `vibe/setup/onboarding/screens/api_key.py` → `vibe/core/config.py` (Calls VibeConfig.model_construct() and then uses its methods get_active_model() and get_provider_for_model() to determine the active provider.)
- `vibe/cli/textual_ui/widgets/chat_input/body.py` → `vibe/cli/history_manager.py` (Instantiates HistoryManager; calls its methods add, get_previous, get_next, reset_navigation; accesses private attributes _current_index and _entries.)
- `vibe/cli/textual_ui/widgets/chat_input/body.py` → `vibe/cli/textual_ui/widgets/chat_input/text_area.py` (Instantiates ChatTextArea for the input widget; calls its methods load_text, move_cursor, clear_text, set_cursor_offset, reset_history_state, and accesses internal flags such as _navigating_history, _original_text, _last_used_prefix, etc.)

**Interacts:**
- `vibe/cli/textual_ui/handlers/event_handler.py` → `vibe/cli/textual_ui/widgets/loading.py` (Calls LoadingWidget.set_status(status_text))

**Patches:**
- `tests/mock/mock_entrypoint.py` → `vibe/core/llm/backend/mistral.py` (Patches MistralBackend.complete and MistralBackend.complete_streaming to yield mocked LLMChunk data.)
- `tests/mock/mock_entrypoint.py` → `vibe/core/llm/backend/generic.py` (Patches GenericBackend.complete and GenericBackend.complete_streaming to yield mocked LLMChunk data.)
- `tests/acp/test_set_mode.py` → `vibe/acp/acp_agent.py` (Patches the VibeAgent class inside vibe.acp.acp_agent with a PatchedAgent subclass.)
- `tests/acp/test_multi_session.py` → `vibe/acp/acp_agent.py` (unittest.mock.patch replaces VibeAgent with PatchedAgent)

**Queries:**
- `tests/test_ui_pending_user_message.py` → `vibe/cli/textual_ui/widgets/messages.py` (Queries for UserMessage and InterruptMessage widgets in the UI)
- `tests/tools/test_ui_bash_execution.py` → `vibe/cli/textual_ui/widgets/messages.py` (Queries for BashOutputMessage and ErrorMessage instances via VibeApp.query.)

**Raises:**
- `tests/update_notifier/test_github_version_update_gateway.py` → `vibe/cli/update_notifier.py` (Raises VersionUpdateGatewayError when fetching updates fails, using VersionUpdateGatewayCause for classification.)
- `vibe/acp/tools/base.py` → `vibe/core/tools/base.py` (BaseAcpTool._load_state raises ToolError defined in vibe/core/tools/base.py)

**Reads:**
- `tests/acp/test_new_session.py` → `vibe/acp/utils.py` (Accesses VibeSessionMode enum values for verification.)
- `vibe/core/system_prompt.py` → `vibe/core/config_path.py` (INSTRUCTIONS_FILE.path.read_text() is used to load user instructions)
- `vibe/core/tools/manager.py` → `vibe/__init__.py` (Accesses VIBE_ROOT constant for default tool directory resolution.)

**Reads/Writes:**
- `tests/onboarding/test_ui_onboarding.py` → `vibe/core/config_path.py` (Reads GLOBAL_ENV_FILE.path and GLOBAL_CONFIG_FILE.path to verify persisted data)

**References:**
- `tests/tools/test_bash.py` → `vibe/core/tools/base.py` (Uses ToolError exception and ToolPermission enum for error handling and permission checks.)

**Returns:**
- `vibe/acp/tools/builtins/read_file.py` → `vibe/core/tools/builtins/read_file.py` (returns an _ReadResult object defined in the core read_file module)

**Sets Attribute:**
- `tests/conftest.py` → `vibe/core/config_path.py` (monkeypatch.setattr(config_path, "_DEFAULT_VIBE_HOME", config_dir) modifies the global default config location.)

**Type_Annotation:**
- `vibe/core/interaction_logger.py` → `vibe/core/config.py` (References SessionLoggingConfig and VibeConfig for configuration objects.)
- `vibe/core/interaction_logger.py` → `vibe/core/tools/manager.py` (References ToolManager for type hinting of the tool manager argument.)

**Type_Hint:**
- `vibe/core/system_prompt.py` → `vibe/core/tools/manager.py` (ToolManager type is imported for type checking)

**Uses:**
- `vibe/cli/textual_ui/app.py` → `vibe/cli/commands.py` (Uses CommandRegistry to parse and execute slash‑style commands.)
- `tests/test_agent_stats.py` → `vibe/core/types.py` (accesses AgentStats fields, LLMMessage class, Role enum, and various event classes.)
- `tests/test_agent_stats.py` → `vibe/core/config.py` (builds VibeConfig objects via make_config.)
- `tests/test_agent_stats.py` → `vibe/core/tools/base.py` (creates BaseToolConfig and sets ToolPermission for the 'todo' tool.)
- `tests/test_agent_tool_call.py` → `vibe/core/tools/base.py` (References BaseToolConfig and ToolPermission to configure tool behavior.)
- `tests/test_agent_tool_call.py` → `vibe/core/tools/builtins/todo.py` (Imports TodoItem for constructing test payloads with duplicate IDs or excessive count.)
- `tests/test_agent_tool_call.py` → `vibe/core/types.py` (Relies on many type definitions such as AssistantEvent, ToolCallEvent, ToolResultEvent, etc.)
- `tests/update_notifier/test_version_update_use_case.py` → `vibe/cli/update_notifier/version_update.py` (Uses VersionUpdateGatewayCause enum values to parameterize error tests.)
- `tests/update_notifier/test_pypi_version_update_gateway.py` → `vibe/cli/update_notifier/ports/version_update_gateway.py` (Uses VersionUpdate for result comparison and VersionUpdateGatewayCause / VersionUpdateGatewayError for error handling.)
- `tests/snapshots/base_snapshot_test_app.py` → `vibe/cli/textual_ui/widgets/chat_input.py` (Queries for a ChatTextArea widget and registers a hidden cursor theme.)
- *...and 33 more*

**Uses_Type:**
- `tests/update_notifier/adapters/fake_update_cache_repository.py` → `vibe/cli/update_notifier/ports/update_cache_repository.py` (Uses the UpdateCache type defined in the target file for method signatures)

**Uses_Type|Accesses_Attributes:**
- `vibe/cli/textual_ui/widgets/config_app.py` → `vibe/core/config.py` (Accepts a VibeConfig instance; reads its 'models', 'active_model' and 'textual_theme' attributes to populate the settings list.)


### Shared State Patterns

*Global variables, singletons, and shared state*

- `vibe/cli/textual_ui/app.py`: self.config (shared configuration object)
- `vibe/cli/textual_ui/app.py`: self.logger (global logger from vibe.core.utils)
- `vibe/cli/textual_ui/app.py`: update cache repository shared between version‑check task and UI
- `tests/test_ui_pending_user_message.py`: Uses pytest fixtures to share a VibeConfig instance across tests
- `tests/test_ui_pending_user_message.py`: Monkeypatch alters class-level method VibeApp._initialize_agent for all tests in this module
- `tests/conftest.py`: modifies config_path._DEFAULT_VIBE_HOME (global configuration path)
- `tests/conftest.py`: sets environment variables via monkeypatch for API key and shell
- `tests/test_agent_stats.py`: Agent.stats (cumulative statistics stored on the Agent instance)
- `tests/test_agent_stats.py`: Agent.session_id and Agent.interaction_logger.session_id (shared session identifier state)
- `scripts/install.sh`: PLATFORM (global variable)
- `scripts/install.sh`: UV_INSTALLED (global flag)
- `scripts/install.sh`: PATH modification after uv installation
- `vibe/__init__.py`: VIBE_ROOT (global Path variable representing the package root)
- `tests/tools/test_grep.py`: Uses GrepState instance to store and update search_history across calls.
- `tests/tools/test_ui_bash_execution.py`: Uses a shared VibeConfig object passed to VibeApp across tests.
- `tests/core/test_config_migration.py`: Modifies global VibeConfig.dump_config attribute
- `tests/core/test_config_migration.py`: Temporarily overwrites vibe.core.CONFIG_FILE
- `tests/core/test_config_resolution.py`: CONFIG_FILE
- `tests/core/test_config_resolution.py`: GLOBAL_CONFIG_FILE
- `tests/core/test_config_resolution.py`: VIBE_HOME
- *...and 85 more*


### Entry Point Dependencies

*What each entry point directly depends on*


**`vibe/cli/textual_ui/app.py`**:
- `vibe/cli/clipboard/copy_selection_to_clipboard.py`
- `vibe/cli/commands/CommandRegistry.py`
- `vibe/cli/init/execute_init.py`
- `vibe/cli/init/executor/InitProgress.py`
- `vibe/cli/init/executor/format_init_summary.py`
- `vibe/cli/textual_ui/handlers/event_handler/EventHandler.py`
- `vibe/cli/textual_ui/widgets/approval_app/ApprovalApp.py`
- `vibe/cli/textual_ui/widgets/chat_input/ChatInputContainer.py`
- `vibe/cli/textual_ui/widgets/compact/CompactMessage.py`
- `vibe/cli/textual_ui/widgets/config_app/ConfigApp.py`
- *...and 48 more*


---

## Project Structure

```
mistral-vibe/
├── .github/
│   ├── workflows/
│   │   ├── build-and-upload.yml
│   │   ├── ci.yml
│   │   └── release.yml
│   └── CODEOWNERS
├── distribution/
│   └── zed/
│       ├── icons/
│       │   └── mistral_vibe.svg
│       ├── extension.toml
│       └── LICENSE
├── scripts/
│   ├── bump_version.py
│   ├── install.sh
│   └── README.md
├── tests/
│   ├── acp/
│   │   ├── test_acp.py
│   │   ├── test_bash.py
│   │   ├── test_content.py
│   │   ├── test_initialize.py
│   │   ├── test_multi_session.py
│   │   ├── test_new_session.py
│   │   ├── test_read_file.py
│   │   ├── test_search_replace.py
│   │   ├── test_set_mode.py
│   │   ├── test_set_model.py
│   │   └── test_write_file.py
│   ├── autocompletion/
│   │   ├── test_file_indexer.py
│   │   ├── test_fuzzy.py
│   │   ├── test_path_completer_fuzzy.py
│   │   ├── test_path_completer_recursive.py
│   │   ├── test_path_completion_controller.py
│   │   ├── test_path_prompt_transformer.py
│   │   ├── test_slash_command_controller.py
│   │   └── test_ui_chat_autocompletion.py
│   ├── backend/
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── fireworks.py
│   │   │   └── mistral.py
│   │   ├── __init__.py
│   │   └── test_backend.py
│   ├── cli/
│   │   └── test_clipboard.py
│   ├── core/
│   │   ├── test_config_migration.py
│   │   └── test_config_resolution.py
│   ├── mock/
│   │   ├── __init__.py
│   │   ├── mock_backend_factory.py
│   │   ├── mock_entrypoint.py
│   │   └── utils.py
│   ├── onboarding/
│   │   ├── test_run_onboarding.py
│   │   └── test_ui_onboarding.py
│   ├── playground/
│   ├── snapshots/
│   │   ├── __snapshots__/
│   │   │   ├── test_ui_snapshot_basic_conversation/
│   │   │   │   └── test_snapshot_shows_basic_conversation.svg
│   │   │   ├── test_ui_snapshot_code_block_horizontal_scrolling/
│   │   │   │   └── test_snapshot_allows_horizontal_scrolling_for_long_code_blocks.svg
│   │   │   └── test_ui_snapshot_release_update_notification/
│   │   │       └── test_snapshot_shows_release_update_notification.svg
│   │   ├── base_snapshot_test_app.py
│   │   ├── snap_compare.py
│   │   ├── test_ui_snapshot_basic_conversation.py
│   │   ├── test_ui_snapshot_code_block_horizontal_scrolling.py
│   │   └── test_ui_snapshot_release_update_notification.py
│   ├── stubs/
│   │   ├── fake_backend.py
│   │   ├── fake_connection.py
│   │   └── fake_tool.py
│   ├── tools/
│   │   ├── test_bash.py
│   │   ├── test_grep.py
│   │   ├── test_manager_get_tool_config.py
│   │   └── test_ui_bash_execution.py
│   ├── update_notifier/
│   │   ├── adapters/
│   │   │   ├── fake_update_cache_repository.py
│   │   │   └── fake_version_update_gateway.py
│   │   ├── test_filesystem_update_cache_repository.py
│   │   ├── test_github_version_update_gateway.py
│   │   ├── test_pypi_version_update_gateway.py
│   │   ├── test_ui_version_update_notification.py
│   │   └── test_version_update_use_case.py
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agent_auto_compact.py
│   ├── test_agent_backend.py
│   ├── test_agent_observer_streaming.py
│   ├── test_agent_stats.py
│   ├── test_agent_tool_call.py
│   ├── test_cli_programmatic_preload.py
│   ├── test_history_manager.py
│   ├── test_system_prompt.py
│   ├── test_tagged_text.py
│   ├── test_ui_input_history.py
│   └── test_ui_pending_user_message.py
├── vibe/
│   ├── acp/
│   │   ├── tools/
│   │   │   ├── builtins/
│   │   │   │   ├── bash.py
│   │   │   │   ├── read_file.py
│   │   │   │   ├── search_replace.py
│   │   │   │   ├── todo.py
│   │   │   │   └── write_file.py
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── session_update.py
│   │   ├── __init__.py
│   │   ├── acp_agent.py
│   │   ├── entrypoint.py
│   │   └── utils.py
│   ├── cli/
│   │   ├── autocompletion/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── path_completion.py
│   │   │   └── slash_command.py
│   │   ├── init/
│   │   │   ├── __init__.py
│   │   │   ├── analysis_index.py
│   │   │   ├── contracts.py
│   │   │   ├── discovery.py
│   │   │   ├── executor.py
│   │   │   ├── generator.py
│   │   │   ├── glossary.py
│   │   │   └── indexer.py
│   │   ├── textual_ui/
│   │   │   ├── handlers/
│   │   │   │   ├── __init__.py
│   │   │   │   └── event_handler.py
│   │   │   ├── renderers/
│   │   │   │   ├── __init__.py
│   │   │   │   └── tool_renderers.py
│   │   │   ├── widgets/
│   │   │   │   ├── chat_input/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── body.py
│   │   │   │   │   ├── completion_manager.py
│   │   │   │   │   ├── completion_popup.py
│   │   │   │   │   ├── container.py
│   │   │   │   │   └── text_area.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── approval_app.py
│   │   │   │   ├── blinking_message.py
│   │   │   │   ├── compact.py
│   │   │   │   ├── config_app.py
│   │   │   │   ├── context_progress.py
│   │   │   │   ├── loading.py
│   │   │   │   ├── messages.py
│   │   │   │   ├── mode_indicator.py
│   │   │   │   ├── path_display.py
│   │   │   │   ├── tool_widgets.py
│   │   │   │   ├── tools.py
│   │   │   │   └── welcome.py
│   │   │   ├── __init__.py
│   │   │   ├── app.py
│   │   │   └── app.tcss
│   │   ├── update_notifier/
│   │   │   ├── adapters/
│   │   │   │   ├── filesystem_update_cache_repository.py
│   │   │   │   ├── github_version_update_gateway.py
│   │   │   │   └── pypi_version_update_gateway.py
│   │   │   ├── ports/
│   │   │   │   ├── update_cache_repository.py
│   │   │   │   └── version_update_gateway.py
│   │   │   ├── __init__.py
│   │   │   └── version_update.py
│   │   ├── __init__.py
│   │   ├── clipboard.py
│   │   ├── commands.py
│   │   ├── entrypoint.py
│   │   └── history_manager.py
│   ├── core/
│   │   ├── autocompletion/
│   │   │   ├── file_indexer/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ignore_rules.py
│   │   │   │   ├── indexer.py
│   │   │   │   ├── store.py
│   │   │   │   └── watcher.py
│   │   │   ├── __init__.py
│   │   │   ├── completers.py
│   │   │   ├── fuzzy.py
│   │   │   ├── path_prompt.py
│   │   │   └── path_prompt_adapter.py
│   │   ├── llm/
│   │   │   ├── backend/
│   │   │   │   ├── watsonx/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── backend.py
│   │   │   │   │   └── models.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── factory.py
│   │   │   │   ├── generic.py
│   │   │   │   └── mistral.py
│   │   │   ├── __init__.py
│   │   │   ├── exceptions.py
│   │   │   ├── format.py
│   │   │   └── types.py
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   ├── cli.md
│   │   │   ├── compact.md
│   │   │   ├── dangerous_directory.md
│   │   │   ├── project_context.md
│   │   │   └── tests.md
│   │   ├── tools/
│   │   │   ├── builtins/
│   │   │   │   ├── prompts/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── bash.md
│   │   │   │   │   ├── grep.md
│   │   │   │   │   ├── read_file.md
│   │   │   │   │   ├── search_replace.md
│   │   │   │   │   ├── todo.md
│   │   │   │   │   └── write_file.md
│   │   │   │   ├── bash.py
│   │   │   │   ├── grep.py
│   │   │   │   ├── read_file.py
│   │   │   │   ├── search_replace.py
│   │   │   │   ├── todo.py
│   │   │   │   └── write_file.py
│   │   │   ├── base.py
│   │   │   ├── manager.py
│   │   │   ├── mcp.py
│   │   │   └── ui.py
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── config.py
│   │   ├── config_path.py
│   │   ├── context_injector.py
│   │   ├── interaction_logger.py
│   │   ├── middleware.py
│   │   ├── output_formatters.py
│   │   ├── programmatic.py
│   │   ├── system_prompt.py
│   │   ├── types.py
│   │   └── utils.py
│   ├── setup/
│   │   └── onboarding/
│   │       ├── screens/
│   │       │   ├── __init__.py
│   │       │   ├── api_key.py
│   │       │   ├── model_selection.py
│   │       │   ├── provider_selection.py
│   │       │   ├── theme_selection.py
│   │       │   ├── watsonx_setup.py
│   │       │   └── welcome.py
│   │       ├── __init__.py
│   │       ├── base.py
│   │       └── onboarding.tcss
│   └── __init__.py
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── .typos.toml
├── action.yml
├── AGENTS.md
├── CHANGELOG.md
├── CLAUDE.md
├── CONTRIBUTING.md
├── flake.nix
├── LICENSE
├── pyproject.toml
├── README.md
└── vibe-acp.spec
```

---

## File Index

*Analyzed 192 files, 192 chunks processed*

### Module: `(root)/`

#### `pyproject.toml`

**Purpose**: Defines the project's metadata, dependencies, build configuration, scripts, and development tool settings for the Python package.

**Dependencies**: agent-client-protocol==0.6.3, aiofiles>=24.1.0, httpx>=0.28.1, mcp>=1.14.0, mistralai==1.9.11

**Complexity**: low

#### `.pre-commit-config.yaml`

**Purpose**: Defines the pre-commit hooks configuration for the project, specifying which external hook repositories to use, their versions, and any arguments or exclusions.

**Patterns**: configuration

**Dependencies**: https://github.com/mpalmer/action-validator, https://github.com/pre-commit/pre-commit-hooks, https://github.com/fsouza/mirrors-pyright, https://github.com/astral-sh/ruff-pre-commit, https://github.com/crate-ci/typos

**Complexity**: low

#### `.typos.toml`

**Purpose**: Provides configuration for the Typos spell‑checking tool, extending the ignore list with regular expressions to skip certain lines.

**Complexity**: low

#### `action.yml`

**Purpose**: Defines a composite GitHub Action that optionally installs a specific Python version, sets up uv, installs the Mistral Vibe package, and runs it with a provided prompt and API key.

**Dependencies**: actions/setup-python, astral-sh/setup-uv, uv (Python package manager), Mistral Vibe (installed via uv sync)

**Complexity**: low

### Module: `.github/workflows/`

#### `.github/workflows/release.yml`

**Purpose**: Defines a GitHub Actions workflow that builds the Python package and publishes it to PyPI when a new release is published or when manually triggered.

**Patterns**: CI/CD workflow, GitHub Actions pipeline

**Dependencies**: actions/checkout, actions/setup-python, astral-sh/setup-uv, actions/upload-artifact, pypa/gh-action-pypi-publish

**Complexity**: low

#### `.github/workflows/build-and-upload.yml`

**Purpose**: Defines a GitHub Actions workflow that builds the project on multiple OS/architecture runners, determines the package version with uv, and uploads the built binary as an artifact.

**Dependencies**: actions/checkout, astral-sh/setup-uv, actions/setup-python, actions/upload-artifact, uv (Python package)

**Complexity**: low

#### `.github/workflows/ci.yml`

**Purpose**: Defines the CI workflow for the repository using GitHub Actions, including pre‑commit checks, unit tests, and snapshot tests on pushes and pull requests to the main branch.

**Patterns**: CI pipeline, GitHub Actions workflow

**Dependencies**: astral-sh/setup-uv, actions/checkout, actions/setup-python, actions/cache, actions/upload-artifact

**Complexity**: low

### Module: `distribution/zed/`

#### `distribution/zed/extension.toml`

**Purpose**: Defines the Zed extension metadata and agent server configuration for the Mistral Vibe coding assistant, including versioned download URLs and command info for each platform.

**Complexity**: low

### Module: `scripts/`

#### `scripts/install.sh`

**Purpose**: Installs the `uv` package manager if missing and then installs the `mistral-vibe` tool using `uv` on Linux or macOS systems.

**Exports**: `error`, `info`, `success`, `warning`, `check_platform`, `check_uv_installed`, `install_uv`, `install_vibe`, `main`, `RED` (+6 more)

**Functions**: `error()`, `info()`, `success()`, `warning()`, `check_platform()`, `check_uv_installed()`, `install_uv()`, `install_vibe()`

**Patterns**: Procedural script with helper functions, Guard clauses for error handling

**Dependencies**: uv (Python package manager), curl (CLI HTTP client)

**Complexity**: low

#### `scripts/bump_version.py`

**Purpose**: CLI script that bumps the semantic version of the project by updating pyproject.toml and several related files.

**Exports**: `BumpType`, `BUMP_TYPES`, `parse_version`, `format_version`, `bump_version`, `update_hard_values_files`, `get_current_version`, `main`

**Functions**: `parse_version()`, `format_version()`, `bump_version()`, `update_hard_values_files()`, `get_current_version()`, `main()`

**Complexity**: low

### Module: `tests/`

#### `tests/test_ui_input_history.py`

**Purpose**: Provides pytest test cases for the textual UI input history functionality, verifying navigation through past inputs, interaction with command completion, and cursor behavior.

**Functions**: `vibe_config()`, `vibe_app()`, `history_file()`, `inject_history_file()`, `test_ui_navigation_through_input_history()`, `test_ui_does_nothing_if_command_completion_is_active()`, `test_ui_does_not_prevent_arrow_down_to_move_cursor_to_bottom_lines()`, `test_ui_resumes_arrow_down_after_manual_move()`

**Patterns**: pytest fixtures, dependency injection (manual), async test functions

**Dependencies**: pytest, pytest-asyncio, textual (indirect via VibeApp)

**Complexity**: medium

#### `tests/test_history_manager.py`

**Purpose**: Defines pytest test cases that verify the behaviour of the project's HistoryManager class.

**Functions**: `test_history_manager_normalizes_loaded_entries_like_numbers_to_strings()`, `test_history_manager_retains_a_fixed_number_of_entries()`, `test_history_manager_filters_invalid_and_duplicated_entries()`, `test_history_manager_filters_commands()`, `test_history_manager_allows_navigation_round_trip()`, `test_history_manager_prefix_filtering()`

**Complexity**: low

#### `tests/test_ui_pending_user_message.py`

**Purpose**: Provides pytest‑asyncio test cases for the textual UI, focusing on how user messages are shown as pending while the Vibe agent is initializing, how they can be interrupted, and how initialization can be retried.

**Exports**: `StubAgent`, `_wait_for`, `vibe_config`, `vibe_app`, `_patch_delayed_init`, `test_shows_user_message_as_pending_until_agent_is_initialized`, `test_can_interrupt_pending_message_during_initialization`, `test_retry_initialization_after_interrupt`

**Classes**: `StubAgent`

**Functions**: `vibe_config()`, `vibe_app()`, `test_shows_user_message_as_pending_until_agent_is_initialized()`, `test_can_interrupt_pending_message_during_initialization()`, `test_retry_initialization_after_interrupt()`

**Patterns**: Test Double (StubAgent), Monkeypatching / Patch, Fixture-based setup (pytest fixtures), Async testing with pytest-asyncio

**Dependencies**: pytest, asyncio (standard library), time (standard library), collections (standard library), types (standard library)

**Complexity**: medium

#### `tests/conftest.py`

**Purpose**: Provides pytest fixtures that set up a temporary Vibe configuration directory, mock an API key, and mock platform environment for consistent test execution.

**Exports**: `get_base_config`, `config_dir`, `_mock_api_key`, `_mock_platform`

**Functions**: `get_base_config()`, `config_dir()`, `_mock_api_key()`, `_mock_platform()`

**Patterns**: pytest fixtures with autouse, environment variable mocking via monkeypatch, temporary filesystem layout for testing

**Dependencies**: pytest, tomli_w

**Complexity**: low

#### `tests/test_agent_stats.py`

**Purpose**: Provides pytest test cases for verifying the behavior of Agent statistics handling, reloading, compacting, and history clearing in the Vibe project.

**Exports**: `make_config`, `observer_capture`, `TestAgentStatsHelpers`, `TestReloadPreservesStats`, `TestReloadPreservesMessages`, `TestCompactStatsHandling`, `TestAutoCompactIntegration`, `TestClearHistoryFullReset`, `TestStatsEdgeCases`

**Classes**: `TestAgentStatsHelpers`, `TestReloadPreservesStats`, `TestReloadPreservesMessages`, `TestCompactStatsHandling`, `TestAutoCompactIntegration`

**Functions**: `make_config()`, `observer_capture()`

**Patterns**: Observer (message observer capturing emitted LLMMessage objects), Factory (make_config creates test configuration objects), Fixture (pytest fixture for message observation)

**Dependencies**: pytest

**Complexity**: medium

#### `tests/test_agent_backend.py`

**Purpose**: Provides pytest asynchronous test cases for the Agent class, verifying header propagation, token statistics updates, and streaming behavior with a fake backend.

**Exports**: `test_passes_x_affinity_header_when_asking_an_answer`, `test_passes_x_affinity_header_when_asking_an_answer_streaming`, `test_updates_tokens_stats_based_on_backend_response`, `test_updates_tokens_stats_based_on_backend_response_streaming`

**Functions**: `test_passes_x_affinity_header_when_asking_an_answer()`, `test_passes_x_affinity_header_when_asking_an_answer_streaming()`, `test_updates_tokens_stats_based_on_backend_response()`, `test_updates_tokens_stats_based_on_backend_response_streaming()`

**Patterns**: pytest fixture, asynchronous test (asyncio), dependency injection via fixture

**Dependencies**: pytest

**Complexity**: low

#### `tests/__init__.py`

**Purpose**: Defines a constant TESTS_ROOT that points to the directory containing the test suite.

**Exports**: `TESTS_ROOT`

**Complexity**: low

#### `tests/test_system_prompt.py`

**Purpose**: Tests that the universal system prompt includes Windows‑specific information when running on a Windows platform.

**Functions**: `test_get_universal_system_prompt_includes_windows_prompt_on_windows()`

**Patterns**: pytest test function, monkeypatch for environment simulation

**Dependencies**: pytest

**Complexity**: low

#### `tests/test_agent_observer_streaming.py`

**Purpose**: Provides a comprehensive pytest test suite for the Agent class, focusing on streaming responses, middleware injection, tool call handling, cancellation, and error scenarios.

**Classes**: `InjectBeforeMiddleware`, `CountingMiddleware`

**Functions**: `make_config()`, `observer_capture()`, `test_act_flushes_batched_messages_with_injection_middleware()`, `test_stop_action_flushes_user_msg_before_returning()`, `test_act_emits_user_and_assistant_msgs()`, `test_act_streams_batched_chunks_in_order()`, `test_act_handles_streaming_with_tool_call_events_in_sequence()`, `test_act_handles_tool_call_chunk_with_content()`

**Patterns**: Observer (message_observer callback), Middleware (before/after turn pipeline), Factory (make_config), Async Generator (Agent.act), Fixture (pytest fixtures)

**Dependencies**: pytest, unittest.mock

**Complexity**: medium

#### `tests/test_agent_tool_call.py`

**Purpose**: Test suite that verifies the behavior of the Vibe Agent when handling tool calls, approvals, permissions, errors, and edge cases.

**Functions**: `act_and_collect_events()`, `make_config()`, `make_todo_tool_call()`, `make_agent()`

**Patterns**: Factory (make_* helper functions), Dependency Injection (passing FakeBackend / FakeTool), Test Double (mock_llm_chunk), Async testing with pytest

**Dependencies**: pytest

**Complexity**: medium

#### `tests/test_cli_programmatic_preload.py`

**Purpose**: Provides pytest unit tests for the programmatic CLI interface, verifying that previous messages are correctly preloaded and system messages are ignored, and that streaming output is batched as expected.

**Exports**: `SpyStreamingFormatter`, `test_run_programmatic_preload_streaming_is_batched`, `test_run_programmatic_ignores_system_messages_in_previous`

**Classes**: `SpyStreamingFormatter`

**Functions**: `test_run_programmatic_preload_streaming_is_batched()`, `test_run_programmatic_ignores_system_messages_in_previous()`

**Patterns**: Factory (mock_backend_factory), Dependency Injection (monkeypatching create_formatter), Test Fixture (pytest monkeypatch)

**Dependencies**: pytest

**Complexity**: low

#### `tests/test_agent_auto_compact.py`

**Purpose**: Provides an asynchronous pytest test that verifies the auto‑compact feature of the Agent triggers correctly, batches observer messages, and yields the expected event sequence.

**Functions**: `test_auto_compact_triggers_and_batches_observer()`

**Patterns**: Observer, Async testing (pytest‑asyncio)

**Dependencies**: pytest

**Complexity**: low

#### `tests/test_tagged_text.py`

**Purpose**: Provides unit tests for the TaggedText utility class, verifying its creation, string conversion, parsing, and edge‑case handling.

**Functions**: `test_tagged_text_creation_without_tag()`, `test_tagged_text_creation_with_tag()`, `test_tagged_text_from_string_with_known_tag()`, `test_tagged_text_from_string_with_known_tag_multiline()`, `test_tagged_text_from_string_with_known_tag_whitespace()`, `test_tagged_text_from_string_with_unknown_tag()`, `test_tagged_text_from_string_with_text_before_tag()`, `test_tagged_text_from_string_with_text_after_tag()`

**Dependencies**: pytest

**Complexity**: low

### Module: `tests/acp/`

#### `tests/acp/test_write_file.py`

**Purpose**: Provides pytest test cases for the ACP WriteFile tool, verifying its behavior under various conditions such as successful writes, overwrites, errors, and session updates.

**Exports**: `MockConnection`, `mock_connection`, `acp_write_file_tool`, `TestAcpWriteFileBasic`, `TestAcpWriteFileExecution`, `TestAcpWriteFileSessionUpdates`

**Classes**: `MockConnection`, `TestAcpWriteFileBasic`, `TestAcpWriteFileExecution`, `TestAcpWriteFileSessionUpdates`

**Functions**: `mock_connection()`, `acp_write_file_tool()`

**Patterns**: Test fixture pattern (pytest), Mock object pattern

**Dependencies**: pytest

**Complexity**: low

#### `tests/acp/test_set_mode.py`

**Purpose**: Provides pytest test cases for the ACP agent's session mode management, verifying transitions between auto‑approve and approval‑required modes and handling invalid inputs.

**Exports**: `backend`, `acp_agent`, `TestACPSetMode`

**Classes**: `TestACPSetMode`

**Functions**: `backend()`, `acp_agent()`

**Patterns**: Fixture (pytest), Mock / Patch (unittest.mock), Factory (creating agents via a callable), Dependency Injection

**Dependencies**: pytest

**Complexity**: medium

#### `tests/acp/test_multi_session.py`

**Purpose**: Test suite that verifies multi‑session behavior of the Vibe ACP agent, ensuring separate agents per session, proper error handling for unknown sessions, and concurrent prompt processing.

**Exports**: `backend`, `acp_agent`, `TestMultiSessionCore`

**Classes**: `TestMultiSessionCore`

**Functions**: `backend()`, `acp_agent()`

**Patterns**: Factory (pytest fixtures), Mock/patch (unittest.mock.patch), Async testing (pytest-asyncio), Dependency injection via fixture

**Dependencies**: pytest, pytest-asyncio

**Complexity**: medium

#### `tests/acp/test_bash.py`

**Purpose**: Defines pytest fixtures and a suite of unit tests for the ACP Bash tool implementation, covering parsing, execution, timeout handling, embedding, configuration defaults, and cleanup behavior.

**Exports**: `MockTerminalHandle`, `MockConnection`, `mock_connection`, `acp_bash_tool`, `TestAcpBashBasic`, `TestAcpBashExecution`, `TestAcpBashTimeout`, `TestAcpBashEmbedding`, `TestAcpBashConfig`, `TestAcpBashCleanup`

**Classes**: `MockTerminalHandle`, `MockConnection`, `TestAcpBashBasic`, `TestAcpBashExecution`, `TestAcpBashTimeout`

**Functions**: `mock_connection()`, `acp_bash_tool()`

**Patterns**: Fixture pattern (pytest), Async test pattern (pytest.mark.asyncio), Mock object pattern

**Dependencies**: pytest, asyncio

**Complexity**: medium

#### `tests/acp/test_set_model.py`

**Purpose**: Provides pytest test cases for the ACP SetSessionModel functionality, verifying model switching, config updates, and session behavior in VibeAcpAgent.

**Classes**: `TestACPSetModel`

**Functions**: `backend()`, `acp_agent()`

**Patterns**: Fixture (pytest), Mocking (unittest.mock.patch), Factory (inner _create_agent function to instantiate VibeAcpAgent), Dependency Injection via pytest fixtures

**Dependencies**: pytest

**Complexity**: medium

#### `tests/acp/test_read_file.py`

**Purpose**: Provides pytest unit tests for the ACP read_file tool, including a mock connection and several test cases covering basic functionality, offsets, limits, error handling, and missing session/connection scenarios.

**Exports**: `MockConnection`, `mock_connection`, `acp_read_file_tool`, `TestAcpReadFileBasic`, `TestAcpReadFileExecution`

**Classes**: `MockConnection`, `TestAcpReadFileBasic`, `TestAcpReadFileExecution`

**Functions**: `mock_connection()`, `acp_read_file_tool()`

**Patterns**: pytest fixtures, dependency injection (mock connection), factory (model_construct for state), async testing

**Dependencies**: pytest

**Complexity**: medium

#### `tests/acp/test_search_replace.py`

**Purpose**: Provides pytest test cases for the ACP SearchReplace tool, verifying its behavior including successful replacement, backup creation, error handling, and session update generation.

**Exports**: `MockConnection`, `mock_connection`, `acp_search_replace_tool`, `TestAcpSearchReplaceBasic`, `TestAcpSearchReplaceExecution`, `TestAcpSearchReplaceSessionUpdates`

**Classes**: `MockConnection`, `TestAcpSearchReplaceBasic`, `TestAcpSearchReplaceExecution`, `TestAcpSearchReplaceSessionUpdates`

**Functions**: `mock_connection()`, `acp_search_replace_tool()`

**Patterns**: Dependency Injection (mock connection passed via state), Factory (pydantic model_construct for state), Fixture-based testing (pytest fixtures), Parametrized testing (pytest.mark.parametrize)

**Dependencies**: pytest

**Complexity**: medium

#### `tests/acp/test_content.py`

**Purpose**: Provides pytest fixtures and async test cases to verify that the VibeAcpAgent correctly formats various content blocks (text, embedded resources, resource links) into user messages sent to the backend.

**Classes**: `TestACPContent`

**Functions**: `backend()`, `acp_agent()`

**Patterns**: pytest fixtures, async test functions (pytest‑asyncio), factory pattern for patched agent class, dependency injection via fixtures

**Dependencies**: pytest

**Complexity**: low

#### `tests/acp/test_acp.py`

**Purpose**: Provides async pytest integration tests for the ACP (Agent Communication Protocol) JSON‑RPC interface, spawning a mock agent process, sending requests, reading responses and validating message structures such as session management, tool calls and permission handling.

**Exports**: `deep_merge`, `_create_vibe_home_dir`, `JsonRpcRequest`, `JsonRpcError`, `JsonRpcResponse`, `JsonRpcNotification`, `InitializeJsonRpcRequest`, `InitializeJsonRpcResponse`, `NewSessionJsonRpcRequest`, `NewSessionJsonRpcResponse` (+21 more)

**Classes**: `JsonRpcRequest`, `JsonRpcError`, `JsonRpcResponse`, `JsonRpcNotification`, `InitializeJsonRpcRequest`

**Functions**: `deep_merge()`, `_create_vibe_home_dir()`, `get_acp_agent_process()`, `send_json_rpc()`, `read_response()`, `read_response_for_id()`, `read_multiple_responses()`, `parse_conversation()`

**Patterns**: Async generator for resource management, Pytest fixture and test class pattern, Factory‑like construction of typed JSON‑RPC message classes, Builder pattern for temporary config directory

**Dependencies**: pydantic, pytest, tomli_w

**Complexity**: medium

#### `tests/acp/test_new_session.py`

**Purpose**: Tests the behavior of VibeAcpAgent's new session functionality, verifying response structure and model persistence across sessions.

**Exports**: `backend`, `acp_agent`, `TestACPNewSession`

**Classes**: `TestACPNewSession`

**Functions**: `backend()`, `acp_agent()`

**Patterns**: Fixture (pytest), Mocking (unittest.mock.patch), Factory (agent creation via callback), Async test (pytest.mark.asyncio)

**Dependencies**: pytest

**Complexity**: low

#### `tests/acp/test_initialize.py`

**Purpose**: Provides pytest tests for the ACP initialize flow of VibeAcpAgent, checking default capabilities and terminal‑auth integration.

**Classes**: `TestACPInitialize`

**Functions**: `acp_agent()`

**Patterns**: pytest fixture, async test

**Dependencies**: pytest

**Complexity**: low

### Module: `tests/autocompletion/`

#### `tests/autocompletion/test_path_completer_fuzzy.py`

**Purpose**: Provides pytest tests that verify the fuzzy matching behavior of the PathCompleter class, covering subsequence matching, case insensitivity, directory traversal, hidden files, sorting, and more.

**Exports**: `file_tree`, `test_fuzzy_matches_subsequence_characters`, `test_fuzzy_matches_consecutive_characters_higher`, `test_fuzzy_matches_prefix_highest`, `test_fuzzy_matches_across_directory_boundaries`, `test_fuzzy_matches_case_insensitive`, `test_fuzzy_matches_word_boundaries_preferred`, `test_fuzzy_matches_empty_pattern_shows_all`, `test_fuzzy_matches_hidden_files_only_with_dot`, `test_fuzzy_matches_directories_and_files` (+6 more)

**Functions**: `file_tree()`, `test_fuzzy_matches_subsequence_characters()`, `test_fuzzy_matches_consecutive_characters_higher()`, `test_fuzzy_matches_prefix_highest()`, `test_fuzzy_matches_across_directory_boundaries()`, `test_fuzzy_matches_case_insensitive()`, `test_fuzzy_matches_word_boundaries_preferred()`, `test_fuzzy_matches_empty_pattern_shows_all()`

**Patterns**: pytest fixture, unit testing

**Dependencies**: pytest

**Complexity**: low

#### `tests/autocompletion/test_path_completion_controller.py`

**Purpose**: Provides pytest test cases for the PathCompletionController, using a stub view to verify suggestion rendering, navigation, and completion behaviours.

**Exports**: `StubView`, `file_tree`, `make_controller`, `test_lists_root_entries`, `test_suggests_hidden_entries_only_with_dot_prefix`, `test_lists_nested_entries_when_prefixing_with_folder_name`, `test_resets_when_fragment_invalid`, `test_applies_selected_completion_on_tab_keycode`, `test_applies_selected_completion_on_enter_keycode`, `test_navigates_and_cycles_across_suggestions` (+8 more)

**Classes**: `StubView`

**Functions**: `file_tree()`, `make_controller()`, `test_lists_root_entries()`, `test_suggests_hidden_entries_only_with_dot_prefix()`, `test_lists_nested_entries_when_prefixing_with_folder_name()`, `test_resets_when_fragment_invalid()`, `test_applies_selected_completion_on_tab_keycode()`, `test_applies_selected_completion_on_enter_keycode()`

**Patterns**: Stub (test double) pattern, Fixture pattern (pytest), MVC‑like separation (controller vs view) in tests

**Dependencies**: pytest, textual

**Complexity**: low

#### `tests/autocompletion/test_ui_chat_autocompletion.py`

**Purpose**: Provides pytest asynchronous tests for the Vibe textual UI chat input autocompletion feature, covering command and path completions, navigation, and UI behavior.

**Exports**: `vibe_config`, `vibe_app`, `ensure_selected_command`, `test_popup_appears_with_matching_suggestions`, `test_popup_hides_when_input_cleared`, `test_pressing_tab_writes_selected_command_and_keeps_popup_visible`, `test_arrow_navigation_updates_selected_suggestion`, `test_arrow_navigation_cycles_through_suggestions`, `test_pressing_enter_submits_selected_command_and_hides_popup`, `file_tree` (+9 more)

**Functions**: `vibe_config()`, `vibe_app()`, `ensure_selected_command()`, `test_popup_appears_with_matching_suggestions()`, `test_popup_hides_when_input_cleared()`, `test_pressing_tab_writes_selected_command_and_keeps_popup_visible()`, `test_arrow_navigation_updates_selected_suggestion()`, `test_arrow_navigation_cycles_through_suggestions()`

**Patterns**: Pytest fixtures, Async test functions, UI integration testing with Textual pilot, Helper assertion function

**Dependencies**: pytest, textual

**Complexity**: medium

#### `tests/autocompletion/test_slash_command_controller.py`

**Purpose**: Provides unit tests for the SlashCommandController, using a StubView to verify suggestion rendering, selection cycling, and completion replacement behavior.

**Exports**: `Suggestion`, `SuggestionEvent`, `Replacement`, `StubView`, `key_event`, `make_controller`, `test_on_text_change_emits_matching_suggestions_in_insertion_order_and_ignores_duplicates`, `test_on_text_change_filters_suggestions_case_insensitively`, `test_on_text_change_clears_suggestions_when_no_matches`, `test_on_text_change_limits_the_number_of_results_to_five_and_preserve_insertion_order` (+3 more)

**Classes**: `Suggestion`, `SuggestionEvent`, `Replacement`, `StubView`

**Functions**: `key_event()`, `make_controller()`, `test_on_text_change_emits_matching_suggestions_in_insertion_order_and_ignores_duplicates()`, `test_on_text_change_filters_suggestions_case_insensitively()`, `test_on_text_change_clears_suggestions_when_no_matches()`, `test_on_text_change_limits_the_number_of_results_to_five_and_preserve_insertion_order()`, `test_on_key_tab_applies_selected_completion()`, `test_on_key_down_and_up_cycle_selection()`

**Patterns**: Test Stub / Mock (StubView), Factory (make_controller helper)

**Dependencies**: textual

**Complexity**: low

#### `tests/autocompletion/test_file_indexer.py`

**Purpose**: Integration test suite for the FileIndexer class, verifying that the index updates correctly on file system changes and that resource management works as expected.

**Exports**: `file_indexer`, `_wait_for`, `test_updates_index_on_file_creation`, `test_updates_index_on_file_deletion`, `test_updates_index_on_file_rename`, `test_updates_index_on_folder_rename`, `test_updates_index_incrementally_by_default`, `test_rebuilds_index_when_mass_change_threshold_is_exceeded`, `test_switching_between_roots_restarts_index`, `test_watcher_failure_does_not_break_existing_index` (+1 more)

**Functions**: `file_indexer()`, `_wait_for()`, `test_updates_index_on_file_creation()`, `test_updates_index_on_file_deletion()`, `test_updates_index_on_file_rename()`, `test_updates_index_on_folder_rename()`, `test_updates_index_incrementally_by_default()`, `test_rebuilds_index_when_mass_change_threshold_is_exceeded()`

**Patterns**: pytest fixtures, integration testing with real filesystem, resource cleanup via explicit shutdown

**Dependencies**: pytest

**Complexity**: medium

#### `tests/autocompletion/test_path_completer_recursive.py`

**Purpose**: Provides pytest tests for the recursive behaviour of the PathCompleter autocompletion class, ensuring it finds files and directories correctly based on various query patterns.

**Functions**: `file_tree()`, `test_finds_files_recursively_by_filename()`, `test_finds_files_recursively_by_partial_path()`, `test_finds_files_recursively_with_subsequence()`, `test_finds_multiple_matches_recursively()`, `test_prioritizes_exact_path_matches()`, `test_finds_files_when_pattern_matches_directory_name()`

**Patterns**: pytest fixture, unit test

**Dependencies**: pytest

**Complexity**: low

#### `tests/autocompletion/test_fuzzy.py`

**Purpose**: Provides a suite of unit tests for the `fuzzy_match` function in the project's autocompletion module, verifying its matching, scoring, and edge‑case behavior.

**Functions**: `test_empty_pattern_matches_anything()`, `test_matches_exact_prefix()`, `test_no_match_when_characters_are_out_of_order()`, `test_treats_consecutive_characters_as_subsequence()`, `test_ignores_case()`, `test_treats_scattered_characters_as_subsequence()`, `test_treats_path_separator_as_word_boundary()`, `test_prefers_word_boundary_matching_over_subsequence()`

**Dependencies**: pytest

**Complexity**: low

#### `tests/autocompletion/test_path_prompt_transformer.py`

**Purpose**: Provides pytest unit tests for the render_path_prompt function, verifying its handling of file and directory references, embedding limits, and edge cases.

**Exports**: `test_treats_paths_to_files_as_embedded_resources`, `test_treats_path_to_directory_as_resource_links`, `test_keeps_emails_and_embeds_paths`, `test_ignores_nonexistent_paths`, `test_falls_back_to_link_for_binary_files`, `test_excludes_supposed_binary_files_quickly_before_reading_content`, `test_applies_max_embed_size_guard`, `test_parses_paths_with_special_characters_when_quoted`, `test_deduplicates_identical_paths`

**Functions**: `test_treats_paths_to_files_as_embedded_resources()`, `test_treats_path_to_directory_as_resource_links()`, `test_keeps_emails_and_embeds_paths()`, `test_ignores_nonexistent_paths()`, `test_falls_back_to_link_for_binary_files()`, `test_excludes_supposed_binary_files_quickly_before_reading_content()`, `test_applies_max_embed_size_guard()`, `test_parses_paths_with_special_characters_when_quoted()`

**Patterns**: pytest test functions, fixture usage (tmp_path), assert-driven verification

**Dependencies**: pytest

**Complexity**: low

### Module: `tests/backend/`

#### `tests/backend/test_backend.py`

**Purpose**: Provides pytest async test cases for verifying the behavior of generic and Mistral LLM backends, including normal completions, streaming, error handling, payload options, and user-agent headers.

**Exports**: `TestBackend`

**Classes**: `TestBackend`

**Patterns**: Factory, Dependency Injection, Mocking (respx), Parameterization (pytest.mark.parametrize)

**Dependencies**: httpx, pytest, respx

**Complexity**: medium

### Module: `tests/backend/data/`

#### `tests/backend/data/mistral.py`

**Purpose**: Defines static test fixture data for Mistral API interactions used in backend unit tests, including normal, tool, and streamed conversation scenarios.

**Exports**: `SIMPLE_CONVERSATION_PARAMS`, `TOOL_CONVERSATION_PARAMS`, `STREAMED_SIMPLE_CONVERSATION_PARAMS`, `STREAMED_TOOL_CONVERSATION_PARAMS`

**Complexity**: low

#### `tests/backend/data/__init__.py`

**Purpose**: Defines simple type aliases for common data structures used in the backend tests.

**Exports**: `Url`, `JsonResponse`, `ResultData`, `Chunk`

**Complexity**: low

#### `tests/backend/data/fireworks.py`

**Purpose**: Provides static test data for Fireworks API interactions, including simple and tool‑based conversations as well as their streaming variants.

**Exports**: `SIMPLE_CONVERSATION_PARAMS`, `TOOL_CONVERSATION_PARAMS`, `STREAMED_SIMPLE_CONVERSATION_PARAMS`, `STREAMED_TOOL_CONVERSATION_PARAMS`

**Complexity**: low

### Module: `tests/cli/`

#### `tests/cli/test_clipboard.py`

**Purpose**: Provides pytest test cases for the clipboard CLI utilities, verifying behavior of copy_selection_to_clipboard and the OSC‑52 sequence writer.

**Classes**: `MockWidget`

**Functions**: `mock_app()`, `test_copy_selection_to_clipboard_no_notification()`, `test_copy_selection_to_clipboard_success_with_osc52()`, `test_copy_selection_to_clipboard_osc52_fails_success_with_pyperclip()`, `test_copy_selection_to_clipboard_osc52_and_pyperclip_fail_success_with_app_copy()`, `test_copy_selection_to_clipboard_all_methods_fail()`, `test_copy_selection_to_clipboard_multiple_widgets()`, `test_copy_selection_to_clipboard_preview_shortening()`

**Patterns**: Test pattern with pytest fixtures and parametrize, Mocking external dependencies with unittest.mock

**Dependencies**: pytest, textual, pyperclip, unittest.mock (standard library), base64 (standard library)

**Complexity**: medium

### Module: `tests/core/`

#### `tests/core/test_config_migration.py`

**Purpose**: Provides helper functions and a context manager used by tests to create, migrate, and load temporary Vibe configuration files.

**Exports**: `_restore_dump_config`, `_migrate_config_file`, `_load_migrated_config`

**Patterns**: ContextManager (via @contextmanager), Monkey‑patching (runtime replacement of classmethod)

**Dependencies**: tomli_w

**Complexity**: low

#### `tests/core/test_config_resolution.py`

**Purpose**: Provides pytest unit tests that verify how the configuration file resolution works, including local vs global config selection and handling of the VIBE_HOME environment variable.

**Classes**: `TestResolveConfigFile`

**Dependencies**: pytest

**Complexity**: low

### Module: `tests/mock/`

#### `tests/mock/mock_entrypoint.py`

**Purpose**: Provides a wrapper script that intercepts and mocks LLM calls during tests by reading mock data from an environment variable and patching the LLM backend methods.

**Exports**: `mock_llm_output`

**Functions**: `mock_llm_output()`

**Patterns**: Monkey patching, Dependency injection via unittest.mock.patch, Environment‑variable‑driven configuration

**Dependencies**: pydantic

**Complexity**: medium

#### `tests/mock/mock_backend_factory.py`

**Purpose**: Provides a context manager to temporarily replace a backend factory function in the global BACKEND_FACTORY mapping for testing or mocking purposes.

**Exports**: `mock_backend_factory`

**Functions**: `mock_backend_factory()`

**Patterns**: Factory, Context Manager, Mocking

**Complexity**: low

#### `tests/mock/utils.py`

**Purpose**: Utility functions for creating mock LLMChunk objects and generating an environment variable dictionary containing their JSON representation for testing.

**Exports**: `MOCK_DATA_ENV_VAR`, `mock_llm_chunk`, `get_mocking_env`

**Functions**: `mock_llm_chunk()`, `get_mocking_env()`

**Patterns**: Factory function

**Complexity**: low

### Module: `tests/onboarding/`

#### `tests/onboarding/test_ui_onboarding.py`

**Purpose**: Contains asynchronous pytest UI integration tests for the onboarding flow of the Vibe application, verifying theme selection and API key handling.

**Exports**: `_wait_for`, `pass_welcome_screen`, `test_ui_gets_through_the_onboarding_successfully`, `test_ui_can_pick_a_theme_and_saves_selection`

**Functions**: `_wait_for()`, `pass_welcome_screen()`, `test_ui_gets_through_the_onboarding_successfully()`, `test_ui_can_pick_a_theme_and_saves_selection()`

**Patterns**: Async testing with pytest-asyncio, Polling wait (retry) pattern, Arrange‑Act‑Assert test structure

**Dependencies**: pytest, textual

**Complexity**: medium

#### `tests/onboarding/test_run_onboarding.py`

**Purpose**: Provides pytest unit tests for the onboarding flow by simulating the textual App and verifying exit, warning, and successful completion behaviours.

**Exports**: `StubApp`, `_exit_raiser`, `test_exits_on_cancel`, `test_warns_on_save_error`, `test_successfully_completes`

**Classes**: `StubApp`

**Functions**: `_exit_raiser()`, `test_exits_on_cancel()`, `test_warns_on_save_error()`, `test_successfully_completes()`

**Patterns**: Test fixture pattern (pytest fixtures), Monkey‑patching

**Dependencies**: pytest, textual

**Complexity**: low

### Module: `tests/snapshots/`

#### `tests/snapshots/test_ui_snapshot_code_block_horizontal_scrolling.py`

**Purpose**: Provides a snapshot test that verifies long code blocks can be horizontally scrolled in the textual UI.

**Exports**: `test_snapshot_allows_horizontal_scrolling_for_long_code_blocks`

**Functions**: `test_snapshot_allows_horizontal_scrolling_for_long_code_blocks()`

**Patterns**: Snapshot testing

**Dependencies**: textual

**Complexity**: low

#### `tests/snapshots/base_snapshot_test_app.py`

**Purpose**: Provides a VibeApp subclass with a deterministic configuration for snapshot testing, injecting a fake backend and hiding the chat input cursor.

**Exports**: `default_config`, `BaseSnapshotTestApp`

**Classes**: `BaseSnapshotTestApp`

**Functions**: `default_config()`

**Patterns**: Dependency Injection, Template Method (subclass overrides lifecycle hooks)

**Dependencies**: rich, textual

**Complexity**: low

#### `tests/snapshots/snap_compare.py`

**Purpose**: Defines a typing Protocol for snapshot comparison used in tests, specifying the callable signature expected for snapshot compare functions.

**Exports**: `SnapCompare`

**Classes**: `SnapCompare`

**Patterns**: Protocol (type hinting)

**Dependencies**: textual

**Complexity**: low

#### `tests/snapshots/test_ui_snapshot_basic_conversation.py`

**Purpose**: Defines a snapshot test application that includes a conversation with a fake backend and a pytest test that verifies the UI snapshot of a basic conversation.

**Exports**: `SnapshotTestAppWithConversation`, `test_snapshot_shows_basic_conversation`

**Classes**: `SnapshotTestAppWithConversation`

**Functions**: `test_snapshot_shows_basic_conversation()`

**Patterns**: Test fixture pattern, Factory-like setup for test app

**Dependencies**: textual

**Complexity**: low

#### `tests/snapshots/test_ui_snapshot_release_update_notification.py`

**Purpose**: Defines a snapshot test application that enables update checks with fake adapters and a test that verifies the UI shows a release update notification.

**Exports**: `SnapshotTestAppWithUpdate`, `test_snapshot_shows_release_update_notification`

**Classes**: `SnapshotTestAppWithUpdate`

**Functions**: `test_snapshot_shows_release_update_notification()`

**Patterns**: Test fixture pattern

**Dependencies**: textual

**Complexity**: low

### Module: `tests/stubs/`

#### `tests/stubs/fake_backend.py`

**Purpose**: Provides a minimal asynchronous backend stub for tests, supplying predefined LLMChunk results and tracking request data without making real network calls.

**Exports**: `FakeBackend`

**Classes**: `FakeBackend`

**Patterns**: Test Double (mock/stub), Async Context Manager

**Complexity**: low

#### `tests/stubs/fake_tool.py`

**Purpose**: Provides stub implementations of a tool, its argument, result, and state models for testing within the Vibe framework.

**Exports**: `FakeToolArgs`, `FakeToolResult`, `FakeToolState`, `FakeTool`

**Classes**: `FakeToolArgs`, `FakeToolResult`, `FakeToolState`, `FakeTool`

**Patterns**: Inheritance (subclassing BaseTool), Generic typing for tool configuration

**Dependencies**: pydantic

**Complexity**: low

#### `tests/stubs/fake_connection.py`

**Purpose**: Provides a fake implementation of the AgentSideConnection interface for use in tests, recording session updates and exposing async context‑manager behavior.

**Exports**: `FakeAgentSideConnection`

**Classes**: `FakeAgentSideConnection`

**Patterns**: Fake Object / Test Stub, Async Context Manager

**Complexity**: low

### Module: `tests/tools/`

#### `tests/tools/test_grep.py`

**Purpose**: Provides a comprehensive pytest test suite for the Grep tool implementation, verifying backend detection, pattern searching, ignore handling, truncation, configuration, and search history tracking.

**Exports**: `grep`, `grep_gnu_only`, `test_detects_ripgrep_when_available`, `test_falls_back_to_gnu_grep`, `test_raises_error_if_no_grep_available`, `test_finds_pattern_in_file`, `test_finds_multiple_matches`, `test_returns_empty_on_no_matches`, `test_fails_with_empty_pattern`, `test_fails_with_nonexistent_path` (+20 more)

**Functions**: `grep()`, `grep_gnu_only()`, `test_detects_ripgrep_when_available()`, `test_falls_back_to_gnu_grep()`, `test_raises_error_if_no_grep_available()`, `test_finds_pattern_in_file()`, `test_finds_multiple_matches()`, `test_returns_empty_on_no_matches()`

**Patterns**: Fixture (dependency injection), Async test pattern, Strategy (backend selection), Factory (creation of Grep instance via config/state)

**Dependencies**: pytest

**Complexity**: medium

#### `tests/tools/test_ui_bash_execution.py`

**Purpose**: Provides pytest‑asyncio tests for the Textual UI of the Vibe application, verifying correct handling of Bash command output, exit codes, and error cases.

**Exports**: `vibe_config`, `vibe_app`, `_wait_for_bash_output_message`, `assert_no_command_error`, `test_ui_reports_no_output`, `test_ui_shows_success_in_case_of_zero_code`, `test_ui_shows_failure_in_case_of_non_zero_code`, `test_ui_handles_non_utf8_output`, `test_ui_handles_utf8_output`, `test_ui_handles_non_utf8_stderr`

**Functions**: `vibe_config()`, `vibe_app()`, `_wait_for_bash_output_message()`, `assert_no_command_error()`, `test_ui_reports_no_output()`, `test_ui_shows_success_in_case_of_zero_code()`, `test_ui_shows_failure_in_case_of_non_zero_code()`, `test_ui_handles_non_utf8_output()`

**Patterns**: pytest fixtures, async test with pytest-asyncio, UI driver/pilot pattern (Textual testing)

**Dependencies**: pytest, pytest-asyncio, textual

**Complexity**: medium

#### `tests/tools/test_bash.py`

**Purpose**: Provides pytest test cases for the Bash tool implementation, verifying command execution, error handling, workdir usage, timeouts, output truncation, encoding handling, and allowlist/denylist logic.

**Functions**: `bash()`, `test_runs_echo_successfully()`, `test_fails_cat_command_with_missing_file()`, `test_uses_effective_workdir()`, `test_handles_timeout()`, `test_truncates_output_to_max_bytes()`, `test_decodes_non_utf8_bytes()`, `test_check_allowlist_denylist()`

**Patterns**: pytest fixtures, async test functions, exception assertion with pytest.raises, parameterized command arguments via BashArgs

**Dependencies**: pytest

**Complexity**: low

#### `tests/tools/test_manager_get_tool_config.py`

**Purpose**: Provides pytest unit tests for the ToolManager.get_tool_config method, verifying default behavior, override merging, tool‑specific field preservation, fallback handling, and workdir application.

**Exports**: `config`, `tool_manager`, `test_returns_default_config_when_no_overrides`, `test_merges_user_overrides_with_defaults`, `test_preserves_tool_specific_fields_from_overrides`, `test_falls_back_to_base_config_for_unknown_tool`, `test_applies_workdir_from_vibe_config`

**Functions**: `config()`, `tool_manager()`, `test_returns_default_config_when_no_overrides()`, `test_merges_user_overrides_with_defaults()`, `test_preserves_tool_specific_fields_from_overrides()`, `test_falls_back_to_base_config_for_unknown_tool()`, `test_applies_workdir_from_vibe_config()`

**Patterns**: fixture-based testing (pytest), configuration merging

**Dependencies**: pytest

**Complexity**: low

### Module: `tests/update_notifier/`

#### `tests/update_notifier/test_filesystem_update_cache_repository.py`

**Purpose**: Provides pytest asynchronous test cases for the FileSystemUpdateCacheRepository implementation, verifying read/write behavior and error handling of the update cache JSON file.

**Exports**: `test_reads_cache_from_file_when_present`, `test_returns_none_when_cache_file_is_missing`, `test_returns_none_when_cache_file_is_corrupted`, `test_overwrites_existing_cache`, `test_silently_ignores_errors_when_writing_cache_fails`

**Functions**: `test_reads_cache_from_file_when_present()`, `test_returns_none_when_cache_file_is_missing()`, `test_returns_none_when_cache_file_is_corrupted()`, `test_overwrites_existing_cache()`, `test_silently_ignores_errors_when_writing_cache_fails()`

**Patterns**: pytest async test pattern

**Dependencies**: pytest

**Complexity**: low

#### `tests/update_notifier/test_github_version_update_gateway.py`

**Purpose**: Test suite for the GitHubVersionUpdateGateway class, verifying its behavior under various GitHub API responses and error conditions.

**Exports**: `Handler`, `GITHUB_API_URL`, `_raise_connect_timeout`, `test_retrieves_latest_version_when_available`, `test_strips_uppercase_prefix_from_tag_name`, `test_considers_no_update_available_when_no_releases_are_found`, `test_considers_no_update_available_when_only_drafts_and_prereleases_are_found`, `test_picks_the_most_recently_published_non_prerelease_and_non_draft`, `test_ignores_draft_releases_and_prereleases`, `test_retrieves_nothing_when_fetching_update_fails`

**Functions**: `test_retrieves_latest_version_when_available()`, `test_strips_uppercase_prefix_from_tag_name()`, `test_considers_no_update_available_when_no_releases_are_found()`, `test_considers_no_update_available_when_only_drafts_and_prereleases_are_found()`, `test_picks_the_most_recently_published_non_prerelease_and_non_draft()`, `test_ignores_draft_releases_and_prereleases()`, `test_retrieves_nothing_when_fetching_update_fails()`

**Patterns**: Parameterized testing (pytest.mark.parametrize), Async testing with pytest.mark.asyncio

**Dependencies**: httpx, pytest

**Complexity**: low

#### `tests/update_notifier/test_ui_version_update_notification.py`

**Purpose**: Provides pytest‑asyncio test cases for the Vibe CLI UI update‑notification feature, verifying notification display, cache behavior, and error handling.

**Exports**: `_wait_for_notification`, `_assert_no_notifications`, `vibe_config_with_update_checks_enabled`, `make_vibe_app`, `VibeAppFactory`, `test_ui_displays_update_notification`, `test_ui_does_not_display_update_notification_when_not_available`, `test_ui_displays_warning_toast_when_check_fails`, `test_ui_does_not_invoke_gateway_nor_show_error_notification_when_update_checks_are_disabled`, `test_ui_does_not_invoke_gateway_nor_show_update_notification_when_update_checks_are_disabled` (+2 more)

**Classes**: `VibeAppFactory`

**Functions**: `vibe_config_with_update_checks_enabled()`, `make_vibe_app()`, `test_ui_displays_update_notification()`, `test_ui_does_not_display_update_notification_when_not_available()`, `test_ui_displays_warning_toast_when_check_fails()`, `test_ui_does_not_invoke_gateway_nor_show_error_notification_when_update_checks_are_disabled()`, `test_ui_does_not_invoke_gateway_nor_show_update_notification_when_update_checks_are_disabled()`, `test_ui_does_not_show_toast_when_update_is_known_in_recent_cache_already()`

**Patterns**: Factory (make_vibe_app fixture), Protocol (VibeAppFactory), Dependency Injection (inject fake notifier and cache), Fixture‑based testing (pytest fixtures), Async testing (pytest‑asyncio), Observer pattern (notifications displayed by VibeApp)

**Dependencies**: pytest, textual

**Complexity**: medium

#### `tests/update_notifier/test_version_update_use_case.py`

**Purpose**: Defines a suite of asynchronous pytest test cases for the version update use‑case, exercising caching, notification logic, error handling and version parsing.

**Functions**: `current_timestamp()`, `test_retrieves_the_latest_version_update_when_available()`, `test_retrieves_nothing_when_the_current_version_is_the_latest()`, `test_retrieves_nothing_when_the_current_version_is_greater_than_the_latest()`, `test_retrieves_nothing_when_no_version_is_available()`, `test_retrieves_nothing_when_latest_version_is_invalid()`, `test_replaces_hyphens_with_plus_signs_in_latest_version_to_conform_with_PEP_440()`, `test_retrieves_nothing_when_current_version_is_invalid()`

**Patterns**: Fixture pattern (pytest.fixture), Parametrized testing (pytest.mark.parametrize), Async testing (pytest.mark.asyncio), Dependency injection via constructor arguments (gateway, cache repository, timestamp provider)

**Dependencies**: pytest

**Complexity**: medium

#### `tests/update_notifier/test_pypi_version_update_gateway.py`

**Purpose**: Provides unit tests for the PyPIVersionUpdateGateway, verifying correct handling of PyPI responses, yanked releases, version matching, and error conditions.

**Functions**: `test_retrieves_nothing_when_no_versions_are_available()`, `test_retrieves_the_latest_non_yanked_version()`, `test_retrieves_nothing_when_only_yanked_versions_are_available()`, `test_does_not_match_versions_by_substring()`, `test_retrieves_nothing_when_fetching_update_fails()`

**Patterns**: pytest asynchronous testing, parameterized testing, dependency injection via mock transport

**Dependencies**: httpx, pytest

**Complexity**: low

### Module: `tests/update_notifier/adapters/`

#### `tests/update_notifier/adapters/fake_version_update_gateway.py`

**Purpose**: Provides a fake implementation of VersionUpdateGateway for testing, allowing predefined update data or error injection and tracking call count.

**Exports**: `FakeVersionUpdateGateway`

**Classes**: `FakeVersionUpdateGateway`

**Patterns**: Test Double (Fake), Dependency Injection

**Complexity**: low

#### `tests/update_notifier/adapters/fake_update_cache_repository.py`

**Purpose**: Provides a fake in‑memory implementation of the UpdateCacheRepository interface for tests.

**Exports**: `FakeUpdateCacheRepository`

**Classes**: `FakeUpdateCacheRepository`

**Patterns**: Test Double (Fake), Repository Pattern, Dependency Injection

**Complexity**: low

### Module: `vibe/`

#### `vibe/__init__.py`

**Purpose**: Defines the root directory of the Vibe package as a Path object for use throughout the project.

**Exports**: `VIBE_ROOT`

**Complexity**: low

### Module: `vibe/acp/`

#### `vibe/acp/entrypoint.py`

**Purpose**: Provides the command‑line entry point for running Vibe in ACP mode, handling a '--setup' flag to run onboarding or starting the ACP server.

**Exports**: `Arguments`, `parse_arguments`, `main`

**Classes**: `Arguments`

**Functions**: `parse_arguments()`, `main()`

**Patterns**: Command‑line interface (CLI) entry point

**Complexity**: low

#### `vibe/acp/utils.py`

**Purpose**: Defines Vibe‑specific session mode enum with conversion helpers to the generic ACP SessionMode, and declares tool permission options as enums and PermissionOption instances.

**Exports**: `VibeSessionMode`, `ToolOption`, `TOOL_OPTIONS`

**Classes**: `VibeSessionMode`, `ToolOption`

**Patterns**: Adapter (VibeSessionMode ↔ SessionMode conversion), Enum

**Complexity**: low

#### `vibe/acp/acp_agent.py`

**Purpose**: Implements the ACP (Agent Communication Protocol) server for Mistral Vibe, managing sessions, handling prompts, tool calls and approval callbacks, and interfacing between the ACP connection and the Vibe core agent.

**Exports**: `AcpSession`, `VibeAcpAgent`, `_run_acp_server`, `run_acp_server`

**Classes**: `AcpSession`, `VibeAcpAgent`

**Functions**: `run_acp_server()`

**Patterns**: Factory (creation of VibeAgent and session objects), Callback (approval callback mechanism), Adapter (render_path_prompt adapts path prompts), Observer (connection sends notifications/events)

**Dependencies**: acp, pydantic

**Complexity**: medium

### Module: `vibe/acp/tools/`

#### `vibe/acp/tools/session_update.py`

**Purpose**: Generates session update objects for tool call and tool result events, delegating to custom protocol implementations when available.

**Exports**: `TOOL_KIND`, `tool_call_session_update`, `tool_result_session_update`

**Functions**: `tool_call_session_update()`, `tool_result_session_update()`

**Patterns**: Adapter (ToolUIDataAdapter), Strategy (protocol‑based delegation), Factory (dynamic construction of schema objects)

**Complexity**: medium

#### `vibe/acp/tools/base.py`

**Purpose**: Provides a generic base class and related protocols for tools that operate within an ACP (Agent‑Side Connection Protocol) session, handling shared state and session update communication.

**Exports**: `ToolCallSessionUpdateProtocol`, `ToolResultSessionUpdateProtocol`, `AcpToolState`, `BaseAcpTool`

**Classes**: `ToolCallSessionUpdateProtocol`, `ToolResultSessionUpdateProtocol`, `AcpToolState`, `BaseAcpTool`

**Patterns**: Protocol (interface), Abstract Base Class, Factory Method, Dependency Injection

**Dependencies**: acp, pydantic

**Complexity**: medium

### Module: `vibe/acp/tools/builtins/`

#### `vibe/acp/tools/builtins/search_replace.py`

**Purpose**: Implements an ACP‑integrated search‑and‑replace tool that reads, edits, and writes files via the ACP protocol, extending the core search‑replace functionality and providing session update events for the VIBE system.

**Exports**: `AcpSearchReplaceState`, `SearchReplace`

**Classes**: `AcpSearchReplaceState`, `SearchReplace`

**Patterns**: Template Method (overriding abstract hooks from BaseAcpTool/CoreSearchReplaceTool), Adapter (wrapping core search‑replace logic for ACP communication), Factory (via classmethod _get_tool_state_class to provide state instances)

**Dependencies**: acp

**Complexity**: medium

#### `vibe/acp/tools/builtins/bash.py`

**Purpose**: Implements an ACP‑integrated Bash tool that creates a remote terminal, runs a command with optional timeout and environment variables, streams progress updates, and returns the command result.

**Exports**: `AcpBashState`, `Bash`

**Classes**: `AcpBashState`, `Bash`

**Patterns**: Inheritance, Async/Await, Template Method (overriding run in subclass), Factory (creation of request objects)

**Dependencies**: acp

**Complexity**: medium

#### `vibe/acp/tools/builtins/read_file.py`

**Purpose**: Implements an ACP‑specific read‑file tool that sends a ReadTextFileRequest over a connection, handling offsets, limits and truncation, and integrates with the Vibe core read‑file functionality.

**Exports**: `ReadFileResult`, `AcpReadFileState`, `ReadFile`

**Classes**: `AcpReadFileState`, `ReadFile`

**Patterns**: Adapter (adapts core read‑file tool to ACP interface), Template Method (overrides _read_file), Multiple Inheritance

**Dependencies**: acp

**Complexity**: medium

#### `vibe/acp/tools/builtins/todo.py`

**Purpose**: Provides an ACP‑compatible wrapper around the core Todo tool, translating Todo results into agent plan updates.

**Exports**: `AcpTodoState`, `Todo`, `TodoArgs`

**Classes**: `AcpTodoState`, `Todo`

**Patterns**: Adapter, Multiple Inheritance, Factory Method (via classmethod for state creation)

**Dependencies**: typing

**Complexity**: low

#### `vibe/acp/tools/builtins/write_file.py`

**Purpose**: Implements the ACP‑specific WriteFile tool by extending the core WriteFile implementation and handling session updates for file edit tool calls.

**Exports**: `AcpWriteFileState`, `WriteFile`

**Classes**: `AcpWriteFileState`, `WriteFile`

**Patterns**: Adapter (wrapping core WriteFile with ACP behaviour), Template Method (overriding _write_file), Factory Method (class method to provide the tool state class)

**Dependencies**: acp

**Complexity**: medium

### Module: `vibe/cli/`

#### `vibe/cli/entrypoint.py`

**Purpose**: Provides the entry point for the Vibe CLI, handling argument parsing, configuration loading, session continuation, and dispatching to either programmatic execution or the interactive Textual UI.

**Exports**: `parse_arguments`, `get_prompt_from_stdin`, `load_config_or_exit`, `main`

**Functions**: `parse_arguments()`, `get_prompt_from_stdin()`, `load_config_or_exit()`, `main()`

**Patterns**: Command‑line Interface (CLI) pattern, Factory pattern (used indirectly when loading/creating VibeConfig), Strategy pattern (different execution strategies: programmatic vs interactive UI)

**Dependencies**: rich

**Complexity**: medium

#### `vibe/cli/history_manager.py`

**Purpose**: Provides a manager for storing, retrieving, and navigating command-line input history with persistence to a file.

**Exports**: `HistoryManager`

**Classes**: `HistoryManager`

**Complexity**: low

#### `vibe/cli/clipboard.py`

**Purpose**: Provides utilities to copy the current text selection from a Textual App to the system clipboard using OSC‑52, pyperclip, or the app's own clipboard method, and shows a notification.

**Exports**: `copy_selection_to_clipboard`

**Functions**: `copy_selection_to_clipboard()`

**Patterns**: Fallback/Strategy pattern (tries multiple clipboard methods in order)

**Dependencies**: pyperclip, textual

**Complexity**: low

#### `vibe/cli/commands.py`

**Purpose**: Defines a registry of CLI commands for the VIBE application, mapping command aliases to handler identifiers and providing help text generation.

**Exports**: `Command`, `CommandRegistry`

**Classes**: `Command`, `CommandRegistry`

**Patterns**: Registry pattern

**Complexity**: low

### Module: `vibe/cli/autocompletion/`

#### `vibe/cli/autocompletion/path_completion.py`

**Purpose**: Provides a controller that computes and displays path‑based autocompletion suggestions for the CLI, handling asynchronous computation and user interaction.

**Exports**: `PathCompletionController`, `MAX_SUGGESTIONS_COUNT`

**Classes**: `PathCompletionController`

**Patterns**: Callback (Future done callback), Thread‑pool background execution, Controller (MVC) pattern

**Dependencies**: textual

**Complexity**: medium

#### `vibe/cli/autocompletion/slash_command.py`

**Purpose**: Implements a controller that handles slash‑command autocompletion in the CLI, interacting with a completer to fetch suggestions and a view to render them.

**Exports**: `SlashCommandController`

**Classes**: `SlashCommandController`

**Patterns**: Controller (separating UI view updates from business logic), Command (handling user key events)

**Dependencies**: textual

**Complexity**: medium

#### `vibe/cli/autocompletion/base.py`

**Purpose**: Defines core abstractions for autocompletion handling, including a result enum and a view protocol that specifies how suggestions are rendered and applied.

**Exports**: `CompletionResult`, `CompletionView`

**Classes**: `CompletionResult`, `CompletionView`

**Patterns**: Enum, Protocol (interface), Strategy (via protocol abstraction)

**Complexity**: low

### Module: `vibe/cli/init/`

#### `vibe/cli/init/discovery.py`

**Purpose**: Provides functions to discover files in a codebase, classify them, build a directory‑tree representation, and handle chunking of large files for the initialization phase.

**Exports**: `MAX_FILE_SIZE_BYTES`, `CHUNK_SIZE_CHARS`, `DEFAULT_IGNORE_PATTERNS`, `SOURCE_EXTENSIONS`, `CONFIG_EXTENSIONS`, `DOC_EXTENSIONS`, `PACKAGE_FILES`, `ENTRY_POINT_PATTERNS`, `FileInfo`, `DiscoveryResult` (+7 more)

**Classes**: `FileInfo`, `DiscoveryResult`

**Functions**: `load_gitignore_patterns()`, `is_ignored()`, `classify_file()`, `build_tree_structure()`, `discover_codebase()`, `get_file_content()`, `get_chunk_count()`

**Complexity**: medium

#### `vibe/cli/init/analysis_index.py`

**Purpose**: Provides data‑class structures and a builder to create a JSON index of the VIBE‑ANALYSIS.md document, enabling fast lookup of sections, files, topics and positions.

**Exports**: `SubsectionIndex`, `FileMention`, `FilePositions`, `FileEntry`, `SectionIndex`, `AnalysisIndex`, `build_index_from_context`, `IndexBuilder`

**Classes**: `SubsectionIndex`, `FileMention`, `FilePositions`, `FileEntry`, `SectionIndex`

**Functions**: `build_index_from_context()`

**Patterns**: DataClass, Builder

**Complexity**: medium

#### `vibe/cli/init/__init__.py`

**Purpose**: Provides the public interface for the Vibe CLI's `/init` command by re‑exporting the core execution, contracts extraction, and section name utilities.

**Exports**: `execute_init`, `extract_contracts`, `ContractsResult`, `get_section_names`

**Complexity**: low

#### `vibe/cli/init/generator.py`

**Purpose**: Generates the comprehensive VIBE-ANALYSIS.md documentation for a codebase by assembling LLM‑generated sections, building a deterministic markdown structure, and creating a searchable JSON index.

**Exports**: `GenerationContext`, `GenerationResult`, `SECTION_PROMPTS`, `generate_vibe_md`, `update_vibe_md`, `get_section_names`

**Classes**: `GenerationContext`, `GenerationResult`

**Functions**: `generate_vibe_md()`, `update_vibe_md()`, `get_section_names()`

**Patterns**: Builder pattern (IndexBuilder), Async streaming, Factory‑style prompt construction, Separation of concerns (section generation vs. final assembly)

**Complexity**: medium

#### `vibe/cli/init/indexer.py`

**Purpose**: Provides functionality to analyze project files in chunks using an LLM, merge the chunk analyses, and build a comprehensive index describing file purposes, exports, relationships, and other metadata for the VIBE CLI initialization process.

**Exports**: `FunctionInfo`, `ClassInfo`, `FileRelationship`, `FileAnalysis`, `IndexResult`, `FILE_ANALYSIS_PROMPT`, `CHUNK_MERGE_PROMPT`, `analyze_file_chunk`, `merge_chunk_analyses`, `_parse_analysis_json` (+4 more)

**Classes**: `FunctionInfo`, `ClassInfo`, `FileRelationship`, `FileAnalysis`, `IndexResult`

**Functions**: `analyze_file_chunk()`, `merge_chunk_analyses()`, `build_index()`, `format_index_as_markdown()`

**Patterns**: Builder (constructing IndexResult), Chunking (processing large files in pieces), Factory (creating analysis objects), Adapter (LLM interface abstraction)

**Dependencies**: vibe (internal package), standard library (json, logging, dataclasses, typing, re, asyncio)

**Complexity**: medium

#### `vibe/cli/init/contracts.py`

**Purpose**: Aggregates file relationship data after indexing, builds a dependency graph, identifies hub files, and formats contracts information for the analysis markdown.

**Exports**: `DependencyEdge`, `FileNode`, `ContractsResult`, `extract_contracts`, `_normalize_import_to_path`, `_add_edge_to_graph`, `format_contracts_as_markdown`

**Classes**: `DependencyEdge`, `FileNode`, `ContractsResult`

**Functions**: `extract_contracts()`, `format_contracts_as_markdown()`

**Patterns**: Data Class, Graph Construction

**Complexity**: medium

#### `vibe/cli/init/executor.py`

**Purpose**: Coordinates the /init command workflow by discovering files, building an index, extracting glossary terms and contracts, and generating the VIBE-ANALYSIS.md report.

**Exports**: `InitProgress`, `InitResult`, `execute_init`, `format_init_summary`

**Classes**: `InitProgress`, `InitResult`

**Functions**: `execute_init()`, `format_init_summary()`

**Patterns**: Facade (orchestrator) pattern to coordinate multiple sub‑processes

**Complexity**: medium

#### `vibe/cli/init/glossary.py`

**Purpose**: Extracts glossary terms from indexed project content using an LLM, builds structured GlossaryResult objects, and formats them as markdown or prompt sections for VIBE analysis.

**Exports**: `GlossaryEntry`, `GlossaryResult`, `GLOSSARY_EXTRACTION_PROMPT`, `extract_glossary`, `_build_index_summary`, `_collect_key_concepts`, `_read_documentation`, `_parse_glossary_json`, `format_glossary_as_markdown`, `build_glossary_context_prompt`

**Classes**: `GlossaryEntry`, `GlossaryResult`

**Functions**: `extract_glossary()`, `format_glossary_as_markdown()`, `build_glossary_context_prompt()`

**Complexity**: medium

### Module: `vibe/cli/textual_ui/`

#### `vibe/cli/textual_ui/app.py`

**Purpose**: Provides the Textual UI application (VibeApp) for the VIBE CLI, managing the chat interface, user input, agent interaction, tool approvals, and configuration panels; also exposes run_textual_ui to launch the app.

**Exports**: `BottomApp`, `VibeApp`, `run_textual_ui`

**Classes**: `BottomApp`, `VibeApp`

**Functions**: `run_textual_ui()`

**Patterns**: Observer (Textual event handling), Command (CommandRegistry), Factory (widget creation), Async Task orchestration

**Dependencies**: textual

**Complexity**: medium

### Module: `vibe/cli/textual_ui/handlers/`

#### `vibe/cli/textual_ui/handlers/event_handler.py`

**Purpose**: Handles incoming event objects from the Vibe core, converting them into appropriate textual UI widgets and managing their lifecycle within the Textual interface.

**Exports**: `EventHandler`

**Classes**: `EventHandler`

**Patterns**: Callback pattern, Async event handling

**Dependencies**: textual

**Complexity**: medium

#### `vibe/cli/textual_ui/handlers/__init__.py`

**Purpose**: Provides a public API shortcut by re-exporting the EventHandler class for the textual UI handlers package.

**Exports**: `EventHandler`

**Complexity**: low

### Module: `vibe/cli/textual_ui/renderers/`

#### `vibe/cli/textual_ui/renderers/__init__.py`

**Purpose**: Re-exports the `get_renderer` function from the tool_renderers module for convenient import elsewhere in the package.

**Exports**: `get_renderer`

**Complexity**: low

#### `vibe/cli/textual_ui/renderers/tool_renderers.py`

**Purpose**: Provides renderer classes that map tool execution data to specific Textual UI widget classes and supplies a factory function to obtain the appropriate renderer based on a tool name.

**Exports**: `ToolRenderer`, `BashRenderer`, `WriteFileRenderer`, `SearchReplaceRenderer`, `TodoRenderer`, `ReadFileRenderer`, `GrepRenderer`, `get_renderer`

**Classes**: `ToolRenderer`, `BashRenderer`, `WriteFileRenderer`, `SearchReplaceRenderer`, `TodoRenderer`

**Functions**: `get_renderer()`

**Patterns**: Factory (renderer registry), Strategy (different renderer per tool type)

**Complexity**: medium

### Module: `vibe/cli/textual_ui/widgets/`

#### `vibe/cli/textual_ui/widgets/approval_app.py`

**Purpose**: Defines a Textual UI widget that displays a tool command, shows detailed information, lets the user navigate approval options, and posts messages indicating approval granted, always‑allow for the session, or rejection.

**Exports**: `ApprovalApp`

**Classes**: `ApprovalApp`

**Patterns**: Observer (via Textual Message posting), Command (action_* methods for user commands)

**Dependencies**: textual

**Complexity**: medium

#### `vibe/cli/textual_ui/widgets/loading.py`

**Purpose**: Provides a Textual UI widget that displays an animated loading spinner with gradient-colored text and occasional easter‑egg status messages.

**Exports**: `LoadingWidget`

**Classes**: `LoadingWidget`

**Patterns**: Observer (event‑driven UI updates via set_interval), Factory (creation of child Static widgets in compose)

**Dependencies**: textual

**Complexity**: medium

#### `vibe/cli/textual_ui/widgets/path_display.py`

**Purpose**: Defines a Textual widget that displays a filesystem path, shortening it with a tilde for the user's home directory.

**Exports**: `PathDisplay`

**Classes**: `PathDisplay`

**Dependencies**: textual

**Complexity**: low

#### `vibe/cli/textual_ui/widgets/mode_indicator.py`

**Purpose**: Provides a Textual UI widget that displays the current auto‑approve mode and allows toggling it via shift+tab.

**Exports**: `ModeIndicator`

**Classes**: `ModeIndicator`

**Dependencies**: textual

**Complexity**: low

#### `vibe/cli/textual_ui/widgets/tools.py`

**Purpose**: Defines Textual UI widgets for displaying tool call and result messages, handling rendering, collapsing, and error/skip states.

**Exports**: `ToolCallMessage`, `ToolResultMessage`

**Classes**: `ToolCallMessage`, `ToolResultMessage`

**Patterns**: Factory (renderer.get_result_widget returns a widget class and data), Composite (ToolResultMessage composes a result widget), Observer-like (uses async lifecycle hooks on_mount)

**Dependencies**: textual

**Complexity**: low

#### `vibe/cli/textual_ui/widgets/compact.py`

**Purpose**: Provides a UI widget that displays the progress and result of compacting conversation history, extending the blinking message behavior.

**Exports**: `CompactMessage`

**Classes**: `CompactMessage`

**Patterns**: Inheritance, Template Method (overriding get_content)

**Complexity**: low

#### `vibe/cli/textual_ui/widgets/blinking_message.py`

**Purpose**: Provides a Textual UI widget that displays a message with a blinking dot, allowing the blink to be stopped and marked as success or error.

**Exports**: `BlinkingMessage`

**Classes**: `BlinkingMessage`

**Patterns**: Observer (timer callback via set_interval), Component (UI widget composition)

**Dependencies**: textual

**Complexity**: medium

#### `vibe/cli/textual_ui/widgets/tool_widgets.py`

**Purpose**: Defines a collection of Textual UI widgets for displaying tool approval prompts and results (e.g., bash commands, file writes, search‑replace diffs, todos, file reads, grep output). Each widget formats the provided data and optionally truncates long content.

**Exports**: `ToolApprovalWidget`, `ToolResultWidget`, `BashApprovalWidget`, `BashResultWidget`, `WriteFileApprovalWidget`, `WriteFileResultWidget`, `SearchReplaceApprovalWidget`, `SearchReplaceResultWidget`, `TodoApprovalWidget`, `TodoResultWidget` (+4 more)

**Classes**: `ToolApprovalWidget`, `ToolResultWidget`, `BashApprovalWidget`, `BashResultWidget`, `WriteFileApprovalWidget`

**Patterns**: Template Method (subclass overrides compose), Inheritance hierarchy for widget specialization

**Dependencies**: textual

**Complexity**: medium

#### `vibe/cli/textual_ui/widgets/context_progress.py`

**Purpose**: Defines a dataclass to store token usage and a Textual widget that reactively displays the token usage percentage.

**Exports**: `TokenState`, `ContextProgress`

**Classes**: `TokenState`, `ContextProgress`

**Patterns**: Observer (reactive property watching), Dataclass

**Dependencies**: textual

**Complexity**: low

#### `vibe/cli/textual_ui/widgets/messages.py`

**Purpose**: Defines Textual widget classes for displaying different kinds of messages (user, assistant, command, interruption, bash output, and errors) in the Vibe CLI UI.

**Exports**: `UserMessage`, `AssistantMessage`, `UserCommandMessage`, `InterruptMessage`, `BashOutputMessage`, `ErrorMessage`

**Classes**: `UserMessage`, `AssistantMessage`, `UserCommandMessage`, `InterruptMessage`, `BashOutputMessage`

**Dependencies**: textual

**Complexity**: low

#### `vibe/cli/textual_ui/widgets/config_app.py`

**Purpose**: Provides a Textual UI widget (ConfigApp) that displays and lets the user edit core Vibe settings such as the active model and UI theme.

**Exports**: `SettingDefinition`, `THEMES`, `ConfigApp`

**Classes**: `ConfigApp`, `ConfigApp.SettingChanged`, `ConfigApp.ConfigClosed`

**Patterns**: Observer (message‑passing via Textual Message objects), Command pattern (actions bound to keys)

**Dependencies**: textual

**Complexity**: medium

#### `vibe/cli/textual_ui/widgets/welcome.py`

**Purpose**: Renders an animated welcome banner in the Textual UI, interpolating colors for several lines and the border based on configuration.

**Exports**: `hex_to_rgb`, `rgb_to_hex`, `interpolate_color`, `LineAnimationState`, `WelcomeBanner`

**Classes**: `LineAnimationState`, `WelcomeBanner`

**Functions**: `hex_to_rgb()`, `rgb_to_hex()`, `interpolate_color()`

**Patterns**: State pattern (LineAnimationState stores per‑line animation state), Observer pattern (timer callback via set_interval reacts to time changes), Factory‑like creation of colour strings using interpolation functions

**Dependencies**: rich, textual

**Complexity**: medium

### Module: `vibe/cli/textual_ui/widgets/chat_input/`

#### `vibe/cli/textual_ui/widgets/chat_input/completion_popup.py`

**Purpose**: Defines a UI widget that displays a popup list of completion suggestions in the textual chat input interface.

**Exports**: `CompletionPopup`

**Classes**: `CompletionPopup`

**Dependencies**: rich, textual

**Complexity**: low

#### `vibe/cli/textual_ui/widgets/chat_input/body.py`

**Purpose**: Provides a Textual widget that manages the chat input area, handling user input, history navigation, prompt updates, and submission events.

**Exports**: `ChatInputBody`

**Classes**: `ChatInputBody`, `ChatInputBody.Submitted`

**Patterns**: Observer (event‑driven message handling), Callback (completion reset)

**Dependencies**: textual

**Complexity**: medium

#### `vibe/cli/textual_ui/widgets/chat_input/__init__.py`

**Purpose**: Re-exports the main chat input widget classes for easy import elsewhere in the project.

**Exports**: `ChatInputBody`, `ChatInputContainer`, `ChatTextArea`

**Complexity**: low

#### `vibe/cli/textual_ui/widgets/chat_input/container.py`

**Purpose**: Defines the ChatInputContainer widget for the Textual UI, handling user input, history, autocompletion (slash commands and file paths), and rendering of completion suggestions.

**Exports**: `ChatInputContainer`

**Classes**: `ChatInputContainer`, `ChatInputContainer.Submitted`

**Patterns**: Observer (via Textual Message system), Composition (building UI from smaller widgets)

**Dependencies**: textual

**Complexity**: medium

#### `vibe/cli/textual_ui/widgets/chat_input/text_area.py`

**Purpose**: Provides a custom TextArea widget for the chat UI that handles message submission, history navigation, and autocompletion integration.

**Exports**: `ChatTextArea`

**Classes**: `ChatTextArea`

**Patterns**: Observer (message passing via post_message), Command (bindings for key actions), State Machine (history navigation state)

**Dependencies**: textual

**Complexity**: medium

#### `vibe/cli/textual_ui/widgets/chat_input/completion_manager.py`

**Purpose**: Defines a protocol for autocompletion controllers and a manager that selects and delegates to the appropriate controller based on the current text input.

**Exports**: `CompletionController`, `MultiCompletionManager`

**Classes**: `CompletionController`, `MultiCompletionManager`

**Patterns**: Chain of Responsibility, Strategy (via Protocol interface)

**Dependencies**: textual

**Complexity**: low

### Module: `vibe/cli/update_notifier/`

#### `vibe/cli/update_notifier/version_update.py`

**Purpose**: Provides functionality to check for newer software versions, using a cache and a gateway, and returns an availability object indicating whether a notification should be shown.

**Exports**: `VersionUpdateAvailability`, `VersionUpdateError`, `UPDATE_CACHE_TTL_SECONDS`, `get_update_if_available`

**Classes**: `VersionUpdateAvailability`, `VersionUpdateError`

**Functions**: `get_update_if_available()`

**Patterns**: Repository pattern (UpdateCacheRepository), Gateway pattern (VersionUpdateGateway), Cache‑aside pattern, Async/await for I/O

**Dependencies**: packaging

**Complexity**: medium

#### `vibe/cli/update_notifier/__init__.py`

**Purpose**: Provides a public API for the update_notifier package by importing and re‑exporting key classes, functions, and constants.

**Exports**: `DEFAULT_GATEWAY_MESSAGES`, `FileSystemUpdateCacheRepository`, `GitHubVersionUpdateGateway`, `PyPIVersionUpdateGateway`, `UpdateCache`, `UpdateCacheRepository`, `VersionUpdate`, `VersionUpdateAvailability`, `VersionUpdateError`, `VersionUpdateGateway` (+3 more)

**Patterns**: Facade, Aggregator

**Complexity**: low

### Module: `vibe/cli/update_notifier/adapters/`

#### `vibe/cli/update_notifier/adapters/filesystem_update_cache_repository.py`

**Purpose**: Provides a filesystem‑based implementation of the UpdateCacheRepository interface, allowing the update notifier to persist and retrieve cached version information in a JSON file.

**Exports**: `FileSystemUpdateCacheRepository`

**Classes**: `FileSystemUpdateCacheRepository`

**Patterns**: Repository, Adapter

**Complexity**: low

#### `vibe/cli/update_notifier/adapters/pypi_version_update_gateway.py`

**Purpose**: Implements a gateway that queries the PyPI simple API to determine the latest non‑yanked version of a package.

**Exports**: `PyPIVersionUpdateGateway`, `_parse_filename_version`

**Classes**: `PyPIVersionUpdateGateway`

**Patterns**: Adapter, Strategy

**Dependencies**: httpx, packaging

**Complexity**: medium

#### `vibe/cli/update_notifier/adapters/github_version_update_gateway.py`

**Purpose**: Implements a gateway that queries the GitHub releases API to determine the latest non‑prerelease, non‑draft version of a repository.

**Exports**: `GitHubVersionUpdateGateway`, `_extract_version`

**Classes**: `GitHubVersionUpdateGateway`

**Patterns**: Adapter, Gateway

**Dependencies**: httpx

**Complexity**: medium

### Module: `vibe/cli/update_notifier/ports/`

#### `vibe/cli/update_notifier/ports/update_cache_repository.py`

**Purpose**: Defines a dataclass for storing update cache information and a protocol interface for a repository that can get and set this cache asynchronously.

**Exports**: `UpdateCache`, `UpdateCacheRepository`

**Classes**: `UpdateCache`, `UpdateCacheRepository`

**Patterns**: Dataclass, Protocol (interface)

**Complexity**: low

#### `vibe/cli/update_notifier/ports/version_update_gateway.py`

**Purpose**: Defines the data structures and protocol for fetching version update information, including a dataclass for the version, an enum for error causes, default messages, a custom exception, and an async protocol interface.

**Exports**: `VersionUpdate`, `VersionUpdateGatewayCause`, `DEFAULT_GATEWAY_MESSAGES`, `VersionUpdateGatewayError`, `VersionUpdateGateway`

**Classes**: `VersionUpdate`, `VersionUpdateGatewayCause`, `VersionUpdateGatewayError`, `VersionUpdateGateway`

**Patterns**: Protocol (interface) pattern, Enum for error codes, Dataclass for immutable value objects

**Complexity**: low

### Module: `vibe/core/`

#### `vibe/core/context_injector.py`

**Purpose**: Provides intelligent context injection by scanning VIBE-ANALYSIS JSON index, extracting relevant markdown excerpts, and synthesizing a focused context summary using an LLM.

**Exports**: `RelevantItem`, `ContextResult`, `ContextInjector`, `format_context_for_injection`, `format_context_for_enhancement`

**Classes**: `RelevantItem`, `ContextResult`, `ContextInjector`

**Functions**: `format_context_for_injection()`, `format_context_for_enhancement()`

**Complexity**: medium

#### `vibe/core/config.py`

**Purpose**: Defines the configuration schema and loading/saving logic for the Vibe application, including providers, models, prompts, MCP servers, and runtime settings.

**Exports**: `PROJECT_DOC_FILENAMES`, `load_api_keys_from_env`, `MissingAPIKeyError`, `MissingPromptFileError`, `WrongBackendError`, `TomlFileSettingsSource`, `ProjectContextConfig`, `SessionLoggingConfig`, `Backend`, `ProviderConfig` (+10 more)

**Classes**: `MissingAPIKeyError`, `MissingPromptFileError`, `WrongBackendError`, `TomlFileSettingsSource`, `ProjectContextConfig`

**Functions**: `load_api_keys_from_env()`

**Patterns**: Factory (custom settings source), Validator (Pydantic field/model validators), Builder (deep_merge for config updates), Singleton-like global configuration (VibeConfig accessed via class methods)

**Dependencies**: python-dotenv, pydantic, pydantic-settings, tomli-w

**Complexity**: medium

#### `vibe/core/interaction_logger.py`

**Purpose**: Provides functionality to log interactions of a Vibe agent session to JSON files, managing session metadata, saving interaction data, and locating previous sessions.

**Exports**: `InteractionLogger`

**Classes**: `InteractionLogger`

**Patterns**: Static method helper pattern, Builder‑like pattern for assembling session metadata

**Dependencies**: aiofiles

**Complexity**: medium

#### `vibe/core/system_prompt.py`

**Purpose**: Provides utilities to build a system prompt that includes project directory structure, git status, and user instructions, and assembles the universal system prompt for the Vibe agent.

**Exports**: `ProjectContextProvider`, `get_universal_system_prompt`

**Classes**: `ProjectContextProvider`

**Functions**: `get_universal_system_prompt()`

**Patterns**: Factory (building prompt strings from multiple optional sections), Template Method (subclass‑agnostic prompt assembly using UtilityPrompt templates)

**Complexity**: medium

#### `vibe/core/__init__.py`

**Purpose**: Exports package metadata and re-exports the `run_programmatic` function for external use.

**Exports**: `__version__`, `run_programmatic`

**Complexity**: low

#### `vibe/core/types.py`

**Purpose**: Defines core data structures, enums, and type aliases used throughout the Vibe agent system such as session info, LLM messages, tool calls, and event models.

**Exports**: `ResumeSessionInfo`, `AgentStats`, `SessionInfo`, `SessionMetadata`, `StrToolChoice`, `AvailableFunction`, `AvailableTool`, `FunctionCall`, `ToolCall`, `Content` (+15 more)

**Classes**: `ResumeSessionInfo`, `AgentStats`, `SessionInfo`, `SessionMetadata`, `AvailableFunction`

**Patterns**: Dataclass, Pydantic Model, Enum (StrEnum), Callback (async/sync) pattern, Type alias (Annotated, Literal), Factory via model_validator

**Dependencies**: pydantic

**Complexity**: medium

#### `vibe/core/config_path.py`

**Purpose**: Provides a lazy path resolver via the ConfigPath class and defines project-wide path constants for configuration, logs, tools, and other resources.

**Exports**: `ConfigPath`, `_get_vibe_home`, `_resolve_config_file`, `resolve_local_tools_dir`, `VIBE_HOME`, `GLOBAL_CONFIG_FILE`, `GLOBAL_ENV_FILE`, `GLOBAL_TOOLS_DIR`, `SESSION_LOG_DIR`, `CONFIG_FILE` (+7 more)

**Classes**: `ConfigPath`

**Functions**: `_get_vibe_home()`, `_resolve_config_file()`, `resolve_local_tools_dir()`

**Patterns**: Lazy evaluation, Factory (using lambdas to create ConfigPath instances), Singleton‑like global configuration objects

**Complexity**: low

#### `vibe/core/utils.py`

**Purpose**: Provides core utility helpers for Vibe, including tagged text handling, cancellation utilities, logging setup, user‑agent generation, async retry decorators, and synchronous execution of async coroutines.

**Exports**: `CANCELLATION_TAG`, `TOOL_ERROR_TAG`, `VIBE_STOP_EVENT_TAG`, `VIBE_WARNING_TAG`, `KNOWN_TAGS`, `TaggedText`, `CancellationReason`, `ConversationLimitException`, `get_user_cancellation_message`, `is_user_cancellation_event` (+8 more)

**Classes**: `TaggedText`, `CancellationReason`, `ConversationLimitException`

**Functions**: `get_user_cancellation_message()`, `is_user_cancellation_event()`, `is_dangerous_directory()`, `get_user_agent()`, `async_retry()`, `async_generator_retry()`, `run_sync()`, `is_windows()`

**Patterns**: Decorator (retry logic), Factory (decorator factory), Singleton-like global logger, Enum for domain constants

**Dependencies**: httpx

**Complexity**: medium

#### `vibe/core/agent.py`

**Purpose**: Implements the Agent class that orchestrates a conversational loop with an LLM, handling middleware, tool execution, streaming, context management and logging.

**Exports**: `ToolExecutionResponse`, `ToolDecision`, `AgentError`, `AgentStateError`, `LLMResponseError`, `Agent`

**Classes**: `ToolExecutionResponse`, `ToolDecision`, `AgentError`, `AgentStateError`, `LLMResponseError`

**Patterns**: Factory (backend selection via BACKEND_FACTORY), Middleware/Chain‑of‑Responsibility (MiddlewarePipeline), Observer (message_observer callback), Command (tool call handling), Async Generator (streaming events)

**Dependencies**: pydantic

**Complexity**: high

#### `vibe/core/programmatic.py`

**Purpose**: Executes a user prompt in programmatic mode using a Vibe Agent and returns the assistant's final response.

**Exports**: `run_programmatic`

**Functions**: `run_programmatic()`

**Patterns**: Factory, Observer

**Complexity**: medium

#### `vibe/core/output_formatters.py`

**Purpose**: Defines abstract and concrete output formatter classes for text, JSON, and streaming JSON output, and provides a factory function to create the appropriate formatter based on an OutputFormat enum.

**Exports**: `OutputFormatter`, `TextOutputFormatter`, `JsonOutputFormatter`, `StreamingJsonOutputFormatter`, `create_formatter`

**Classes**: `OutputFormatter`, `TextOutputFormatter`, `JsonOutputFormatter`, `StreamingJsonOutputFormatter`

**Functions**: `create_formatter()`

**Patterns**: Factory, Strategy

**Complexity**: low

#### `vibe/core/middleware.py`

**Purpose**: Defines middleware actions, results, various middleware implementations (turn limit, price limit, auto‑compact, context warning), a middleware pipeline, and a context‑injection middleware that enhances LLM responses with relevant codebase context.

**Exports**: `MiddlewareAction`, `ResetReason`, `ConversationContext`, `MiddlewareResult`, `ConversationMiddleware`, `TurnLimitMiddleware`, `PriceLimitMiddleware`, `AutoCompactMiddleware`, `ContextWarningMiddleware`, `MiddlewarePipeline` (+1 more)

**Classes**: `MiddlewareAction`, `ResetReason`, `ConversationContext`, `MiddlewareResult`, `ConversationMiddleware`

**Patterns**: Chain of Responsibility (middleware pipeline), Protocol for defining a middleware interface, Lazy initialization (deferred ContextInjector creation), Factory‑style addition of middleware via add()

**Complexity**: medium

### Module: `vibe/core/autocompletion/`

#### `vibe/core/autocompletion/fuzzy.py`

**Purpose**: Provides fuzzy string matching utilities with scoring based on prefix, word boundary, consecutive and subsequence matches.

**Exports**: `PREFIX_MULTIPLIER`, `WORD_BOUNDARY_MULTIPLIER`, `CONSECUTIVE_MULTIPLIER`, `MatchResult`, `fuzzy_match`

**Classes**: `MatchResult`

**Functions**: `fuzzy_match()`

**Patterns**: Chain of Responsibility (trying multiple matcher strategies sequentially), Functional decomposition

**Complexity**: medium

#### `vibe/core/autocompletion/path_prompt_adapter.py`

**Purpose**: Converts a path‑based autocompletion payload into a formatted text prompt, optionally embedding small text files directly in the prompt.

**Exports**: `DEFAULT_MAX_EMBED_BYTES`, `ResourceBlock`, `BINARY_MIME_PREFIXES`, `render_path_prompt`, `_path_prompt_to_content_blocks`, `_try_embed_text_resource`, `_content_blocks_to_prompt_text`, `_format_content_block`, `_is_probably_text`

**Functions**: `render_path_prompt()`

**Patterns**: Structural pattern matching (match‑case)

**Dependencies**: Standard Library (collections, mimetypes, pathlib, __future__)

**Complexity**: medium

#### `vibe/core/autocompletion/path_prompt.py`

**Purpose**: Parses a text message for @‑prefixed filesystem paths, resolves them against a base directory, deduplicates the resulting resources, and returns a structured payload for autocompletion.

**Exports**: `PathResource`, `PathPromptPayload`, `build_path_prompt_payload`

**Classes**: `PathResource`, `PathPromptPayload`

**Functions**: `build_path_prompt_payload()`

**Complexity**: medium

#### `vibe/core/autocompletion/completers.py`

**Purpose**: Provides a set of autocompletion classes for command aliases, filesystem paths, and composition of multiple completers.

**Exports**: `DEFAULT_MAX_ENTRIES_TO_PROCESS`, `DEFAULT_TARGET_MATCHES`, `Completer`, `CommandCompleter`, `PathCompleter`, `MultiCompleter`

**Classes**: `Completer`, `CommandCompleter`, `PathCompleter`, `MultiCompleter`

**Patterns**: Composite (MultiCompleter aggregates other Completers), Template Method (Completer defines the interface that subclasses implement)

**Complexity**: medium

### Module: `vibe/core/autocompletion/file_indexer/`

#### `vibe/core/autocompletion/file_indexer/store.py`

**Purpose**: Provides an in‑memory store for file index entries used by the autocompletion system, supporting full rebuilds, snapshots and incremental updates while respecting ignore rules.

**Exports**: `FileIndexStats`, `IndexEntry`, `FileIndexStore`

**Classes**: `FileIndexStats`, `IndexEntry`, `FileIndexStore`

**Patterns**: Factory method (via _create_entry), Lazy caching (ordered snapshot built on demand), Repository‑like storage

**Complexity**: medium

#### `vibe/core/autocompletion/file_indexer/ignore_rules.py`

**Purpose**: Provides ignore rule handling for file indexing, including default patterns and .gitignore parsing, and determines whether a given path should be ignored.

**Exports**: `DEFAULT_IGNORE_PATTERNS`, `CompiledPattern`, `IgnoreRules`

**Classes**: `CompiledPattern`, `IgnoreRules`

**Complexity**: low

#### `vibe/core/autocompletion/file_indexer/__init__.py`

**Purpose**: Provides a convenient public interface for the file indexer package by re‑exporting core classes (FileIndexer, FileIndexStore, FileIndexStats, IndexEntry).

**Exports**: `FileIndexStats`, `FileIndexStore`, `FileIndexer`, `IndexEntry`

**Patterns**: Facade (re‑export) pattern

**Complexity**: low

#### `vibe/core/autocompletion/file_indexer/indexer.py`

**Purpose**: Manages a file index for autocompletion, handling background rebuilding, watching for filesystem changes, and applying ignore rules.

**Exports**: `FileIndexer`

**Classes**: `_RebuildTask`, `FileIndexer`

**Patterns**: Observer (watcher callbacks), Worker Thread (ThreadPoolExecutor for background rebuild), Command (encapsulating rebuild actions in _RebuildTask), Locking (RLock to protect shared state)

**Complexity**: medium

#### `vibe/core/autocompletion/file_indexer/watcher.py`

**Purpose**: Provides a WatchController class that runs a background thread to monitor filesystem changes under a given root directory using the watchfiles library and forwards those changes to a user‑provided callback.

**Exports**: `WatchController`

**Classes**: `WatchController`

**Patterns**: Observer (callback on change), Thread worker

**Dependencies**: watchfiles

**Complexity**: medium

### Module: `vibe/core/llm/`

#### `vibe/core/llm/format.py`

**Purpose**: Provides utilities to filter active tool classes and defines data models plus a handler for formatting and processing API‑style tool calls in the Vibe LLM framework.

**Exports**: `_is_regex_hint`, `_compile_icase`, `_regex_match_icase`, `_name_matches`, `get_active_tool_classes`, `ParsedToolCall`, `ResolvedToolCall`, `FailedToolCall`, `ParsedMessage`, `ResolvedMessage` (+1 more)

**Classes**: `ParsedToolCall`, `ResolvedToolCall`, `FailedToolCall`, `ParsedMessage`, `ResolvedMessage`

**Functions**: `get_active_tool_classes()`

**Patterns**: Factory (APIToolFormatHandler creates tool‑related messages), Strategy (different format handlers could be swapped), Cache (lru_cache for compiled regexes), Data‑validation (Pydantic models)

**Dependencies**: pydantic

**Complexity**: medium

#### `vibe/core/llm/types.py`

**Purpose**: Defines the BackendLike protocol that specifies the interface for injectable LLM backend implementations.

**Exports**: `BackendLike`

**Classes**: `BackendLike`

**Patterns**: Protocol (interface), Dependency Injection, Async Context Manager

**Dependencies**: collections.abc, types, typing

**Complexity**: medium

#### `vibe/core/llm/exceptions.py`

**Purpose**: Defines custom exception and helper classes for handling errors returned by LLM provider back‑ends, including parsing error responses and summarizing request payloads.

**Exports**: `ErrorDetail`, `PayloadSummary`, `BackendError`, `ErrorResponse`, `BackendErrorBuilder`

**Classes**: `ErrorDetail`, `PayloadSummary`, `BackendError`, `ErrorResponse`, `BackendErrorBuilder`

**Patterns**: Factory, Builder

**Dependencies**: httpx, pydantic

**Complexity**: medium

### Module: `vibe/core/llm/backend/`

#### `vibe/core/llm/backend/mistral.py`

**Purpose**: Provides a backend implementation for interacting with Mistral LLM APIs, mapping internal message formats to the Mistral SDK, handling synchronous and streaming completions, and counting tokens.

**Exports**: `MistralMapper`, `MistralBackend`

**Classes**: `MistralMapper`, `MistralBackend`

**Patterns**: Adapter (mapper between internal types and SDK types), Mapper (MistralMapper), Async Context Manager (via __aenter__/__aexit__), Factory (creation of Mistral client instance)

**Dependencies**: httpx, mistralai

**Complexity**: medium

#### `vibe/core/llm/backend/generic.py`

**Purpose**: Implements a generic LLM backend that can send completion requests (including streaming) to different providers via registered adapters, handling request construction, response parsing, error handling, and token counting.

**Exports**: `PreparedRequest`, `APIAdapter`, `register_adapter`, `OpenAIAdapter`, `GenericBackend`, `BACKEND_ADAPTERS`, `T`

**Classes**: `PreparedRequest`, `APIAdapter`, `OpenAIAdapter`, `GenericBackend`

**Functions**: `register_adapter()`

**Patterns**: Factory (adapter registration), Strategy (different adapters selected at runtime), Decorator (register_adapter)

**Dependencies**: httpx

**Complexity**: medium

#### `vibe/core/llm/backend/factory.py`

**Purpose**: Defines a factory mapping Backend enum values to their corresponding backend implementation classes.

**Exports**: `BACKEND_FACTORY`

**Patterns**: Factory

**Complexity**: low

### Module: `vibe/core/llm/backend/watsonx/`

#### `vibe/core/llm/backend/watsonx/auth.py`

**Purpose**: Provides an async httpx authentication handler for IBM WatsonX that automatically obtains, caches, and refreshes IAM tokens with proactive and reactive strategies.

**Exports**: `WatsonXAuth`, `WatsonXAuthError`, `TokenData`, `HTTP_UNAUTHORIZED`

**Classes**: `WatsonXAuthError`, `TokenData`, `WatsonXAuth`

**Patterns**: Async context manager, Double‑check locking, Retry with exponential backoff (tenacity), Strategy pattern for proactive/reactive token refresh, Adapter pattern (httpx.Auth implementation)

**Dependencies**: httpx, tenacity

**Complexity**: medium

#### `vibe/core/llm/backend/watsonx/backend.py`

**Purpose**: Provides an adapter backend that allows the Vibe framework to communicate with IBM WatsonX LLMs, emulating native tool‑calling through prompt engineering and handling retries, response parsing, and token counting.

**Exports**: `WatsonXBackendError`, `ToolParsingError`, `EmptyResponseError`, `WatsonXBackend`, `WATSONX_API_VERSION`, `DEFAULT_MAX_TOKENS`, `DEFAULT_TIMEOUT`, `HTTP_SERVER_ERROR_MIN`, `HTTP_SERVER_ERROR_MAX`

**Classes**: `WatsonXBackendError`, `ToolParsingError`, `EmptyResponseError`, `WatsonXBackend`

**Patterns**: Adapter pattern (WatsonXBackend adapts WatsonX API to Vibe interface), Retry pattern with exponential backoff (tenacity), Context manager for resource handling (__aenter__/__aexit__), Factory‑style request building

**Dependencies**: httpx, tenacity

**Complexity**: medium

#### `vibe/core/llm/backend/watsonx/models.py`

**Purpose**: Provides a service to discover and retrieve available WatsonX foundation models via the WatsonX API, exposing a convenience async function for callers.

**Exports**: `WATSONX_API_VERSION`, `DEFAULT_TIMEOUT`, `WatsonXModel`, `WatsonXModelService`, `fetch_watsonx_models`

**Classes**: `WatsonXModel`, `WatsonXModelService`

**Functions**: `fetch_watsonx_models()`

**Patterns**: Retry, Service, Async

**Dependencies**: httpx, tenacity

**Complexity**: medium

#### `vibe/core/llm/backend/watsonx/__init__.py`

**Purpose**: Exports key WatsonX LLM backend components (authentication, backend class, models, and helper functions) for easy import elsewhere in the project.

**Exports**: `WatsonXAuth`, `WatsonXBackend`, `WatsonXModel`, `WatsonXModelService`, `fetch_watsonx_models`

**Complexity**: low

### Module: `vibe/core/prompts/`

#### `vibe/core/prompts/__init__.py`

**Purpose**: Defines enumeration classes for prompt identifiers and provides utilities to locate and read the corresponding markdown prompt files.

**Exports**: `SystemPrompt`, `UtilityPrompt`

**Classes**: `Prompt`, `SystemPrompt`, `UtilityPrompt`

**Patterns**: Enum (StrEnum) pattern

**Complexity**: low

### Module: `vibe/core/tools/`

#### `vibe/core/tools/ui.py`

**Purpose**: Provides data models and an adapter to generate UI display information for tool call and result events within the Vibe framework.

**Exports**: `ToolCallDisplay`, `ToolResultDisplay`, `ToolUIData`, `ToolUIDataAdapter`

**Classes**: `ToolCallDisplay`, `ToolResultDisplay`, `ToolUIData`, `ToolUIDataAdapter`

**Patterns**: Adapter, Protocol/Interface

**Dependencies**: pydantic

**Complexity**: low

#### `vibe/core/tools/mcp.py`

**Purpose**: Defines models and factory functions to create proxy tools that call remote MCP tools via HTTP or stdio, handling result parsing and UI display.

**Exports**: `MCPToolResult`, `RemoteTool`, `list_tools_http`, `call_tool_http`, `create_mcp_http_proxy_tool_class`, `list_tools_stdio`, `call_tool_stdio`, `create_mcp_stdio_proxy_tool_class`

**Classes**: `_OpenArgs`, `MCPToolResult`, `RemoteTool`, `_MCPContentBlock`, `_MCPResultIn`

**Functions**: `list_tools_http()`, `call_tool_http()`, `create_mcp_http_proxy_tool_class()`, `list_tools_stdio()`, `call_tool_stdio()`, `create_mcp_stdio_proxy_tool_class()`

**Patterns**: Factory (create_mcp_*_proxy_tool_class), Proxy/Adapter (proxy tool classes forwarding calls), Dynamic class generation

**Dependencies**: mcp, pydantic

**Complexity**: medium

#### `vibe/core/tools/manager.py`

**Purpose**: Provides a ToolManager class that discovers, registers, and lazily instantiates tool implementations (including built‑in and remote MCP tools) for an Agent.

**Exports**: `NoSuchToolError`, `DEFAULT_TOOL_DIR`, `ToolManager`

**Classes**: `NoSuchToolError`, `ToolManager`

**Patterns**: Factory, Registry, Lazy Initialization, Proxy (via generated MCP proxy classes)

**Complexity**: medium

#### `vibe/core/tools/base.py`

**Purpose**: Defines the generic abstract base class infrastructure for tools, including configuration, state handling, permission logic, and utilities for argument validation and prompt loading.

**Exports**: `ARGS_COUNT`, `ToolError`, `ToolInfo`, `ToolPermissionError`, `ToolPermission`, `BaseToolConfig`, `BaseToolState`, `BaseTool`

**Classes**: `ToolError`, `ToolInfo`, `ToolPermissionError`, `ToolPermission`, `BaseToolConfig`

**Patterns**: Abstract Base Class (ABC), Template Method (run / invoke pattern), Factory Method (from_config), Memoization (functools.cache on get_tool_prompt), Enum-based Strategy (ToolPermission)

**Dependencies**: pydantic

**Complexity**: medium

### Module: `vibe/core/tools/builtins/`

#### `vibe/core/tools/builtins/search_replace.py`

**Purpose**: Implements the SearchReplace tool that patches files based on SEARCH/REPLACE blocks with optional fuzzy matching and detailed error reporting.

**Exports**: `_BLOCK_RE`, `_BLOCK_WITH_FENCE_RE`, `SearchReplaceBlock`, `FuzzyMatch`, `BlockApplyResult`, `SearchReplaceArgs`, `SearchReplaceResult`, `SearchReplaceConfig`, `SearchReplaceState`, `SearchReplace`

**Classes**: `SearchReplaceBlock`, `FuzzyMatch`, `BlockApplyResult`, `SearchReplaceArgs`, `SearchReplaceResult`

**Patterns**: Template Method (run method orchestrates a series of hook methods), Factory (tool instantiated via BaseTool subclassing), Strategy (fuzzy‑matching algorithm selectable via config)

**Dependencies**: aiofiles, pydantic

**Complexity**: medium

#### `vibe/core/tools/builtins/bash.py`

**Purpose**: Implements a Bash tool that safely runs one‑off shell commands, enforcing allow/deny lists and handling timeouts, output capture, and error reporting.

**Exports**: `Bash`, `BashArgs`, `BashResult`, `BashToolConfig`

**Classes**: `BashToolConfig`, `BashArgs`, `BashResult`, `Bash`

**Patterns**: Template Method (run overrides BaseTool.run), Factory/Builder (configuration objects constructed via Pydantic models), Strategy (allowlist/denylist decision encapsulated in check_allowlist_denylist)

**Dependencies**: pydantic

**Complexity**: medium

#### `vibe/core/tools/builtins/grep.py`

**Purpose**: Implements a Vibe core tool that recursively searches files for a regex pattern using ripgrep (rg) or GNU grep, with support for exclusion patterns, timeouts, and result truncation.

**Exports**: `GrepBackend`, `GrepToolConfig`, `GrepState`, `GrepArgs`, `GrepResult`, `Grep`

**Classes**: `GrepBackend`, `GrepToolConfig`, `GrepState`, `GrepArgs`, `GrepResult`

**Patterns**: Strategy (different command builders per backend), Factory (backend detection), Template Method (run orchestrates steps), Async I/O

**Dependencies**: pydantic

**Complexity**: medium

#### `vibe/core/tools/builtins/read_file.py`

**Purpose**: Provides a tool that safely reads a UTF-8 file, returning lines from a specified offset with optional line limit and a byte‑size cap, while keeping a short history of recently read files.

**Exports**: `_ReadResult`, `ReadFileArgs`, `ReadFileResult`, `ReadFileToolConfig`, `ReadFileState`, `ReadFile`

**Classes**: `_ReadResult`, `ReadFileArgs`, `ReadFileResult`, `ReadFileToolConfig`, `ReadFileState`

**Patterns**: Template Method (run overridden from BaseTool), Async I/O (aiofiles), Data Validation with Pydantic

**Dependencies**: aiofiles, pydantic

**Complexity**: medium

#### `vibe/core/tools/builtins/todo.py`

**Purpose**: Provides a Todo management tool that can read or write a list of todos, exposing configuration, state, and UI display logic.

**Exports**: `TodoStatus`, `TodoPriority`, `TodoItem`, `TodoArgs`, `TodoResult`, `TodoConfig`, `TodoState`, `Todo`

**Classes**: `TodoStatus`, `TodoPriority`, `TodoItem`, `TodoArgs`, `TodoResult`

**Patterns**: Mixin, Template Method, Factory Method

**Dependencies**: pydantic

**Complexity**: medium

#### `vibe/core/tools/builtins/write_file.py`

**Purpose**: Implements the WriteFile tool that creates or overwrites UTF-8 files within the project's working directory, handling validation, permissions, and recent write tracking.

**Exports**: `WriteFileArgs`, `WriteFileResult`, `WriteFileConfig`, `WriteFileState`, `WriteFile`

**Classes**: `WriteFileArgs`, `WriteFileResult`, `WriteFileConfig`, `WriteFileState`, `WriteFile`

**Patterns**: Command pattern (tool as executable command), Template Method (run method defined by base class), Factory/Generic pattern (BaseTool generic inheritance)

**Dependencies**: aiofiles, pydantic

**Complexity**: medium

### Module: `vibe/setup/onboarding/`

#### `vibe/setup/onboarding/__init__.py`

**Purpose**: Defines the Textual onboarding application for the Vibe CLI, installs the onboarding screens, runs the onboarding flow, and applies the selected provider and model to the Vibe configuration.

**Exports**: `OnboardingApp`, `run_onboarding`, `_apply_provider_config`, `_ensure_model_in_config`

**Classes**: `OnboardingApp`

**Functions**: `run_onboarding()`

**Patterns**: Match‑case control flow (Python structural pattern matching), Screen‑based UI navigation (Textual framework)

**Dependencies**: rich, textual

**Complexity**: medium

#### `vibe/setup/onboarding/base.py`

**Purpose**: Defines a base onboarding screen class that provides navigation actions for the onboarding flow.

**Exports**: `OnboardingScreen`

**Classes**: `OnboardingScreen`

**Dependencies**: textual

**Complexity**: low

### Module: `vibe/setup/onboarding/screens/`

#### `vibe/setup/onboarding/screens/watsonx_setup.py`

**Purpose**: Provides a Textual onboarding screen to collect and persist WatsonX API key, project ID, and region configuration.

**Exports**: `WATSONX_REGIONS`, `WATSONX_DOCS_URL`, `WATSONX_CONSOLE_URL`, `UUID_LENGTH`, `_save_env_value`, `WatsonXSetupScreen`

**Classes**: `WatsonXSetupScreen`

**Patterns**: Event‑driven UI (Observer pattern via Textual event handlers), Command pattern for screen navigation (push_screen)

**Dependencies**: python-dotenv, textual

**Complexity**: medium

#### `vibe/setup/onboarding/screens/model_selection.py`

**Purpose**: Provides an onboarding screen that lets the user select a LLM model from the configured provider (currently WatsonX) by dynamically fetching the model list and displaying it in a Textual UI.

**Exports**: `ModelSelectionScreen`, `MAX_DESC_LENGTH`

**Classes**: `ModelSelectionScreen`

**Patterns**: Observer (event handling), Command (action methods), Factory (dynamic Option creation)

**Dependencies**: textual

**Complexity**: medium

#### `vibe/setup/onboarding/screens/__init__.py`

**Purpose**: Aggregates and re‑exports onboarding screen classes for easy import elsewhere in the project.

**Exports**: `ApiKeyScreen`, `ModelSelectionScreen`, `ProviderSelectionScreen`, `ThemeSelectionScreen`, `WatsonXSetupScreen`, `WelcomeScreen`

**Patterns**: Facade

**Complexity**: low

#### `vibe/setup/onboarding/screens/provider_selection.py`

**Purpose**: Provides an onboarding screen that lets the user select an LLM provider and navigates to the appropriate next configuration screen.

**Exports**: `ProviderSelectionScreen`, `PROVIDERS`

**Classes**: `ProviderSelectionScreen`

**Patterns**: Command pattern (Textual action bindings), Factory-like navigation (selecting next screen based on provider)

**Dependencies**: textual

**Complexity**: low

#### `vibe/setup/onboarding/screens/api_key.py`

**Purpose**: Provides an onboarding screen that prompts the user to enter their provider API key, validates it, and saves it to the project's .env file.

**Exports**: `ApiKeyScreen`, `_save_api_key_to_env_file`, `PROVIDER_HELP`, `CONFIG_DOCS_URL`

**Classes**: `ApiKeyScreen`

**Patterns**: Observer (event‑handler methods like on_input_changed, on_mouse_up), Factory (compose method builds the UI hierarchy)

**Dependencies**: python-dotenv, textual

**Complexity**: medium

#### `vibe/setup/onboarding/screens/welcome.py`

**Purpose**: Defines the WelcomeScreen onboarding view with animated gradient typing effect for the welcome message and a press‑Enter hint.

**Exports**: `WELCOME_PREFIX`, `WELCOME_HIGHLIGHT`, `WELCOME_SUFFIX`, `WELCOME_TEXT`, `HIGHLIGHT_START`, `HIGHLIGHT_END`, `BUTTON_TEXT`, `GRADIENT_COLORS`, `_apply_gradient`, `WelcomeScreen`

**Classes**: `WelcomeScreen`

**Patterns**: Command pattern via Textual bindings, Timer‑driven animation (state‑machine like behaviour)

**Dependencies**: textual

**Complexity**: medium

#### `vibe/setup/onboarding/screens/theme_selection.py`

**Purpose**: Provides the onboarding screen that lets the user select a Textual UI theme, shows a preview, and saves the chosen theme to the Vibe configuration.

**Exports**: `ThemeSelectionScreen`, `THEMES`, `VISIBLE_NEIGHBORS`, `FADE_CLASSES`, `PREVIEW_MARKDOWN`

**Classes**: `ThemeSelectionScreen`

**Patterns**: Observer (event handling via on_* methods), Command (action_* methods mapped to key bindings), Template Method (compose method defines UI structure for subclass)

**Dependencies**: textual

**Complexity**: medium


---

## Glossary

*38 terms defined*


### Acronyms

- **ACP**: Agent Communication Protocol – internal protocol used for communication between the Vibe agent and tools/services.
- **API**: Application Programming Interface – the set of HTTP endpoints exposed by Mistral models and external services.
- **CD**: Continuous Delivery – pipeline that packages and publishes the project after successful CI.
- **CI**: Continuous Integration – automated process that runs tests and builds on each commit.
- **CLI**: Command‑Line Interface – the textual entry point for interacting with Mistral Vibe via the terminal.
- **SDK**: Software Development Kit – collections of helper classes (e.g., Mistral SDK) used to talk to model APIs.
- **TUI**: Textual User Interface – terminal‑based UI built with the Textual framework.
- **UI**: User Interface – the interactive front‑end of the Vibe application (either TUI or future GUI).


### Domain Terms

- **async generator**: An async function that yields values over time, used for streaming LLM events or file chunks.
- **backend selection**: Strategy pattern that chooses the concrete implementation (e.g., Mistral, WatsonX) based on configuration.
- **context manager**: Object implementing __aenter__/__aexit__ (or __enter__/__exit__) to manage resources such as temporary files or network sessions.
- **environment‑variable‑driven configuration**: Runtime configuration that reads values from OS environment variables to override defaults (e.g., API keys).
- **event‑driven UI**: UI architecture where user actions and internal state changes emit events that observers (handlers) react to.
- **middleware pipeline**: Chain of responsibility where each middleware component can inspect, modify, or halt a message before it reaches the agent.
- **retry logic**: Decorator‑based mechanism (using tenacity) that automatically retries failing I/O or network operations with exponential back‑off.
- **snapshot testing**: Testing technique that compares the current output (e.g., rendered UI or LLM messages) against a stored reference snapshot.


### Project Terminology

- **AcpReadFileState**: Concrete AcpToolState storing the path and last known content for the read_file tool.
- **AcpSession**: A session object that carries context (e.g., chat history, tool state) between the agent and the client during a conversation.
- **AcpToolState**: Base data model representing the persisted state of a specific tool (e.g., read_file, grep) across turns.
- **AcpWriteFileState**: Concrete AcpToolState tracking pending write operations and diffs for the write_file tool.
- **BackendFactory**: Factory that constructs the appropriate backend client (Mistral, WatsonX, etc.) based on configuration.
- **Builder (IndexBuilder)**: Helper class that incrementally assembles an IndexResult object from file chunks and metadata.
- **CommandRegistry**: Central registry that maps textual command strings (e.g., "/init") to callable handler functions.
- **Pilot pattern**: Testing pattern provided by Textual where a Pilot object drives the UI programmatically to simulate user input.
- **Renderer registry**: Mapping from tool type identifiers to renderer classes that know how to display tool results in the UI.
- **Snapshot (SnapshotTesting)**: Recorded representation of UI output or LLM messages used to assert that future runs remain unchanged.
- **ToolResultMessage**: Typed Textual message object that carries the rendered result of a tool execution back to the UI.
- **VibeAgent**: Core AI agent implementation that processes user prompts, maintains plan/state, and invokes tools via the ACP protocol.
- **VibeApp**: The main Textual application class that hosts the chat view, input box, tool panels and orchestrates agent interaction.
- **VibeConfig**: Singleton‑like global configuration object that loads, merges and validates the TOML config file and env overrides.


### Frameworks & Libraries

- **Textual**: TUI framework used to build the interactive terminal UI for Vibe, providing widgets, layout, and event handling.
- **httpx**: Async HTTP client used by backend adapters to call Mistral, WatsonX or other external services.
- **pydantic**: Data‑validation library for defining strongly‑typed configuration and tool‑state models.
- **pytest**: Testing framework that runs unit, integration and snapshot tests across the codebase.
- **pytest‑asyncio**: Plugin that enables asynchronous test functions (async def) to be executed with pytest.
- **rich**: Library for rich‑text rendering in the terminal; leveraged by Textual for styling and console output.
- **tenacity**: Utility library providing retry decorators with exponential back‑off for resilient I/O operations.
- **uv**: Modern Python package manager used in the project’s installation scripts and CI workflow.


---

*This file was generated by `/init` command. 
Re-run `/init` to update when the codebase changes significantly.*