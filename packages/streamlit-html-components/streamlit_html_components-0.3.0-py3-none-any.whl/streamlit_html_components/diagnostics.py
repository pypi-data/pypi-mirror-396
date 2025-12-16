"""
Diagnostics and error suggestion utilities for streamlit-html-components.

This module provides helpful error messages with:
- "Did you mean?" suggestions for typos
- File path suggestions
- Validation error formatting
- Debug mode utilities
"""

from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
import difflib
from dataclasses import dataclass


@dataclass
class Suggestion:
    """A suggestion for correcting a user error."""
    suggestion: str
    confidence: float  # 0.0 to 1.0
    context: Optional[str] = None

    def __str__(self) -> str:
        if self.context:
            return f"'{self.suggestion}' ({self.context})"
        return f"'{self.suggestion}'"


class FuzzyMatcher:
    """Provides fuzzy string matching for helpful suggestions."""

    @staticmethod
    def get_close_matches(
        word: str,
        possibilities: List[str],
        n: int = 3,
        cutoff: float = 0.6
    ) -> List[Suggestion]:
        """
        Get close matches to a word from a list of possibilities.

        Args:
            word: The word to match
            possibilities: List of possible correct values
            n: Maximum number of suggestions to return
            cutoff: Similarity threshold (0.0 to 1.0)

        Returns:
            List of Suggestion objects sorted by confidence

        Example:
            >>> matcher = FuzzyMatcher()
            >>> suggestions = matcher.get_close_matches('buton', ['button', 'card', 'form'])
            >>> print(suggestions[0].suggestion)
            button
        """
        # Use difflib for fuzzy matching
        matches = difflib.get_close_matches(word, possibilities, n=n, cutoff=cutoff)

        # Calculate confidence scores
        suggestions = []
        for match in matches:
            ratio = difflib.SequenceMatcher(None, word.lower(), match.lower()).ratio()
            suggestions.append(Suggestion(
                suggestion=match,
                confidence=ratio
            ))

        return sorted(suggestions, key=lambda s: s.confidence, reverse=True)

    @staticmethod
    def get_best_match(word: str, possibilities: List[str], cutoff: float = 0.6) -> Optional[Suggestion]:
        """
        Get the single best match for a word.

        Args:
            word: The word to match
            possibilities: List of possible correct values
            cutoff: Similarity threshold (0.0 to 1.0)

        Returns:
            Best Suggestion or None if no good match

        Example:
            >>> matcher = FuzzyMatcher()
            >>> best = matcher.get_best_match('templte', ['template', 'component'])
            >>> print(best.suggestion)
            template
        """
        matches = FuzzyMatcher.get_close_matches(word, possibilities, n=1, cutoff=cutoff)
        return matches[0] if matches else None


class PathSuggester:
    """Suggests file paths when files are not found."""

    @staticmethod
    def suggest_similar_files(
        missing_file: Path,
        search_dir: Path,
        pattern: str = "*",
        max_suggestions: int = 3
    ) -> List[Suggestion]:
        """
        Suggest similar files in a directory.

        Args:
            missing_file: The file that wasn't found
            search_dir: Directory to search in
            pattern: Glob pattern for file search
            max_suggestions: Maximum suggestions to return

        Returns:
            List of Suggestion objects with file paths

        Example:
            >>> suggester = PathSuggester()
            >>> suggestions = suggester.suggest_similar_files(
            ...     Path('buttn.html'),
            ...     Path('templates'),
            ...     '*.html'
            ... )
        """
        if not search_dir.exists():
            return []

        # Get all matching files in directory
        all_files = list(search_dir.glob(pattern))
        file_names = [f.name for f in all_files]

        # Find similar file names
        missing_name = missing_file.name
        matches = FuzzyMatcher.get_close_matches(
            missing_name,
            file_names,
            n=max_suggestions,
            cutoff=0.5
        )

        # Add context with full path
        suggestions = []
        for match in matches:
            full_path = search_dir / match.suggestion
            suggestions.append(Suggestion(
                suggestion=str(full_path.relative_to(search_dir.parent) if full_path.is_relative_to(search_dir.parent) else full_path),
                confidence=match.confidence,
                context=f"in {search_dir.name}/"
            ))

        return suggestions

    @staticmethod
    def suggest_directory_structure(base_dir: Path) -> Dict[str, List[str]]:
        """
        Analyze directory structure for diagnostic output.

        Args:
            base_dir: Base directory to analyze

        Returns:
            Dictionary mapping directory names to file lists

        Example:
            >>> suggester = PathSuggester()
            >>> structure = suggester.suggest_directory_structure(Path('components'))
            >>> print(structure['templates'])
            ['button.html', 'card.html']
        """
        structure = {}

        if not base_dir.exists():
            return structure

        for subdir in ['templates', 'styles', 'scripts']:
            dir_path = base_dir / subdir
            if dir_path.exists():
                structure[subdir] = [f.name for f in dir_path.iterdir() if f.is_file()]

        return structure


