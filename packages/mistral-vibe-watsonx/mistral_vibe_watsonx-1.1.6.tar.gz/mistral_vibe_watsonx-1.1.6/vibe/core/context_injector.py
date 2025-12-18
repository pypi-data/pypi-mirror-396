"""Context Injector - Intelligent Context Injection from VIBE-ANALYSIS

This module provides intelligent context injection based on VIBE-ANALYSIS.md
and its JSON index. It uses a two-pass LLM approach:

Pass 1: Scan JSON chunks to find relevant content
  - Iterate through JSON in manageable chunks
  - Ask LLM "does anything in this chunk relate to the user's input?"
  - Collect relevant file paths, sections, and topics

Pass 2: Extract and synthesize context
  - Use position data to extract markdown excerpts
  - LLM synthesizes a focused context summary
  - Returns context ready for injection into conversation
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

logger = logging.getLogger(__name__)


@dataclass
class RelevantItem:
    """An item identified as relevant during JSON scanning."""

    item_type: str  # "file", "section", "topic", "pattern"
    identifier: str  # file path, section name, topic, etc.
    relevance: str  # brief explanation of why it's relevant
    positions: dict[str, int] = field(default_factory=dict)  # char_start, char_end


@dataclass
class ContextResult:
    """Result of context injection analysis."""

    has_context: bool = False
    relevant_items: list[RelevantItem] = field(default_factory=list)
    markdown_excerpts: list[str] = field(default_factory=list)
    synthesized_context: str = ""
    token_estimate: int = 0


# Prompt for Pass 1: JSON chunk scanning
CHUNK_SCAN_PROMPT = """You are analyzing a JSON chunk from a codebase analysis index to find content relevant to a user's question/task.

USER INPUT:
{user_input}

JSON CHUNK:
```json
{json_chunk}
```

Does anything in this JSON chunk relate to the user's input? If yes, identify the relevant items.

Respond with a JSON object:
{{
  "has_relevant_content": true/false,
  "relevant_items": [
    {{
      "type": "file|section|topic|pattern",
      "identifier": "the file path, section name, topic, or pattern",
      "relevance": "brief explanation of why it's relevant"
    }}
  ]
}}

Be selective - only include items that would genuinely help understand or address the user's input.
If nothing is relevant, return {{"has_relevant_content": false, "relevant_items": []}}"""


# Prompt for Pass 2: Context synthesis
SYNTHESIS_PROMPT = """Based on the following relevant excerpts from the codebase analysis, synthesize a focused context summary that would help an AI assistant understand and address the user's input.

USER INPUT:
{user_input}

RELEVANT EXCERPTS:
{excerpts}

Create a concise context summary (max {max_tokens} tokens) that:
1. Highlights the most important information for addressing the user's input
2. Explains relationships between files/components if relevant
3. Notes any patterns, conventions, or architectural decisions that apply
4. Omits information that isn't directly useful

