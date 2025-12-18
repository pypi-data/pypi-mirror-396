"""Init Discovery - File Discovery and Tree Structure Generation

This module handles the first phase of /init:
- Scan codebase for all relevant files
- Build directory tree structure
- Identify package files, configs, documentation, entry points
- Filter out ignored files (.gitignore, common excludes)
"""

from __future__ import annotations

from dataclasses import dataclass, field
import fnmatch
from pathlib import Path

# File size limits
MAX_FILE_SIZE_BYTES = 512 * 1024  # 512KB - files larger than this get chunked
CHUNK_SIZE_CHARS = 8000  # Characters per chunk for large files

# Common patterns to ignore
DEFAULT_IGNORE_PATTERNS = [
    ".git",
    ".git/*",
    "__pycache__",
    "__pycache__/*",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
    ".pytest_cache/*",
    ".mypy_cache",
    ".mypy_cache/*",
    ".ruff_cache",
    ".ruff_cache/*",
    "node_modules",
    "node_modules/*",
    ".venv",
    ".venv/*",
    "venv",
    "venv/*",
    ".env",
    ".env.*",
    "*.egg-info",
    "*.egg-info/*",
    "dist",
    "dist/*",
    "build",
    "build/*",
    "*.min.js",
    "*.min.css",
    "*.bundle.js",
    "*.map",
    ".DS_Store",
    "Thumbs.db",
    "*.log",
    "*.lock",
    "uv.lock",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "*.sqlite",
    "*.db",
    "coverage",
    "coverage/*",
    ".coverage",
    "htmlcov",
    "htmlcov/*",
    ".idea",
    ".idea/*",
    ".vscode",
    ".vscode/*",
    "*.whl",
    "*.tar.gz",
    "*.zip",
]

# File extensions to analyze
SOURCE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".java", ".kt", ".scala",
    ".go", ".rs", ".c", ".cpp", ".h", ".hpp",
    ".rb", ".php", ".swift", ".m",
    ".cs", ".fs", ".vb",
    ".sh", ".bash", ".zsh",
    ".sql", ".graphql",
}

CONFIG_EXTENSIONS = {
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".xml", ".conf", ".config",
}

DOC_EXTENSIONS = {
    ".md", ".rst", ".txt", ".adoc",
}

# Package/config files to always include
PACKAGE_FILES = {
    "package.json",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "Pipfile",
    "Cargo.toml",
    "go.mod",
    "Gemfile",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "Makefile",
    "CMakeLists.txt",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".dockerignore",
}

# Entry point patterns
ENTRY_POINT_PATTERNS = [
    "main.py", "app.py", "index.py", "__main__.py", "cli.py",
    "main.js", "index.js", "app.js", "server.js",
    "main.ts", "index.ts", "app.ts",
    "Main.java", "Application.java",
    "main.go", "cmd/main.go",
    "main.rs", "lib.rs",
]


@dataclass
class FileInfo:
    """Information about a discovered file."""

    path: Path
    relative_path: str
    size_bytes: int
    extension: str
    file_type: str  # "source", "config", "doc", "package", "entry_point", "other"
    needs_chunking: bool = False
    chunk_count: int = 1


@dataclass
class DiscoveryResult:
    """Result of codebase discovery."""

    root_path: Path
    files: list[FileInfo] = field(default_factory=list)
    tree_structure: str = ""
    package_files: list[FileInfo] = field(default_factory=list)
    entry_points: list[FileInfo] = field(default_factory=list)
    source_files: list[FileInfo] = field(default_factory=list)
    config_files: list[FileInfo] = field(default_factory=list)
    doc_files: list[FileInfo] = field(default_factory=list)
    total_files: int = 0
    total_source_files: int = 0
    ignored_patterns: list[str] = field(default_factory=list)


def load_gitignore_patterns(root_path: Path) -> list[str]:
    """Load patterns from .gitignore file."""
    patterns = list(DEFAULT_IGNORE_PATTERNS)
    gitignore_path = root_path / ".gitignore"

    if gitignore_path.exists():
        try:
            content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
        except OSError:
            pass

    return patterns


def is_ignored(path: Path, root_path: Path, patterns: list[str]) -> bool:
    """Check if a path should be ignored based on patterns."""
    try:
        relative = path.relative_to(root_path)
        rel_str = str(relative)

        for pattern in patterns:
            # Handle directory patterns
            if pattern.endswith("/"):
                if path.is_dir() and fnmatch.fnmatch(f"{rel_str}/", pattern):
                    return True
            # Handle glob patterns
            elif fnmatch.fnmatch(rel_str, pattern):
                return True
            elif fnmatch.fnmatch(path.name, pattern):
                return True
            # Check each path component
            for part in relative.parts:
                if fnmatch.fnmatch(part, pattern.rstrip("/*")):
                    return True
    except (ValueError, OSError):
        return True

    return False


def classify_file(path: Path, root_path: Path) -> str:
    """Classify a file by its type."""
    name = path.name
    ext = path.suffix.lower()

    # Check for package files first
    if name in PACKAGE_FILES:
        return "package"

    # Check for entry points
    rel_path = str(path.relative_to(root_path))
    for pattern in ENTRY_POINT_PATTERNS:
        if fnmatch.fnmatch(rel_path, f"**/{pattern}") or name == pattern:
            return "entry_point"

    # Classify by extension
    if ext in SOURCE_EXTENSIONS:
        return "source"
    if ext in CONFIG_EXTENSIONS:
        return "config"
    if ext in DOC_EXTENSIONS:
        return "doc"

    return "other"


