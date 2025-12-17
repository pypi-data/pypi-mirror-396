"""
AST-based Python code parser.
"""

import ast
from typing import List, Optional, Set
from pathlib import Path

from .models import FunctionInfo, GlobalVarInfo, ImportInfo, FileAnalysis


class ASTParser:
    """Parse Python source code using AST."""
    
    def __init__(self, source_code: str, filepath: str = "<unknown>"):
        self.source_code = source_code
        self.filepath = filepath
        self.source_lines = source_code.splitlines()
        self._tree: Optional[ast.AST] = None
        
    def parse(self) -> FileAnalysis:
        """Parse the source code and return a FileAnalysis."""
        try:
            self._tree = ast.parse(self.source_code)
        except SyntaxError as e:
            raise ValueError(f"Failed to parse {self.filepath}: {e}")
        
        functions = self._extract_functions()
        global_vars = self._extract_global_vars()
        imports = self._extract_imports()
        
        return FileAnalysis(
            filepath=self.filepath,
            functions=functions,
            global_vars=global_vars,
            imports=imports,
            raw_source=self.source_code
        )
    
    def _extract_functions(self) -> List[FunctionInfo]:
        """Extract all top-level function definitions."""
        functions = []
        
        for node in ast.iter_child_nodes(self._tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = self._parse_function(node)
                functions.append(func_info)
                
        return functions
    
    def _parse_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """Parse a function definition node."""
        # Get arguments
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        
        # Get decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(ast.unparse(dec))
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    decorators.append(dec.func.id)
                elif isinstance(dec.func, ast.Attribute):
                    decorators.append(ast.unparse(dec.func))
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Get function calls within this function
        calls = self._get_function_calls(node)
        
        # Get global variable access
        global_reads, global_writes = self._get_global_access(node)
        
        # Get source code for the function
        source_code = self._get_source_segment(node.lineno, node.end_lineno)
        
        # Get return annotation
        return_annotation = None
        if node.returns:
            return_annotation = ast.unparse(node.returns)
        
        return FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=node.end_lineno,
            args=args,
            decorators=decorators,
            docstring=docstring,
            calls=calls,
            global_reads=global_reads,
            global_writes=global_writes,
            source_code=source_code,
            return_annotation=return_annotation,
            is_async=isinstance(node, ast.AsyncFunctionDef)
        )
    
    def _get_function_calls(self, node: ast.FunctionDef) -> Set[str]:
        """Get all function calls made within a function."""
        calls = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    # For method calls like obj.method(), we track the method name
                    calls.add(child.func.attr)
                    
        return calls
    
    def _get_global_access(self, node: ast.FunctionDef) -> tuple:
        """Get global variables read and written within a function."""
        reads = set()
        writes = set()
        
        # Get all names used in assignments
        assigned_names = set()
        local_names = set()
        
        # Collect local names (function arguments, loop variables, etc.)
        for arg in node.args.args:
            local_names.add(arg.arg)
        
        for child in ast.walk(node):
            # Track assignments
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        assigned_names.add(target.id)
            elif isinstance(child, ast.AugAssign):
                if isinstance(child.target, ast.Name):
                    assigned_names.add(child.target.id)
            elif isinstance(child, ast.AnnAssign):
                if isinstance(child.target, ast.Name):
                    assigned_names.add(child.target.id)
            # Track loop variables
            elif isinstance(child, ast.For):
                if isinstance(child.target, ast.Name):
                    local_names.add(child.target.id)
            # Track comprehension variables
            elif isinstance(child, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
                for gen in child.generators:
                    if isinstance(gen.target, ast.Name):
                        local_names.add(gen.target.id)
            # Check for global declarations
            elif isinstance(child, ast.Global):
                for name in child.names:
                    writes.add(name)
        
        return reads, writes
    
    def _extract_global_vars(self) -> List[GlobalVarInfo]:
        """Extract all top-level variable assignments."""
        global_vars = []
        
        for node in ast.iter_child_nodes(self._tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Skip uppercase constants (conventional)
                        name = target.id
                        if not name.startswith('_'):
                            value_type = self._infer_type(node.value)
                            initial_value = ast.unparse(node.value) if len(ast.unparse(node.value)) < 50 else "..."
                            global_vars.append(GlobalVarInfo(
                                name=name,
                                lineno=node.lineno,
                                value_type=value_type,
                                initial_value=initial_value
                            ))
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    name = node.target.id
                    value_type = ast.unparse(node.annotation) if node.annotation else None
                    initial_value = ast.unparse(node.value) if node.value else None
                    global_vars.append(GlobalVarInfo(
                        name=name,
                        lineno=node.lineno,
                        value_type=value_type,
                        initial_value=initial_value
                    ))
                    
        return global_vars
    
    def _infer_type(self, node: ast.expr) -> Optional[str]:
        """Infer the type of a value expression."""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.List):
            return "list"
        elif isinstance(node, ast.Dict):
            return "dict"
        elif isinstance(node, ast.Set):
            return "set"
        elif isinstance(node, ast.Tuple):
            return "tuple"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
        return None
    
    def _extract_imports(self) -> List[ImportInfo]:
        """Extract all import statements."""
        imports = []
        
        for node in ast.iter_child_nodes(self._tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportInfo(
                        module=alias.name,
                        alias=alias.asname,
                        is_from_import=False,
                        lineno=node.lineno
                    ))
            elif isinstance(node, ast.ImportFrom):
                names = [alias.name for alias in node.names]
                imports.append(ImportInfo(
                    module=node.module or "",
                    names=names,
                    is_from_import=True,
                    lineno=node.lineno
                ))
                
        return imports
    
    def _get_source_segment(self, start_line: int, end_line: int) -> str:
        """Get source code segment for given line range."""
        if start_line <= 0 or end_line > len(self.source_lines):
            return ""
        return "\n".join(self.source_lines[start_line - 1:end_line])


def parse_file(filepath: str) -> FileAnalysis:
    """Parse a Python file and return its analysis."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if not path.suffix == '.py':
        raise ValueError(f"Not a Python file: {filepath}")
    
    source_code = path.read_text(encoding='utf-8')
    parser = ASTParser(source_code, str(path))
    return parser.parse()