Format as markdown. Focus on actionable, specific information."""


class ContextInjector:
    """Intelligent context injection from VIBE-ANALYSIS."""

    def __init__(
        self,
        workspace: Path,
        llm_complete: Callable[[str], AsyncGenerator[str, None]],
        max_context_tokens: int = 4000,
        chunk_size: int = 8000,  # chars per JSON chunk
    ) -> None:
        """Initialize the context injector.

        Args:
            workspace: Root directory of the project
            llm_complete: Async function to call LLM
            max_context_tokens: Maximum tokens for synthesized context
            chunk_size: Size of JSON chunks for scanning
        """
        self.workspace = workspace
        self.llm_complete = llm_complete
        self.max_context_tokens = max_context_tokens
        self.chunk_size = chunk_size

        # Paths to analysis files
        self.index_path = workspace / "VIBE-ANALYSIS.json"
        self.markdown_path = workspace / "VIBE-ANALYSIS.md"

        # Cached content
        self._index_data: dict[str, Any] | None = None
        self._markdown_content: str | None = None
        self._loaded = False

    def is_available(self) -> bool:
        """Check if VIBE-ANALYSIS files are available."""
        return self.index_path.exists() and self.markdown_path.exists()

    def _load_files(self) -> bool:
        """Load analysis files into memory.

        Returns:
            True if files loaded successfully
        """
        if self._loaded:
            return True

        if not self.is_available():
            return False

        try:
            self._index_data = json.loads(
                self.index_path.read_text(encoding="utf-8")
            )
            self._markdown_content = self.markdown_path.read_text(encoding="utf-8")
            self._loaded = True
            return True
        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load VIBE-ANALYSIS files: {e}")
            return False

    def _chunk_json(self) -> list[tuple[str, dict[str, Any]]]:
        """Split index JSON into chunks for scanning.

        Returns:
            List of (chunk_name, chunk_data) tuples
        """
        if not self._index_data:
            return []

        chunks = []

        # Chunk by sections
        for section in self._index_data.get("sections", []):
            section_name = section.get("name", "Unknown")

            # If section has file_entries, chunk those separately
            file_entries = section.get("file_entries", {})
            if file_entries:
                # Group file entries into chunks
                entries_list = list(file_entries.items())
                for i in range(0, len(entries_list), 10):  # 10 files per chunk
                    batch = dict(entries_list[i:i + 10])
                    chunk_data = {
                        "section": section_name,
                        "file_entries": batch,
                    }
                    chunk_name = f"{section_name}_files_{i // 10}"
                    chunks.append((chunk_name, chunk_data))

            # Also include section-level metadata
            section_meta = {
                "name": section.get("name"),
                "topics": section.get("topics", []),
                "files_mentioned": section.get("files_mentioned", [])[:20],
                "patterns": section.get("patterns", []),
                "summary": section.get("summary", ""),
            }
            chunks.append((f"{section_name}_meta", section_meta))

        # Include lookup maps
        if "file_to_sections" in self._index_data:
            chunks.append(("file_to_sections", {
                "file_to_sections": dict(
                    list(self._index_data["file_to_sections"].items())[:50]
                )
            }))

        if "topic_to_sections" in self._index_data:
            chunks.append(("topic_to_sections", self._index_data["topic_to_sections"]))

        return chunks

    async def _scan_chunk(
        self,
        user_input: str,
        chunk_name: str,
        chunk_data: dict[str, Any],
    ) -> list[RelevantItem]:
        """Scan a single JSON chunk for relevant content.

        Args:
            user_input: The user's input/question
            chunk_name: Name of the chunk being scanned
            chunk_data: JSON data for this chunk

        Returns:
            List of relevant items found
        """
        # Format chunk as JSON string
        chunk_json = json.dumps(chunk_data, indent=2)

        # If chunk is too large, truncate
        if len(chunk_json) > self.chunk_size:
            chunk_json = chunk_json[:self.chunk_size] + "\n... (truncated)"

        prompt = CHUNK_SCAN_PROMPT.format(
            user_input=user_input,
            json_chunk=chunk_json,
        )

        # Get LLM response
        response = ""
        async for chunk in self.llm_complete(prompt):
            response += chunk

        # Parse response
        try:
            # Extract JSON from response (handle markdown code blocks)
            response = response.strip()
            if response.startswith("```"):
                # Remove code block markers
                lines = response.split("\n")
                response = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            result = json.loads(response)

            if not result.get("has_relevant_content", False):
                return []

            items = []
            for item_data in result.get("relevant_items", []):
                items.append(RelevantItem(
                    item_type=item_data.get("type", "unknown"),
                    identifier=item_data.get("identifier", ""),
                    relevance=item_data.get("relevance", ""),
                ))

            return items

        except json.JSONDecodeError:
            logger.debug(f"Failed to parse LLM response for chunk {chunk_name}")
            return []

    def _extract_markdown(self, items: list[RelevantItem]) -> list[str]:
        """Extract markdown excerpts for relevant items.

        Args:
            items: List of relevant items with positions

        Returns:
            List of markdown excerpts
        """
        if not self._markdown_content or not self._index_data:
            return []

        excerpts = []
        seen_ranges: set[tuple[int, int]] = set()

        for item in items:
            # Try to find position data for this item
            positions = self._find_positions(item)

            if positions:
                char_start = positions.get("char_start", 0)
                char_end = positions.get("char_end", 0)

                if char_start > 0 and char_end > char_start:
                    # Avoid duplicate extractions
                    range_key = (char_start, char_end)
                    if range_key in seen_ranges:
                        continue
                    seen_ranges.add(range_key)

                    # Extract the excerpt
                    excerpt = self._markdown_content[char_start:char_end]
                    if excerpt.strip():
                        excerpts.append(f"### {item.identifier}\n{excerpt}")

        return excerpts

    def _find_positions(self, item: RelevantItem) -> dict[str, int]:
        """Find position data for a relevant item.

        Args:
            item: The relevant item to find positions for

        Returns:
            Dict with char_start and char_end, or empty dict
        """
        if not self._index_data:
            return {}

        # Check if it's a file - look in file_entries
        if item.item_type == "file":
            for section in self._index_data.get("sections", []):
                file_entries = section.get("file_entries", {})
                if item.identifier in file_entries:
                    entry = file_entries[item.identifier]
                    positions = entry.get("positions", {})
                    primary = positions.get("primary", {})
                    if primary.get("char_start"):
                        return {
                            "char_start": primary["char_start"],
                            "char_end": primary["char_end"],
                        }

        # Check if it's a section
        if item.item_type == "section":
            for section in self._index_data.get("sections", []):
                if section.get("name") == item.identifier:
                    return {
                        "char_start": section.get("char_start", 0),
                        "char_end": section.get("char_end", 0),
                    }

        return {}

    async def _synthesize_context(
        self,
        user_input: str,
        excerpts: list[str],
    ) -> str:
        """Synthesize extracted excerpts into focused context.

        Args:
            user_input: The user's input/question
            excerpts: List of markdown excerpts

        Returns:
            Synthesized context string
        """
        if not excerpts:
            return ""

        # Combine excerpts
        combined_excerpts = "\n\n---\n\n".join(excerpts)

        # If combined is small enough, might not need synthesis
        if len(combined_excerpts) < 2000:
            return combined_excerpts

        prompt = SYNTHESIS_PROMPT.format(
            user_input=user_input,
            excerpts=combined_excerpts,
            max_tokens=self.max_context_tokens,
        )

        # Get LLM response
        response = ""
        async for chunk in self.llm_complete(prompt):
            response += chunk

        return response.strip()

    async def get_context(self, user_input: str) -> ContextResult:
        """Get relevant context for a user input.

        This is the main entry point. It:
        1. Loads VIBE-ANALYSIS files if not loaded
        2. Scans JSON chunks to find relevant content
        3. Extracts markdown excerpts using position data
        4. Synthesizes a focused context summary

        Args:
            user_input: The user's input/question

        Returns:
            ContextResult with relevant context
        """
        result = ContextResult()

        # Load files
        if not self._load_files():
            return result

        # Pass 1: Scan JSON chunks
        chunks = self._chunk_json()
        all_relevant_items: list[RelevantItem] = []

        for chunk_name, chunk_data in chunks:
            items = await self._scan_chunk(user_input, chunk_name, chunk_data)
            all_relevant_items.extend(items)

        if not all_relevant_items:
            return result

        # Deduplicate items by identifier
        seen_identifiers: set[str] = set()
        unique_items: list[RelevantItem] = []
        for item in all_relevant_items:
            if item.identifier not in seen_identifiers:
                seen_identifiers.add(item.identifier)
                unique_items.append(item)

        result.relevant_items = unique_items
        result.has_context = True

        # Pass 2: Extract markdown and synthesize
        excerpts = self._extract_markdown(unique_items)
        result.markdown_excerpts = excerpts

        if excerpts:
            synthesized = await self._synthesize_context(user_input, excerpts)
            result.synthesized_context = synthesized
            # Rough token estimate (4 chars per token)
            result.token_estimate = len(synthesized) // 4

        return result

    def reload(self) -> bool:
        """Reload analysis files from disk.

        Returns:
            True if reload successful
        """
        self._loaded = False
        self._index_data = None
        self._markdown_content = None
        return self._load_files()


def format_context_for_injection(result: ContextResult) -> str:
    """Format a ContextResult for injection into a conversation.

    Args:
        result: ContextResult from get_context

    Returns:
        Formatted string ready for injection as system context
    """
    if not result.has_context or not result.synthesized_context:
        return ""

    return f"""<codebase-context>
The following context from codebase analysis may be relevant to the user's request:

{result.synthesized_context}
</codebase-context>"""


def format_context_for_enhancement(result: ContextResult) -> str:
    """Format a ContextResult for post-response enhancement.

    This is injected AFTER the LLM has done its work (read files, used tools, etc.)
    as an additional user message with context that may help provide a better answer.
    The LLM's original response is discarded and it generates a new response with this context.

    Args:
        result: ContextResult from get_context

    Returns:
        Formatted string with context for the LLM to use in its response
    """
    if not result.has_context or not result.synthesized_context:
        return ""

    return f"""<codebase-analysis-context>
Here is relevant context from the codebase analysis that may help you provide a better answer:

{result.synthesized_context}
</codebase-analysis-context>

Please use this context along with what you learned from reading files and using tools to provide a comprehensive answer to the user's question."""