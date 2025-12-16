"""Core API for rendering HTML components in Streamlit."""

from typing import Optional, Dict, Any, Callable, List, Union
import streamlit.components.v1 as components

from .template_engine import TemplateEngine
from .asset_loader import AssetLoader
from .cache_manager import get_cache_manager
from .config import get_config
from .validators import Validator
from .bidirectional import get_bridge
from .exceptions import ComponentNotFoundError, AssetNotFoundError


# Global instances (will be updated when directories change)
_template_engine: Optional[TemplateEngine] = None
_asset_loader: Optional[AssetLoader] = None


def _get_template_engine(templates_dir: Optional[str] = None) -> TemplateEngine:
    """Get or create template engine with current configuration."""
    global _template_engine

    config = get_config()
    dir_path = templates_dir or config.templates_dir

    if _template_engine is None or _template_engine.templates_dir != dir_path:
        _template_engine = TemplateEngine(dir_path)

    return _template_engine


def _get_asset_loader(styles_dir: Optional[str] = None, scripts_dir: Optional[str] = None) -> AssetLoader:
    """Get or create asset loader with current configuration."""
    global _asset_loader

    config = get_config()
    s_dir = styles_dir or config.styles_dir
    j_dir = scripts_dir or config.scripts_dir

    if _asset_loader is None or _asset_loader.styles_dir != s_dir or _asset_loader.scripts_dir != j_dir:
        _asset_loader = AssetLoader(s_dir, j_dir)

    return _asset_loader


def render_component(
    component_name: str,
    props: Optional[Dict[str, Any]] = None,
    *,
    templates_dir: Optional[str] = None,
    styles_dir: Optional[str] = None,
    scripts_dir: Optional[str] = None,
    styles: Optional[List[str]] = None,
    scripts: Optional[List[str]] = None,
    frameworks: Optional[List[str]] = None,
    height: Optional[int] = None,
    width: Optional[int] = None,
    scrolling: bool = False,
    key: Optional[str] = None,
    cache: Optional[bool] = None,
    cache_ttl: Optional[int] = None,
    on_event: Optional[Callable] = None
) -> Any:
    """
    Render an HTML component in Streamlit.

    This is the main API function that:
    1. Validates inputs
    2. Loads and renders template
    3. Loads CSS and JavaScript assets
    4. Applies caching for performance
    5. Injects bidirectional communication bridge if needed
    6. Renders in Streamlit using st.components.v1.html()

    Args:
        component_name: Name of the component (matches template filename without .html)
        props: Dictionary of variables to pass to the template

        templates_dir: Override default templates directory for this component
        styles_dir: Override default styles directory for this component
        scripts_dir: Override default scripts directory for this component

        styles: List of CSS file names to load (without .css extension).
               If None, auto-loads {component_name}.css if it exists.
               Pass [] to skip CSS loading.
        scripts: List of JS file names to load (without .js extension).
                If None, auto-loads {component_name}.js if it exists.
                Pass [] to skip JS loading.
        frameworks: List of external frameworks to include ('tailwind', 'bootstrap', etc.)
                   Overrides global configuration if specified.

        height: Component height in pixels
        width: Component width in pixels (Streamlit default handles this)
        scrolling: Enable scrolling in iframe
        key: Unique key for Streamlit component

        cache: Enable caching for this component (overrides global default)
        cache_ttl: Cache time-to-live in seconds (None = no expiration)

        on_event: Callback function for JavaScript events.
                 Function signature: def callback(data: Dict[str, Any]) -> None

    Returns:
        Component return value (for interactive components with callbacks)

    Raises:
        ComponentNotFoundError: If template file not found
        AssetNotFoundError: If required CSS/JS file not found
        InvalidPropsError: If props validation fails

    Example:
        >>> from streamlit_html_components import render_component, configure
        >>>
        >>> configure(
        ...     templates_dir='components/templates',
        ...     styles_dir='components/styles',
        ...     scripts_dir='components/scripts'
        ... )
        >>>
        >>> render_component(
        ...     'button',
        ...     props={'text': 'Click me!', 'color': 'primary'},
        ...     height=100
        ... )
    """
    # Get configuration
    config = get_config()

    # Validate component name
    Validator.validate_component_name(component_name)

    # Validate and sanitize props
    props = Validator.validate_props(props)

    # Determine caching behavior
    use_cache = cache if cache is not None else config.default_cache
    ttl = cache_ttl if cache_ttl is not None else config.default_cache_ttl

    # Get engines with configured or overridden directories
    template_engine = _get_template_engine(templates_dir)
    asset_loader = _get_asset_loader(styles_dir, scripts_dir)

    # Determine which CSS/JS files to load
    if styles is None:
        # Auto-discover: try to load {component_name}.css
        css_files = [component_name]
    else:
        css_files = styles

    if scripts is None:
        # Auto-discover: try to load {component_name}.js
        js_files = [component_name]
    else:
        js_files = scripts

    # Determine frameworks to include
    framework_list = frameworks if frameworks is not None else config.external_frameworks

    # Generate cache key if caching is enabled
    cache_manager = get_cache_manager()
    cache_key = None

    if use_cache:
        # For cache key, we need content hashes
        # This is a simplified version - in production, you'd hash actual file contents
        template_hash = component_name  # Simplified
        style_hash = ",".join(css_files) if css_files else ""
        script_hash = ",".join(js_files) if js_files else ""

        cache_key = cache_manager.cache_key(
            component_name,
            props,
            template_hash,
            style_hash,
            script_hash
        )

        # Check cache
        cached_html = cache_manager.get_cached(cache_key, ttl)
        if cached_html:
            # Render cached HTML
            return components.html(
                cached_html,
                height=height,
                width=width,
                scrolling=scrolling
            )

    # Render template
    try:
        html = template_engine.render(component_name, props)
    except ComponentNotFoundError:
        raise

    # Load CSS assets
    css_content = ""
    if css_files:
        try:
            css_parts = []
            for css_file in css_files:
                try:
                    css_parts.append(asset_loader.load_css(css_file, wrap_in_style_tag=True))
                except AssetNotFoundError:
                    # If auto-discovery and file doesn't exist, skip silently
                    if styles is None:  # Auto-discovery mode
                        pass
                    else:  # Explicit mode - raise error
                        raise

            css_content = "\n".join(css_parts)
        except AssetNotFoundError:
            raise

    # Load JavaScript assets
    js_content = ""
    if js_files:
        try:
            js_parts = []
            for js_file in js_files:
                try:
                    js_parts.append(asset_loader.load_js(js_file, wrap_in_script_tag=True))
                except AssetNotFoundError:
                    # If auto-discovery and file doesn't exist, skip silently
                    if scripts is None:  # Auto-discovery mode
                        pass
                    else:  # Explicit mode - raise error
                        raise

            js_content = "\n".join(js_parts)
        except AssetNotFoundError:
            raise

    # Load framework CDN includes
    framework_includes = ""
    if framework_list:
        framework_includes = asset_loader.get_framework_includes(framework_list)

    # Combine all parts
    # Order: Framework CDNs → CSS → HTML → JS
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {framework_includes}
    {css_content}
