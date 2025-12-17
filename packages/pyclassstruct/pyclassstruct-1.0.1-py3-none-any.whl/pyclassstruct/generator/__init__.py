"""
Generator module - Generate structured Python code from analysis.
"""

from .class_builder import build_class, build_module, ClassBuilder
from .structure import generate_structure, StructureGenerator, check_needs_user_input
from .naming import (
    to_snake_case,
    to_camel_case,
    to_method_name,
    to_class_name,
    to_filename,
    split_function_name,
    get_common_prefix,
    sanitize_identifier
)

__all__ = [
    # Class building
    'build_class',
    'build_module',
    'ClassBuilder',
    
    # Structure generation
    'generate_structure',
    'StructureGenerator',
    'check_needs_user_input',
    
    # Naming utilities
    'to_snake_case',
    'to_camel_case',
    'to_method_name',
    'to_class_name',
    'to_filename',
    'split_function_name',
    'get_common_prefix',
    'sanitize_identifier',
]
