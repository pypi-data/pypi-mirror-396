"""Init Contracts - File Dependency and Relationship Analysis

This module handles Phase 4 of /init:
- Aggregate relationships from indexed files
- Build dependency graphs
- Identify hub files (high connectivity)
- Generate contracts section for VIBE-ANALYSIS.md
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vibe.cli.analyze.indexer import IndexResult


@dataclass
class DependencyEdge:
    """An edge in the dependency graph."""

    source_file: str
    target_file: str
    relationship_type: str  # import, config, resource, calls, inherits, etc.
    details: str = ""


@dataclass
class FileNode:
    """A node in the dependency graph representing a file."""

    path: str
    incoming: list[DependencyEdge] = field(default_factory=list)  # Files that depend on this
    outgoing: list[DependencyEdge] = field(default_factory=list)  # Files this depends on

    @property
    def in_degree(self) -> int:
        """Number of files that depend on this file."""
        return len(self.incoming)

    @property
    def out_degree(self) -> int:
        """Number of files this file depends on."""
        return len(self.outgoing)

    @property
    def total_degree(self) -> int:
        """Total connectivity."""
        return self.in_degree + self.out_degree


@dataclass
class ContractsResult:
    """Aggregated contracts and dependency analysis."""

    # Dependency graph
    nodes: dict[str, FileNode] = field(default_factory=dict)

    # Categorized relationships
    internal_imports: list[DependencyEdge] = field(default_factory=list)
    config_dependencies: list[DependencyEdge] = field(default_factory=list)
    resource_dependencies: list[DependencyEdge] = field(default_factory=list)
    cross_file_calls: list[DependencyEdge] = field(default_factory=list)

    # Aggregated data
    all_env_vars: dict[str, list[str]] = field(default_factory=dict)  # var -> files using it
    all_config_files: dict[str, list[str]] = field(default_factory=dict)  # config -> files using it
    all_resources: dict[str, list[str]] = field(default_factory=dict)  # resource -> files using it
    shared_state_patterns: list[tuple[str, str]] = field(default_factory=list)  # (file, pattern)

    # Analysis
    hub_files: list[tuple[str, int]] = field(default_factory=list)  # (file, degree) sorted by degree
    entry_point_deps: dict[str, list[str]] = field(default_factory=dict)  # entry_point -> direct deps


def extract_contracts(index: IndexResult) -> ContractsResult:
    """Extract and aggregate contracts/relationships from indexed files.

    Args:
        index: IndexResult with all file analyses

    Returns:
        ContractsResult with aggregated dependency information
    """
    result = ContractsResult()

    # Process each file's relationships
    for file_analysis in index.files:
        source = file_analysis.relative_path

        # Ensure node exists
        if source not in result.nodes:
            result.nodes[source] = FileNode(path=source)

        # Process internal imports
        for imp in file_analysis.internal_imports:
            # Try to normalize the import to a file path
            target = _normalize_import_to_path(imp)
            if target:
                edge = DependencyEdge(
                    source_file=source,
                    target_file=target,
                    relationship_type="import",
                    details=imp,
                )
                result.internal_imports.append(edge)
                _add_edge_to_graph(result.nodes, edge)

        # Process config file usage
        for config in file_analysis.config_files_used:
            edge = DependencyEdge(
                source_file=source,
                target_file=config,
                relationship_type="config",
                details=f"reads {config}",
            )
            result.config_dependencies.append(edge)
            _add_edge_to_graph(result.nodes, edge)

            # Track which files use this config
            if config not in result.all_config_files:
                result.all_config_files[config] = []
            if source not in result.all_config_files[config]:
                result.all_config_files[config].append(source)

        # Process resource loading
        for resource in file_analysis.resources_loaded:
            edge = DependencyEdge(
                source_file=source,
                target_file=resource,
                relationship_type="resource",
                details=f"loads {resource}",
            )
            result.resource_dependencies.append(edge)
            _add_edge_to_graph(result.nodes, edge)

            # Track which files use this resource
            if resource not in result.all_resources:
                result.all_resources[resource] = []
            if source not in result.all_resources[resource]:
                result.all_resources[resource].append(source)

        # Process cross-file calls
        for call in file_analysis.cross_file_calls:
            if call.target_file:
                edge = DependencyEdge(
                    source_file=source,
                    target_file=call.target_file,
                    relationship_type=call.relationship_type,
                    details=call.details,
                )
                result.cross_file_calls.append(edge)
                _add_edge_to_graph(result.nodes, edge)

        # Process environment variables
        for env_var in file_analysis.env_vars_used:
            if env_var not in result.all_env_vars:
                result.all_env_vars[env_var] = []
            if source not in result.all_env_vars[env_var]:
                result.all_env_vars[env_var].append(source)

        # Process shared state patterns
        for pattern in file_analysis.shared_state:
            result.shared_state_patterns.append((source, pattern))

    # Calculate hub files (highest connectivity)
    result.hub_files = sorted(
        [(path, node.total_degree) for path, node in result.nodes.items()],
        key=lambda x: x[1],
        reverse=True,
    )[:20]  # Top 20 hub files

    # Track entry point dependencies
    for entry in index.entry_points:
        entry_path = entry.relative_path
        if entry_path in result.nodes:
            node = result.nodes[entry_path]
            result.entry_point_deps[entry_path] = [
                edge.target_file for edge in node.outgoing
            ]

    return result


def _normalize_import_to_path(import_str: str) -> str | None:
    """Try to convert an import string to a file path.

    Args:
        import_str: Import string like 'from .config import X' or 'from vibe.core.agent import Agent'

    Returns:
        Normalized path or None if can't be determined
    """
    if not import_str:
        return None

    # Handle various import formats
    import_str = import_str.strip()

    # Extract module path from "from X import Y" or "import X"
    if import_str.startswith("from "):
        # "from .config import X" -> ".config"
        # "from vibe.core.agent import Agent" -> "vibe.core.agent"
        parts = import_str.split(" import ")[0].replace("from ", "").strip()
    elif import_str.startswith("import "):
        parts = import_str.replace("import ", "").strip().split(" as ")[0]
    else:
        parts = import_str

    # Convert dots to path separators
    # Handle relative imports
    if parts.startswith("."):
        # Relative import - keep as is for now, will be resolved in context
        path = parts.replace(".", "/").lstrip("/")
        if path:
            return path + ".py"
        return None

    # Convert module.path.to.file to module/path/to/file.py
    path = parts.replace(".", "/") + ".py"

    # Also check for __init__.py
    # (the actual file might be module/path/__init__.py)

    return path


def _add_edge_to_graph(nodes: dict[str, FileNode], edge: DependencyEdge) -> None:
    """Add an edge to the dependency graph."""
    # Ensure both nodes exist
    if edge.source_file not in nodes:
        nodes[edge.source_file] = FileNode(path=edge.source_file)
    if edge.target_file not in nodes:
        nodes[edge.target_file] = FileNode(path=edge.target_file)

    # Add edge
    nodes[edge.source_file].outgoing.append(edge)
    nodes[edge.target_file].incoming.append(edge)


def format_contracts_as_markdown(contracts: ContractsResult) -> str:
    """Format ContractsResult as markdown for inclusion in VIBE-ANALYSIS.md.

    Args:
        contracts: ContractsResult to format

    Returns:
        Markdown string
    """
    lines = []
    lines.append("## File Contracts & Dependencies\n")
    lines.append("*This section documents the relationships and contracts between files in the codebase.*\n")

    # Hub Files (most connected)
    if contracts.hub_files:
        lines.append("\n### Hub Files\n")
        lines.append("*Files with the most connections (imports, dependencies, calls)*\n")
        lines.append("")
        lines.append("| File | Connections |")
        lines.append("|------|-------------|")
        for path, degree in contracts.hub_files[:10]:
            if degree > 0:
                lines.append(f"| `{path}` | {degree} |")
        lines.append("")

    # Configuration Dependencies
    if contracts.all_config_files:
        lines.append("\n### Configuration Dependencies\n")
        lines.append("*Config files and which source files depend on them*\n")
        for config, users in sorted(contracts.all_config_files.items()):
            lines.append(f"\n**`{config}`** used by:")
            for user in users[:10]:
                lines.append(f"- `{user}`")
            if len(users) > 10:
                lines.append(f"- *...and {len(users) - 10} more*")
        lines.append("")

    # Resource Dependencies
    if contracts.all_resources:
        lines.append("\n### Resource Dependencies\n")
        lines.append("*Templates, static files, and data files*\n")
        for resource, users in sorted(contracts.all_resources.items()):
            lines.append(f"\n**`{resource}`** loaded by:")
            for user in users[:10]:
                lines.append(f"- `{user}`")
            if len(users) > 10:
                lines.append(f"- *...and {len(users) - 10} more*")
        lines.append("")

    # Environment Variables
    if contracts.all_env_vars:
        lines.append("\n### Environment Variables\n")
        lines.append("*Environment variables used across the codebase*\n")
        lines.append("")
        lines.append("| Variable | Used By |")
        lines.append("|----------|---------|")
        for var, users in sorted(contracts.all_env_vars.items()):
            user_list = ", ".join(f"`{u}`" for u in users[:3])
            if len(users) > 3:
                user_list += f" (+{len(users) - 3})"
            lines.append(f"| `{var}` | {user_list} |")
        lines.append("")

    # Internal Import Graph (summarized)
    if contracts.internal_imports:
        lines.append("\n### Internal Import Graph\n")
        lines.append("*How project files import from each other*\n")

        # Group by source file
        imports_by_source: dict[str, list[str]] = defaultdict(list)
        for edge in contracts.internal_imports:
            imports_by_source[edge.source_file].append(edge.target_file)

        # Show top importers
        sorted_sources = sorted(
            imports_by_source.items(),
            key=lambda x: len(x[1]),
            reverse=True,
        )[:15]

        for source, targets in sorted_sources:
            unique_targets = list(set(targets))[:5]
            targets_str = ", ".join(f"`{t}`" for t in unique_targets)
            if len(set(targets)) > 5:
                targets_str += f" (+{len(set(targets)) - 5})"
            lines.append(f"- `{source}` → {targets_str}")
        lines.append("")

    # Cross-File Calls (most interesting relationships)
    if contracts.cross_file_calls:
        lines.append("\n### Cross-File Calls\n")
        lines.append("*Function calls, class instantiations, and inheritance across files*\n")

        # Group by relationship type
        by_type: dict[str, list[DependencyEdge]] = defaultdict(list)
        for edge in contracts.cross_file_calls:
            by_type[edge.relationship_type].append(edge)

        for rel_type, edges in sorted(by_type.items()):
            lines.append(f"\n**{rel_type.title()}:**")
            for edge in edges[:10]:
                detail = f" ({edge.details})" if edge.details else ""
                lines.append(f"- `{edge.source_file}` → `{edge.target_file}`{detail}")
            if len(edges) > 10:
                lines.append(f"- *...and {len(edges) - 10} more*")
        lines.append("")

    # Shared State Patterns
    if contracts.shared_state_patterns:
        lines.append("\n### Shared State Patterns\n")
        lines.append("*Global variables, singletons, and shared state*\n")
        for file, pattern in contracts.shared_state_patterns[:20]:
            lines.append(f"- `{file}`: {pattern}")
        if len(contracts.shared_state_patterns) > 20:
            lines.append(f"- *...and {len(contracts.shared_state_patterns) - 20} more*")
        lines.append("")

    # Entry Point Dependencies
    if contracts.entry_point_deps:
        lines.append("\n### Entry Point Dependencies\n")
        lines.append("*What each entry point directly depends on*\n")
        for entry, deps in contracts.entry_point_deps.items():
            if deps:
                lines.append(f"\n**`{entry}`**:")
                for dep in deps[:10]:
                    lines.append(f"- `{dep}`")
                if len(deps) > 10:
                    lines.append(f"- *...and {len(deps) - 10} more*")
        lines.append("")

    return "\n".join(lines)