def build_tree_structure(
    root_path: Path,
    ignore_patterns: list[str],
    max_depth: int = 6,
    max_files_per_dir: int = 50,
) -> str:
    """Build a directory tree structure string."""
    lines = [f"{root_path.name}/"]

    def walk_dir(dir_path: Path, prefix: str, depth: int) -> None:
        if depth > max_depth:
            return

        try:
            items = sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except (PermissionError, OSError):
            return

        # Filter ignored items
        items = [item for item in items if not is_ignored(item, root_path, ignore_patterns)]

        # Limit items per directory
        show_truncation = len(items) > max_files_per_dir
        if show_truncation:
            items = items[:max_files_per_dir]

        for i, item in enumerate(items):
            is_last = i == len(items) - 1 and not show_truncation
            connector = "└── " if is_last else "├── "

            if item.is_dir():
                lines.append(f"{prefix}{connector}{item.name}/")
                child_prefix = prefix + ("    " if is_last else "│   ")
                walk_dir(item, child_prefix, depth + 1)
            else:
                lines.append(f"{prefix}{connector}{item.name}")

        if show_truncation:
            remaining = len(list(dir_path.iterdir())) - max_files_per_dir
            lines.append(f"{prefix}└── ... ({remaining} more items)")

    walk_dir(root_path, "", 1)
    return "\n".join(lines)


def discover_codebase(root_path: Path) -> DiscoveryResult:
    """Discover all relevant files in the codebase.

    Args:
        root_path: Root directory to scan

    Returns:
        DiscoveryResult with all discovered files and metadata
    """
    result = DiscoveryResult(root_path=root_path)
    ignore_patterns = load_gitignore_patterns(root_path)
    result.ignored_patterns = ignore_patterns

    # Build tree structure
    result.tree_structure = build_tree_structure(root_path, ignore_patterns)

    # Walk the directory tree
    for item in root_path.rglob("*"):
        if not item.is_file():
            continue

        if is_ignored(item, root_path, ignore_patterns):
            continue

        try:
            size = item.stat().st_size
        except OSError:
            continue

        # Skip very large files (likely binary/generated)
        if size > MAX_FILE_SIZE_BYTES * 4:
            continue

        file_type = classify_file(item, root_path)

        # Skip "other" files unless they're small text files
        if file_type == "other":
            # Check if it might be a script without extension
            if size < 1024:
                try:
                    first_line = item.read_text(errors="ignore")[:100]
                    if first_line.startswith("#!"):
                        file_type = "source"
                    else:
                        continue
                except OSError:
                    continue
            else:
                continue

        needs_chunking = size > MAX_FILE_SIZE_BYTES
        chunk_count = max(1, size // (CHUNK_SIZE_CHARS * 4)) if needs_chunking else 1

        file_info = FileInfo(
            path=item,
            relative_path=str(item.relative_to(root_path)),
            size_bytes=size,
            extension=item.suffix.lower(),
            file_type=file_type,
            needs_chunking=needs_chunking,
            chunk_count=chunk_count,
        )

        result.files.append(file_info)

        # Categorize
        match file_type:
            case "package":
                result.package_files.append(file_info)
            case "entry_point":
                result.entry_points.append(file_info)
                result.source_files.append(file_info)
            case "source":
                result.source_files.append(file_info)
            case "config":
                result.config_files.append(file_info)
            case "doc":
                result.doc_files.append(file_info)

    result.total_files = len(result.files)
    result.total_source_files = len(result.source_files)

    # Sort files by importance (entry points first, then by path)
    result.files.sort(key=lambda f: (
        0 if f.file_type == "entry_point" else
        1 if f.file_type == "package" else
        2 if f.file_type == "source" else
        3 if f.file_type == "config" else
        4,
        f.relative_path
    ))

    return result


def get_file_content(file_info: FileInfo, chunk_index: int = 0) -> str:
    """Read file content, optionally returning a specific chunk for large files.

    Args:
        file_info: FileInfo for the file to read
        chunk_index: Which chunk to return (0-indexed) for large files

    Returns:
        File content or chunk content
    """
    try:
        content = file_info.path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""

    if not file_info.needs_chunking:
        return content

    # Split into chunks
    start = chunk_index * CHUNK_SIZE_CHARS
    end = start + CHUNK_SIZE_CHARS

    # Try to break at line boundaries
    if end < len(content):
        next_newline = content.find("\n", end)
        if next_newline != -1 and next_newline < end + 500:
            end = next_newline + 1

    return content[start:end]


def get_chunk_count(file_info: FileInfo) -> int:
    """Get the number of chunks for a file."""
    if not file_info.needs_chunking:
        return 1

    try:
        content = file_info.path.read_text(encoding="utf-8", errors="ignore")
        return max(1, (len(content) + CHUNK_SIZE_CHARS - 1) // CHUNK_SIZE_CHARS)
    except OSError:
        return 1