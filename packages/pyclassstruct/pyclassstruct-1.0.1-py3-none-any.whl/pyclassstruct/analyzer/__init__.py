"""
Analyzer module - Parse and analyze Python source code.
"""

from pathlib import Path
from typing import List, Optional

from .models import FileAnalysis, FolderAnalysis, ClassProposal
from .ast_parser import ASTParser, parse_file
from .dependency import DependencyAnalyzer


def analyze_file(filepath: str) -> FileAnalysis:
    """
    Analyze a single Python file.
    
    Args:
        filepath: Path to the Python file
        
    Returns:
        FileAnalysis object with extracted information
    """
    analysis = parse_file(filepath)
    
    # Add dependency-based class proposals
    dep_analyzer = DependencyAnalyzer(analysis)
    analysis.class_proposals = dep_analyzer.detect_class_proposals()
    
    return analysis


def analyze_folder(folderpath: str, recursive: bool = True) -> FolderAnalysis:
    """
    Analyze all Python files in a folder.
    
    Args:
        folderpath: Path to the folder
        recursive: Whether to search recursively
        
    Returns:
        FolderAnalysis object with all file analyses
    """
    path = Path(folderpath)
    if not path.exists():
        raise FileNotFoundError(f"Folder not found: {folderpath}")
    if not path.is_dir():
        raise ValueError(f"Not a directory: {folderpath}")
    
    folder_analysis = FolderAnalysis(folderpath=str(path))
    
    # Find all Python files
    pattern = "**/*.py" if recursive else "*.py"
    py_files = list(path.glob(pattern))
    
    # Analyze each file
    for py_file in py_files:
        # Skip __pycache__ and hidden files
        if '__pycache__' in str(py_file) or py_file.name.startswith('.'):
            continue
        try:
            file_analysis = parse_file(str(py_file))
            folder_analysis.file_analyses.append(file_analysis)
        except (ValueError, SyntaxError) as e:
            print(f"Warning: Skipping {py_file}: {e}")
    
    # Generate folder-level class proposals
    if folder_analysis.file_analyses:
        dep_analyzer = DependencyAnalyzer(folder_analysis)
        folder_analysis.class_proposals = dep_analyzer.detect_class_proposals()
    
    return folder_analysis


def parse_classes_txt(classes_txt_path: str) -> List[ClassProposal]:
    """
    Parse a classes.txt file to get user-defined class structure.
    
    Format:
        ClassName: function1, function2, function3
        
    Args:
        classes_txt_path: Path to classes.txt
        
    Returns:
        List of ClassProposal objects
    """
    path = Path(classes_txt_path)
    if not path.exists():
        return []
    
    proposals = []
    content = path.read_text(encoding='utf-8')
    
    for line in content.splitlines():
        line = line.strip()
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        # Parse "ClassName: func1, func2, func3"
        if ':' in line:
            class_name, funcs_part = line.split(':', 1)
            class_name = class_name.strip()
            func_names = [f.strip() for f in funcs_part.split(',') if f.strip()]
            
            if class_name and func_names:
                proposals.append(ClassProposal(
                    name=class_name,
                    methods=[],  # Will be filled later with actual FunctionInfo
                    description=f"User-defined class with {len(func_names)} methods"
                ))
                # Store function names temporarily
                proposals[-1]._method_names = func_names
    
    return proposals


def can_detect_structure(analysis: FileAnalysis | FolderAnalysis) -> bool:
    """Check if the analyzer can automatically detect class structure."""
    dep_analyzer = DependencyAnalyzer(analysis)
    return dep_analyzer.can_detect_structure()


__all__ = [
    'analyze_file',
    'analyze_folder',
    'parse_classes_txt',
    'can_detect_structure',
    'FileAnalysis',
    'FolderAnalysis',
    'ClassProposal',
]
