"""
PyStruct - Convert Python scripts to class-based structures.
"""

__version__ = "1.0.0"
__author__ = "PyStruct Team"

from pyclassstruct.analyzer import analyze_file, analyze_folder
from pyclassstruct.generator import generate_structure
from pyclassstruct.reporter import generate_report

__all__ = [
    "analyze_file",
    "analyze_folder", 
    "generate_structure",
    "generate_report",
]
