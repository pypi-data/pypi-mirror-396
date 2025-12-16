"""
Modern configuration system using Pydantic for validation and immutability.

This replaces the old mutable dataclass-based config with a robust,
validated, immutable configuration system.
"""

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class CacheConfig(BaseModel):
    """Cache configuration with validation."""

    enabled: bool = Field(
        default=True,
        description="Enable component caching"
    )

    max_size_mb: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum cache size in megabytes"
    )

    ttl_seconds: Optional[int] = Field(
        default=None,
        ge=0,
        description="Time-to-live for cache entries in seconds (None = no expiration)"
    )

    model_config = ConfigDict(frozen=True)


class SecurityConfig(BaseModel):
    """Security configuration."""

    enable_csp: bool = Field(
        default=True,
        description="Enable Content Security Policy headers"
    )

    allowed_origins: List[str] = Field(
        default_factory=lambda: ['*'],
        description="Allowed origins for bidirectional communication"
    )

    validate_paths: bool = Field(
        default=True,
        description="Enable path traversal validation"
    )

    sandbox_templates: bool = Field(
        default=False,
        description="Use Jinja2 sandbox mode (future feature)"
    )

    model_config = ConfigDict(frozen=True)


class ComponentConfig(BaseModel):
    """
    Main configuration for the component renderer.

    This configuration is immutable once created, preventing accidental
    mutation bugs. All paths are validated to exist and be directories.

    Example:
        >>> config = ComponentConfig(
        ...     templates_dir='components/templates',
        ...     styles_dir='components/styles',
        ...     scripts_dir='components/scripts',
        ...     frameworks=['tailwind']
        ... )
    """

    templates_dir: Path = Field(
        description="Directory containing Jinja2 templates"
    )

    styles_dir: Path = Field(
        description="Directory containing CSS files"
    )

    scripts_dir: Path = Field(
        description="Directory containing JavaScript files"
    )

    frameworks: List[str] = Field(
        default_factory=list,
        description="External frameworks to load (e.g., 'tailwind', 'bootstrap')"
    )

    cache: CacheConfig = Field(
        default_factory=CacheConfig,
        description="Cache configuration"
    )

    security: SecurityConfig = Field(
        default_factory=SecurityConfig,
        description="Security configuration"
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator('templates_dir', 'styles_dir', 'scripts_dir', mode='before')
    @classmethod
    def validate_directory(cls, v) -> Path:
        """
        Validate that the directory exists and is actually a directory.
        Also checks for path traversal attacks.
        """
        path = Path(v)

        # Check existence
        if not path.exists():
            raise ValueError(f"Directory does not exist: {path}")

        # Check it's actually a directory
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        # Resolve to absolute path
        resolved_path = path.resolve()

        # Path traversal check - ensure path is within or descendant of cwd
        try:
            cwd = Path.cwd().resolve()
            # This will raise ValueError if resolved_path is not relative to cwd
            # We allow both subdirectories of cwd and the cwd itself
            if not (str(resolved_path).startswith(str(cwd)) or resolved_path == cwd):
                # Check if it's an absolute path that's explicitly allowed
                # (for system-wide installations)
                if not resolved_path.is_absolute():
                    raise ValueError(
                        f"Path outside working directory: {resolved_path}\n"
                        f"Working directory: {cwd}\n"
                        f"For security, only paths within the working directory are allowed."
                    )
        except Exception as e:
            # If any error occurs during validation, be safe and reject
            raise ValueError(
                f"Invalid directory path: {path}\n"
                f"Error: {e}"
            )

        return resolved_path

    @field_validator('frameworks')
    @classmethod
    def validate_frameworks(cls, v: List[str]) -> List[str]:
        """Validate framework names."""
        valid_frameworks = {'tailwind', 'bootstrap', 'bulma', 'material'}

        for framework in v:
            # Allow known frameworks or HTTP(S) URLs
            if framework.lower() not in valid_frameworks:
                if not (framework.startswith('http://') or framework.startswith('https://')):
                    raise ValueError(
                        f"Unknown framework: {framework}\n"
                        f"Valid frameworks: {', '.join(sorted(valid_frameworks))}\n"
                        f"Or provide a full HTTP(S) URL"
                    )

        return v


def create_default_config(
    templates_dir: str = 'templates',
    styles_dir: str = 'styles',
    scripts_dir: str = 'scripts',
    **kwargs
) -> ComponentConfig:
    """
    Create a configuration with common defaults.

    Args:
        templates_dir: Path to templates directory
        styles_dir: Path to styles directory
        scripts_dir: Path to scripts directory
        **kwargs: Additional configuration options

    Returns:
        ComponentConfig instance

    Example:
        >>> config = create_default_config(
        ...     templates_dir='my_app/templates',
        ...     frameworks=['tailwind']
        ... )
    """
    return ComponentConfig(
        templates_dir=templates_dir,
        styles_dir=styles_dir,
        scripts_dir=scripts_dir,
        **kwargs
    )
