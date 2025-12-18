"""Analysis Index - JSON Index for VIBE-ANALYSIS.md

This module provides structured indexing of VIBE-ANALYSIS.md content
for fast, intelligent retrieval without full document scanning.

The index enables:
- Quick section lookup by file/function/class mentions
- Topic-based filtering without LLM calls
- Direct line/char offsets for content extraction
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from vibe.cli.analyze.contracts import ContractsResult
from vibe.cli.analyze.glossary import GlossaryResult
from vibe.cli.analyze.indexer import IndexResult


@dataclass
class SubsectionIndex:
    """Index entry for a subsection within a section."""

    name: str
    line_start: int = 0
    line_end: int = 0
    char_start: int = 0
    char_end: int = 0
    files_mentioned: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "name": self.name,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "files_mentioned": self.files_mentioned,
            "topics": self.topics,
        }


@dataclass
class FileMention:
    """A mention of a file in a section of VIBE-ANALYSIS.md."""

    section: str
    char_start: int
    char_end: int
    context_type: str = ""  # "architecture", "hub_file", "dependency", "data_flow", etc.

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "section": self.section,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "context_type": self.context_type,
        }


@dataclass
class FilePositions:
    """Tracks where a file is documented in VIBE-ANALYSIS.md."""

    # Primary location (usually in File Index section)
    primary_section: str = ""
    primary_char_start: int = 0
    primary_char_end: int = 0

    # Other mentions across sections
    mentions: list[FileMention] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "primary": {
                "section": self.primary_section,
                "char_start": self.primary_char_start,
                "char_end": self.primary_char_end,
            },
            "mentions": [m.to_dict() for m in self.mentions],
        }


@dataclass
class FileEntry:
    """Index entry for a specific file in the codebase."""

    path: str
    purpose: str = ""
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)

    # Position tracking for markdown extraction
    positions: FilePositions = field(default_factory=FilePositions)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "path": self.path,
            "purpose": self.purpose,
            "classes": self.classes,
            "functions": self.functions,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
            "patterns": self.patterns,
            "positions": self.positions.to_dict(),
        }


@dataclass
class SectionIndex:
    """Index entry for a top-level section."""

    name: str
    header: str  # The actual markdown header (e.g., "## Project Overview")
    line_start: int = 0
    line_end: int = 0
    char_start: int = 0
    char_end: int = 0
    files_mentioned: list[str] = field(default_factory=list)
    functions_mentioned: list[str] = field(default_factory=list)
    classes_mentioned: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    summary: str = ""
    subsections: list[SubsectionIndex] = field(default_factory=list)
    file_entries: dict[str, FileEntry] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        result: dict[str, Any] = {
            "name": self.name,
            "header": self.header,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "files_mentioned": self.files_mentioned,
            "functions_mentioned": self.functions_mentioned,
            "classes_mentioned": self.classes_mentioned,
            "patterns": self.patterns,
            "topics": self.topics,
            "summary": self.summary,
        }
        if self.subsections:
            result["subsections"] = [s.to_dict() for s in self.subsections]
        if self.file_entries:
            result["file_entries"] = {k: v.to_dict() for k, v in self.file_entries.items()}
        return result


@dataclass
class AnalysisIndex:
    """Complete index for VIBE-ANALYSIS.md."""

    generated: str = ""
    total_lines: int = 0
    total_chars: int = 0
    sections: list[SectionIndex] = field(default_factory=list)

    # Quick lookup maps (built from sections)
    _file_to_sections: dict[str, list[str]] = field(default_factory=dict, repr=False)
    _topic_to_sections: dict[str, list[str]] = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "generated": self.generated,
            "total_lines": self.total_lines,
            "total_chars": self.total_chars,
            "sections": [s.to_dict() for s in self.sections],
            "file_to_sections": self._file_to_sections,
            "topic_to_sections": self._topic_to_sections,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, path: Path) -> None:
        """Save index to JSON file."""
        path.write_text(self.to_json(), encoding="utf-8")

    def build_lookup_maps(self) -> None:
        """Build quick lookup maps from sections."""
        self._file_to_sections = {}
        self._topic_to_sections = {}

        for section in self.sections:
            # Map files to sections
            for file_path in section.files_mentioned:
                if file_path not in self._file_to_sections:
                    self._file_to_sections[file_path] = []
                if section.name not in self._file_to_sections[file_path]:
                    self._file_to_sections[file_path].append(section.name)

            # Map topics to sections
            for topic in section.topics:
                if topic not in self._topic_to_sections:
                    self._topic_to_sections[topic] = []
                if section.name not in self._topic_to_sections[topic]:
                    self._topic_to_sections[topic].append(section.name)

    @classmethod
    def from_json(cls, json_str: str) -> AnalysisIndex:
        """Load index from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnalysisIndex:
        """Load index from dict."""
        index = cls(
            generated=data.get("generated", ""),
            total_lines=data.get("total_lines", 0),
            total_chars=data.get("total_chars", 0),
        )

        for section_data in data.get("sections", []):
            section = SectionIndex(
                name=section_data.get("name", ""),
                header=section_data.get("header", ""),
                line_start=section_data.get("line_start", 0),
                line_end=section_data.get("line_end", 0),
                char_start=section_data.get("char_start", 0),
                char_end=section_data.get("char_end", 0),
                files_mentioned=section_data.get("files_mentioned", []),
                functions_mentioned=section_data.get("functions_mentioned", []),
                classes_mentioned=section_data.get("classes_mentioned", []),
                patterns=section_data.get("patterns", []),
                topics=section_data.get("topics", []),
                summary=section_data.get("summary", ""),
            )

            # Load subsections
            for sub_data in section_data.get("subsections", []):
                section.subsections.append(SubsectionIndex(
                    name=sub_data.get("name", ""),
                    line_start=sub_data.get("line_start", 0),
                    line_end=sub_data.get("line_end", 0),
                    char_start=sub_data.get("char_start", 0),
                    char_end=sub_data.get("char_end", 0),
                    files_mentioned=sub_data.get("files_mentioned", []),
                    topics=sub_data.get("topics", []),
                ))

            # Load file entries
            for file_path, entry_data in section_data.get("file_entries", {}).items():
                # Parse positions if present
                positions = FilePositions()
                if "positions" in entry_data:
                    pos_data = entry_data["positions"]
                    if "primary" in pos_data:
                        primary = pos_data["primary"]
                        positions.primary_section = primary.get("section", "")
                        positions.primary_char_start = primary.get("char_start", 0)
                        positions.primary_char_end = primary.get("char_end", 0)
                    for mention_data in pos_data.get("mentions", []):
                        positions.mentions.append(FileMention(
                            section=mention_data.get("section", ""),
                            char_start=mention_data.get("char_start", 0),
                            char_end=mention_data.get("char_end", 0),
                            context_type=mention_data.get("context_type", ""),
                        ))

                section.file_entries[file_path] = FileEntry(
                    path=entry_data.get("path", file_path),
                    purpose=entry_data.get("purpose", ""),
                    classes=entry_data.get("classes", []),
                    functions=entry_data.get("functions", []),
                    dependencies=entry_data.get("dependencies", []),
                    dependents=entry_data.get("dependents", []),
                    patterns=entry_data.get("patterns", []),
                    positions=positions,
                )

            index.sections.append(section)

        # Load or rebuild lookup maps
        if "file_to_sections" in data:
            index._file_to_sections = data["file_to_sections"]
        if "topic_to_sections" in data:
            index._topic_to_sections = data["topic_to_sections"]

        if not index._file_to_sections or not index._topic_to_sections:
            index.build_lookup_maps()

        return index

    @classmethod
    def load(cls, path: Path) -> AnalysisIndex:
        """Load index from JSON file."""
        return cls.from_json(path.read_text(encoding="utf-8"))


