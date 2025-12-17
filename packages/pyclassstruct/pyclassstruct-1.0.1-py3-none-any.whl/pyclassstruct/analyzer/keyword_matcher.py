"""
Advanced keyword matching with stemming, fuzzy matching, and priority weights.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from functools import lru_cache


class KeywordMatcher:
    """Advanced keyword matcher with stemming and priority support."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Singleton pattern to avoid reloading config."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load keyword configuration from JSON file."""
        config_path = Path(__file__).parent / "keywords.json"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        else:
            self._config = self._get_default_config()
        
        # Build reverse lookup dictionaries
        self._keyword_to_class: Dict[str, Tuple[str, int]] = {}
        self._stem_to_root: Dict[str, str] = {}
        
        self._build_lookups()
    
    def _build_lookups(self):
        """Build optimized lookup dictionaries."""
        # Build keyword -> (class_name, priority) mapping
        categories = self._config.get("categories", {})
        for cat_name, cat_data in categories.items():
            class_name = cat_data.get("class_name", "Handler")
            priority = cat_data.get("priority", 5)
            
            for keyword in cat_data.get("keywords", []):
                keyword_lower = keyword.lower()
                # Only override if new priority is higher
                if keyword_lower not in self._keyword_to_class or \
                   priority > self._keyword_to_class[keyword_lower][1]:
                    self._keyword_to_class[keyword_lower] = (class_name, priority)
        
        # Build stem mappings
        stem_mappings = self._config.get("stem_mappings", {})
        for root, variations in stem_mappings.items():
            root_lower = root.lower()
            for variation in variations:
                self._stem_to_root[variation.lower()] = root_lower
    
    @lru_cache(maxsize=1000)
    def _get_root_form(self, word: str) -> str:
        """Get the root form of a word using stem mappings."""
        word_lower = word.lower()
        
        # Check direct stem mapping
        if word_lower in self._stem_to_root:
            return self._stem_to_root[word_lower]
        
        # Try common suffix stripping (simple stemming)
        suffixes = ['ing', 'ed', 'er', 'or', 's', 'tion', 'ation', 'ment', 'ness', 'able', 'ible', 'ity']
        for suffix in suffixes:
            if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
                stem = word_lower[:-len(suffix)]
                if stem in self._keyword_to_class:
                    return stem
                # Handle doubling consonant (e.g., "logging" -> "log")
                if stem.endswith(stem[-1]) and len(stem) > 2:
                    shortened = stem[:-1]
                    if shortened in self._keyword_to_class:
                        return shortened
        
        return word_lower
    
    def match_keywords(self, function_names: List[str]) -> Dict[str, Tuple[int, int]]:
        """
        Match function names to class names with priority weights.
        
        Args:
            function_names: List of function names to analyze
            
        Returns:
            Dict mapping class_name -> (match_count, total_priority)
        """
        class_scores: Dict[str, Tuple[int, int]] = defaultdict(lambda: (0, 0))
        
        for func_name in function_names:
            # Split function name into parts
            parts = self._split_name(func_name)
            
            for part in parts:
                # Get root form
                root = self._get_root_form(part)
                
                # Check for match
                if root in self._keyword_to_class:
                    class_name, priority = self._keyword_to_class[root]
                    count, total_pri = class_scores[class_name]
                    class_scores[class_name] = (count + 1, total_pri + priority)
                elif part in self._keyword_to_class:
                    class_name, priority = self._keyword_to_class[part]
                    count, total_pri = class_scores[class_name]
                    class_scores[class_name] = (count + 1, total_pri + priority)
        
        return dict(class_scores)
    
    def get_best_class_name(self, function_names: List[str]) -> Optional[str]:
        """
        Get the best matching class name for a group of functions.
        
        Uses a scoring algorithm that considers:
        - Number of keyword matches
        - Priority weight of matched keywords
        
        Args:
            function_names: List of function names
            
        Returns:
            Best matching class name, or None if no matches
        """
        scores = self.match_keywords(function_names)
        
        if not scores:
            return None
        
        # Score = (match_count * 10) + total_priority
        # This favors classes with many matches but also considers priority
        best_class = max(
            scores.keys(),
            key=lambda c: (scores[c][0] * 10) + scores[c][1]
        )
        
        return best_class
    
    def _split_name(self, name: str) -> List[str]:
        """Split a function name into component words."""
        # Handle snake_case
        if '_' in name:
            parts = [p.lower() for p in name.split('_') if p]
        else:
            # Handle camelCase/PascalCase
            parts = re.findall('[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', name)
            parts = [p.lower() for p in parts]
        
        return parts
    
    def get_all_keywords(self) -> Dict[str, str]:
        """Get all keywords and their class mappings."""
        return {k: v[0] for k, v in self._keyword_to_class.items()}
    
    def add_custom_keyword(self, keyword: str, class_name: str, priority: int = 5):
        """Add a custom keyword mapping at runtime."""
        self._keyword_to_class[keyword.lower()] = (class_name, priority)
    
    def _get_default_config(self) -> dict:
        """Return default configuration if JSON file not found."""
        return {
            "categories": {
                "utility": {
                    "class_name": "Utils",
                    "priority": 2,
                    "keywords": ["util", "utils", "helper", "common"]
                }
            },
            "stem_mappings": {}
        }


# Convenience function
def get_matcher() -> KeywordMatcher:
    """Get the singleton KeywordMatcher instance."""
    return KeywordMatcher()


def match_function_names(function_names: List[str]) -> Optional[str]:
    """
    Convenience function to get best class name for function names.
    
    Args:
        function_names: List of function names
        
    Returns:
        Best matching class name
    """
    matcher = get_matcher()
    return matcher.get_best_class_name(function_names)
