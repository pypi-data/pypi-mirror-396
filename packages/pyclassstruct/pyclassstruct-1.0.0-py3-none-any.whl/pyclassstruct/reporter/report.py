"""
Report generator - generates report.txt and classes.txt
"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime

from pyclassstruct.analyzer.models import FileAnalysis, FolderAnalysis, ClassProposal


class ReportGenerator:
    """Generate analysis reports."""
    
    def __init__(self, analysis: FileAnalysis | FolderAnalysis):
        self.analysis = analysis
        
    def generate_report(self) -> str:
        """Generate the report content."""
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("PYSTRUCT ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Source info
        if isinstance(self.analysis, FileAnalysis):
            lines.append(f"Source: {self.analysis.filepath}")
            lines.append(f"Type: Single file analysis")
        else:
            lines.append(f"Source: {self.analysis.folderpath}")
            lines.append(f"Type: Folder analysis")
            lines.append(f"Files analyzed: {self.analysis.total_files}")
        
        lines.append("")
        lines.append("-" * 60)
        
        # Statistics
        lines.append("")
        lines.append("STATISTICS")
        lines.append("-" * 30)
        
        stats = self._calculate_stats()
        lines.append(f"Total functions found:     {stats['total_functions']}")
        lines.append(f"Total global variables:    {stats['total_globals']}")
        lines.append(f"Proposed classes:          {stats['total_classes']}")
        lines.append(f"Methods (in classes):      {stats['total_methods']}")
        lines.append(f"Properties (from globals): {stats['total_properties']}")
        
        lines.append("")
        lines.append("-" * 60)
        
        # Function list
        lines.append("")
        lines.append("FUNCTIONS DETECTED")
        lines.append("-" * 30)
        
        functions = self._get_all_functions()
        if functions:
            for func in functions:
                args_str = ", ".join(func.args) if func.args else "()"
                calls_str = f" -> calls: {', '.join(list(func.calls)[:3])}" if func.calls else ""
                lines.append(f"  • {func.name}({args_str}){calls_str}")
        else:
            lines.append("  No functions found.")
        
        lines.append("")
        lines.append("-" * 60)
        
        # Global variables
        lines.append("")
        lines.append("GLOBAL VARIABLES DETECTED")
        lines.append("-" * 30)
        
        globals_list = self._get_all_globals()
        if globals_list:
            for gvar in globals_list:
                type_str = f": {gvar.value_type}" if gvar.value_type else ""
                value_str = f" = {gvar.initial_value}" if gvar.initial_value else ""
                lines.append(f"  • {gvar.name}{type_str}{value_str}")
        else:
            lines.append("  No global variables found.")
        
        lines.append("")
        lines.append("-" * 60)
        
        # Proposed structure
        lines.append("")
        lines.append("PROPOSED CLASS STRUCTURE")
        lines.append("-" * 30)
        
        proposals = self._get_proposals()
        if proposals:
            for proposal in proposals:
                lines.append(f"")
                lines.append(f"  class {proposal.name}:")
                lines.append(f"    # {proposal.description}")
                if proposal.properties:
                    lines.append(f"    # Properties:")
                    for prop in proposal.properties:
                        lines.append(f"    #   - {prop.name}")
                lines.append(f"    # Methods:")
                for method in proposal.methods:
                    lines.append(f"    #   - {method.name}()")
        else:
            lines.append("  No class structure could be detected.")
            lines.append("  Please create a classes.txt file to define the structure.")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("END OF REPORT")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def generate_classes_txt(self) -> str:
        """Generate classes.txt content."""
        lines = []
        
        lines.append("# PyClassStruct Class Definitions")
        lines.append("# Format: ClassName: function1, function2, function3")
        lines.append("# Edit this file to customize the class structure")
        lines.append("# Then run: pyclassstruct convert <path>")
        lines.append("")
        
        proposals = self._get_proposals()
        if proposals:
            for proposal in proposals:
                method_names = ", ".join(m.name for m in proposal.methods)
                lines.append(f"{proposal.name}: {method_names}")
        else:
            # List all functions for user to organize
            lines.append("# No structure detected. Please define your classes below.")
            lines.append("# Available functions:")
            functions = self._get_all_functions()
            for func in functions:
                lines.append(f"#   {func.name}")
            lines.append("")
            lines.append("# Example:")
            lines.append("# MyClass: function1, function2, function3")
        
        return "\n".join(lines)
    
    def _calculate_stats(self) -> dict:
        """Calculate statistics from the analysis."""
        functions = self._get_all_functions()
        globals_list = self._get_all_globals()
        proposals = self._get_proposals()
        
        total_methods = sum(len(p.methods) for p in proposals)
        total_properties = sum(len(p.properties) for p in proposals)
        
        return {
            'total_functions': len(functions),
            'total_globals': len(globals_list),
            'total_classes': len(proposals),
            'total_methods': total_methods,
            'total_properties': total_properties
        }
    
    def _get_all_functions(self):
        """Get all functions from analysis."""
        if isinstance(self.analysis, FileAnalysis):
            return self.analysis.functions
        else:
            return self.analysis.all_functions
    
    def _get_all_globals(self):
        """Get all global variables from analysis."""
        if isinstance(self.analysis, FileAnalysis):
            return self.analysis.global_vars
        else:
            return self.analysis.all_global_vars
    
    def _get_proposals(self):
        """Get class proposals from analysis."""
        if isinstance(self.analysis, FileAnalysis):
            return self.analysis.class_proposals
        else:
            return self.analysis.class_proposals


def generate_report(
    analysis: FileAnalysis | FolderAnalysis,
    output_path: Optional[str] = None
) -> str:
    """
    Generate a report from the analysis.
    
    Args:
        analysis: The file or folder analysis
        output_path: Optional path to save the report
        
    Returns:
        The report content as a string
    """
    generator = ReportGenerator(analysis)
    report = generator.generate_report()
    
    if output_path:
        Path(output_path).write_text(report, encoding='utf-8')
    
    return report


def generate_classes_txt(
    analysis: FileAnalysis | FolderAnalysis,
    output_path: Optional[str] = None
) -> str:
    """
    Generate classes.txt from the analysis.
    
    Args:
        analysis: The file or folder analysis
        output_path: Optional path to save the file
        
    Returns:
        The classes.txt content as a string
    """
    generator = ReportGenerator(analysis)
    content = generator.generate_classes_txt()
    
    if output_path:
        Path(output_path).write_text(content, encoding='utf-8')
    
    return content
