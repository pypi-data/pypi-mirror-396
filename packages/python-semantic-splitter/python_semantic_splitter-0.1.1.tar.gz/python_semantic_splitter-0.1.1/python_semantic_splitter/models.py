"""
Data models for Python semantic splitter.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class DocumentChunk:
    """Represents a semantic chunk of code."""
    content: str
    metadata: Dict[str, Any]
    chunk_type: str  # 'function', 'class', 'module'
    start_line: int
    end_line: int
    chunk_id: str


@dataclass
class ParsedDocument:
    """Represents a parsed Python document with metadata and chunks."""
    content: str
    metadata: Dict[str, Any]
    chunks: List[DocumentChunk]
    document_type: str
    category: str
    file_path: str


@dataclass
class SplitterConfig:
    """Configuration for the Python semantic splitter."""
    max_chunk_size: int = 1000
    min_chunk_size: int = 100
    preserve_functions: bool = True
    preserve_classes: bool = True
    include_docstrings: bool = True
    include_imports: bool = True
    include_global_vars: bool = True
