"""
Naming utilities for snake_case and CamelCase conversions.
"""

import re
from typing import List


def to_snake_case(name: str) -> str:
    """
    Convert a name to snake_case.
    
    Examples:
        UserManager -> user_manager
        HTTPHandler -> http_handler
        getUserName -> get_user_name
    """
    # Handle already snake_case
    if '_' in name and name.islower():
        return name
    
    # Insert underscore before uppercase letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    
    return s2.lower()


def to_camel_case(name: str) -> str:
    """
    Convert a name to CamelCase (PascalCase).
    
    Examples:
        user_manager -> UserManager
        http_handler -> HttpHandler
        get_user_name -> GetUserName
    """
    # Handle already CamelCase
    if not '_' in name and name[0].isupper():
        return name
    
    # Split by underscores and capitalize each part
    parts = name.split('_')
    return ''.join(word.capitalize() for word in parts if word)


def to_method_name(name: str) -> str:
    """
    Convert to a valid method name (snake_case, lowercase).
    
    Examples:
        GetUser -> get_user
        UserManager -> user_manager
    """
    snake = to_snake_case(name)
    # Remove leading/trailing underscores
    return snake.strip('_')


def to_class_name(name: str, suffix: str = "") -> str:
    """
    Convert to a valid class name (CamelCase).
    
    Args:
        name: The name to convert
        suffix: Optional suffix like 'Handler', 'Manager', etc.
    """
    camel = to_camel_case(name)
    if suffix and not camel.endswith(suffix):
        camel += suffix
    return camel


def to_filename(class_name: str) -> str:
    """
    Convert a class name to a valid Python filename (snake_case).
    
    Examples:
        UserManager -> user_manager.py
        HTTPHandler -> http_handler.py
    """
    snake = to_snake_case(class_name)
    if not snake.endswith('.py'):
        snake += '.py'
    return snake


def split_function_name(name: str) -> List[str]:
    """
    Split a function name into its component words.
    
    Examples:
        get_user_name -> ['get', 'user', 'name']
        getUserName -> ['get', 'User', 'Name']
    """
    if '_' in name:
        return [p for p in name.split('_') if p]
    else:
        # Split on CamelCase
        parts = re.findall('[A-Z][a-z]*|[a-z]+|[0-9]+', name)
        return parts


def get_common_prefix(names: List[str]) -> str:
    """
    Get the common prefix from a list of snake_case names.
    
    Examples:
        ['user_create', 'user_delete', 'user_update'] -> 'user'
        ['get_name', 'set_name'] -> ''
    """
    if not names:
        return ''
    
    # Convert all to snake_case and split
    split_names = [n.split('_') for n in names]
    
    # Find common prefix parts
    common = []
    for parts in zip(*split_names):
        if len(set(parts)) == 1:
            common.append(parts[0])
        else:
            break
    
    return '_'.join(common)


def sanitize_identifier(name: str) -> str:
    """
    Sanitize a string to be a valid Python identifier.
    
    - Remove invalid characters
    - Ensure doesn't start with a number
    - Replace spaces with underscores
    """
    # Replace spaces and hyphens with underscores
    name = re.sub(r'[\s\-]+', '_', name)
    
    # Remove invalid characters
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    
    # Ensure doesn't start with a number
    if name and name[0].isdigit():
        name = '_' + name
    
    return name or 'unnamed'
