"""
Main splitter class for Python semantic splitting.
"""
import os
import glob
from typing import List, Dict, Any, Optional, Union
from .models import DocumentChunk, SplitterConfig
from .parser import PythonParser


class PythonSplitter:
    """Main class for splitting Python code into semantic chunks."""
    
    def __init__(self, config: Optional[SplitterConfig] = None):
        """Initialize the splitter with optional configuration."""
        self.config = config or SplitterConfig()
        self.parser = PythonParser(self.config)
    
    def split_file(self, file_path: str, category: str = "python") -> List[DocumentChunk]:
        """
        Split a single Python file into semantic chunks.
        
        Args:
            file_path: Path to the Python file
            category: Category for the document (default: "python")
            
        Returns:
            List of DocumentChunk objects
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.endswith('.py'):
            raise ValueError(f"File must be a Python file (.py): {file_path}")
        
        parsed_doc = self.parser.parse(file_path, category)
        return parsed_doc.chunks
    
    def split_directory(self, 
                       directory: str, 
                       pattern: str = "*.py",
                       recursive: bool = True,
                       category: str = "python") -> Dict[str, List[DocumentChunk]]:
        """
        Split all Python files in a directory into semantic chunks.
        
        Args:
            directory: Path to the directory
            pattern: File pattern to match (default: "*.py")
            recursive: Whether to search recursively (default: True)
            category: Category for the documents (default: "python")
            
        Returns:
            Dictionary mapping file paths to lists of DocumentChunk objects
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not os.path.isdir(directory):
            raise ValueError(f"Path is not a directory: {directory}")
        
        # Find all Python files
        if recursive:
            search_pattern = os.path.join(directory, "**", pattern)
            files = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = os.path.join(directory, pattern)
            files = glob.glob(search_pattern)
        
        results = {}
        for file_path in files:
            try:
                chunks = self.split_file(file_path, category)
                results[file_path] = chunks
            except Exception as e:
                print(f"Warning: Failed to process {file_path}: {e}")
                results[file_path] = []
        
        return results
    
    def split_text(self, 
                   code_text: str, 
                   file_name: str = "inline.py",
                   category: str = "python") -> List[DocumentChunk]:
        """
        Split Python code text into semantic chunks.
        
        Args:
            code_text: Python code as string
            file_name: Virtual file name for identification
            category: Category for the document (default: "python")
            
        Returns:
            List of DocumentChunk objects
        """
        # Create a temporary file to parse
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code_text)
            temp_path = f.name
        
        try:
            parsed_doc = self.parser.parse(temp_path, category)
            # Update chunk IDs to use the provided file name
            for chunk in parsed_doc.chunks:
                chunk.chunk_id = chunk.chunk_id.replace(temp_path, file_name)
                chunk.metadata['file_path'] = file_name
            return parsed_doc.chunks
        finally:
            os.unlink(temp_path)
    
    def get_stats(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Get statistics about the chunks.
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            Dictionary with statistics
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'chunk_types': {},
                'total_lines': 0,
                'total_characters': 0,
                'average_chunk_size': 0
            }
        
        chunk_types = {}
        total_lines = 0
        total_characters = 0
        
        for chunk in chunks:
            # Count chunk types
            chunk_types[chunk.chunk_type] = chunk_types.get(chunk.chunk_type, 0) + 1
            
            # Count lines and characters
            lines = chunk.end_line - chunk.start_line + 1
            total_lines += lines
            total_characters += len(chunk.content)
        
        return {
            'total_chunks': len(chunks),
            'chunk_types': chunk_types,
            'total_lines': total_lines,
            'total_characters': total_characters,
            'average_chunk_size': total_characters // len(chunks) if chunks else 0
        }
    
    def export_chunks(self, 
                     chunks: List[DocumentChunk], 
                     output_path: str,
                     format: str = "json") -> None:
        """
        Export chunks to a file.
        
        Args:
            chunks: List of DocumentChunk objects
            output_path: Path to save the output
            format: Output format ("json" or "yaml")
        """
        import json
        
        # Convert chunks to serializable format
        chunks_data = []
        for chunk in chunks:
            chunk_dict = {
                'content': chunk.content,
                'metadata': chunk.metadata,
                'chunk_type': chunk.chunk_type,
                'start_line': chunk.start_line,
                'end_line': chunk.end_line,
                'chunk_id': chunk.chunk_id
            }
            chunks_data.append(chunk_dict)
        
        if format.lower() == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(chunks_data, f, indent=2, ensure_ascii=False, default=str)
        elif format.lower() == "yaml":
            try:
                import yaml
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(chunks_data, f, default_flow_style=False, allow_unicode=True)
            except ImportError:
                raise ImportError("PyYAML is required for YAML export. Install with: pip install PyYAML")
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'yaml'")
    
    def filter_chunks(self, 
                     chunks: List[DocumentChunk],
                     chunk_type: Optional[str] = None,
                     min_size: Optional[int] = None,
                     max_size: Optional[int] = None,
                     has_docstring: Optional[bool] = None) -> List[DocumentChunk]:
        """
        Filter chunks based on criteria.
        
        Args:
            chunks: List of DocumentChunk objects
            chunk_type: Filter by chunk type ('function', 'class', 'module')
            min_size: Minimum chunk size in characters
            max_size: Maximum chunk size in characters
            has_docstring: Filter by presence of docstring
            
        Returns:
            Filtered list of DocumentChunk objects
        """
        filtered = chunks
        
        if chunk_type:
            filtered = [c for c in filtered if c.chunk_type == chunk_type]
        
        if min_size is not None:
            filtered = [c for c in filtered if len(c.content) >= min_size]
        
        if max_size is not None:
            filtered = [c for c in filtered if len(c.content) <= max_size]
        
        if has_docstring is not None:
            if has_docstring:
                filtered = [c for c in filtered if c.metadata.get('docstring')]
            else:
                filtered = [c for c in filtered if not c.metadata.get('docstring')]
        
        return filtered
