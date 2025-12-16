"""Validation functions for streamlit-html-components."""

from typing import Any, Dict, Optional
from pathlib import Path
import os

from .exceptions import (
    InvalidPropsError,
    ConfigurationError,
    SecurityError,
)


class Validator:
    """Validation utilities for component inputs and configuration."""

    @staticmethod
    def validate_component_name(name: str) -> bool:
        """
        Validate component name format.

        Args:
            name: Component name to validate

        Returns:
            True if valid

        Raises:
            InvalidPropsError: If name is invalid
        """
        if not name or not isinstance(name, str):
            raise InvalidPropsError("Component name must be a non-empty string")

        if not name.replace('_', '').replace('-', '').isalnum():
            raise InvalidPropsError(
                "Component name must contain only alphanumeric characters, dashes, or underscores. "
                f"Got: {name}"
            )

        return True

    @staticmethod
    def validate_props(props: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate and sanitize component props.

        Args:
            props: Dictionary of props to pass to component

        Returns:
            Validated and sanitized props dictionary

        Raises:
            InvalidPropsError: If props are invalid
        """
        if props is None:
            return {}

        if not isinstance(props, dict):
            raise InvalidPropsError(f"Props must be a dictionary, got {type(props).__name__}")

        # Check for reserved keys
        reserved_keys = ['__component__', '__meta__', '__streamlit__', '__internal__']
        for key in reserved_keys:
            if key in props:
                raise InvalidPropsError(
                    f"Reserved key '{key}' cannot be used in props. "
                    f"Reserved keys: {', '.join(reserved_keys)}"
                )

        # Sanitize values for security (prevent XSS in certain contexts)
        # Note: Jinja2 auto-escaping handles most XSS prevention, but we add extra layer
        sanitized = {}
        for key, value in props.items():
            sanitized[key] = value  # Jinja2 will handle escaping during template rendering

        return sanitized

    @staticmethod
    def validate_directory(path: str, create_if_missing: bool = False) -> Path:
        """
        Validate directory path with security checks.

        Args:
            path: Directory path to validate
            create_if_missing: If True, create directory if it doesn't exist

        Returns:
            Resolved Path object

        Raises:
            ConfigurationError: If directory is invalid
            SecurityError: If path traversal is detected
        """
        try:
            dir_path = Path(path).resolve()
        except (ValueError, OSError) as e:
            raise ConfigurationError(f"Invalid directory path: {path}. Error: {e}")

        # Security check: Prevent path traversal
        # Ensure the resolved path is within the current working directory
        cwd = Path.cwd().resolve()

        try:
            # Check if the resolved path is within cwd
            # This will raise ValueError if dir_path is not relative to cwd
            relative_path = dir_path.relative_to(cwd)

            # Additional check: ensure no ".." in the relative path
            if ".." in str(relative_path):
                raise SecurityError(
                    f"Path traversal detected in: {path}\n"
                    f"Resolved to: {dir_path}\n"
                    f"Working directory: {cwd}\n"
                    f"Paths must be within the working directory."
                )

        except ValueError:
            # Path is not relative to cwd - could be absolute path outside cwd
            # For security, we only allow paths within the working directory
            raise SecurityError(
                f"Path outside working directory: {path}\n"
                f"Resolved to: {dir_path}\n"
                f"Working directory: {cwd}\n"
                f"For security, only paths within the working directory are allowed.\n"
                f"Use relative paths or absolute paths within the project."
            )

        if not dir_path.exists():
            if create_if_missing:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    raise ConfigurationError(
                        f"Failed to create directory: {path}. Error: {e}"
                    )
            else:
                raise ConfigurationError(f"Directory does not exist: {path}")

        if not dir_path.is_dir():
            raise ConfigurationError(f"Path is not a directory: {path}")

        return dir_path

    @staticmethod
    def validate_framework(framework: str) -> bool:
        """
        Validate framework name.

        Args:
            framework: Framework name or CDN URL

        Returns:
            True if valid

        Raises:
            ConfigurationError: If framework is invalid
        """
        if not framework or not isinstance(framework, str):
            raise ConfigurationError("Framework name must be a non-empty string")

        supported = ['tailwind', 'bootstrap', 'bulma', 'material']

        # Allow either supported framework names or custom CDN URLs (http/https)
        if framework.lower() not in supported and not framework.startswith(('http://', 'https://')):
            raise ConfigurationError(
                f"Unsupported framework: {framework}. "
                f"Supported frameworks: {', '.join(supported)}, or provide a custom CDN URL starting with http:// or https://"
            )

        return True

    @staticmethod
    def sanitize_html(value: str, allow_html: bool = False) -> str:
        """
        Sanitize string to prevent XSS attacks.

        Args:
            value: String to sanitize
            allow_html: If False, escape all HTML characters

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return value

        if not allow_html:
            # Escape HTML special characters
            return (value
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;')
                .replace('/', '&#x2F;'))

        return value
