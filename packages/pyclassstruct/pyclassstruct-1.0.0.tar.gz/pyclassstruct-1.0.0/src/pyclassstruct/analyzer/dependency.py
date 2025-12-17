"""
Dependency analysis and smart class grouping.
"""

from collections import defaultdict
from typing import List, Dict, Set, Tuple
import re

from .models import FunctionInfo, GlobalVarInfo, ClassProposal, FileAnalysis, FolderAnalysis


class DependencyAnalyzer:
    """Analyze function dependencies and group into classes."""
    
    def __init__(self, analysis: FileAnalysis | FolderAnalysis):
        self.analysis = analysis
        self.functions = self._get_all_functions()
        self.function_names = {f.name for f in self.functions}
        self.global_vars = self._get_all_global_vars()
        
        # Build dependency graph
        self.call_graph: Dict[str, Set[str]] = {}
        self.reverse_call_graph: Dict[str, Set[str]] = {}
        self._build_call_graph()
    
    def _get_all_functions(self) -> List[FunctionInfo]:
        """Get all functions from the analysis."""
        if isinstance(self.analysis, FileAnalysis):
            return self.analysis.functions
        else:
            return self.analysis.all_functions
    
    def _get_all_global_vars(self) -> List[GlobalVarInfo]:
        """Get all global variables from the analysis."""
        if isinstance(self.analysis, FileAnalysis):
            return self.analysis.global_vars
        else:
            return self.analysis.all_global_vars
    
    def _build_call_graph(self):
        """Build call graph showing which functions call which."""
        for func in self.functions:
            # Filter calls to only include local functions
            local_calls = func.calls & self.function_names
            self.call_graph[func.name] = local_calls
            
            # Build reverse graph (who calls this function)
            for called in local_calls:
                if called not in self.reverse_call_graph:
                    self.reverse_call_graph[called] = set()
                self.reverse_call_graph[called].add(func.name)
    
    def detect_class_proposals(self) -> List[ClassProposal]:
        """Detect and propose class structures based on analysis."""
        proposals = []
        
        # Strategy 1: Group by call relationships
        call_groups = self._group_by_calls()
        
        # Strategy 2: Group by naming patterns
        naming_groups = self._group_by_naming()
        
        # Strategy 3: Group by shared state
        state_groups = self._group_by_shared_state()
        
        # Merge strategies with priority
        merged = self._merge_groups(call_groups, naming_groups, state_groups)
        
        # Convert to ClassProposal objects
        for class_name, func_names in merged.items():
            funcs = [f for f in self.functions if f.name in func_names]
            proposals.append(ClassProposal(
                name=class_name,
                methods=funcs,
                description=f"Auto-detected class grouping {len(funcs)} related functions"
            ))
        
        # Handle ungrouped functions
        grouped_funcs = set()
        for p in proposals:
            grouped_funcs.update(p.method_names)
        
        ungrouped = [f for f in self.functions if f.name not in grouped_funcs]
        if ungrouped:
            # Try to create a Utils class or individual classes
            if len(ungrouped) <= 5:
                proposals.append(ClassProposal(
                    name="Utils",
                    methods=ungrouped,
                    description="Utility functions"
                ))
            else:
                # Create individual classes for standalone functions
                for func in ungrouped:
                    class_name = self._function_to_class_name(func.name)
                    proposals.append(ClassProposal(
                        name=class_name,
                        methods=[func],
                        description=f"Standalone function as class"
                    ))
        
        return proposals
    
    def _group_by_calls(self) -> Dict[str, Set[str]]:
        """Group functions that call each other."""
        groups = {}
        visited = set()
        
        def dfs(func_name: str, group: Set[str]):
            """Depth-first search to find connected functions."""
            if func_name in visited:
                return
            visited.add(func_name)
            group.add(func_name)
            
            # Add functions this function calls
            for called in self.call_graph.get(func_name, set()):
                dfs(called, group)
            
            # Add functions that call this function
            for caller in self.reverse_call_graph.get(func_name, set()):
                dfs(caller, group)
        
        # Find connected components
        for func in self.functions:
            if func.name not in visited:
                group = set()
                dfs(func.name, group)
                if len(group) > 1:  # Only create groups with multiple functions
                    # Use smart naming based on common prefix or semantic analysis
                    class_name = self._get_smart_class_name(list(group))
                    groups[class_name] = group
        
        return groups
    
    def _get_smart_class_name(self, func_names: List[str]) -> str:
        """Generate a smart class name from a group of functions."""
        # Strategy 1: Find common prefix
        common_prefix = self._find_common_prefix(func_names)
        if common_prefix and len(common_prefix) >= 3:
            return self._prefix_to_class_name(common_prefix)
        
        # Strategy 2: Look for domain-specific keywords
        keywords = {
            'user': 'UserManager',
            'database': 'DatabaseManager', 
            'db': 'DatabaseManager',
            'file': 'FileHandler',
            'read': 'FileHandler',
            'write': 'FileHandler',
            'query': 'DatabaseManager',
            'connect': 'ConnectionManager',
            'validate': 'Validator',
            'parse': 'Parser',
            'format': 'Formatter',
            'create': 'Factory',
            'delete': 'Manager',
            'update': 'Manager',
            'get': 'Manager',
            'save': 'Storage',
            'load': 'Loader',
        }
        
        # Count keyword occurrences
        keyword_counts = defaultdict(int)
        for name in func_names:
            parts = name.lower().split('_')
            for part in parts:
                if part in keywords:
                    keyword_counts[keywords[part]] += 1
        
        if keyword_counts:
            # Return the most common class name
            best_name = max(keyword_counts.keys(), key=lambda k: keyword_counts[k])
            return best_name
        
        # Strategy 3: Fallback - use the first function that looks like an entry point
        # (functions with fewer dependencies)
        entry_points = [f for f in func_names if len(self.call_graph.get(f, set())) > 0]
        if entry_points:
            main_func = entry_points[0]
            return self._function_to_class_name(main_func)
        
        # Final fallback
        return self._function_to_class_name(func_names[0])
    
    def _find_common_prefix(self, func_names: List[str]) -> str:
        """Find common prefix among function names."""
        if not func_names:
            return ""
        
        # Split all names by underscore
        split_names = [name.split('_') for name in func_names]
        
        # Find common prefix parts
        common = []
        min_len = min(len(parts) for parts in split_names)
        
        for i in range(min_len):
            parts_at_i = [parts[i] for parts in split_names]
            if len(set(parts_at_i)) == 1:
                common.append(parts_at_i[0])
            else:
                break
        
        return '_'.join(common)
    
    def _group_by_naming(self) -> Dict[str, Set[str]]:
        """Group functions by common naming prefixes."""
        groups = defaultdict(set)
        
        for func in self.functions:
            parts = func.name.split('_')
            if len(parts) >= 2:
                prefix = parts[0]
                # Only group if prefix is meaningful (not too short)
                if len(prefix) >= 3:
                    groups[prefix].add(func.name)
        
        # Filter out groups with only one function
        result = {}
        for prefix, funcs in groups.items():
            if len(funcs) > 1:
                class_name = self._prefix_to_class_name(prefix)
                result[class_name] = funcs
        
        return result
    
    def _group_by_shared_state(self) -> Dict[str, Set[str]]:
        """Group functions that share global state."""
        groups = defaultdict(set)
        
        # Map global variables to functions that use them
        var_to_funcs: Dict[str, Set[str]] = defaultdict(set)
        
        for func in self.functions:
            for var in func.global_reads | func.global_writes:
                var_to_funcs[var].add(func.name)
        
        # Group functions that share variables
        for var, funcs in var_to_funcs.items():
            if len(funcs) > 1:
                class_name = self._prefix_to_class_name(var)
                groups[class_name].update(funcs)
        
        return dict(groups)
    
    def _merge_groups(self, *group_dicts) -> Dict[str, Set[str]]:
        """Merge multiple grouping strategies, preferring call-based groups."""
        merged = {}
        assigned = set()
        
        for groups in group_dicts:
            for class_name, funcs in groups.items():
                # Remove already assigned functions
                remaining = funcs - assigned
                if len(remaining) > 1:
                    # Check if class name already exists
                    if class_name in merged:
                        class_name = f"{class_name}2"
                    merged[class_name] = remaining
                    assigned.update(remaining)
        
        return merged
    
    def _function_to_class_name(self, func_name: str) -> str:
        """Convert a function name to a CamelCase class name."""
        # Remove leading underscores
        name = func_name.lstrip('_')
        # Split by underscores and capitalize
        parts = name.split('_')
        class_name = ''.join(word.capitalize() for word in parts)
        # Add 'Handler' or 'Manager' suffix if needed
        if not class_name.endswith(('Handler', 'Manager', 'Service', 'Utils', 'Helper')):
            class_name += 'Handler'
        return class_name
    
    def _prefix_to_class_name(self, prefix: str) -> str:
        """Convert a prefix to a CamelCase class name."""
        class_name = prefix.capitalize()
        if len(class_name) < 4:
            return class_name + "Handler"
        if not class_name.endswith(('Handler', 'Manager', 'Service', 'Utils', 'Helper')):
            class_name += 'Manager'
        return class_name
    
    def get_shared_functions(self) -> List[FunctionInfo]:
        """Get functions that are called by multiple other functions (utility functions)."""
        shared = []
        for func in self.functions:
            callers = self.reverse_call_graph.get(func.name, set())
            if len(callers) >= 2:
                shared.append(func)
        return shared
    
    def can_detect_structure(self) -> bool:
        """Check if enough structure can be detected."""
        if len(self.functions) == 0:
            return False
        
        # Check if we have at least some call relationships or naming patterns
        has_calls = any(len(calls) > 0 for calls in self.call_graph.values())
        has_naming = any(len(f.name.split('_')) >= 2 for f in self.functions)
        
        return has_calls or has_naming
