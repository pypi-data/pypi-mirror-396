"""Analyze Executor - Orchestrate /analyze Command Phases

This module coordinates the entire /analyze workflow:
1. Discovery - Find all files and build tree
2. Indexing - Analyze files with LLM (chunking large files)
3. Glossary - Extract terms from indexed content
4. Contracts - Extract file relationships and dependencies
5. Generation - Create VIBE-ANALYSIS.md with all context

Provides progress feedback throughout the process.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from vibe.cli.analyze.contracts import ContractsResult, extract_contracts
from vibe.cli.analyze.discovery import DiscoveryResult, discover_codebase
from vibe.cli.analyze.generator import GenerationContext, generate_vibe_md
from vibe.cli.analyze.glossary import GlossaryResult, extract_glossary
from vibe.cli.analyze.indexer import IndexProgress, IndexResult, build_index

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable


@dataclass
class AnalyzeProgress:
    """Progress information for the entire /analyze process."""

    phase: str  # "discovery", "indexing", "glossary", "generation", "complete"
    phase_progress: float  # 0.0 to 1.0
    message: str
    current_file: str | None = None
    files_completed: int = 0
    total_files: int = 0


@dataclass
class AnalyzeResult:
    """Result of /analyze execution."""

    success: bool
    vibe_md_path: Path | None = None
    vibe_md_content: str = ""
    discovery: DiscoveryResult | None = None
    index: IndexResult | None = None
    glossary: GlossaryResult | None = None
    error_message: str = ""
    total_files_analyzed: int = 0
    total_chunks_processed: int = 0
    glossary_terms_extracted: int = 0


async def execute_analyze(
    workspace: Path,
    llm_complete: Callable[[str], AsyncGenerator[str, None]],
    progress_callback: Callable[[AnalyzeProgress], None] | None = None,
    max_files: int = 10000,
) -> AnalyzeResult:
    """Execute the complete /analyze workflow.

    Args:
        workspace: Root directory to analyze
        llm_complete: Async function to call LLM for analysis
        progress_callback: Optional callback for progress updates
        max_files: Maximum number of files to analyze in indexing phase

    Returns:
        AnalyzeResult with generated VIBE-ANALYSIS.md and all analysis data
    """
    result = AnalyzeResult(success=False)

    def report_progress(phase: str, progress: float, message: str, **kwargs) -> None:
        if progress_callback:
            progress_callback(AnalyzeProgress(
                phase=phase,
                phase_progress=progress,
                message=message,
                **kwargs,
            ))

    try:
        # ═══════════════════════════════════════════════════════════════
        # PHASE 1: Discovery
        # ═══════════════════════════════════════════════════════════════
        report_progress("discovery", 0.0, "Scanning codebase...")

        discovery = discover_codebase(workspace)
        result.discovery = discovery

        report_progress(
            "discovery", 1.0,
            f"Found {discovery.total_files} files, {discovery.total_source_files} source files"
        )

        if discovery.total_files == 0:
            result.error_message = "No files found to analyze"
            return result

        # ═══════════════════════════════════════════════════════════════
        # PHASE 2: Indexing
        # ═══════════════════════════════════════════════════════════════
        report_progress("indexing", 0.0, "Analyzing files...")

        def on_index_progress(ip: IndexProgress) -> None:
            progress = ip.files_completed / max(ip.total_files, 1)
            chunk_info = ""
            if ip.total_chunks > 1:
                chunk_info = f" (chunk {ip.current_chunk}/{ip.total_chunks})"
            report_progress(
                "indexing", progress,
                f"Analyzing {ip.current_file}{chunk_info}",
                current_file=ip.current_file,
                files_completed=ip.files_completed,
                total_files=ip.total_files,
            )

        index = await build_index(
            discovery=discovery,
            llm_complete=llm_complete,
            progress_callback=on_index_progress,
            max_files=max_files,
        )
        result.index = index
        result.total_files_analyzed = index.total_files_analyzed
        result.total_chunks_processed = index.total_chunks_processed

        report_progress(
            "indexing", 1.0,
            f"Analyzed {index.total_files_analyzed} files, "
            f"{index.total_chunks_processed} chunks"
        )

        # ═══════════════════════════════════════════════════════════════
        # PHASE 3: Glossary Extraction
        # ═══════════════════════════════════════════════════════════════
        report_progress("glossary", 0.0, "Extracting terminology...")

        glossary = await extract_glossary(
            discovery=discovery,
            index=index,
            llm_complete=llm_complete,
        )
        result.glossary = glossary
        result.glossary_terms_extracted = len(glossary.entries)

        report_progress(
            "glossary", 1.0,
            f"Extracted {len(glossary.entries)} terms"
        )

        # ═══════════════════════════════════════════════════════════════
        # PHASE 4: Contracts Extraction
        # ═══════════════════════════════════════════════════════════════
        report_progress("contracts", 0.0, "Extracting file relationships...")

        contracts = extract_contracts(index)

        # Count relationships for summary
        total_relationships = (
            len(contracts.internal_imports)
            + len(contracts.config_dependencies)
            + len(contracts.resource_dependencies)
            + len(contracts.cross_file_calls)
        )

        report_progress(
            "contracts", 1.0,
            f"Found {total_relationships} file relationships, "
            f"{len(contracts.hub_files)} hub files"
        )

        # ═══════════════════════════════════════════════════════════════
        # PHASE 5: VIBE-ANALYSIS.md Generation
        # ═══════════════════════════════════════════════════════════════
        report_progress("generation", 0.0, "Generating VIBE-ANALYSIS.md...")

        context = GenerationContext(
            discovery=discovery,
            index=index,
            glossary=glossary,
            contracts=contracts,
        )

        # Check for existing VIBE-ANALYSIS.md
        vibe_md_path = workspace / "VIBE-ANALYSIS.md"
        existing_content = None
        if vibe_md_path.exists():
            try:
                existing_content = vibe_md_path.read_text(encoding="utf-8")
                context.existing_vibe_md = existing_content
            except OSError:
                pass

        report_progress("generation", 0.5, "Writing content...")

        vibe_md_content = await generate_vibe_md(
            context=context,
            llm_complete=llm_complete,
            output_path=vibe_md_path,
        )

        result.vibe_md_path = vibe_md_path
        result.vibe_md_content = vibe_md_content

        # ═══════════════════════════════════════════════════════════════
        # Complete
        # ═══════════════════════════════════════════════════════════════
        action = "Updated" if existing_content else "Created"
        report_progress(
            "complete", 1.0,
            f"{action} VIBE-ANALYSIS.md ({len(vibe_md_content)} chars)"
        )

        result.success = True
        return result

    except Exception as e:
        result.error_message = str(e)
        report_progress("error", 0.0, f"Error: {e}")
        return result


def format_analyze_summary(result: AnalyzeResult) -> str:
    """Format a human-readable summary of the /analyze result.

    Args:
        result: AnalyzeResult from execute_analyze

    Returns:
        Formatted summary string
    """
    lines = []

    if result.success:
        lines.append("✅ **VIBE-ANALYSIS.md generated successfully**")
        lines.append("")

        if result.vibe_md_path:
            lines.append(f"📄 **Output**: `{result.vibe_md_path}`")

        lines.append("")
        lines.append("**Analysis Summary:**")
        lines.append(f"- Files discovered: {result.discovery.total_files if result.discovery else 0}")
        lines.append(f"- Files analyzed: {result.total_files_analyzed}")
        lines.append(f"- Chunks processed: {result.total_chunks_processed}")
        lines.append(f"- Glossary terms: {result.glossary_terms_extracted}")

        if result.index:
            if result.index.detected_frameworks:
                lines.append(f"- Frameworks: {', '.join(result.index.detected_frameworks)}")
            if result.index.detected_patterns:
                lines.append(f"- Patterns: {', '.join(result.index.detected_patterns)}")

        lines.append("")
        lines.append("The VIBE-ANALYSIS.md file provides comprehensive codebase analysis.")
        lines.append("Run `/analyze` again to update after significant changes.")

    else:
        lines.append("❌ **VIBE-ANALYSIS.md generation failed**")
        lines.append("")
        if result.error_message:
            lines.append(f"**Error**: {result.error_message}")

    return "\n".join(lines)