"""
Data models for the analyzer module.
"""

from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional


@dataclass
class FunctionInfo:
    """Information about a function in the source code."""
    name: str
    lineno: int
    end_lineno: int
    args: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    calls: Set[str] = field(default_factory=set)  # Functions this function calls
    global_reads: Set[str] = field(default_factory=set)  # Global variables read
    global_writes: Set[str] = field(default_factory=set)  # Global variables written
    source_code: str = ""
    return_annotation: Optional[str] = None
    is_async: bool = False
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, FunctionInfo):
            return self.name == other.name
        return False


@dataclass  
class GlobalVarInfo:
    """Information about a global variable (potential property)."""
    name: str
    lineno: int
    value_type: Optional[str] = None
    initial_value: Optional[str] = None
    

@dataclass
class ImportInfo:
    """Information about an import statement."""
    module: str
    names: List[str] = field(default_factory=list)  # For 'from x import a, b'
    alias: Optional[str] = None
    is_from_import: bool = False
    lineno: int = 0


@dataclass
class ClassProposal:
    """A proposed class structure."""
    name: str  # CamelCase class name
    methods: List[FunctionInfo] = field(default_factory=list)
    properties: List[GlobalVarInfo] = field(default_factory=list)
    description: str = ""
    
    @property
    def method_names(self) -> List[str]:
        return [m.name for m in self.methods]


@dataclass
class FileAnalysis:
    """Complete analysis of a Python file."""
    filepath: str
    functions: List[FunctionInfo] = field(default_factory=list)
    global_vars: List[GlobalVarInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    class_proposals: List[ClassProposal] = field(default_factory=list)
    raw_source: str = ""
    
    @property
    def function_names(self) -> List[str]:
        return [f.name for f in self.functions]
    
    @property
    def global_var_names(self) -> List[str]:
        return [g.name for g in self.global_vars]


@dataclass
class FolderAnalysis:
    """Complete analysis of a folder containing Python files."""
    folderpath: str
    file_analyses: List[FileAnalysis] = field(default_factory=list)
    class_proposals: List[ClassProposal] = field(default_factory=list)
    
    @property
    def all_functions(self) -> List[FunctionInfo]:
        funcs = []
        for fa in self.file_analyses:
            funcs.extend(fa.functions)
        return funcs
    
    @property
    def all_global_vars(self) -> List[GlobalVarInfo]:
        gvars = []
        for fa in self.file_analyses:
            gvars.extend(fa.global_vars)
        return gvars
    
    @property
    def total_files(self) -> int:
        return len(self.file_analyses)