def build_index_from_context(
    index_result: IndexResult,
    glossary: GlossaryResult,
    contracts: ContractsResult | None,
) -> dict[str, Any]:
    """Build pre-computed metadata from generation context.

    This extracts files, functions, classes, patterns, etc. from the
    structured data that will be used when building the full index.

    Args:
        index_result: IndexResult from indexing phase
        glossary: GlossaryResult from glossary phase
        contracts: ContractsResult from contracts phase (optional)

    Returns:
        Dict with pre-computed metadata for each section type
    """
    metadata: dict[str, Any] = {}

    # File Index metadata - per-file details
    file_index_files: dict[str, dict[str, Any]] = {}
    all_files: list[str] = []
    all_classes: list[str] = []
    all_functions: list[str] = []
    all_patterns: list[str] = []

    for file_analysis in index_result.files:
        path = file_analysis.relative_path
        all_files.append(path)

        classes = [c.name for c in file_analysis.classes]
        functions = [f.name for f in file_analysis.functions if f.is_public]

        all_classes.extend(classes)
        all_functions.extend(functions)
        all_patterns.extend(file_analysis.patterns)

        file_index_files[path] = {
            "purpose": file_analysis.purpose,
            "classes": classes,
            "functions": functions,
            "dependencies": file_analysis.dependencies,
            "internal_imports": file_analysis.internal_imports,
            "patterns": file_analysis.patterns,
        }

    metadata["file_index"] = {
        "files": file_index_files,
        "all_files": all_files,
        "all_classes": list(set(all_classes)),
        "all_functions": list(set(all_functions)),
        "all_patterns": list(set(all_patterns)),
    }

    # Contracts metadata
    if contracts:
        hub_files = [f for f, _ in contracts.hub_files[:20]]
        config_files = list(contracts.all_config_files.keys())
        resource_files = list(contracts.all_resources.keys())
        env_vars = list(contracts.all_env_vars.keys())

        # Build dependents map (who depends on each file)
        dependents_map: dict[str, list[str]] = {}
        for edge in contracts.internal_imports:
            target = edge.target_file
            if target not in dependents_map:
                dependents_map[target] = []
            if edge.source_file not in dependents_map[target]:
                dependents_map[target].append(edge.source_file)

        metadata["contracts"] = {
            "hub_files": hub_files,
            "config_files": config_files,
            "resource_files": resource_files,
            "env_vars": env_vars,
            "dependents_map": dependents_map,
            "files_mentioned": list(set(
                hub_files + config_files + resource_files +
                [e.source_file for e in contracts.internal_imports] +
                [e.target_file for e in contracts.internal_imports]
            )),
        }

    # Glossary metadata
    metadata["glossary"] = {
        "terms": list(glossary.entries.keys()),
        "categories": list(set(e.category for e in glossary.entries.values() if e.category)),
    }

    # Detected patterns and frameworks
    metadata["detected"] = {
        "frameworks": index_result.detected_frameworks,
        "patterns": index_result.detected_patterns,
    }

    return metadata