class ErrorFormatter:
    """Formats error messages with helpful context."""

    @staticmethod
    def format_validation_error(
        error_type: str,
        message: str,
        suggestions: Optional[List[Suggestion]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format a validation error with suggestions and context.

        Args:
            error_type: Type of error (e.g., "ComponentNotFound")
            message: Main error message
            suggestions: Optional list of suggestions
            context: Optional context dictionary

        Returns:
            Formatted error message

        Example:
            >>> formatter = ErrorFormatter()
            >>> msg = formatter.format_validation_error(
            ...     "ComponentNotFound",
            ...     "Component 'buton' not found",
            ...     suggestions=[Suggestion('button', 0.83)]
            ... )
        """
        lines = [f"{error_type}: {message}"]

        # Add suggestions if available
        if suggestions:
            lines.append("")
            if len(suggestions) == 1:
                lines.append(f"Did you mean '{suggestions[0].suggestion}'?")
            else:
                lines.append("Did you mean one of these?")
                for i, sug in enumerate(suggestions[:3], 1):
                    confidence_pct = int(sug.confidence * 100)
                    context_str = f" {sug.context}" if sug.context else ""
                    lines.append(f"  {i}. {sug.suggestion}{context_str} ({confidence_pct}% match)")

        # Add context if available
        if context:
            lines.append("")
            lines.append("Context:")
            for key, value in context.items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)

    @staticmethod
    def format_component_list(components: List[str], title: str = "Available components") -> str:
        """
        Format a list of components for display.

        Args:
            components: List of component names
            title: Title for the list

        Returns:
            Formatted component list

        Example:
            >>> formatter = ErrorFormatter()
            >>> msg = formatter.format_component_list(['button', 'card', 'form'])
        """
        if not components:
            return f"{title}: (none)"

        lines = [f"{title}:"]
        for component in sorted(components):
            lines.append(f"  - {component}")

        return "\n".join(lines)

    @staticmethod
    def format_file_tree(structure: Dict[str, List[str]], title: str = "Component directory structure") -> str:
        """
        Format a directory structure as a tree.

        Args:
            structure: Dictionary mapping directories to file lists
            title: Title for the tree

        Returns:
            Formatted file tree

        Example:
            >>> formatter = ErrorFormatter()
            >>> tree = formatter.format_file_tree({
            ...     'templates': ['button.html'],
            ...     'styles': ['button.css']
            ... })
        """
        if not structure:
            return f"{title}: (empty)"

        lines = [f"{title}:"]
        for dir_name, files in sorted(structure.items()):
            lines.append(f"  {dir_name}/")
            if files:
                for file in sorted(files):
                    lines.append(f"    - {file}")
            else:
                lines.append("    (empty)")

        return "\n".join(lines)


class DebugMode:
    """Utilities for debug mode with verbose output."""

    _enabled: bool = False
    _verbose_level: int = 0  # 0=off, 1=info, 2=debug, 3=trace

    @classmethod
    def enable(cls, verbose_level: int = 1):
        """
        Enable debug mode.

        Args:
            verbose_level: Level of verbosity (0-3)
        """
        cls._enabled = True
        cls._verbose_level = verbose_level

    @classmethod
    def disable(cls):
        """Disable debug mode."""
        cls._enabled = False
        cls._verbose_level = 0

    @classmethod
    def is_enabled(cls) -> bool:
        """Check if debug mode is enabled."""
        return cls._enabled

    @classmethod
    def get_level(cls) -> int:
        """Get current verbosity level."""
        return cls._verbose_level

    @classmethod
    def log(cls, message: str, level: int = 1, prefix: str = "DEBUG"):
        """
        Log a debug message if debug mode is enabled and level is appropriate.

        Args:
            message: Message to log
            level: Required verbosity level to show this message
            prefix: Prefix for the log message
        """
        if cls._enabled and cls._verbose_level >= level:
            print(f"[{prefix}] {message}")

    @classmethod
    def log_info(cls, message: str):
        """Log an info message (level 1)."""
        cls.log(message, level=1, prefix="INFO")

    @classmethod
    def log_debug(cls, message: str):
        """Log a debug message (level 2)."""
        cls.log(message, level=2, prefix="DEBUG")

    @classmethod
    def log_trace(cls, message: str):
        """Log a trace message (level 3)."""
        cls.log(message, level=3, prefix="TRACE")


# Export public API
__all__ = [
    'Suggestion',
    'FuzzyMatcher',
    'PathSuggester',
    'ErrorFormatter',
    'DebugMode'
]
