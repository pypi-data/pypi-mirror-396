"""
Development server with hot reload for streamlit-html-components.

Enables automatic cache invalidation and component reloading when
template, style, or script files change during development.

Usage:
    >>> from streamlit_html_components import enable_hot_reload, configure_v2
    >>>
    >>> configure_v2(templates_dir='templates', ...)
    >>> enable_hot_reload()  # Start watching for file changes
    >>>
    >>> # Now any changes to component files will trigger auto-reload
"""

from typing import Optional, Dict, Set
from pathlib import Path
import atexit

from .file_watcher import FileWatcher, FileChangeEvent
from .cache_manager import CacheManager
from .config_v2 import ComponentConfig
from .diagnostics import DebugMode


class DevServer:
    """
    Development server with hot reload functionality.

    Monitors component files and automatically invalidates cache when changes
    are detected, enabling instant updates during development.

    Example:
        >>> dev = DevServer(config, cache_manager)
        >>> dev.start()
        >>> # Edit template files...
        >>> # Changes are automatically detected and cache invalidated
        >>> dev.stop()
    """

    def __init__(
        self,
        config: ComponentConfig,
        cache_manager: Optional[CacheManager] = None,
        poll_interval: float = 1.0
    ):
        """
        Initialize development server.

        Args:
            config: Component configuration with directory paths
            cache_manager: Cache manager to invalidate on changes
            poll_interval: Seconds between file checks (polling mode)
        """
        self.config = config
        self.cache_manager = cache_manager or CacheManager()
        self.poll_interval = poll_interval
        self.watcher = FileWatcher(poll_interval=poll_interval)
        self._component_files: Dict[str, Set[Path]] = {}  # Track which files belong to which component
        self._running = False

        # Setup watches for each directory
        self._setup_watches()

    def _setup_watches(self):
        """Setup file watches for templates, styles, and scripts."""
        # Watch templates directory
        if self.config.templates_dir.exists():
            self.watcher.watch(
                self.config.templates_dir,
                '*.html',
                self._on_template_change,
                recursive=False
            )
            DebugMode.log_info(f"DevServer: Watching templates in {self.config.templates_dir}")

        # Watch styles directory
        if self.config.styles_dir.exists():
            self.watcher.watch(
                self.config.styles_dir,
                '*.css',
                self._on_style_change,
                recursive=False
            )
            DebugMode.log_info(f"DevServer: Watching styles in {self.config.styles_dir}")

        # Watch scripts directory
        if self.config.scripts_dir.exists():
            self.watcher.watch(
                self.config.scripts_dir,
                '*.js',
                self._on_script_change,
                recursive=False
            )
            DebugMode.log_info(f"DevServer: Watching scripts in {self.config.scripts_dir}")

    def _on_template_change(self, event: FileChangeEvent):
        """Handle template file change."""
        # Determine component name from template filename
        component_name = event.path.stem

        DebugMode.log_info(f"DevServer: Template changed for '{component_name}': {event.path.name}")

        # Invalidate cache for this component
        if self.cache_manager:
            self.cache_manager.invalidate(component_name)
            DebugMode.log_info(f"DevServer: Cache invalidated for '{component_name}'")

        # Trigger Streamlit rerun if available
        self._trigger_rerun()

    def _on_style_change(self, event: FileChangeEvent):
        """Handle style file change."""
        # Find which components use this style file
        affected_components = self._find_components_using_file(event.path, 'css')

        for component_name in affected_components:
            DebugMode.log_info(f"DevServer: Style changed for '{component_name}': {event.path.name}")

            if self.cache_manager:
                self.cache_manager.invalidate(component_name)
                DebugMode.log_info(f"DevServer: Cache invalidated for '{component_name}'")

        # If no specific components found, invalidate all (style might be new)
        if not affected_components:
            DebugMode.log_info(f"DevServer: Style changed: {event.path.name} (invalidating all)")
            if self.cache_manager:
                self.cache_manager.invalidate()

        self._trigger_rerun()

    def _on_script_change(self, event: FileChangeEvent):
        """Handle script file change."""
        # Find which components use this script file
        affected_components = self._find_components_using_file(event.path, 'js')

        for component_name in affected_components:
            DebugMode.log_info(f"DevServer: Script changed for '{component_name}': {event.path.name}")

            if self.cache_manager:
                self.cache_manager.invalidate(component_name)
                DebugMode.log_info(f"DevServer: Cache invalidated for '{component_name}'")

        # If no specific components found, invalidate all
        if not affected_components:
            DebugMode.log_info(f"DevServer: Script changed: {event.path.name} (invalidating all)")
            if self.cache_manager:
                self.cache_manager.invalidate()

        self._trigger_rerun()

    def _find_components_using_file(self, file_path: Path, file_type: str) -> Set[str]:
        """
        Find components that use a specific file.

        Args:
            file_path: Path to the file
            file_type: Type of file ('css' or 'js')

        Returns:
            Set of component names
        """
        # This is a simple heuristic: if the filename matches the component name,
        # assume they're related. For more complex setups, this could be enhanced
        # by tracking component schemas.
        components = set()

        file_stem = file_path.stem
        components.add(file_stem)

        return components

    def _trigger_rerun(self):
        """Trigger Streamlit to rerun and show updated components."""
        try:
            import streamlit as st
            # Use experimental_rerun if available, or st.rerun
            if hasattr(st, 'rerun'):
                st.rerun()
            elif hasattr(st, 'experimental_rerun'):
                st.experimental_rerun()
            else:
                DebugMode.log_debug("DevServer: Streamlit rerun not available")
        except ImportError:
            DebugMode.log_debug("DevServer: Streamlit not imported, skipping rerun")
        except Exception as e:
            DebugMode.log_debug(f"DevServer: Could not trigger rerun: {e}")

    def start(self):
        """Start the development server and file watching."""
        if self._running:
            DebugMode.log_debug("DevServer: Already running")
            return

        self.watcher.start()
        self._running = True

        DebugMode.log_info("DevServer: Hot reload enabled")
        print("🔥 Hot reload enabled - component files will be watched for changes")

    def stop(self):
        """Stop the development server."""
        if not self._running:
            return

        self.watcher.stop()
        self._running = False

        DebugMode.log_info("DevServer: Stopped")

    def is_running(self) -> bool:
        """Check if development server is running."""
        return self._running

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