</head>
<body>
    {html}
    {js_content}
</body>
</html>"""

    # Add bidirectional bridge if callback is provided
    if on_event and config.enable_bidirectional:
        bridge = get_bridge()
        full_html = bridge.wrap_with_bridge(full_html, component_name)

        # Register callback
        # Note: In actual Streamlit usage, the component would need to return
        # the event data, which we'd then pass to the callback
        # This is a simplified implementation
        bridge.register_callback(component_name, 'event', on_event)

    # Cache the result if caching is enabled
    if use_cache and cache_key:
        cache_manager.set_cached(cache_key, full_html)

    # Render using Streamlit components API
    result = components.html(
        full_html,
        height=height,
        width=width,
        scrolling=scrolling
    )

    # Handle callback if event data is returned
    if result and on_event:
        on_event(result)

    return result


def add_framework(
    framework: str,
    version: Optional[str] = None,
    css_urls: Optional[List[str]] = None,
    js_urls: Optional[List[str]] = None
):
    """
    Add a custom CSS/JS framework via CDN.

    Args:
        framework: Framework name
        version: Version (currently not used, for future enhancement)
        css_urls: List of CSS CDN URLs
        js_urls: List of JavaScript CDN URLs

    Example:
        >>> add_framework(
        ...     'my_framework',
        ...     css_urls=['https://cdn.example.com/framework.css'],
        ...     js_urls=['https://cdn.example.com/framework.js']
        ... )
    """
    Validator.validate_framework(framework)

    asset_loader = _get_asset_loader()
    asset_loader.add_framework_cdn(framework, css_urls, js_urls)
