"""
Structure generator - orchestrates the conversion process.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from pyclassstruct.analyzer.models import FileAnalysis, FolderAnalysis, ClassProposal, FunctionInfo
from pyclassstruct.analyzer import parse_classes_txt, can_detect_structure
from .class_builder import build_class, build_module
from .naming import to_snake_case, to_filename


class StructureGenerator:
    """Generate structured class files from analysis."""
    
    def __init__(
        self,
        analysis: FileAnalysis | FolderAnalysis,
        output_dir: str = "structured",
        classes_txt_path: Optional[str] = None
    ):
        self.analysis = analysis
        self.output_dir = output_dir
        self.classes_txt_path = classes_txt_path
        self.proposals: List[ClassProposal] = []
        self._needs_user_input = False
        
    def generate(self) -> Tuple[bool, str]:
        """
        Generate the structured output.
        
        Returns:
            Tuple of (success, message)
        """
        # Step 1: Get class proposals
        self.proposals = self._get_proposals()
        
        if not self.proposals:
            return False, "No class structures could be generated."
        
        # Step 2: Create output directory
        output_path = self._create_output_dir()
        
        # Step 3: Generate class files
        generated_files = self._generate_files(output_path)
        
        return True, f"Generated {len(generated_files)} files in {output_path}"
    
    def _get_proposals(self) -> List[ClassProposal]:
        """Get class proposals from classes.txt or auto-detection."""
        proposals = []
        
        # Try to load user-defined classes.txt
        if self.classes_txt_path:
            user_proposals = parse_classes_txt(self.classes_txt_path)
            if user_proposals:
                # Map function names to actual FunctionInfo objects
                proposals = self._map_user_proposals(user_proposals)
                return proposals
        
        # Use auto-detected proposals from analysis
        if isinstance(self.analysis, FileAnalysis):
            proposals = self.analysis.class_proposals
        else:
            proposals = self.analysis.class_proposals
        
        # Check if we need user input
        if not proposals or not can_detect_structure(self.analysis):
            self._needs_user_input = True
        
        return proposals
    
    def _map_user_proposals(self, user_proposals: List[ClassProposal]) -> List[ClassProposal]:
        """Map user-defined class proposals to actual function info."""
        # Get all functions
        if isinstance(self.analysis, FileAnalysis):
            all_funcs = {f.name: f for f in self.analysis.functions}
        else:
            all_funcs = {f.name: f for fa in self.analysis.file_analyses for f in fa.functions}
        
        mapped = []
        for proposal in user_proposals:
            # Get function names from the temporary attribute
            func_names = getattr(proposal, '_method_names', [])
            methods = []
            for name in func_names:
                if name in all_funcs:
                    methods.append(all_funcs[name])
            
            if methods:
                mapped.append(ClassProposal(
                    name=proposal.name,
                    methods=methods,
                    properties=proposal.properties,
                    description=proposal.description
                ))
        
        return mapped
    
    def _create_output_dir(self) -> Path:
        """Create the output directory."""
        if isinstance(self.analysis, FileAnalysis):
            base_path = Path(self.analysis.filepath).parent
        else:
            base_path = Path(self.analysis.folderpath)
        
        output_path = base_path / self.output_dir
        output_path.mkdir(parents=True, exist_ok=True)
        
        return output_path
    
    def _generate_files(self, output_path: Path) -> List[str]:
        """Generate Python class files."""
        generated = []
        
        # Get imports from analysis
        imports = []
        if isinstance(self.analysis, FileAnalysis):
            imports = self.analysis.imports
        elif self.analysis.file_analyses:
            # Merge imports from all files
            for fa in self.analysis.file_analyses:
                imports.extend(fa.imports)
        
        # Group proposals by potential file (based on naming similarity)
        file_groups = self._group_proposals_for_files()
        
        for filename, proposals in file_groups.items():
            filepath = output_path / filename
            
            if len(proposals) == 1:
                # Single class per file
                content = build_class(proposals[0], imports)
            else:
                # Multiple classes per file
                content = build_module(proposals, imports)
            
            # Write file
            filepath.write_text(content, encoding='utf-8')
            generated.append(str(filepath))
        
        # Generate __init__.py
        init_path = output_path / "__init__.py"
        init_content = self._generate_init(file_groups)
        init_path.write_text(init_content, encoding='utf-8')
        generated.append(str(init_path))
        
        return generated
    
    def _group_proposals_for_files(self) -> Dict[str, List[ClassProposal]]:
        """Group class proposals into files."""
        groups: Dict[str, List[ClassProposal]] = {}
        
        for proposal in self.proposals:
            filename = to_filename(proposal.name)
            if filename not in groups:
                groups[filename] = []
            groups[filename].append(proposal)
        
        return groups
    
    def _generate_init(self, file_groups: Dict[str, List[ClassProposal]]) -> str:
        """Generate __init__.py content."""
        lines = ['"""', 'Auto-generated structured module.', '"""', '']
        
        # Add imports for each class
        for filename, proposals in file_groups.items():
            module_name = filename[:-3]  # Remove .py
            class_names = [p.name for p in proposals]
            names_str = ", ".join(class_names)
            lines.append(f"from .{module_name} import {names_str}")
        
        lines.append("")
        
        # Add __all__
        all_classes = [p.name for p in self.proposals]
        lines.append("__all__ = [")
        for name in all_classes:
            lines.append(f'    "{name}",')
        lines.append("]")
        
        return "\n".join(lines)
    
    @property
    def needs_user_input(self) -> bool:
        """Check if user input is needed for structure definition."""
        return self._needs_user_input


def generate_structure(
    analysis: FileAnalysis | FolderAnalysis,
    output_dir: str = "structured",
    classes_txt_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Generate structured class files from analysis.
    
    Args:
        analysis: The file or folder analysis
        output_dir: Output directory name
        classes_txt_path: Optional path to classes.txt
        
    Returns:
        Tuple of (success, message)
    """
    generator = StructureGenerator(analysis, output_dir, classes_txt_path)
    return generator.generate()


def check_needs_user_input(analysis: FileAnalysis | FolderAnalysis) -> bool:
    """Check if user input is needed for structure definition."""
    generator = StructureGenerator(analysis)
    generator._get_proposals()
    return generator.needs_user_input
