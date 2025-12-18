"""Init Generator - VIBE-ANALYSIS.md Generation with Full Context

This module handles Phase 5 of /init:
- Generate each section separately with controlled headers
- Uses INDEX + GLOSSARY + CONTRACTS as context for LLM
- Assembles deterministic structure for reliable parsing
- Generates JSON index for fast retrieval
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from vibe.cli.analyze.analysis_index import (
    AnalysisIndex,
    FileEntry,
    IndexBuilder,
    build_index_from_context,
)
from vibe.cli.analyze.contracts import ContractsResult, format_contracts_as_markdown
from vibe.cli.analyze.discovery import DiscoveryResult, get_file_content
from vibe.cli.analyze.glossary import (
    GlossaryResult,
    build_glossary_context_prompt,
    format_glossary_as_markdown,
)
from vibe.cli.analyze.indexer import IndexResult

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

logger = logging.getLogger(__name__)


@dataclass
class GenerationContext:
    """All context needed for VIBE-ANALYSIS.md generation."""

    discovery: DiscoveryResult
    index: IndexResult
    glossary: GlossaryResult
    contracts: ContractsResult | None = None
    existing_vibe_md: str | None = None


# Section-specific prompts - each generates ONLY the content, no headers
SECTION_PROMPTS = {
    "overview": '''Based on this codebase analysis, write a concise Project Overview (2-3 sentences).

{context}

Write ONLY the overview content. Focus on:
- What does this codebase DO? (Not what it "is", but what it accomplishes)
- Who would use it and why?

Be specific and avoid generic descriptions. Output ONLY the overview text, no headers:''',

    "tech_stack": '''Based on this codebase analysis, document the Technology Stack.

{context}

Write a markdown table and list covering:
- Languages with versions (from package files)
- Key frameworks and libraries (from detected frameworks + dependencies)
- Build tools, testing frameworks, linters
- Any databases, message queues, or external services

Format as a clean markdown table where appropriate. Output ONLY the content, no headers:''',

    "commands": '''Based on this codebase analysis, document the Development Commands.

{context}

Write EXACT, copy-pasteable commands for:
- Installing dependencies
- Running the application
- Running all tests
- Running a specific test file/function
- Linting and formatting
- Building/packaging
- Any other common development tasks

Look at package.json scripts, pyproject.toml, Makefile, etc.
Include actual command syntax (e.g., `pytest tests/test_foo.py::test_bar -v`)

Format as a markdown table. Output ONLY the content, no headers:''',

    "code_style": '''Based on this codebase analysis, document the Code Style Guidelines.

{context}

Document THIS PROJECT'S specific conventions (not generic advice):
- Naming conventions observed (classes, functions, variables, files)
- Import ordering and organization patterns
- Type hints/annotations usage and style
- Error handling patterns
- Documentation style (docstrings, comments)
- Formatting rules (from configs like pyproject.toml, .prettierrc, etc.)

Be specific to what you observe in the analysis. Output ONLY the content, no headers:''',

    "architecture": '''Based on this codebase analysis, document the Architecture Overview.

{context}

Cover:
- High-level system design (what are the main components/layers?)
- How modules relate to each other (use the contracts/dependency data)
- Key abstractions and design patterns detected
- Data flow or request lifecycle
- Critical files and their purposes
- Entry points and their roles

Use the module summary and contracts data to be accurate. Output ONLY the content, no headers:''',
}


def _build_section_context(context: GenerationContext) -> str:
    """Build the context string used for all section prompts."""
    parts = []

    # Glossary context (terminology to use)
    parts.append(build_glossary_context_prompt(context.glossary))

    # Discovery summary
    parts.append(f"""
## Discovery Summary
- Total files: {context.discovery.total_files}
- Source files: {context.discovery.total_source_files}
- Entry points: {len(context.discovery.entry_points)}
- Detected frameworks: {', '.join(context.index.detected_frameworks) or 'None'}
- Detected patterns: {', '.join(context.index.detected_patterns) or 'None'}
""")

    # Project structure (abbreviated)
    tree_lines = context.discovery.tree_structure.split('\n')[:50]
    if len(context.discovery.tree_structure.split('\n')) > 50:
        tree_lines.append("... (truncated)")
    parts.append(f"""
