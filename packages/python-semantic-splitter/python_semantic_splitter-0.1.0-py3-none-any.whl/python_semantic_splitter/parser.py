"""
Python semantic parser for extracting functions, classes, and modules.
"""
import ast
from typing import Dict, Any, List, Optional
from .models import DocumentChunk, ParsedDocument, SplitterConfig


class PythonParser:
    """Parser for Python code that extracts semantic chunks."""
    
    def __init__(self, config: Optional[SplitterConfig] = None):
        self.config = config or SplitterConfig()
    
    def parse(self, file_path: str, category: str = "python") -> ParsedDocument:
        """Parse a Python file and extract semantic chunks."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            # Parse AST for functions/classes
            tree = ast.parse(content)
        except SyntaxError as e:
            # Handle syntax errors gracefully
            return self._create_error_document(file_path, category, content, str(e))
        
        # Extract metadata
        metadata = self._extract_metadata(tree, file_path, content)
        
        # Create semantic chunks
        chunks = self._create_semantic_chunks(tree, content, file_path)
        
        return ParsedDocument(
            content=content,
            metadata=metadata,
            chunks=chunks,
            document_type="python",
            category=category,
            file_path=file_path
        )
    
    def _create_error_document(self, file_path: str, category: str, content: str, error: str) -> ParsedDocument:
        """Create a document for files with syntax errors."""
        return ParsedDocument(
            content=content,
            metadata={
                'file_path': file_path,
                'language': 'python',
                'error': error,
                'total_lines': len(content.splitlines()),
                'functions': [],
                'classes': [],
                'imports': [],
                'global_variables': [],
                'dependencies': []
            },
            chunks=[],
            document_type="python",
            category=category,
            file_path=file_path
        )
    
    def _create_semantic_chunks(self, tree: ast.AST, content: str, file_path: str) -> List[DocumentChunk]:
        """Create semantically meaningful chunks from Python code."""
        chunks = []
        lines = content.splitlines()

        # Module level chunk (imports + module docstring + global variables)
        if self.config.include_imports or self.config.include_global_vars:
            module_chunk = self._create_module_chunk(tree, lines, file_path)
            if module_chunk:
                chunks.append(module_chunk)

        # Function and class chunks
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and self.config.preserve_functions:
                # Skip methods inside classes (they'll be included in class chunks)
                if not self._is_method(node, tree):
                    func_chunk = self._create_function_chunk(node, lines, file_path)
                    chunks.append(func_chunk)
                    
            elif isinstance(node, ast.ClassDef) and self.config.preserve_classes:
                class_chunk = self._create_class_chunk(node, lines, file_path)
                chunks.append(class_chunk)
        
        return chunks
    
    def _is_method(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if a function is a method inside a class."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if func_node in node.body:
                    return True
        return False

    def _create_module_chunk(self, tree: ast.AST, lines: List[str], file_path: str) -> Optional[DocumentChunk]:
        """Create chunk for module-level content."""
        imports = []
        global_vars = []
        module_docstring = None
        
        # Get module docstring
        if (tree.body and isinstance(tree.body[0], ast.Expr) and 
            isinstance(tree.body[0].value, ast.Constant) and 
            isinstance(tree.body[0].value.value, str)):
            module_docstring = tree.body[0].value.value
        
        # Collect imports and global variables
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)) and self.config.include_imports:
                start_line = node.lineno - 1
                end_line = (node.end_lineno or node.lineno) - 1
                imports.extend(lines[start_line:end_line + 1])
            elif (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) 
                  and self.config.include_global_vars):
                start_line = node.lineno - 1
                end_line = (node.end_lineno or node.lineno) - 1
                global_vars.extend(lines[start_line:end_line + 1])
        
        if imports or global_vars or (module_docstring and self.config.include_docstrings):
            content_parts = []
            if module_docstring and self.config.include_docstrings:
                content_parts.append(f'"""Module: {file_path}"""\n{module_docstring}')
            if imports:
                content_parts.append("# Imports\n" + "\n".join(imports))
            if global_vars:
                content_parts.append("# Global Variables\n" + "\n".join(global_vars))
            
            return DocumentChunk(
                content="\n\n".join(content_parts),
                metadata={
                    'chunk_type': 'module',
                    'file_path': file_path,
                    'imports_count': len([i for i in imports if i.strip()]),
                    'global_vars_count': len([g for g in global_vars if g.strip()]),
                    'has_docstring': module_docstring is not None
                },
                chunk_type='module',
                start_line=1,
                end_line=max([node.end_lineno or node.lineno for node in tree.body[:10]], default=1),
                chunk_id=f"{file_path}:module"
            )
        return None

    def _create_function_chunk(self, node: ast.FunctionDef, lines: List[str], file_path: str) -> DocumentChunk:
        """Create chunk for individual function."""
        start_line = node.lineno - 1
        end_line = (node.end_lineno or node.lineno) - 1
        
        function_lines = lines[start_line:end_line + 1]
        context = f"# Function: {node.name} (lines {node.lineno}-{node.end_lineno or node.lineno})\n"
        content = context + "\n".join(function_lines)
        
        return DocumentChunk(
            content=content,
            metadata={
                'chunk_type': 'function',
                'function_name': node.name,
                'file_path': file_path,
                'docstring': ast.get_docstring(node) if self.config.include_docstrings else None,
                'parameters': [arg.arg for arg in node.args.args],
                'line_count': end_line - start_line + 1,
                'has_decorators': len(node.decorator_list) > 0,
                'is_async': isinstance(node, ast.AsyncFunctionDef)
            },
            chunk_type='function',
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            chunk_id=f"{file_path}:function:{node.name}"
        )

    def _create_class_chunk(self, node: ast.ClassDef, lines: List[str], file_path: str) -> DocumentChunk:
        """Create chunk for entire class including all methods."""
        start_line = node.lineno - 1
        end_line = (node.end_lineno or node.lineno) - 1
        
        class_lines = lines[start_line:end_line + 1]
        context = f"# Class: {node.name} (lines {node.lineno}-{node.end_lineno or node.lineno})\n"
        content = context + "\n".join(class_lines)
        
        method_names = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
        
        return DocumentChunk(
            content=content,
            metadata={
                'chunk_type': 'class',
                'class_name': node.name,
                'file_path': file_path,
                'docstring': ast.get_docstring(node) if self.config.include_docstrings else None,
                'methods': method_names,
                'method_count': len(method_names),
                'base_classes': [self._get_base_class_name(base) for base in node.bases],
                'line_count': end_line - start_line + 1
            },
            chunk_type='class',
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            chunk_id=f"{file_path}:class:{node.name}"
        )

    def _extract_metadata(self, tree: ast.AST, file_path: str, content: str) -> Dict[str, Any]:
        """Extract metadata from python ast."""
        metadata = {
            'file_path': file_path,
            'language': 'python',
            'total_lines': len(content.splitlines()),
            'functions': [],
            'classes': [],
            'imports': [],
            'global_variables': [],
            'module_docstring': None,
            'dependencies': set()
        }

        # Extract module docstring
        if (tree.body and isinstance(tree.body[0], ast.Expr) and
           isinstance(tree.body[0].value, ast.Constant) and
           isinstance(tree.body[0].value.value, str)):
            metadata['module_docstring'] = tree.body[0].value.value

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = self._extract_function_info(node)
                metadata['functions'].append(func_info)

            elif isinstance(node, ast.ClassDef):
                class_info = self._extract_class_info(node)
                metadata['classes'].append(class_info)
            
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                import_info = self._extract_import_info(node)
                metadata['imports'].append(import_info)
                metadata['dependencies'].update(import_info.get('modules', []))
            
            elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                # Global variable assignment
                var_name = node.targets[0].id
                if not var_name.startswith('_'):  # Skip private variables
                    metadata['global_variables'].append({
                        'name': var_name,
                        'line': node.lineno,
                        'type': self._infer_type(node.value)
                    })
        
        metadata['dependencies'] = list(metadata['dependencies'])
        return metadata
    
    def _extract_function_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract detailed function information."""
        return {
            'name': node.name,
            'line_start': node.lineno,
            'line_end': node.end_lineno or node.lineno,
            'docstring': ast.get_docstring(node),
            'parameters': [arg.arg for arg in node.args.args],
            'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list],
            'returns_annotation': self._get_annotation(node.returns),
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'complexity': 1  # Simplified complexity
        }

    def _extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract detailed class information."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._extract_function_info(item))
        
        return {
            'name': node.name,
            'line_start': node.lineno,
            'line_end': node.end_lineno or node.lineno,
            'docstring': ast.get_docstring(node),
            'methods': methods,
            'base_classes': [self._get_base_class_name(base) for base in node.bases],
            'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list]
        }
    
    def _extract_import_info(self, node) -> Dict[str, Any]:
        """Extract import information."""
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
            return {
                'type': 'import',
                'modules': modules,
                'line': node.lineno,
                'aliases': {alias.name: alias.asname for alias in node.names if alias.asname},
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                'type': 'from_import',
                'module': node.module or '',
                'names': [alias.name for alias in node.names],
                'line': node.lineno,
                'level': node.level,
                'aliases': {alias.name: alias.asname for alias in node.names if alias.asname}
            }
        return {}
    
    def _get_decorator_name(self, decorator) -> str:
        """Extract decorator name."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return f"{decorator.func.value.id}.{decorator.func.attr}"
        return str(decorator)

    def _get_annotation(self, annotation) -> Optional[str]:
        """Extract type annotation as string."""
        if annotation is None:
            return None
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Attribute):
            return f"{annotation.value.id}.{annotation.attr}"
        try:
            return ast.unparse(annotation)
        except:
            return str(annotation)

    def _get_base_class_name(self, base) -> str:
        """Extract base class name."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{base.value.id}.{base.attr}"
        return str(base)

    def _infer_type(self, node) -> str:
        """Infer type from AST node."""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.List):
            return 'list'
        elif isinstance(node, ast.Dict):
            return 'dict'
        elif isinstance(node, ast.Set):
            return 'set'
        elif isinstance(node, ast.Tuple):
            return 'tuple'
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
        return 'unknown'
