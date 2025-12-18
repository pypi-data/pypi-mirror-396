"""Analyze Command Module - VIBE-ANALYSIS.md Generation

This module provides the /analyze command implementation for Vibe CLI.
The command analyzes the codebase and generates a comprehensive VIBE-ANALYSIS.md file.

## Generation Strategy

The /analyze command uses a multi-phase approach for maximum accuracy:

### Phase 1: Discovery
- Scan codebase for all relevant files
- Build directory tree structure
- Identify package files, configs, entry points

### Phase 2: Indexing (builds INDEX data)
- Analyze each file (chunking large files)
- Extract: purpose, exports, classes, functions, patterns, relationships
- Track internal imports, config usage, cross-file calls
- Multiple LLM iterations as needed per file

### Phase 3: Glossary Extraction (builds GLOSSARY data)
- Extract acronyms, domain terms, project jargon from indexed content
- Provides accurate terminology for final generation

### Phase 4: Contracts Extraction (builds CONTRACTS data)
- Aggregate file relationships from indexed content
- Build dependency graph
- Identify hub files (high connectivity)
- Track config/resource dependencies, env vars, shared state

### Phase 5: VIBE-ANALYSIS.md Generation
- Uses INDEX + GLOSSARY + CONTRACTS as context for accuracy
- Generates each section separately with controlled headers
- Deterministic structure for reliable parsing
- Appends code-generated sections (contracts, index, glossary)

## Output Structure

The generated VIBE-ANALYSIS.md includes (in order):
1. Project Overview (LLM-generated)
2. Technology Stack (LLM-generated)
3. Development Commands (LLM-generated)
4. Code Style Guidelines (LLM-generated)
5. Architecture Overview (LLM-generated)
6. File Contracts & Dependencies (code-generated)
7. Project Structure (code-generated tree)
8. File Index (code-generated, detailed)
9. Glossary (code-generated)

All section headers are controlled by code for reliable parsing.
"""
from __future__ import annotations

from vibe.cli.analyze.contracts import ContractsResult, extract_contracts
from vibe.cli.analyze.executor import execute_analyze
from vibe.cli.analyze.generator import get_section_names

__all__ = ["execute_analyze", "extract_contracts", "ContractsResult", "get_section_names"]