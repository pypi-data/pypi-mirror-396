"""
File operations utilities.
"""

import os
from pathlib import Path
from typing import Tuple


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()


def prompt_file_overwrite(filepath: str, file_type: str) -> Tuple[bool, str]:
    """
    Check if file exists and return appropriate message.
    
    Returns:
        Tuple of (can_proceed, message)
    """
    if check_file_exists(filepath):
        return False, f"{file_type} already exists at {filepath}. Please delete it or use --force to overwrite."
    return True, ""


def ensure_dir_exists(dirpath: str) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path = Path(dirpath)
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_python_file(filepath: str) -> bool:
    """Check if a file is a Python file."""
    return Path(filepath).suffix == '.py'


def is_directory(path: str) -> bool:
    """Check if a path is a directory."""
    return Path(path).is_dir()


def get_python_files(dirpath: str, recursive: bool = True) -> list:
    """Get all Python files in a directory."""
    path = Path(dirpath)
    pattern = "**/*.py" if recursive else "*.py"
    return [str(f) for f in path.glob(pattern) if '__pycache__' not in str(f)]
