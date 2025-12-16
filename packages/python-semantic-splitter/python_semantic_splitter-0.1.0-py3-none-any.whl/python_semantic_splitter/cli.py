"""
Command-line interface for Python Semantic Splitter.
"""
import argparse
import json
import os
import sys
from typing import Dict, Any

from .splitter import PythonSplitter
from .models import SplitterConfig


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Python Semantic Splitter - Split Python code into semantic chunks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split a single file
  python-splitter split my_code.py
  
  # Split with custom configuration
  python-splitter split --max-size 1500 --no-docstrings my_code.py
  
  # Split directory recursively
  python-splitter split-dir ./src --output chunks.json
  
  # Analyze without splitting
  python-splitter analyze my_code.py
        """
    )
    
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Split file command
    split_parser = subparsers.add_parser('split', help='Split a Python file')
    split_parser.add_argument('file', help='Python file to split')
    split_parser.add_argument('--output', '-o', help='Output file (JSON format)')
    split_parser.add_argument('--max-size', type=int, default=1000, help='Maximum chunk size')
    split_parser.add_argument('--min-size', type=int, default=100, help='Minimum chunk size')
    split_parser.add_argument('--no-functions', action='store_true', help='Don\'t preserve functions')
    split_parser.add_argument('--no-classes', action='store_true', help='Don\'t preserve classes')
    split_parser.add_argument('--no-docstrings', action='store_true', help='Don\'t include docstrings')
    split_parser.add_argument('--no-imports', action='store_true', help='Don\'t include imports')
    split_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Split directory command
    splitdir_parser = subparsers.add_parser('split-dir', help='Split all Python files in a directory')
    splitdir_parser.add_argument('directory', help='Directory to process')
    splitdir_parser.add_argument('--output', '-o', required=True, help='Output file (JSON format)')
    splitdir_parser.add_argument('--pattern', default='*.py', help='File pattern to match')
    splitdir_parser.add_argument('--no-recursive', action='store_true', help='Don\'t search recursively')
    splitdir_parser.add_argument('--max-size', type=int, default=1000, help='Maximum chunk size')
    splitdir_parser.add_argument('--min-size', type=int, default=100, help='Minimum chunk size')
    splitdir_parser.add_argument('--no-functions', action='store_true', help='Don\'t preserve functions')
    splitdir_parser.add_argument('--no-classes', action='store_true', help='Don\'t preserve classes')
    splitdir_parser.add_argument('--no-docstrings', action='store_true', help='Don\'t include docstrings')
    splitdir_parser.add_argument('--no-imports', action='store_true', help='Don\'t include imports')
    splitdir_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a Python file without splitting')
    analyze_parser.add_argument('file', help='Python file to analyze')
    analyze_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    return parser


def create_config_from_args(args) -> SplitterConfig:
    """Create a SplitterConfig from command-line arguments."""
    return SplitterConfig(
        max_chunk_size=getattr(args, 'max_size', 1000),
        min_chunk_size=getattr(args, 'min_size', 100),
        preserve_functions=not getattr(args, 'no_functions', False),
        preserve_classes=not getattr(args, 'no_classes', False),
        include_docstrings=not getattr(args, 'no_docstrings', False),
        include_imports=not getattr(args, 'no_imports', False),
    )


def print_chunk_summary(chunks, verbose=False):
    """Print a summary of the chunks."""
    if not chunks:
        print("No chunks found.")
        return
    
    # Count chunk types
    chunk_types = {}
    total_lines = 0
    total_chars = 0
    
    for chunk in chunks:
        chunk_types[chunk.chunk_type] = chunk_types.get(chunk.chunk_type, 0) + 1
        lines = chunk.end_line - chunk.start_line + 1
        total_lines += lines
        total_chars += len(chunk.content)
    
    print(f"📊 CHUNK SUMMARY:")
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Total lines: {total_lines:,}")
    print(f"  Total characters: {total_chars:,}")
    print(f"  Average chunk size: {total_chars // len(chunks):,} chars")
    
    print(f"\n📄 CHUNK TYPES:")
    for chunk_type, count in chunk_types.items():
        print(f"  {chunk_type.title()}: {count}")
    
    if verbose:
        print(f"\n📋 CHUNK DETAILS:")
        print("-" * 50)
        
        for i, chunk in enumerate(chunks, 1):
            # Get chunk name from metadata
            if chunk.chunk_type == 'function':
                name = chunk.metadata.get('function_name', 'unknown')
            elif chunk.chunk_type == 'class':
                name = chunk.metadata.get('class_name', 'unknown')
            else:
                name = chunk.chunk_type
            
            lines = chunk.end_line - chunk.start_line + 1
            chars = len(chunk.content)
            
            print(f"{i:2d}. {chunk.chunk_type.upper()}: {name}")
            print(f"    Lines: {chunk.start_line}-{chunk.end_line} ({lines} lines)")
            print(f"    Size: {chars:,} chars")
            
            # Show first line of content (cleaned)
            first_line = chunk.content.split('\n')[0].strip()
            if len(first_line) > 60:
                first_line = first_line[:60] + "..."
            print(f"    Start: {first_line}")
            print()


def cmd_split(args):
    """Handle the split command."""
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        return 1
    
    if not args.file.endswith('.py'):
        print(f"Error: File must be a Python file (.py): {args.file}")
        return 1
    
    try:
        config = create_config_from_args(args)
        splitter = PythonSplitter(config)
        
        if args.verbose:
            print(f"🔍 Splitting: {args.file}")
        
        chunks = splitter.split_file(args.file)
        
        if args.output:
            splitter.export_chunks(chunks, args.output, "json")
            print(f"💾 Chunks saved to: {args.output}")
        
        print_chunk_summary(chunks, args.verbose)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_split_dir(args):
    """Handle the split-dir command."""
    if not os.path.exists(args.directory):
        print(f"Error: Directory not found: {args.directory}")
        return 1
    
    if not os.path.isdir(args.directory):
        print(f"Error: Path is not a directory: {args.directory}")
        return 1
    
    try:
        config = create_config_from_args(args)
        splitter = PythonSplitter(config)
        
        if args.verbose:
            print(f"🔍 Processing directory: {args.directory}")
            print(f"   Pattern: {args.pattern}")
            print(f"   Recursive: {not args.no_recursive}")
        
        results = splitter.split_directory(
            args.directory,
            pattern=args.pattern,
            recursive=not args.no_recursive
        )
        
        # Flatten results for export
        all_chunks = []
        file_stats = {}
        
        for file_path, chunks in results.items():
            file_stats[file_path] = len(chunks)
            for chunk in chunks:
                all_chunks.append({
                    'content': chunk.content,
                    'metadata': chunk.metadata,
                    'chunk_type': chunk.chunk_type,
                    'start_line': chunk.start_line,
                    'end_line': chunk.end_line,
                    'chunk_id': chunk.chunk_id,
                    'source_file': file_path
                })
        
        # Save results
        output_data = {
            'summary': {
                'total_files': len(results),
                'total_chunks': len(all_chunks),
                'files_processed': file_stats
            },
            'chunks': all_chunks
        }
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Results saved to: {args.output}")
        print(f"📊 Processed {len(results)} files, created {len(all_chunks)} chunks")
        
        if args.verbose:
            print(f"\n📁 FILES PROCESSED:")
            for file_path, chunk_count in file_stats.items():
                print(f"  {os.path.basename(file_path)}: {chunk_count} chunks")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_analyze(args):
    """Handle the analyze command."""
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        return 1
    
    if not args.file.endswith('.py'):
        print(f"Error: File must be a Python file (.py): {args.file}")
        return 1
    
    try:
        config = SplitterConfig()  # Use default config for analysis
        splitter = PythonSplitter(config)
        
        print(f"🔍 ANALYZING: {args.file}")
        print("=" * 50)
        
        chunks = splitter.split_file(args.file)
        
        # Get the parsed document for metadata
        parsed_doc = splitter.parser.parse(args.file)
        metadata = parsed_doc.metadata
        
        print(f"📄 FILE INFO:")
        print(f"  Language: {metadata['language']}")
        print(f"  Total lines: {metadata['total_lines']:,}")
        print(f"  Functions: {len(metadata['functions'])}")
        print(f"  Classes: {len(metadata['classes'])}")
        print(f"  Imports: {len(metadata['imports'])}")
        print(f"  Dependencies: {len(metadata['dependencies'])}")
        
        if metadata['module_docstring']:
            print(f"\n📝 MODULE DOCSTRING:")
            docstring = metadata['module_docstring'][:200]
            print(f"  {docstring}{'...' if len(metadata['module_docstring']) > 200 else ''}")
        
        print_chunk_summary(chunks, args.verbose)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'split':
        return cmd_split(args)
    elif args.command == 'split-dir':
        return cmd_split_dir(args)
    elif args.command == 'analyze':
        return cmd_analyze(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
