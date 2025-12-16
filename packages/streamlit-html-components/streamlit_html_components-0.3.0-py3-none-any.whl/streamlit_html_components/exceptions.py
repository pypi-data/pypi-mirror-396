"""
Custom exceptions for streamlit-html-components package.

Enhanced exceptions with contextual error messages and suggestions.
"""

from typing import Optional, List, Dict, Any


class StreamlitHtmlComponentsError(Exception):
    """
    Base exception for all streamlit-html-components errors.

    Provides enhanced error messages with context and suggestions.
    """

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize exception with message and optional context.

        Args:
            message: Error message
            context: Optional dictionary with additional context
        """
        self.message = message
        self.context = context or {}
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with context."""
        lines = [self.message]

        if self.context:
            lines.append("")
            lines.append("Context:")
            for key, value in self.context.items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)


class ComponentNotFoundError(StreamlitHtmlComponentsError):
    """
    Raised when a component template cannot be found.

    Provides suggestions for similar component names.
    """

    def __init__(
        self,
        component_name: str,
        suggestions: Optional[List[str]] = None,
        available_components: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize ComponentNotFoundError.

        Args:
            component_name: Name of the component that wasn't found
            suggestions: Optional list of suggested component names
            available_components: Optional list of all available components
            context: Optional additional context
        """
        self.component_name = component_name
        self.suggestions = suggestions or []
        self.available_components = available_components or []

        # Build message
        message = f"Component '{component_name}' not found"

        # Add to context
        full_context = context or {}
        full_context['requested_component'] = component_name

        super().__init__(message, full_context)

    def _format_message(self) -> str:
        """Format error message with suggestions."""
        lines = [f"Component '{self.component_name}' not found"]

        # Add suggestions
        if self.suggestions:
            lines.append("")
            if len(self.suggestions) == 1:
                lines.append(f"Did you mean '{self.suggestions[0]}'?")
            else:
                lines.append("Did you mean one of these?")
                for i, suggestion in enumerate(self.suggestions[:3], 1):
                    lines.append(f"  {i}. {suggestion}")

        # Add available components
        elif self.available_components:
            lines.append("")
            lines.append("Available components:")
            for component in sorted(self.available_components[:10]):
                lines.append(f"  - {component}")
            if len(self.available_components) > 10:
                lines.append(f"  ... and {len(self.available_components) - 10} more")

        # Add context
        if self.context:
            lines.append("")
            lines.append("Context:")
            for key, value in self.context.items():
                if key != 'requested_component':  # Already shown above
                    lines.append(f"  {key}: {value}")

        return "\n".join(lines)


class AssetNotFoundError(StreamlitHtmlComponentsError):
    """
    Raised when a CSS or JavaScript asset file cannot be found.

    Provides suggestions for similar file names and shows directory structure.
    """

    def __init__(
        self,
        asset_path: str,
        asset_type: str,
        suggestions: Optional[List[str]] = None,
        search_directory: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize AssetNotFoundError.

        Args:
            asset_path: Path to the asset that wasn't found
            asset_type: Type of asset ('style' or 'script')
            suggestions: Optional list of similar file names
            search_directory: Directory where asset was searched for
            context: Optional additional context
        """
        self.asset_path = asset_path
        self.asset_type = asset_type
        self.suggestions = suggestions or []
        self.search_directory = search_directory

        message = f"{asset_type.capitalize()} asset '{asset_path}' not found"

        full_context = context or {}
        full_context['asset_path'] = asset_path
        full_context['asset_type'] = asset_type
        if search_directory:
            full_context['searched_in'] = search_directory

        super().__init__(message, full_context)

    def _format_message(self) -> str:
        """Format error message with file suggestions."""
        lines = [f"{self.asset_type.capitalize()} asset '{self.asset_path}' not found"]

        if self.search_directory:
            lines.append(f"Searched in: {self.search_directory}")

        # Add suggestions
        if self.suggestions:
            lines.append("")
            if len(self.suggestions) == 1:
                lines.append(f"Did you mean '{self.suggestions[0]}'?")
            else:
                lines.append("Similar files found:")
                for i, suggestion in enumerate(self.suggestions[:5], 1):
                    lines.append(f"  {i}. {suggestion}")

        # Add context (skip already-shown fields)
        if self.context:
            skip_fields = {'asset_path', 'asset_type', 'searched_in'}
            remaining_context = {k: v for k, v in self.context.items() if k not in skip_fields}

            if remaining_context:
                lines.append("")
                lines.append("Context:")
                for key, value in remaining_context.items():
                    lines.append(f"  {key}: {value}")

        return "\n".join(lines)


class TemplateSyntaxError(StreamlitHtmlComponentsError):
    """
    Raised when a template contains syntax errors.

    Shows the line number and context around the error.
    """

    def __init__(
        self,
        template_path: str,
        error_message: str,
        line_number: Optional[int] = None,
        line_content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize TemplateSyntaxError.

        Args:
            template_path: Path to the template file
            error_message: Underlying error message
            line_number: Line number where error occurred
            line_content: Content of the line with the error
            context: Optional additional context
        """
        self.template_path = template_path
        self.error_message = error_message
        self.line_number = line_number
        self.line_content = line_content

        message = f"Template syntax error in '{template_path}'"

        full_context = context or {}
        full_context['template'] = template_path
        full_context['error'] = error_message
        if line_number is not None:
            full_context['line'] = line_number

        super().__init__(message, full_context)

    def _format_message(self) -> str:
        """Format error message with line context."""
        lines = [f"Template syntax error in '{self.template_path}'"]

        if self.line_number is not None:
            lines.append(f"Line {self.line_number}: {self.error_message}")

            if self.line_content:
                lines.append("")
                lines.append(f"  {self.line_number} | {self.line_content}")
                lines.append("       " + "^" * len(self.line_content))
        else:
            lines.append(f"Error: {self.error_message}")

        return "\n".join(lines)


class InvalidPropsError(StreamlitHtmlComponentsError):
    """
    Raised when component props fail validation.

    Shows which props failed validation and why.
    """

    def __init__(
        self,
        message: str,
        invalid_props: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize InvalidPropsError.

        Args:
            message: Error message
            invalid_props: Dictionary mapping prop names to error messages
            context: Optional additional context
        """
        self.invalid_props = invalid_props or {}

        full_context = context or {}
        if invalid_props:
            full_context['invalid_props'] = invalid_props

        super().__init__(message, full_context)

    def _format_message(self) -> str:
        """Format error message with prop validation details."""
        lines = [self.message]

        if self.invalid_props:
            lines.append("")
            lines.append("Validation errors:")
            for prop_name, error_msg in self.invalid_props.items():
                lines.append(f"  - {prop_name}: {error_msg}")

        return "\n".join(lines)


class ConfigurationError(StreamlitHtmlComponentsError):
    """
    Raised when package configuration is invalid.

    Provides guidance on correct configuration.
    """
    pass


class SecurityError(StreamlitHtmlComponentsError):
    """
    Raised when a security violation is detected (e.g., path traversal).

    Provides details about the security issue and how to fix it.
    """
    pass
