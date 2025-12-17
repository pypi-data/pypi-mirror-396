"""
Class code generator - builds Python class source code.
"""

from typing import List, Optional
import textwrap

from pyclassstruct.analyzer.models import FunctionInfo, GlobalVarInfo, ClassProposal, ImportInfo
from .naming import to_snake_case, to_camel_case, to_method_name


class ClassBuilder:
    """Build Python class source code from ClassProposal."""
    
    def __init__(self, proposal: ClassProposal, imports: List[ImportInfo] = None):
        self.proposal = proposal
        self.imports = imports or []
        self._indent = "    "
    
    def build(self) -> str:
        """Build the complete class source code."""
        lines = []
        
        # Add imports
        import_lines = self._build_imports()
        if import_lines:
            lines.extend(import_lines)
            lines.append("")
            lines.append("")
        
        # Add class definition
        lines.append(f"class {self.proposal.name}:")
        
        # Add class docstring
        docstring = self._build_class_docstring()
        if docstring:
            lines.append(self._indent + docstring)
        
        # Add __init__ method if we have properties
        if self.proposal.properties:
            lines.append("")
            init_method = self._build_init()
            lines.extend(init_method)
        
        # Add methods
        for method in self.proposal.methods:
            lines.append("")
            method_lines = self._build_method(method)
            lines.extend(method_lines)
        
        # If no methods and no properties, add pass
        if not self.proposal.methods and not self.proposal.properties:
            lines.append(self._indent + "pass")
        
        return "\n".join(lines)
    
    def _build_imports(self) -> List[str]:
        """Build import statements."""
        lines = []
        
        # Standard library imports
        stdlib = []
        third_party = []
        local = []
        
        for imp in self.imports:
            if imp.is_from_import:
                names = ", ".join(imp.names)
                line = f"from {imp.module} import {names}"
            else:
                if imp.alias:
                    line = f"import {imp.module} as {imp.alias}"
                else:
                    line = f"import {imp.module}"
            
            # Simple categorization (not perfect but good enough)
            if imp.module.startswith('.') or imp.module.startswith('pystruct'):
                local.append(line)
            elif '.' not in imp.module and len(imp.module) < 15:
                stdlib.append(line)
            else:
                third_party.append(line)
        
        # Add in order: stdlib, third-party, local
        if stdlib:
            lines.extend(sorted(set(stdlib)))
        if third_party:
            if stdlib:
                lines.append("")
            lines.extend(sorted(set(third_party)))
        if local:
            if stdlib or third_party:
                lines.append("")
            lines.extend(sorted(set(local)))
        
        return lines
    
    def _build_class_docstring(self) -> str:
        """Build class-level docstring."""
        if self.proposal.description:
            return f'"""{self.proposal.description}"""'
        
        method_count = len(self.proposal.methods)
        prop_count = len(self.proposal.properties)
        
        parts = []
        if method_count:
            parts.append(f"{method_count} method{'s' if method_count > 1 else ''}")
        if prop_count:
            parts.append(f"{prop_count} propert{'ies' if prop_count > 1 else 'y'}")
        
        if parts:
            return f'"""{self.proposal.name} class with {" and ".join(parts)}."""'
        
        return f'"""{self.proposal.name} class."""'
    
    def _build_init(self) -> List[str]:
        """Build __init__ method with properties."""
        lines = []
        lines.append(self._indent + "def __init__(self):")
        lines.append(self._indent * 2 + '"""Initialize the instance."""')
        
        for prop in self.proposal.properties:
            if prop.initial_value:
                lines.append(self._indent * 2 + f"self.{prop.name} = {prop.initial_value}")
            else:
                lines.append(self._indent * 2 + f"self.{prop.name} = None")
        
        return lines
    
    def _build_method(self, func: FunctionInfo) -> List[str]:
        """Build a method from a FunctionInfo."""
        lines = []
        
        # Add decorators
        for decorator in func.decorators:
            lines.append(self._indent + f"@{decorator}")
        
        # Build method signature
        if func.is_async:
            prefix = "async def"
        else:
            prefix = "def"
        
        # Add self parameter
        args = ["self"] + [arg for arg in func.args if arg != "self"]
        args_str = ", ".join(args)
        
        # Add return annotation if present
        if func.return_annotation:
            sig = f"{prefix} {func.name}({args_str}) -> {func.return_annotation}:"
        else:
            sig = f"{prefix} {func.name}({args_str}):"
        
        lines.append(self._indent + sig)
        
        # Add docstring if present
        if func.docstring:
            # Format docstring with proper indentation
            doc_lines = func.docstring.split('\n')
            if len(doc_lines) == 1:
                lines.append(self._indent * 2 + f'"""{func.docstring}"""')
            else:
                lines.append(self._indent * 2 + '"""')
                for doc_line in doc_lines:
                    lines.append(self._indent * 2 + doc_line)
                lines.append(self._indent * 2 + '"""')
        
        # Add method body from source code
        body_lines = self._extract_method_body(func)
        for body_line in body_lines:
            lines.append(self._indent + body_line)
        
        return lines
    
    def _extract_method_body(self, func: FunctionInfo) -> List[str]:
        """Extract the method body from function source code."""
        if not func.source_code:
            return [self._indent + "pass"]
        
        source_lines = func.source_code.split('\n')
        
        # Find the first line of the body (after def and docstring)
        body_start = 0
        in_docstring = False
        docstring_marker = None
        
        for i, line in enumerate(source_lines):
            stripped = line.strip()
            
            # Skip def line
            if i == 0:
                continue
            
            # Handle docstring
            if not in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    docstring_marker = stripped[:3]
                    if stripped.count(docstring_marker) >= 2:
                        # Single-line docstring
                        continue
                    in_docstring = True
                    continue
                elif stripped:
                    body_start = i
                    break
            else:
                if docstring_marker in stripped:
                    in_docstring = False
                    continue
        
        # Get body lines
        body_lines = source_lines[body_start:]
        
        if not body_lines or all(not line.strip() for line in body_lines):
            return [self._indent + "pass"]
        
        # Find minimum indentation
        min_indent = float('inf')
        for line in body_lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)
        
        if min_indent == float('inf'):
            min_indent = 0
        
        # Remove the base indentation
        result = []
        for line in body_lines:
            if line.strip():
                result.append(self._indent + line[min_indent:])
            else:
                result.append("")
        
        return result if result else [self._indent + "pass"]


def build_class(proposal: ClassProposal, imports: List[ImportInfo] = None) -> str:
    """
    Build Python class source code from a ClassProposal.
    
    Args:
        proposal: The class proposal
        imports: Optional list of imports to include
        
    Returns:
        Python source code string
    """
    builder = ClassBuilder(proposal, imports)
    return builder.build()


def build_module(proposals: List[ClassProposal], imports: List[ImportInfo] = None) -> str:
    """
    Build a complete Python module with multiple classes.
    
    Args:
        proposals: List of class proposals
        imports: Optional list of imports
        
    Returns:
        Python source code string for the entire module
    """
    parts = []
    
    # Add module docstring
    class_names = [p.name for p in proposals]
    parts.append(f'"""')
    parts.append(f"Module containing: {', '.join(class_names)}")
    parts.append(f'"""')
    parts.append("")
    
    # Build each class
    for i, proposal in enumerate(proposals):
        builder = ClassBuilder(proposal, imports if i == 0 else None)
        parts.append(builder.build())
        parts.append("")
        parts.append("")
    
    return "\n".join(parts)
