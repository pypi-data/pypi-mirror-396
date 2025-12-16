"""
Python Semantic Splitter - Intelligent code splitting for AI/RAG pipelines.

This package provides semantic-aware splitting of Python code into meaningful chunks
while preserving code structure and context.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Semantic Python code splitter for AI/RAG pipelines"

from .models import DocumentChunk, ParsedDocument, SplitterConfig
from .parser import PythonParser
from .splitter import PythonSplitter

# Main API exports
__all__ = [
    "PythonSplitter",
    "PythonParser", 
    "DocumentChunk",
    "ParsedDocument",
    "SplitterConfig",
]

# Convenience function for quick usage
def split_python_file(file_path: str, **kwargs) -> list:
    """
    Quick function to split a Python file into semantic chunks.
    
    Args:
        file_path: Path to the Python file
        **kwargs: Additional arguments passed to SplitterConfig
        
    Returns:
        List of DocumentChunk objects
    """
    config = SplitterConfig(**kwargs) if kwargs else None
    splitter = PythonSplitter(config)
    return splitter.split_file(file_path)

def split_python_text(code_text: str, **kwargs) -> list:
    """
    Quick function to split Python code text into semantic chunks.
    
    Args:
        code_text: Python code as string
        **kwargs: Additional arguments passed to SplitterConfig
        
    Returns:
        List of DocumentChunk objects
    """
    config = SplitterConfig(**kwargs) if kwargs else None
    splitter = PythonSplitter(config)
    return splitter.split_text(code_text)
