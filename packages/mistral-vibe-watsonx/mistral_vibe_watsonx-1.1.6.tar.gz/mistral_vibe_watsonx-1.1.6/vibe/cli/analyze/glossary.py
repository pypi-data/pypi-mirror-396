"""Init Glossary - Term Extraction from Indexed Content

This module handles Phase 3 of /init:
- Extract acronyms, domain terms, project-specific jargon
- Build GLOSSARY data structure from indexed content
- Provides accurate terminology context for final VIBE-ANALYSIS.md generation
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
from typing import TYPE_CHECKING

from vibe.cli.analyze.discovery import DiscoveryResult, get_file_content
from vibe.cli.analyze.indexer import IndexResult

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

logger = logging.getLogger(__name__)


@dataclass
class GlossaryEntry:
    """A single glossary entry."""

    term: str
    definition: str
    category: str = "general"  # acronym, domain, project, technical, framework
    source_file: str = ""  # Where this term was found


@dataclass
class GlossaryResult:
    """Complete GLOSSARY data structure."""

    entries: dict[str, GlossaryEntry] = field(default_factory=dict)
    acronyms: dict[str, str] = field(default_factory=dict)
    domain_terms: dict[str, str] = field(default_factory=dict)
    project_terms: dict[str, str] = field(default_factory=dict)
    frameworks: dict[str, str] = field(default_factory=dict)


GLOSSARY_EXTRACTION_PROMPT = '''Extract important terms, acronyms, and definitions from this project context.

PROJECT INDEX SUMMARY:
{index_summary}

KEY CONCEPTS FOUND IN FILES:
{key_concepts}

DOCUMENTATION EXCERPTS:
{doc_content}

Your task: Create a comprehensive glossary of terms important for understanding this project.

WHAT TO EXTRACT:

1. **ACRONYMS** - Abbreviations with their full meanings
   - Look for patterns like "Term (ACRONYM)", "ACRONYM: Definition"
   - Common tech acronyms used in this specific context (API, CLI, DB, etc.)

2. **DOMAIN TERMS** - Industry/domain-specific terminology
   - Terms that have specific meaning in this project's domain
   - Technical jargon that may not be obvious

3. **PROJECT TERMS** - Project-specific concepts
   - Custom names for modules, components, or features
   - Internal terminology unique to this codebase

4. **FRAMEWORKS/LIBRARIES** - Key technologies used
   - Main frameworks with brief descriptions of their role
   - Important libraries and what they're used for

EXTRACTION RULES:
- Extract the MOST SPECIFIC definition for each term
- Skip common programming terms unless they have project-specific meaning
- Include 20-40 important terms (be comprehensive)
- Prioritize terms that would help someone understand the codebase

Respond with JSON:
{{
  "acronyms": {{
    "TERM": "Full meaning",
    "API": "Application Programming Interface"
  }},
  "domain_terms": {{
    "webhook": "HTTP callback for event notifications",
    "pipeline": "Data processing workflow"
  }},
  "project_terms": {{
    "Agent": "AI-powered assistant that processes user requests",
    "Tool": "Function that the agent can call to perform actions"
  }},
  "frameworks": {{
    "Textual": "TUI framework for building terminal applications",
    "httpx": "Async HTTP client library"
  }}
}}

Your response (JSON only):'''


async def extract_glossary(
    discovery: DiscoveryResult,
    index: IndexResult,
    llm_complete: Callable[[str], AsyncGenerator[str, None]],
) -> GlossaryResult:
    """Extract glossary terms from indexed content.

    Args:
        discovery: DiscoveryResult from discovery phase
        index: IndexResult from indexing phase
        llm_complete: Async function to call LLM

    Returns:
        GlossaryResult with all extracted terms
    """
    result = GlossaryResult()

    # Build index summary
    index_summary = _build_index_summary(index)

    # Collect key concepts from all analyzed files
    key_concepts = _collect_key_concepts(index)

    # Read documentation files for context
    doc_content = await _read_documentation(discovery)

    prompt = GLOSSARY_EXTRACTION_PROMPT.format(
        index_summary=index_summary,
        key_concepts=key_concepts,
        doc_content=doc_content,
    )

    response_text = ""
    async for chunk in llm_complete(prompt):
        response_text += chunk

    logger.debug(f"Glossary LLM response: {response_text[:500]}...")

    # Parse response
    parsed = _parse_glossary_json(response_text)
    if not parsed:
        logger.warning("Failed to parse JSON from glossary LLM response")
        logger.debug(f"Full glossary response was: {response_text[:1000]}")
    else:
        logger.debug(f"Parsed glossary categories: {list(parsed.keys())}")

    # Build result
    for term, definition in parsed.get("acronyms", {}).items():
        if term and definition:
            result.acronyms[term] = definition
            result.entries[term] = GlossaryEntry(
                term=term, definition=definition, category="acronym"
            )

    for term, definition in parsed.get("domain_terms", {}).items():
        if term and definition:
            result.domain_terms[term] = definition
            result.entries[term] = GlossaryEntry(
                term=term, definition=definition, category="domain"
            )

    for term, definition in parsed.get("project_terms", {}).items():
        if term and definition:
            result.project_terms[term] = definition
            result.entries[term] = GlossaryEntry(
                term=term, definition=definition, category="project"
            )

    for term, definition in parsed.get("frameworks", {}).items():
        if term and definition:
            result.frameworks[term] = definition
            result.entries[term] = GlossaryEntry(
                term=term, definition=definition, category="framework"
            )

    logger.info(
        f"Glossary extraction complete: {len(result.entries)} total terms "
        f"({len(result.acronyms)} acronyms, {len(result.domain_terms)} domain, "
        f"{len(result.project_terms)} project, {len(result.frameworks)} frameworks)"
    )
    return result


def _build_index_summary(index: IndexResult) -> str:
    """Build a summary of the index for glossary extraction."""
    lines = []

    lines.append(f"Total files analyzed: {index.total_files_analyzed}")

    if index.detected_frameworks:
        lines.append(f"Detected frameworks: {', '.join(index.detected_frameworks)}")

    if index.detected_patterns:
        lines.append(f"Design patterns: {', '.join(index.detected_patterns)}")

    # Summarize entry points
    if index.entry_points:
        lines.append("\nEntry points:")
        for ep in index.entry_points[:5]:
            lines.append(f"  - {ep.relative_path}: {ep.purpose}")

    # Summarize modules
    lines.append(f"\nModules: {', '.join(list(index.modules.keys())[:15])}")

    return "\n".join(lines)


def _collect_key_concepts(index: IndexResult) -> str:
    """Collect all key concepts from indexed files."""
    concepts = set()

    for file_analysis in index.files:
        for concept in file_analysis.key_concepts:
            if concept:
                concepts.add(concept)

        # Also extract class names as potential terms
        for cls in file_analysis.classes:
            if cls.name and len(cls.name) > 2:
                concepts.add(cls.name)

    # Format as bullet list
    if concepts:
        return "\n".join(f"- {c}" for c in sorted(concepts)[:50])
    return "(No key concepts extracted)"


async def _read_documentation(discovery: DiscoveryResult) -> str:
    """Read README and other doc files for context."""
    content_parts = []

    # Priority order for docs
    doc_priority = ["README.md", "README", "CONTRIBUTING.md", "ARCHITECTURE.md"]

    for doc_name in doc_priority:
        for doc_file in discovery.doc_files:
            if doc_file.path.name.lower() == doc_name.lower():
                content = get_file_content(doc_file)
                if content:
                    # Limit each doc to 2000 chars
                    content_parts.append(f"### {doc_file.path.name}\n{content[:2000]}")
                break

    # Also check for existing VIBE.md or similar
    for doc_file in discovery.doc_files:
        name_lower = doc_file.path.name.lower()
        if name_lower in ["vibe.md", ".vibe.md", "agents.md", "claude.md"]:
            content = get_file_content(doc_file)
            if content:
                content_parts.append(f"### {doc_file.path.name}\n{content[:2000]}")

    if content_parts:
        return "\n\n".join(content_parts[:3])  # Max 3 docs
    return "(No documentation files found)"


def _parse_glossary_json(text: str) -> dict:
    """Parse JSON from LLM response."""
    text = text.strip()

    # Remove <think>...</think> reasoning tags (common in reasoning models)
    import re
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = text.strip()

    # Remove markdown code fences
    if "```" in text:
        lines = text.split("\n")
        in_code_block = False
        code_lines = []
        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    break
                else:
                    in_code_block = True
                    continue
            if in_code_block:
                code_lines.append(line)
        if code_lines:
            text = "\n".join(code_lines)

    # Find JSON object
    start_idx = text.find("{")
    if start_idx == -1:
        return {}

    # Use brace counting with string awareness
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
        try:
            return json.loads(json_str.replace("'", '"'))
        except json.JSONDecodeError:
            return {}


def format_glossary_as_markdown(glossary: GlossaryResult) -> str:
    """Format GlossaryResult as markdown for inclusion in VIBE-ANALYSIS.md.

    Args:
        glossary: GlossaryResult to format

    Returns:
        Markdown string
    """
    lines = []
    lines.append("## Glossary\n")

    total_terms = len(glossary.entries)
    lines.append(f"*{total_terms} terms defined*\n")

    # Acronyms section
    if glossary.acronyms:
        lines.append("\n### Acronyms\n")
        for term, definition in sorted(glossary.acronyms.items()):
            lines.append(f"- **{term}**: {definition}")
        lines.append("")

    # Domain terms
    if glossary.domain_terms:
        lines.append("\n### Domain Terms\n")
        for term, definition in sorted(glossary.domain_terms.items()):
            lines.append(f"- **{term}**: {definition}")
        lines.append("")

    # Project-specific terms
    if glossary.project_terms:
        lines.append("\n### Project Terminology\n")
        for term, definition in sorted(glossary.project_terms.items()):
            lines.append(f"- **{term}**: {definition}")
        lines.append("")

    # Frameworks
    if glossary.frameworks:
        lines.append("\n### Frameworks & Libraries\n")
        for term, definition in sorted(glossary.frameworks.items()):
            lines.append(f"- **{term}**: {definition}")
        lines.append("")

    return "\n".join(lines)


def build_glossary_context_prompt(glossary: GlossaryResult) -> str:
    """Build a prompt section that instructs the LLM to use only defined terms.
    This is injected into the main VIBE-ANALYSIS.md generation prompt.

    Args:
        glossary: GlossaryResult

    Returns:
        Prompt section string
    """
    if not glossary.entries:
        return ""

    lines = []
    lines.append("""
═══════════════════════════════════════════════════════════════
📖 PROJECT GLOSSARY - USE THESE DEFINITIONS
═══════════════════════════════════════════════════════════════

The following terms have EXPLICIT meanings in this project.
Use these definitions. Do NOT infer alternative meanings.

**DEFINED TERMS:**
""")

    for term, entry in sorted(glossary.entries.items()):
        lines.append(f"• **{term}** = {entry.definition}")

    lines.append("""
═══════════════════════════════════════════════════════════════
""")

    return "\n".join(lines)