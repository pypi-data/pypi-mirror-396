"""Init Indexer - Chunked File Analysis for INDEX Generation

This module handles Phase 2 of /init:
- Analyze each file with LLM (chunking large files)
- Extract: purpose, exports, classes, functions, patterns, dependencies
- Multiple LLM iterations as needed per file
- Build comprehensive INDEX data structure
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
from typing import TYPE_CHECKING

from vibe.cli.analyze.discovery import (
    DiscoveryResult,
    FileInfo,
    get_chunk_count,
    get_file_content,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

logger = logging.getLogger(__name__)


@dataclass
class FunctionInfo:
    """Information about a function/method."""

    name: str
    description: str = ""
    parameters: list[str] = field(default_factory=list)
    return_type: str = ""
    is_async: bool = False
    is_public: bool = True


@dataclass
class ClassInfo:
    """Information about a class."""

    name: str
    description: str = ""
    base_classes: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    is_public: bool = True


@dataclass
class FileRelationship:
    """A relationship/contract between files."""

    target_file: str  # The file being referenced
    relationship_type: str  # "import", "config", "template", "resource", "calls"
    details: str = ""  # Additional context (e.g., function name, config key)


@dataclass
class FileAnalysis:
    """Analysis result for a single file."""

    relative_path: str
    file_type: str
    purpose: str = ""
    exports: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    complexity: str = "low"  # low, medium, high
    key_concepts: list[str] = field(default_factory=list)
    chunk_summaries: list[str] = field(default_factory=list)

    # Relationship tracking (for contracts)
    internal_imports: list[str] = field(default_factory=list)  # Project file imports
    config_files_used: list[str] = field(default_factory=list)  # Config files read
    resources_loaded: list[str] = field(default_factory=list)  # Templates, static files
    cross_file_calls: list[FileRelationship] = field(default_factory=list)  # Function calls to other files
    env_vars_used: list[str] = field(default_factory=list)  # Environment variables accessed
    shared_state: list[str] = field(default_factory=list)  # Global/shared state patterns


@dataclass
class IndexResult:
    """Complete INDEX data structure."""

    files: list[FileAnalysis] = field(default_factory=list)
    modules: dict[str, list[FileAnalysis]] = field(default_factory=dict)
    entry_points: list[FileAnalysis] = field(default_factory=list)
    total_files_analyzed: int = 0
    total_chunks_processed: int = 0
    detected_patterns: list[str] = field(default_factory=list)
    detected_frameworks: list[str] = field(default_factory=list)


# Prompt for analyzing a file or chunk
FILE_ANALYSIS_PROMPT = '''Analyze this source code file and extract structured information.

File: {file_path}
File Type: {file_type}
{chunk_info}

```{extension}
{content}
```

Extract the following information as JSON. Pay special attention to FILE RELATIONSHIPS - track how this file connects to OTHER PROJECT FILES (not external libraries):

{{
  "purpose": "Brief description of what this file does (1-2 sentences)",
  "exports": ["list of exported functions, classes, or variables"],
  "imports": ["list of ALL imported modules/packages"],
  "classes": [
    {{
      "name": "ClassName",
      "description": "What this class does",
      "base_classes": ["BaseClass1"],
      "methods": ["method1", "method2"],
      "is_public": true
    }}
  ],
  "functions": [
    {{
      "name": "function_name",
      "description": "What this function does",
      "parameters": ["param1", "param2"],
      "return_type": "ReturnType",
      "is_async": false,
      "is_public": true
    }}
  ],
  "patterns": ["Design patterns used, e.g., Singleton, Factory, Observer"],
  "dependencies": ["External packages/libraries (pip, npm, etc.) this file depends on"],
  "complexity": "low|medium|high",
  "key_concepts": ["Important domain concepts, acronyms, or terms defined here"],

  "internal_imports": ["Project-internal imports only - relative imports or imports from this project's packages, e.g., 'from .config import X', 'from myproject.utils import Y'"],
  "config_files_used": ["Config files this file reads/loads, e.g., 'config.toml', '.env', 'settings.json'"],
  "resources_loaded": ["Templates, static files, or data files loaded, e.g., 'templates/email.html', 'prompts/system.md', 'data/schema.sql'"],
  "cross_file_calls": [
    {{
      "target_file": "relative/path/to/file.py",
      "relationship_type": "calls|instantiates|inherits|imports_from",
      "details": "Which function/class is used, e.g., 'calls Agent.run()' or 'inherits from BaseTool'"
    }}
  ],
  "env_vars_used": ["Environment variables accessed, e.g., 'MISTRAL_API_KEY', 'DEBUG'"],
  "shared_state": ["Global variables, singletons, or shared state patterns, e.g., 'uses global config object', 'writes to shared cache'"]
}}

IMPORTANT:
- For internal_imports, ONLY include imports from THIS PROJECT, not external libraries
- For cross_file_calls, identify specific function calls, class instantiations, or inheritance from other project files
- For config_files_used and resources_loaded, use relative paths from project root

Respond with ONLY the JSON object, no explanations:'''


CHUNK_MERGE_PROMPT = '''You have analyzed {chunk_count} chunks of a large file. Merge these chunk analyses into a single coherent file analysis.

File: {file_path}

Chunk analyses:
{chunk_analyses}

Create a merged analysis that:
1. Combines all exports, imports, classes, functions without duplicates
2. Summarizes the overall purpose from all chunks
3. Merges patterns and dependencies
4. Provides accurate complexity assessment for the whole file

Respond with the merged JSON analysis:'''


async def analyze_file_chunk(
    file_info: FileInfo,
    chunk_index: int,
    total_chunks: int,
    llm_complete: Callable[[str], AsyncGenerator[str, None]],
) -> dict:
    """Analyze a single chunk of a file.

    Args:
        file_info: FileInfo for the file
        chunk_index: Which chunk (0-indexed)
        total_chunks: Total number of chunks
        llm_complete: Async function to call LLM

    Returns:
        Parsed analysis dict
    """
    content = get_file_content(file_info, chunk_index)
    if not content.strip():
        return {}

    chunk_info = ""
    if total_chunks > 1:
        chunk_info = f"Chunk {chunk_index + 1} of {total_chunks}"

    extension = file_info.extension.lstrip(".") or "text"

    prompt = FILE_ANALYSIS_PROMPT.format(
        file_path=file_info.relative_path,
        file_type=file_info.file_type,
        chunk_info=chunk_info,
        extension=extension,
        content=content,
    )

    # Collect LLM response
    response_text = ""
    async for chunk in llm_complete(prompt):
        response_text += chunk

    logger.debug(f"Indexer LLM response for {file_info.relative_path}: {response_text[:300]}...")

    # Parse JSON response
    parsed = _parse_analysis_json(response_text)
    if not parsed:
        logger.warning(f"Failed to parse JSON from LLM response for {file_info.relative_path}")
        logger.debug(f"Full response was: {response_text[:500]}")
    else:
        logger.debug(f"Parsed analysis for {file_info.relative_path}: {list(parsed.keys())}")
    return parsed


async def merge_chunk_analyses(
    file_info: FileInfo,
    chunk_analyses: list[dict],
    llm_complete: Callable[[str], AsyncGenerator[str, None]],
) -> dict:
    """Merge multiple chunk analyses into one coherent analysis.

    Args:
        file_info: FileInfo for the file
        chunk_analyses: List of analysis dicts from each chunk
        llm_complete: Async function to call LLM

    Returns:
        Merged analysis dict
    """
    if len(chunk_analyses) == 1:
        return chunk_analyses[0]

    if not chunk_analyses:
        return {}

    # Format chunk analyses for the prompt
    analyses_text = ""
    for i, analysis in enumerate(chunk_analyses, 1):
        analyses_text += f"\n--- Chunk {i} ---\n{json.dumps(analysis, indent=2)}\n"

    prompt = CHUNK_MERGE_PROMPT.format(
        file_path=file_info.relative_path,
        chunk_count=len(chunk_analyses),
        chunk_analyses=analyses_text,
    )

    response_text = ""
    async for chunk in llm_complete(prompt):
        response_text += chunk

    return _parse_analysis_json(response_text)


def _parse_analysis_json(text: str) -> dict:
    """Parse JSON from LLM response, handling common issues."""
    if not text:
        return {}

    text = text.strip()

    # Remove <think>...</think> reasoning tags (common in reasoning models)
    import re
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = text.strip()

    # Remove markdown code fences if present
    if "```" in text:
        # Find content between code fences
        lines = text.split("\n")
        in_code_block = False
        code_lines = []
        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    break  # End of code block
                else:
                    in_code_block = True
                    continue
            if in_code_block:
                code_lines.append(line)
        if code_lines:
            text = "\n".join(code_lines)

    # Try to find JSON object
    start_idx = text.find("{")
    if start_idx == -1:
        return {}

    # Use brace counting to find matching close (handle nested braces)
    brace_count = 0
    end_idx = -1
    in_string = False
    escape_next = False

    for i, char in enumerate(text[start_idx:], start=start_idx):
        if escape_next:
            escape_next = False
            continue
        if char == "\\":
            escape_next = True
            continue
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break

    if end_idx == -1:
        return {}

    json_str = text[start_idx:end_idx]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Try to fix common issues
        # Replace single quotes with double quotes (but not in strings)
        try:
            # Simple replacement - may not work for all cases
            fixed = json_str.replace("'", '"')
            return json.loads(fixed)
        except json.JSONDecodeError:
            return {}


def _dict_to_file_analysis(file_info: FileInfo, analysis_dict: dict) -> FileAnalysis:
    """Convert analysis dict to FileAnalysis dataclass."""
    classes = []
    for cls in analysis_dict.get("classes", []):
        if isinstance(cls, dict):
            classes.append(ClassInfo(
                name=cls.get("name", ""),
                description=cls.get("description", ""),
                base_classes=cls.get("base_classes", []),
                methods=cls.get("methods", []),
                is_public=cls.get("is_public", True),
            ))

    functions = []
    for func in analysis_dict.get("functions", []):
        if isinstance(func, dict):
            functions.append(FunctionInfo(
                name=func.get("name", ""),
                description=func.get("description", ""),
                parameters=func.get("parameters", []),
                return_type=func.get("return_type", ""),
                is_async=func.get("is_async", False),
                is_public=func.get("is_public", True),
            ))

    # Parse cross-file relationships
    cross_file_calls = []
    for call in analysis_dict.get("cross_file_calls", []):
        if isinstance(call, dict):
            cross_file_calls.append(FileRelationship(
                target_file=call.get("target_file", ""),
                relationship_type=call.get("relationship_type", ""),
                details=call.get("details", ""),
            ))

    return FileAnalysis(
        relative_path=file_info.relative_path,
        file_type=file_info.file_type,
        purpose=analysis_dict.get("purpose", ""),
        exports=analysis_dict.get("exports", []),
        imports=analysis_dict.get("imports", []),
        classes=classes,
        functions=functions,
        patterns=analysis_dict.get("patterns", []),
        dependencies=analysis_dict.get("dependencies", []),
        complexity=analysis_dict.get("complexity", "low"),
        key_concepts=analysis_dict.get("key_concepts", []),
        # Relationship fields
        internal_imports=analysis_dict.get("internal_imports", []),
        config_files_used=analysis_dict.get("config_files_used", []),
        resources_loaded=analysis_dict.get("resources_loaded", []),
        cross_file_calls=cross_file_calls,
        env_vars_used=analysis_dict.get("env_vars_used", []),
        shared_state=analysis_dict.get("shared_state", []),
    )


@dataclass
class IndexProgress:
    """Progress information for indexing."""

    current_file: str
    current_chunk: int
    total_chunks: int
    files_completed: int
    total_files: int
    phase: str = "indexing"


async def build_index(
    discovery: DiscoveryResult,
    llm_complete: Callable[[str], AsyncGenerator[str, None]],
    progress_callback: Callable[[IndexProgress], None] | None = None,
    max_files: int = 10000,
) -> IndexResult:
    """Build comprehensive INDEX by analyzing all discovered files.

    Args:
        discovery: DiscoveryResult from discovery phase
        llm_complete: Async function to call LLM for analysis
        progress_callback: Optional callback for progress updates
        max_files: Maximum number of files to analyze (prioritizes important ones)

    Returns:
        IndexResult with all file analyses
    """
    result = IndexResult()

    # Prioritize files: entry points, package files, then source files
    files_to_analyze = []

    # Always include entry points and package files
    for f in discovery.entry_points:
        if f not in files_to_analyze:
            files_to_analyze.append(f)

    for f in discovery.package_files:
        if f not in files_to_analyze:
            files_to_analyze.append(f)

    # Add source files up to limit
    for f in discovery.source_files:
        if len(files_to_analyze) >= max_files:
            break
        if f not in files_to_analyze:
            files_to_analyze.append(f)

    # Add config files if room
    for f in discovery.config_files:
        if len(files_to_analyze) >= max_files:
            break
        if f not in files_to_analyze:
            files_to_analyze.append(f)

    total_files = len(files_to_analyze)
    files_completed = 0

    for file_info in files_to_analyze:
        chunk_count = get_chunk_count(file_info)
        chunk_analyses = []

        for chunk_idx in range(chunk_count):
            if progress_callback:
                progress_callback(IndexProgress(
                    current_file=file_info.relative_path,
                    current_chunk=chunk_idx + 1,
                    total_chunks=chunk_count,
                    files_completed=files_completed,
                    total_files=total_files,
                ))

            try:
                analysis = await analyze_file_chunk(
                    file_info, chunk_idx, chunk_count, llm_complete
                )
                if analysis:
                    chunk_analyses.append(analysis)
                    logger.debug(f"Successfully analyzed chunk {chunk_idx + 1} of {file_info.relative_path}")
                else:
                    logger.warning(f"Empty analysis for chunk {chunk_idx + 1} of {file_info.relative_path}")
                result.total_chunks_processed += 1
            except Exception as e:
                # Continue on error, we'll have partial analysis
                logger.error(f"Error analyzing chunk {chunk_idx + 1} of {file_info.relative_path}: {e}")
                result.total_chunks_processed += 1

        # Merge chunks if needed
        if chunk_analyses:
            if len(chunk_analyses) > 1:
                merged = await merge_chunk_analyses(file_info, chunk_analyses, llm_complete)
            else:
                merged = chunk_analyses[0]

            file_analysis = _dict_to_file_analysis(file_info, merged)

            # Store chunk summaries for large files
            if len(chunk_analyses) > 1:
                file_analysis.chunk_summaries = [
                    a.get("purpose", "") for a in chunk_analyses if a.get("purpose")
                ]

            result.files.append(file_analysis)

            # Track by module (directory)
            module_path = str(file_info.path.parent.relative_to(discovery.root_path))
            if module_path == ".":
                module_path = "(root)"
            if module_path not in result.modules:
                result.modules[module_path] = []
            result.modules[module_path].append(file_analysis)

            # Track entry points
            if file_info.file_type == "entry_point":
                result.entry_points.append(file_analysis)

            # Collect patterns and frameworks
            for pattern in file_analysis.patterns:
                if pattern and pattern not in result.detected_patterns:
                    result.detected_patterns.append(pattern)

            for dep in file_analysis.dependencies:
                # Common framework detection
                if dep and any(fw in dep.lower() for fw in [
                    "fastapi", "flask", "django", "express", "react", "vue",
                    "angular", "spring", "rails", "laravel", "textual", "rich"
                ]):
                    if dep not in result.detected_frameworks:
                        result.detected_frameworks.append(dep)

        files_completed += 1
        result.total_files_analyzed = files_completed

    logger.info(
        f"Index complete: {result.total_files_analyzed} files analyzed, "
        f"{result.total_chunks_processed} chunks processed, "
        f"{len(result.files)} files with data, "
        f"{len(result.modules)} modules, "
        f"{len(result.detected_frameworks)} frameworks detected"
    )
    return result


def format_index_as_markdown(index: IndexResult) -> str:
    """Format IndexResult as markdown for inclusion in VIBE-ANALYSIS.md.

    Args:
        index: IndexResult to format

    Returns:
        Markdown string
    """
    lines = []
    lines.append("## File Index\n")
    lines.append(f"*Analyzed {index.total_files_analyzed} files, "
                 f"{index.total_chunks_processed} chunks processed*\n")

    # Group by module
    for module_path, files in sorted(index.modules.items()):
        lines.append(f"\n### Module: `{module_path}/`\n")

        for f in files:
            lines.append(f"\n#### `{f.relative_path}`\n")

            if f.purpose:
                lines.append(f"**Purpose**: {f.purpose}\n")

            if f.exports:
                exports_str = ", ".join(f"`{e}`" for e in f.exports[:10])
                if len(f.exports) > 10:
                    exports_str += f" (+{len(f.exports) - 10} more)"
                lines.append(f"**Exports**: {exports_str}\n")

            if f.classes:
                class_names = ", ".join(f"`{c.name}`" for c in f.classes[:5])
                lines.append(f"**Classes**: {class_names}\n")

            if f.functions:
                public_funcs = [fn for fn in f.functions if fn.is_public][:8]
                if public_funcs:
                    func_names = ", ".join(f"`{fn.name}()`" for fn in public_funcs)
                    lines.append(f"**Functions**: {func_names}\n")

            if f.patterns:
                lines.append(f"**Patterns**: {', '.join(f.patterns)}\n")

            if f.dependencies:
                deps = ", ".join(f.dependencies[:5])
                lines.append(f"**Dependencies**: {deps}\n")

            lines.append(f"**Complexity**: {f.complexity}\n")

    return "\n".join(lines)