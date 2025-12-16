"""
Modern core API for rendering HTML components in Streamlit.

This is the v2 API that uses:
- ComponentRenderer for thread-safe rendering (renderer.py)
- Pydantic-based configuration (config_v2.py)
- Component registry with validation (registry.py)
- Deterministic serialization (serialization.py)
- Improved caching with file content hashing
"""

from typing import Optional, Dict, Any, Callable, List
from pathlib import Path

from .config_v2 import ComponentConfig, create_default_config
from .renderer import ComponentRenderer
from .registry import ComponentSchema
from .exceptions import ComponentNotFoundError


# Global renderer instance (for convenience API)
_renderer: Optional[ComponentRenderer] = None


def configure_v2(
    templates_dir: str = 'templates',
    styles_dir: str = 'styles',
    scripts_dir: str = 'scripts',
    frameworks: Optional[List[str]] = None,
    enable_cache: bool = True,
    cache_max_size_mb: int = 100,
    cache_ttl_seconds: Optional[int] = None,
    enable_csp: bool = True,
    allowed_origins: Optional[List[str]] = None,
    validate_paths: bool = True,
    auto_discover: bool = True
) -> ComponentConfig:
    """
    Configure the component renderer with modern v2 architecture.

    Args:
        templates_dir: Directory containing Jinja2 templates
        styles_dir: Directory containing CSS files
        scripts_dir: Directory containing JavaScript files
        frameworks: List of external frameworks to load
        enable_cache: Enable component caching
        cache_max_size_mb: Maximum cache size in megabytes
        cache_ttl_seconds: Cache TTL in seconds (None = no expiration)
        enable_csp: Enable Content Security Policy headers
        allowed_origins: Allowed origins for bidirectional communication
        validate_paths: Enable path traversal validation
        auto_discover: Automatically discover and register components

    Returns:
        ComponentConfig instance

    Example:
        >>> config = configure_v2(
        ...     templates_dir='components/templates',
        ...     styles_dir='components/styles',
        ...     scripts_dir='components/scripts',
        ...     frameworks=['tailwind'],
        ...     enable_cache=True,
        ...     auto_discover=True
        ... )
    """
    global _renderer

    # Create configuration
    config = create_default_config(
        templates_dir=templates_dir,
        styles_dir=styles_dir,
        scripts_dir=scripts_dir,
        frameworks=frameworks or [],
        cache={
            'enabled': enable_cache,
            'max_size_mb': cache_max_size_mb,
            'ttl_seconds': cache_ttl_seconds
        },
        security={
            'enable_csp': enable_csp,
            'allowed_origins': allowed_origins or ['*'],
            'validate_paths': validate_paths
        }
    )

    # Create renderer with auto-discovery
    _renderer = ComponentRenderer(config, auto_discover=auto_discover)

    return config


def get_config_v2() -> ComponentConfig:
    """
    Get the current v2 configuration.

    Returns:
        ComponentConfig instance

    Raises:
        ConfigurationError: If not configured yet
    """
    global _renderer

    if _renderer is None:
        # Auto-configure with defaults
        configure_v2()

    return _renderer.config


def get_renderer() -> ComponentRenderer:
    """
    Get the global component renderer instance.

    Returns:
        ComponentRenderer instance

    Raises:
        ConfigurationError: If not configured yet
    """
    global _renderer

    if _renderer is None:
        # Auto-configure with defaults
        configure_v2()

    return _renderer


def get_registry():
    """
    Get the component registry.

    Returns:
        ComponentRegistry instance

    Raises:
        ConfigurationError: If not configured yet
    """
    return get_renderer().registry


def register_component(
    name: str,
    template: str,
    styles: Optional[List[str]] = None,
    scripts: Optional[List[str]] = None,
    validate: bool = True
) -> None:
    """
    Manually register a component.

    Args:
        name: Component name
        template: Template filename
        styles: List of CSS filenames
        scripts: List of JS filenames
        validate: Whether to validate files exist

    Example:
        >>> register_component(
        ...     name='custom_button',
        ...     template='button.html',
        ...     styles=['button.css'],
        ...     scripts=['button.js']
        ... )
    """
    renderer = get_renderer()
    renderer.register_component(name, template, styles, scripts, validate)


def render_component_v2(
    component_name: str,
    props: Optional[Dict[str, Any]] = None,
    *,
    height: Optional[int] = None,
    width: Optional[int] = None,
    scrolling: bool = False,
    key: Optional[str] = None,
    cache: Optional[bool] = None,
    on_event: Optional[Callable] = None
) -> Any:
    """
    Render an HTML component using the v2 architecture.

    This version uses:
    - ComponentRenderer for thread-safe rendering
    - Component registry for validation
    - Deterministic cache keys based on file content
    - Pydantic configuration
    - Early validation with helpful error messages

    Args:
        component_name: Name of the component
        props: Dictionary of variables to pass to the template
        height: Component height in pixels
        width: Component width in pixels
        scrolling: Enable scrolling in iframe
        key: Unique key for Streamlit component
        cache: Enable caching (overrides global default)
        on_event: Callback function for JavaScript events

    Returns:
        Component return value

    Raises:
        ComponentNotFoundError: If component not registered
        AssetNotFoundError: If required assets not found

    Example:
        >>> render_component_v2(
        ...     'button',
        ...     props={'text': 'Click me!', 'color': 'primary'},
        ...     height=100,
        ...     cache=True
        ... )
    """
    renderer = get_renderer()
    return renderer.render(
        component_name,
        props,
        height=height,
        width=width,
        scrolling=scrolling,
        key=key,
        cache=cache,
        on_event=on_event
    )


def list_components() -> List[str]:
    """
    List all registered components.

    Returns:
        Sorted list of component names

    Example:
        >>> components = list_components()
        >>> print(components)
        ['button', 'card', 'hero']
    """
    renderer = get_renderer()
    return renderer.list_components()


def get_component_info(component_name: str):
    """
    Get information about a registered component.

    Args:
        component_name: Name of the component

    Returns:
        ComponentSchema if found, None otherwise

    Example:
        >>> info = get_component_info('button')
        >>> print(info.template, info.styles, info.scripts)
    """
    renderer = get_renderer()
    return renderer.get_component_info(component_name)