# Global dev server instance
_dev_server: Optional[DevServer] = None


def enable_hot_reload(
    config: Optional[ComponentConfig] = None,
    cache_manager: Optional[CacheManager] = None,
    poll_interval: float = 1.0,
    verbose: bool = False
) -> DevServer:
    """
    Enable hot reload for component development.

    Automatically watches component files and invalidates cache when changes
    are detected. Triggers Streamlit rerun to show updated components.

    Args:
        config: Component configuration (uses v2 config if None)
        cache_manager: Cache manager (creates new if None)
        poll_interval: Seconds between file checks (polling mode)
        verbose: Enable verbose debug logging

    Returns:
        DevServer instance

    Example:
        >>> from streamlit_html_components import configure_v2, enable_hot_reload
        >>>
        >>> configure_v2(templates_dir='templates', ...)
        >>> enable_hot_reload(verbose=True)
        >>>
        >>> # Edit your component files...
        >>> # Changes will be automatically detected and applied!

    Note:
        Hot reload is intended for development only. Don't use in production.
    """
    global _dev_server

    if verbose:
        DebugMode.enable(level=2)

    # Get config from v2 if not provided
    if config is None:
        try:
            from .core_v2 import get_config_v2
            config = get_config_v2()
        except Exception as e:
            raise RuntimeError(
                "No config provided and could not get v2 config. "
                "Call configure_v2() before enable_hot_reload()."
            ) from e

    # Get cache manager from renderer if not provided
    if cache_manager is None:
        try:
            from .core_v2 import get_renderer
            renderer = get_renderer()
            cache_manager = renderer.cache if renderer else None
        except Exception:
            pass

    # Create dev server
    _dev_server = DevServer(config, cache_manager, poll_interval)
    _dev_server.start()

    # Register cleanup on exit
    atexit.register(lambda: _dev_server.stop() if _dev_server else None)

    return _dev_server


def disable_hot_reload():
    """Disable hot reload and stop file watching."""
    global _dev_server

    if _dev_server:
        _dev_server.stop()
        _dev_server = None
        print("Hot reload disabled")


def get_dev_server() -> Optional[DevServer]:
    """Get the active development server instance."""
    return _dev_server


# Export public API
__all__ = [
    'DevServer',
    'enable_hot_reload',
    'disable_hot_reload',
    'get_dev_server'
]
