"""Global configuration management for streamlit-html-components."""

from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class Config:
    """
    Global configuration for streamlit-html-components.

    Attributes:
        templates_dir: Directory containing HTML templates
        styles_dir: Directory containing CSS files
        scripts_dir: Directory containing JavaScript files
        default_cache: Enable caching by default for all components
        default_cache_ttl: Default time-to-live for cache (None = no expiration)
        enable_bidirectional: Enable bidirectional JS-Python communication
        external_frameworks: List of external frameworks to include by default
    """

    templates_dir: str = "templates"
    styles_dir: str = "styles"
    scripts_dir: str = "scripts"
    default_cache: bool = True
    default_cache_ttl: Optional[int] = None
    enable_bidirectional: bool = True
    external_frameworks: List[str] = field(default_factory=list)


# Global configuration instance
_config = Config()


def configure(
    templates_dir: Optional[str] = None,
    styles_dir: Optional[str] = None,
    scripts_dir: Optional[str] = None,
    default_cache: Optional[bool] = None,
    default_cache_ttl: Optional[int] = None,
    enable_bidirectional: Optional[bool] = None,
    external_frameworks: Optional[List[str]] = None
) -> None:
    """
    Configure global settings for streamlit-html-components.

    This function updates the global configuration that will be used
    as defaults for all render_component() calls.

    Args:
        templates_dir: Directory containing HTML templates
        styles_dir: Directory containing CSS files
        scripts_dir: Directory containing JavaScript files
        default_cache: Enable caching by default
        default_cache_ttl: Default cache time-to-live in seconds (None = no expiration)
        enable_bidirectional: Enable bidirectional communication
        external_frameworks: List of frameworks to include ('tailwind', 'bootstrap', etc.)

    Example:
        >>> from streamlit_html_components import configure
        >>> configure(
        ...     templates_dir='components/templates',
        ...     styles_dir='components/styles',
        ...     scripts_dir='components/scripts',
        ...     default_cache=True,
        ...     external_frameworks=['tailwind']
        ... )
    """
    global _config

    if templates_dir is not None:
        _config.templates_dir = templates_dir

    if styles_dir is not None:
        _config.styles_dir = styles_dir

    if scripts_dir is not None:
        _config.scripts_dir = scripts_dir

    if default_cache is not None:
        _config.default_cache = default_cache

    if default_cache_ttl is not None:
        _config.default_cache_ttl = default_cache_ttl

    if enable_bidirectional is not None:
        _config.enable_bidirectional = enable_bidirectional

    if external_frameworks is not None:
        _config.external_frameworks = external_frameworks


def get_config() -> Config:
    """
    Get the current global configuration.

    Returns:
        Current Config instance
    """
    return _config


def reset_config():
    """
    Reset configuration to default values.

    Useful for testing or resetting state.
    """
    global _config
    _config = Config()