## Project Structure
```
{chr(10).join(tree_lines)}
```
""")

    # Package files content
    package_content = _format_package_files(context.discovery)
    parts.append(f"""
## Package Files
{package_content}
""")

    # Module summary
    module_summary = _format_module_summary(context.index)
    parts.append(f"""
## Module Summary
{module_summary}
""")

    # Entry points
    entry_point_analysis = _format_entry_points(context.index)
    parts.append(f"""
## Entry Points
{entry_point_analysis}
""")

    # Contracts summary (if available)
    if context.contracts:
        contracts_summary = _format_contracts_summary(context.contracts)
        parts.append(f"""
## File Relationships Summary
{contracts_summary}
""")

    return "\n".join(parts)


def _format_contracts_summary(contracts: ContractsResult) -> str:
    """Format a brief contracts summary for the generation prompt."""
    parts = []

    # Hub files
    if contracts.hub_files:
        hub_list = ", ".join(f"`{f}`({d})" for f, d in contracts.hub_files[:5])
        parts.append(f"**Hub files** (most connected): {hub_list}")

    # Config files
    if contracts.all_config_files:
        configs = ", ".join(f"`{c}`" for c in list(contracts.all_config_files.keys())[:5])
        parts.append(f"**Config files**: {configs}")

    # Resources
    if contracts.all_resources:
        resources = ", ".join(f"`{r}`" for r in list(contracts.all_resources.keys())[:5])
        parts.append(f"**Resources/templates**: {resources}")

    # Env vars
    if contracts.all_env_vars:
        env_vars = ", ".join(f"`{v}`" for v in list(contracts.all_env_vars.keys())[:10])
        parts.append(f"**Environment variables**: {env_vars}")

    # Entry point deps
    if contracts.entry_point_deps:
        for ep, deps in list(contracts.entry_point_deps.items())[:3]:
            dep_list = ", ".join(f"`{d}`" for d in deps[:5])
            parts.append(f"**{ep}** depends on: {dep_list}")

    return "\n".join(parts) if parts else "(No relationship data)"


def _format_package_files(discovery: DiscoveryResult) -> str:
    """Format package file contents for the prompt."""
    parts = []

    for pkg_file in discovery.package_files[:5]:
        content = get_file_content(pkg_file)
        if content:
            if len(content) > 3000:
                content = content[:3000] + "\n... (truncated)"
            parts.append(f"### {pkg_file.relative_path}\n```\n{content}\n```")

    return "\n\n".join(parts) if parts else "(No package files found)"


def _format_entry_points(index: IndexResult) -> str:
    """Format entry point analysis for the prompt."""
    parts = []

    for ep in index.entry_points[:5]:
        parts.append(f"### {ep.relative_path}")
        parts.append(f"**Purpose**: {ep.purpose}")

        if ep.exports:
            parts.append(f"**Exports**: {', '.join(ep.exports[:10])}")

        if ep.classes:
            class_info = ", ".join(f"{c.name}" for c in ep.classes[:5])
            parts.append(f"**Classes**: {class_info}")

        if ep.functions:
            func_info = ", ".join(f"{f.name}()" for f in ep.functions[:10])
            parts.append(f"**Functions**: {func_info}")

        parts.append("")

    return "\n".join(parts) if parts else "(No entry points analyzed)"


def _format_module_summary(index: IndexResult) -> str:
    """Format module summary for the prompt."""
    parts = []

    for module_path, files in sorted(index.modules.items())[:15]:
        file_count = len(files)
        purposes = [f.purpose for f in files if f.purpose][:3]

        parts.append(f"- **{module_path}/**: {file_count} files")
        if purposes:
            parts.append(f"  - {'; '.join(purposes)}")

    return "\n".join(parts) if parts else "(No modules analyzed)"


async def _generate_section(
    section_name: str,
    context: GenerationContext,
    llm_complete: Callable[[str], AsyncGenerator[str, None]],
) -> str:
    """Generate a single section's content.

    Args:
        section_name: Name of the section (key in SECTION_PROMPTS)
        context: GenerationContext with all analysis data
        llm_complete: Async function to call LLM

    Returns:
        Generated content for the section (no header)
    """
    if section_name not in SECTION_PROMPTS:
        logger.warning(f"Unknown section: {section_name}")
        return ""

    prompt_template = SECTION_PROMPTS[section_name]
    section_context = _build_section_context(context)
    prompt = prompt_template.format(context=section_context)

    content = ""
    async for chunk in llm_complete(prompt):
        content += chunk

    # Clean up the response
    content = content.strip()

    # Remove any headers the LLM might have added anyway
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip lines that look like headers for this section
        if line.startswith('## ') or line.startswith('# '):
            continue
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines).strip()


@dataclass
class GenerationResult:
    """Result of VIBE-ANALYSIS generation."""

    markdown: str
    index: AnalysisIndex


async def generate_vibe_md(
    context: GenerationContext,
    llm_complete: Callable[[str], AsyncGenerator[str, None]],
    output_path: Path | None = None,
) -> str:
    """Generate complete VIBE-ANALYSIS.md content with per-section generation.

    Args:
        context: GenerationContext with all analysis data
        llm_complete: Async function to call LLM
        output_path: Optional path to write the file (also writes .json index)

    Returns:
        Complete VIBE-ANALYSIS.md content as string
    """
    sections = {}

    # Generate each section separately
    section_order = ["overview", "tech_stack", "commands", "code_style", "architecture"]

    for section_name in section_order:
        logger.info(f"Generating section: {section_name}")
        sections[section_name] = await _generate_section(
            section_name, context, llm_complete
        )

    # Build complete VIBE-ANALYSIS.md with controlled headers and index
    result = _build_vibe_md_with_index(context, sections)

    # Write files if path provided
    if output_path:
        output_path.write_text(result.markdown, encoding="utf-8")

        # Write JSON index alongside markdown
        index_path = output_path.with_suffix(".json")
        result.index.save(index_path)
        logger.info(f"Wrote index to {index_path}")

    return result.markdown


def _build_vibe_md_with_index(
    context: GenerationContext,
    sections: dict[str, str],
) -> GenerationResult:
    """Build VIBE-ANALYSIS.md and its JSON index simultaneously.

    Args:
        context: GenerationContext with all analysis data
        sections: Dict of section_name -> generated content

    Returns:
        GenerationResult with markdown and index
    """
    builder = IndexBuilder()

    # Pre-compute metadata from context
    metadata = build_index_from_context(
        context.index,
        context.glossary,
        context.contracts,
    )
    builder.set_metadata(metadata)

    lines: list[str] = []

    def add_line(line: str = "") -> None:
        lines.append(line)
        builder.add_content(line + "\n")

    def add_lines(*line_list: str) -> None:
        for line in line_list:
            add_line(line)

    # ═══════════════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════════════
    add_lines(
        "# VIBE-ANALYSIS.md",
        "",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "This file provides comprehensive analysis of the codebase for AI coding assistants.",
        "",
    )

    # ═══════════════════════════════════════════════════════════════
    # PROJECT OVERVIEW (LLM-generated, controlled header)
    # ═══════════════════════════════════════════════════════════════
    builder.start_section(
        name="Project Overview",
        header="## Project Overview",
        topics=["purpose", "overview", "description", "users", "goals"],
        summary="High-level description of what the project does and who it's for.",
    )
    add_lines(
        "## Project Overview",
        "",
        sections.get("overview", "(Not generated)"),
        "",
    )

    # ═══════════════════════════════════════════════════════════════
    # TECHNOLOGY STACK (LLM-generated, controlled header)
    # ═══════════════════════════════════════════════════════════════
    builder.start_section(
        name="Technology Stack",
        header="## Technology Stack",
        topics=["languages", "frameworks", "libraries", "tools", "dependencies", "versions"],
        summary="Languages, frameworks, libraries, and tools used in the project.",
    )
    # Add detected frameworks/patterns to section metadata
    builder.add_section_patterns(context.index.detected_frameworks)
    add_lines(
        "---",
        "",
        "## Technology Stack",
        "",
        sections.get("tech_stack", "(Not generated)"),
        "",
    )

    # ═══════════════════════════════════════════════════════════════
    # DEVELOPMENT COMMANDS (LLM-generated, controlled header)
    # ═══════════════════════════════════════════════════════════════
    builder.start_section(
        name="Development Commands",
        header="## Development Commands",
        topics=["commands", "build", "test", "run", "install", "lint", "format"],
        summary="Commands for building, testing, running, and developing the project.",
    )
    add_lines(
        "---",
        "",
        "## Development Commands",
        "",
        sections.get("commands", "(Not generated)"),
        "",
    )

    # ═══════════════════════════════════════════════════════════════
    # CODE STYLE (LLM-generated, controlled header)
    # ═══════════════════════════════════════════════════════════════
    builder.start_section(
        name="Code Style Guidelines",
        header="## Code Style Guidelines",
        topics=["style", "conventions", "naming", "formatting", "imports", "types"],
        summary="Coding conventions, naming patterns, and style guidelines.",
    )
    add_lines(
        "---",
        "",
        "## Code Style Guidelines",
        "",
        sections.get("code_style", "(Not generated)"),
        "",
    )

    # ═══════════════════════════════════════════════════════════════
    # ARCHITECTURE (LLM-generated, controlled header)
    # ═══════════════════════════════════════════════════════════════
    builder.start_section(
        name="Architecture Overview",
        header="## Architecture Overview",
        topics=["architecture", "design", "components", "layers", "patterns", "data flow"],
        summary="System architecture, components, and design patterns.",
    )
    builder.add_section_patterns(context.index.detected_patterns)
    # Add files mentioned in architecture (entry points, hub files)
    arch_files = [ep.relative_path for ep in context.index.entry_points]
    if context.contracts:
        arch_files.extend([f for f, _ in context.contracts.hub_files[:10]])
    builder.add_section_files(arch_files)
    add_lines(
        "---",
        "",
        "## Architecture Overview",
        "",
        sections.get("architecture", "(Not generated)"),
        "",
    )

    # ═══════════════════════════════════════════════════════════════
    # FILE CONTRACTS (code-generated)
    # ═══════════════════════════════════════════════════════════════
    if context.contracts:
        builder.start_section(
            name="File Contracts & Dependencies",
            header="## File Contracts & Dependencies",
            topics=["dependencies", "imports", "relationships", "contracts", "hub files",
                    "config", "resources", "env vars"],
            summary="File relationships, dependencies, and contracts between modules.",
        )
        # Add all files mentioned in contracts
        contracts_files = metadata.get("contracts", {}).get("files_mentioned", [])
        builder.add_section_files(contracts_files)

        contracts_md = format_contracts_as_markdown(context.contracts)
        add_lines(
            "---",
            "",
            contracts_md,
            "",
        )

    # ═══════════════════════════════════════════════════════════════
    # PROJECT STRUCTURE (code-generated)
    # ═══════════════════════════════════════════════════════════════
    builder.start_section(
        name="Project Structure",
        header="## Project Structure",
        topics=["structure", "directories", "files", "tree", "layout"],
        summary="Directory tree showing project file organization.",
    )
    add_lines(
        "---",
        "",
        "## Project Structure",
        "",
        "```",
        context.discovery.tree_structure,
        "```",
        "",
    )

    # ═══════════════════════════════════════════════════════════════
    # FILE INDEX (code-generated with position tracking)
    # ═══════════════════════════════════════════════════════════════
    builder.start_section(
        name="File Index",
        header="## File Index",
        topics=["files", "modules", "classes", "functions", "exports", "purpose"],
        summary="Detailed index of all analyzed files with their purposes and exports.",
    )
    # Add all files and their metadata
    file_index_data = metadata.get("file_index", {})
    builder.add_section_files(file_index_data.get("all_files", []))
    builder.add_section_classes(file_index_data.get("all_classes", []))
    builder.add_section_functions(file_index_data.get("all_functions", []))
    builder.add_section_patterns(file_index_data.get("all_patterns", []))

    # Build file index with position tracking
    dependents_map = metadata.get("contracts", {}).get("dependents_map", {})

    add_lines(
        "---",
        "",
        "## File Index",
        "",
        f"*Analyzed {context.index.total_files_analyzed} files, "
        f"{context.index.total_chunks_processed} chunks processed*",
        "",
    )

    # Group by module and track positions for each file
    for module_path, files in sorted(context.index.modules.items()):
        add_lines(f"### Module: `{module_path}/`", "")

        for f in files:
            # Record char position before file entry
            file_char_start = builder.get_current_char_position()

            file_lines = [f"#### `{f.relative_path}`", ""]

            if f.purpose:
                file_lines.append(f"**Purpose**: {f.purpose}")
                file_lines.append("")

            if f.exports:
                exports_str = ", ".join(f"`{e}`" for e in f.exports[:10])
                if len(f.exports) > 10:
                    exports_str += f" (+{len(f.exports) - 10} more)"
                file_lines.append(f"**Exports**: {exports_str}")
                file_lines.append("")

            if f.classes:
                class_names = ", ".join(f"`{c.name}`" for c in f.classes[:5])
                file_lines.append(f"**Classes**: {class_names}")
                file_lines.append("")

            if f.functions:
                public_funcs = [fn for fn in f.functions if fn.is_public][:8]
                if public_funcs:
                    func_names = ", ".join(f"`{fn.name}()`" for fn in public_funcs)
                    file_lines.append(f"**Functions**: {func_names}")
                    file_lines.append("")

            if f.patterns:
                file_lines.append(f"**Patterns**: {', '.join(f.patterns)}")
                file_lines.append("")

            if f.dependencies:
                deps = ", ".join(f.dependencies[:5])
                file_lines.append(f"**Dependencies**: {deps}")
                file_lines.append("")

            file_lines.append(f"**Complexity**: {f.complexity}")
            file_lines.append("")

            # Add file content and track position
            add_lines(*file_lines)

            # Record char position after file entry
            file_char_end = builder.get_current_char_position()

            # Record primary position for this file
            builder.record_file_primary_position(
                f.relative_path,
                file_char_start,
                file_char_end,
            )

            # Get file data for FileEntry
            file_data = file_index_data.get("files", {}).get(f.relative_path, {})

            # Add file entry for direct lookup
            builder.add_file_entry(FileEntry(
                path=f.relative_path,
                purpose=file_data.get("purpose", ""),
                classes=file_data.get("classes", []),
                functions=file_data.get("functions", []),
                dependencies=file_data.get("internal_imports", []),
                dependents=dependents_map.get(f.relative_path, []),
                patterns=file_data.get("patterns", []),
            ))

    add_line("")

    # ═══════════════════════════════════════════════════════════════
    # GLOSSARY (code-generated)
    # ═══════════════════════════════════════════════════════════════
    builder.start_section(
        name="Glossary",
        header="## Glossary",
        topics=["terms", "definitions", "acronyms", "jargon", "vocabulary"],
        summary="Project-specific terminology and definitions.",
    )
    glossary_md = format_glossary_as_markdown(context.glossary)
    add_lines(
        "---",
        "",
        glossary_md,
        "",
    )

    # ═══════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════
    add_lines(
        "---",
        "",
        "*This file was generated by `/init` command. ",
        "Re-run `/init` to update when the codebase changes significantly.*",
    )

    # Finalize index
    analysis_index = builder.finalize()

    return GenerationResult(
        markdown="\n".join(lines),
        index=analysis_index,
    )


async def update_vibe_md(
    existing_content: str,
    context: GenerationContext,
    llm_complete: Callable[[str], AsyncGenerator[str, None]],
    output_path: Path | None = None,
) -> str:
    """Update an existing VIBE-ANALYSIS.md with new analysis data.

    Args:
        existing_content: Current VIBE-ANALYSIS.md content
        context: GenerationContext with new analysis data
        llm_complete: Async function to call LLM
        output_path: Optional path to write the updated file

    Returns:
        Updated VIBE-ANALYSIS.md content
    """
    context.existing_vibe_md = existing_content
    return await generate_vibe_md(context, llm_complete, output_path)


def get_section_names() -> list[str]:
    """Get the list of section names in order.

    Returns:
        List of section names that appear in VIBE-ANALYSIS.md
    """
    return [
        "Project Overview",
        "Technology Stack",
        "Development Commands",
        "Code Style Guidelines",
        "Architecture Overview",
        "File Contracts & Dependencies",
        "Project Structure",
        "File Index",
        "Glossary",
    ]