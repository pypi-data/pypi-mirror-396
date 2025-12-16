"""Template engine using Jinja2 for HTML templating with variable interpolation."""

from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError as Jinja2TemplateSyntaxError
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .exceptions import ComponentNotFoundError, TemplateSyntaxError


class TemplateEngine:
    """
    Template engine for rendering HTML templates with Jinja2.

    Features:
    - Auto-escaping for XSS prevention
    - Template caching for performance
    - Custom filters (currency, date formatting)
    - Template inheritance and includes
    """

    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the template engine.

        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = Path(templates_dir)
        self._env = None
        self._initialize_environment()

    def _initialize_environment(self):
        """Initialize Jinja2 environment with security and performance settings."""
        if not self.templates_dir.exists():
            # Don't raise error here - allow creation later
            # Just initialize with empty string loader
            self._env = Environment(
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True,
                cache_size=400  # Jinja's internal template cache
            )
        else:
            self._env = Environment(
                loader=FileSystemLoader(self.templates_dir),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True,
                cache_size=400
            )

        # Add custom filters
        self._env.filters['currency'] = self._format_currency
        self._env.filters['date'] = self._format_date
        self._env.filters['percentage'] = self._format_percentage

    def update_templates_dir(self, templates_dir: str):
        """
        Update the templates directory and reinitialize environment.

        Args:
            templates_dir: New templates directory path
        """
        self.templates_dir = Path(templates_dir)
        self._initialize_environment()

    @lru_cache(maxsize=128)
    def load_template(self, template_name: str) -> Template:
        """
        Load and cache a template by name.

        Args:
            template_name: Name of the template (without .html extension)

        Returns:
            Jinja2 Template object

        Raises:
            ComponentNotFoundError: If template file not found
            TemplateSyntaxError: If template has syntax errors
        """
        # Ensure templates directory exists
        if not self.templates_dir.exists():
            raise ComponentNotFoundError(
                f"Templates directory not found: {self.templates_dir}\n"
                f"Create the directory or specify a valid templates_dir."
            )

        template_file = f"{template_name}.html"

        try:
            return self._env.get_template(template_file)
        except TemplateNotFound:
            # List available templates for helpful error message
            available = []
            if self.templates_dir.exists():
                available = [
                    f.stem for f in self.templates_dir.glob("*.html")
                ]

            error_msg = f"Template '{template_name}' not found in {self.templates_dir}"
            if available:
                error_msg += f"\n\nAvailable templates: {', '.join(available)}"

                # Suggest closest match
                closest = self._find_closest_match(template_name, available)
                if closest:
                    error_msg += f"\n\nDid you mean: '{closest}'?"
            else:
                error_msg += "\n\nNo templates found in directory."

            raise ComponentNotFoundError(error_msg)
        except Jinja2TemplateSyntaxError as e:
            raise TemplateSyntaxError(
                f"Syntax error in template '{template_name}':\n"
                f"Line {e.lineno}: {e.message}"
            )

    def render(self, template_name: str, props: Dict[str, Any]) -> str:
        """
        Render a template with provided props.

        Args:
            template_name: Name of the template to render
            props: Dictionary of variables to pass to template

        Returns:
            Rendered HTML string

        Raises:
            ComponentNotFoundError: If template not found
            TemplateSyntaxError: If template has syntax errors
        """
        template = self.load_template(template_name)
        try:
            return template.render(**props)
        except Exception as e:
            raise TemplateSyntaxError(
                f"Error rendering template '{template_name}': {str(e)}"
            )

    def render_string(self, template_string: str, props: Dict[str, Any]) -> str:
        """
        Render a template from a string (for inline templates).

        Args:
            template_string: Template content as string
            props: Dictionary of variables to pass to template

        Returns:
            Rendered HTML string

        Raises:
            TemplateSyntaxError: If template has syntax errors
        """
        try:
            template = self._env.from_string(template_string)
            return template.render(**props)
        except Jinja2TemplateSyntaxError as e:
            raise TemplateSyntaxError(
                f"Syntax error in inline template:\n"
                f"Line {e.lineno}: {e.message}"
            )
        except Exception as e:
            raise TemplateSyntaxError(
                f"Error rendering inline template: {str(e)}"
            )

    @staticmethod
    def _format_currency(value: float, symbol: str = "$", decimals: int = 2) -> str:
        """
        Custom filter for currency formatting.

        Args:
            value: Numeric value to format
            symbol: Currency symbol (default: $)
            decimals: Number of decimal places (default: 2)

        Returns:
            Formatted currency string

        Example:
            {{ price | currency }} -> "$1,234.56"
            {{ price | currency("€", 0) }} -> "€1,235"
        """
        try:
            value = float(value)
            return f"{symbol}{value:,.{decimals}f}"
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def _format_date(value, format: str = "%Y-%m-%d") -> str:
        """
        Custom filter for date formatting.

        Args:
            value: Date value (datetime object or string)
            format: strftime format string (default: %Y-%m-%d)

        Returns:
            Formatted date string

        Example:
            {{ date | date }} -> "2025-12-10"
            {{ date | date("%B %d, %Y") }} -> "December 10, 2025"
        """
        try:
            if isinstance(value, str):
                # Try to parse string to datetime
                value = datetime.fromisoformat(value)
            return value.strftime(format)
        except (ValueError, AttributeError, TypeError):
            return str(value)

    @staticmethod
    def _format_percentage(value: float, decimals: int = 1) -> str:
        """
        Custom filter for percentage formatting.

        Args:
            value: Numeric value (0.15 = 15%)
            decimals: Number of decimal places (default: 1)

        Returns:
            Formatted percentage string

        Example:
            {{ 0.156 | percentage }} -> "15.6%"
            {{ 0.5 | percentage(0) }} -> "50%"
        """
        try:
            value = float(value) * 100
            return f"{value:.{decimals}f}%"
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def _find_closest_match(target: str, candidates: list) -> str:
        """
        Find closest matching string from candidates (simple Levenshtein distance).

        Args:
            target: String to match
            candidates: List of candidate strings

        Returns:
            Closest matching candidate or empty string
        """
        if not candidates:
            return ""

        def levenshtein_distance(s1: str, s2: str) -> int:
            """Calculate Levenshtein distance between two strings."""
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)

            if len(s2) == 0:
                return len(s1)

            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    # j+1 instead of j since previous_row and current_row are one character longer than s2
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row

            return previous_row[-1]

        # Find candidate with minimum distance
        closest = min(candidates, key=lambda c: levenshtein_distance(target.lower(), c.lower()))

        # Only suggest if distance is reasonable (less than half the length)
        if levenshtein_distance(target.lower(), closest.lower()) < len(target) / 2:
            return closest

        return ""
