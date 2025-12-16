"""
ComponentRenderer - Thread-safe, testable component rendering.

This replaces the global singleton pattern with a context object that
encapsulates all rendering state. Each ComponentRenderer instance is
independent and can have different configurations.
"""

from typing import Optional, Dict, Any, Callable
from pathlib import Path
import streamlit.components.v1 as components

from .config_v2 import ComponentConfig
from .registry import ComponentRegistry
from .template_engine import TemplateEngine
from .asset_loader import AssetLoader
from .cache_manager import CacheManager
from .bidirectional import get_bridge
from .exceptions import ComponentNotFoundError


class ComponentRenderer:
    """
    Thread-safe component renderer with encapsulated state.

    This class replaces global singletons with a context object that can be
    instantiated multiple times with different configurations. Each instance
    maintains its own template engine, asset loader, cache, and registry.

    Example:
        >>> config = ComponentConfig(
        ...     templates_dir='components/templates',
        ...     styles_dir='components/styles',
        ...     scripts_dir='components/scripts'
        ... )
        >>> renderer = ComponentRenderer(config)
        >>> renderer.render('button', props={'text': 'Click me'})
    """

    def __init__(
        self,
        config: ComponentConfig,
        registry: Optional[ComponentRegistry] = None,
        auto_discover: bool = True
    ):
        """
        Initialize component renderer.

        Args:
            config: Component configuration
            registry: Optional pre-configured registry (creates new if None)
            auto_discover: Automatically discover and register components
        """
        self.config = config

        # Initialize registry
        if registry is None:
            self.registry = ComponentRegistry(config)
            if auto_discover:
                self.registry.auto_discover(validate=True)
        else:
            self.registry = registry

        # Initialize engines (each renderer has its own instances)
        self.template_engine = TemplateEngine(str(config.templates_dir))
        self.asset_loader = AssetLoader(
            str(config.styles_dir),
            str(config.scripts_dir)
        )

        # Initialize cache manager
        self.cache = CacheManager()

    def render(
        self,
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
        Render a component.

        Args:
            component_name: Name of the component to render
            props: Props to pass to the component template
            height: Component height in pixels
            width: Component width in pixels
            scrolling: Enable scrolling in iframe
            key: Streamlit component key
            cache: Override cache setting (uses config default if None)
            on_event: Callback for JavaScript events

        Returns:
            Component return value

        Raises:
            ComponentNotFoundError: If component not registered

        Example:
            >>> renderer.render(
            ...     'button',
            ...     props={'text': 'Click me', 'color': 'blue'},
            ...     height=100,
            ...     cache=True
            ... )
        """
        # Validate component is registered
        component_schema = self.registry.get(component_name)
        if component_schema is None:
            available = self.registry.list_components()
            raise ComponentNotFoundError(
                f"Component '{component_name}' not registered.\n"
                f"Available components: {', '.join(available) if available else 'none'}\n"
                f"Use renderer.registry.register() or enable auto_discover=True"
            )

        # Sanitize props
        props = props or {}

        # Determine caching
        use_cache = cache if cache is not None else self.config.cache.enabled
        ttl = self.config.cache.ttl_seconds

        # Build file paths for cache key
        template_path = self.config.templates_dir / component_schema.template

        css_paths = []
        if component_schema.styles:
            css_paths = [
                self.config.styles_dir / style
                for style in component_schema.styles
            ]

        js_paths = []
        if component_schema.scripts:
            js_paths = [
                self.config.scripts_dir / script
                for script in component_schema.scripts
            ]

        # Check cache
        cache_key = None
        if use_cache:
            cache_key = self.cache.cache_key(
                component_name,
                props,
                template_path,
                css_paths,
                js_paths
            )

            cached_html = self.cache.get_cached(cache_key, ttl)
            if cached_html:
                return components.html(
                    cached_html,
                    height=height,
                    width=width,
                    scrolling=scrolling,
                    key=key
                )

        # Render template
        html = self.template_engine.render(component_name, props)

        # Load CSS
        css_content = ""
        if component_schema.styles:
            css_parts = []
            for style_file in component_schema.styles:
                style_name = style_file.replace('.css', '')
                css_parts.append(
                    self.asset_loader.load_css(style_name, wrap_in_style_tag=True)
                )
            css_content = "\n".join(css_parts)

        # Load JavaScript
        js_content = ""
        if component_schema.scripts:
            js_parts = []
            for script_file in component_schema.scripts:
                script_name = script_file.replace('.js', '')
                js_parts.append(
                    self.asset_loader.load_js(script_name, wrap_in_script_tag=True)
                )
            js_content = "\n".join(js_parts)

        # Load framework includes
        framework_includes = ""
        if self.config.frameworks:
            framework_includes = self.asset_loader.get_framework_includes(
                self.config.frameworks
            )

        # Combine HTML
        full_html = self._build_html(
            framework_includes,
            css_content,
            html,
            js_content
        )

        # Add bidirectional bridge if needed
        if on_event:
            bridge = get_bridge()
            full_html = bridge.wrap_with_bridge(
                full_html,
                component_name,
                allowed_origins=self.config.security.allowed_origins
            )
            bridge.register_callback(component_name, 'event', on_event)

        # Cache result
        if use_cache and cache_key:
            self.cache.set_cached(cache_key, full_html, component_name)

        # Render
        result = components.html(
            full_html,
            height=height,
            width=width,
            scrolling=scrolling,
            key=key
        )

        # Handle callback
        if result and on_event:
            on_event(result)

        return result

    def _build_html(
        self,
        framework_includes: str,
        css_content: str,
        html_content: str,
        js_content: str
    ) -> str:
        """
        Build complete HTML document.

        Args:
            framework_includes: CDN links for frameworks
            css_content: CSS content (wrapped in style tags)
            html_content: Rendered HTML from template
            js_content: JavaScript content (wrapped in script tags)

        Returns:
            Complete HTML document
        """
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {framework_includes}
    {css_content}
</head>
<body>
    {html_content}
    {js_content}
</body>
</html>"""

    def invalidate_cache(self, component_name: Optional[str] = None) -> None:
        """
        Invalidate cache for a component or all components.

        Args:
            component_name: Component to invalidate (None = all)

        Example:
            >>> renderer.invalidate_cache('button')  # Clear button cache
            >>> renderer.invalidate_cache()  # Clear all cache
        """
        self.cache.invalidate(component_name)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics

        Example:
            >>> stats = renderer.get_cache_stats()
            >>> print(stats['total_entries'])
        """
        return self.cache.cache_stats()

    def list_components(self) -> list[str]:
        """
        List all registered components.

        Returns:
            Sorted list of component names

        Example:
            >>> components = renderer.list_components()
            >>> print(components)  # ['button', 'card', 'hero']
        """
        return self.registry.list_components()

    def get_component_info(self, component_name: str):
        """
        Get component metadata.

        Args:
            component_name: Name of component

        Returns:
            ComponentSchema if found, None otherwise

        Example:
            >>> info = renderer.get_component_info('button')
            >>> print(info.template)  # 'button.html'
        """
        return self.registry.get(component_name)

    def register_component(
        self,
        name: str,
        template: str,
        styles: Optional[list[str]] = None,
        scripts: Optional[list[str]] = None,
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
            >>> renderer.register_component(
            ...     name='custom_button',
            ...     template='button.html',
            ...     styles=['button.css'],
            ...     scripts=['button.js']
            ... )
        """
        from .registry import ComponentSchema

        schema = ComponentSchema(
            name=name,
            template=template,
            styles=styles,
            scripts=scripts
        )

        self.registry.register(schema, validate=validate)