class IndexBuilder:
    """Builds AnalysisIndex while generating VIBE-ANALYSIS.md content."""

    def __init__(self) -> None:
        self.index = AnalysisIndex(
            generated=datetime.now().isoformat(),
        )
        self._current_line = 0
        self._current_char = 0
        self._current_section: SectionIndex | None = None
        self._metadata: dict[str, Any] = {}
        # Track file positions across all sections
        self._file_positions: dict[str, FilePositions] = {}

    def set_metadata(self, metadata: dict[str, Any]) -> None:
        """Set pre-computed metadata from generation context."""
        self._metadata = metadata

    def start_section(
        self,
        name: str,
        header: str,
        topics: list[str] | None = None,
        summary: str = "",
    ) -> None:
        """Start a new section.

        Args:
            name: Section name (e.g., "Project Overview")
            header: Markdown header (e.g., "## Project Overview")
            topics: List of topics this section covers
            summary: Brief summary of section content
        """
        # Close previous section if any
        if self._current_section:
            self._close_current_section()

        self._current_section = SectionIndex(
            name=name,
            header=header,
            line_start=self._current_line,
            char_start=self._current_char,
            topics=topics or [],
            summary=summary,
        )

    def add_content(self, content: str) -> None:
        """Add content to current section and track positions.

        Args:
            content: Markdown content to add
        """
        lines = content.split('\n')
        self._current_line += len(lines)
        self._current_char += len(content)

    def add_section_files(self, files: list[str]) -> None:
        """Add files mentioned in current section."""
        if self._current_section:
            self._current_section.files_mentioned.extend(files)

    def add_section_functions(self, functions: list[str]) -> None:
        """Add functions mentioned in current section."""
        if self._current_section:
            self._current_section.functions_mentioned.extend(functions)

    def add_section_classes(self, classes: list[str]) -> None:
        """Add classes mentioned in current section."""
        if self._current_section:
            self._current_section.classes_mentioned.extend(classes)

    def add_section_patterns(self, patterns: list[str]) -> None:
        """Add patterns mentioned in current section."""
        if self._current_section:
            self._current_section.patterns.extend(patterns)

    def add_file_entry(self, file_entry: FileEntry) -> None:
        """Add a file entry to current section (for File Index)."""
        if self._current_section:
            self._current_section.file_entries[file_entry.path] = file_entry

    def record_file_primary_position(
        self,
        file_path: str,
        char_start: int,
        char_end: int,
    ) -> None:
        """Record a file's primary documentation position (in File Index section).

        Args:
            file_path: Path to the file
            char_start: Starting character offset in markdown
            char_end: Ending character offset in markdown
        """
        section_name = self._current_section.name if self._current_section else ""

        if file_path not in self._file_positions:
            self._file_positions[file_path] = FilePositions()

        self._file_positions[file_path].primary_section = section_name
        self._file_positions[file_path].primary_char_start = char_start
        self._file_positions[file_path].primary_char_end = char_end

    def record_file_mention(
        self,
        file_path: str,
        char_start: int,
        char_end: int,
        context_type: str = "",
    ) -> None:
        """Record a mention of a file in the current section.

        Args:
            file_path: Path to the file
            char_start: Starting character offset in markdown
            char_end: Ending character offset in markdown
            context_type: Type of mention (e.g., "hub_file", "architecture", "dependency")
        """
        section_name = self._current_section.name if self._current_section else ""

        if file_path not in self._file_positions:
            self._file_positions[file_path] = FilePositions()

        self._file_positions[file_path].mentions.append(FileMention(
            section=section_name,
            char_start=char_start,
            char_end=char_end,
            context_type=context_type,
        ))

    def get_current_char_position(self) -> int:
        """Get current character position in the markdown.

        Returns:
            Current character offset
        """
        return self._current_char

    def start_subsection(
        self,
        name: str,
        topics: list[str] | None = None,
    ) -> SubsectionIndex:
        """Start a subsection within current section.

        Args:
            name: Subsection name
            topics: Topics this subsection covers

        Returns:
            SubsectionIndex for further updates
        """
        subsection = SubsectionIndex(
            name=name,
            line_start=self._current_line,
            char_start=self._current_char,
            topics=topics or [],
        )
        if self._current_section:
            self._current_section.subsections.append(subsection)
        return subsection

    def end_subsection(self, subsection: SubsectionIndex) -> None:
        """End a subsection, recording end positions."""
        subsection.line_end = self._current_line
        subsection.char_end = self._current_char

    def _close_current_section(self) -> None:
        """Close the current section and add to index."""
        if self._current_section:
            self._current_section.line_end = self._current_line
            self._current_section.char_end = self._current_char

            # Deduplicate lists
            self._current_section.files_mentioned = list(set(
                self._current_section.files_mentioned
            ))
            self._current_section.functions_mentioned = list(set(
                self._current_section.functions_mentioned
            ))
            self._current_section.classes_mentioned = list(set(
                self._current_section.classes_mentioned
            ))
            self._current_section.patterns = list(set(
                self._current_section.patterns
            ))

            self.index.sections.append(self._current_section)
            self._current_section = None

    def finalize(self) -> AnalysisIndex:
        """Finalize the index and return it.

        Returns:
            Complete AnalysisIndex
        """
        # Close any open section
        self._close_current_section()

        # Set totals
        self.index.total_lines = self._current_line
        self.index.total_chars = self._current_char

        # Apply tracked file positions to file entries in all sections
        for section in self.index.sections:
            for file_path, file_entry in section.file_entries.items():
                if file_path in self._file_positions:
                    file_entry.positions = self._file_positions[file_path]

        # Build lookup maps
        self.index.build_lookup_maps()

        return self.index

    def get_file_positions(self) -> dict[str, FilePositions]:
        """Get all tracked file positions.

        Returns:
            Dict mapping file paths to their positions in the markdown
        """
        return self._file_positions