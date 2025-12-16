"""Asset loader for CSS and JavaScript files with framework CDN support."""

from pathlib import Path
from typing import List, Optional, Dict
from functools import lru_cache
import hashlib

from .exceptions import AssetNotFoundError


class AssetLoader:
    """
    Manages loading and caching of CSS/JS assets and external framework integration.

    Features:
    - LRU caching for file reads
    - Support for multiple files
    - Built-in CDN support for popular frameworks
    - Content hashing for cache busting
    """

    # Built-in framework CDN configurations
    FRAMEWORK_CDNS = {
        'tailwind': {
            'css': [],
            'js': ['https://cdn.tailwindcss.com']
        },
        'bootstrap': {
            'css': ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'],
            'js': ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js']
        },
        'bulma': {
            'css': ['https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css'],
            'js': []
        },
        'material': {
            'css': ['https://fonts.googleapis.com/icon?family=Material+Icons',
                    'https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css'],
            'js': ['https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js']
        }
    }

    def __init__(self, styles_dir: str = "styles", scripts_dir: str = "scripts"):
        """
        Initialize the asset loader.

        Args:
            styles_dir: Directory containing CSS files
            scripts_dir: Directory containing JavaScript files
        """
        self.styles_dir = Path(styles_dir)
        self.scripts_dir = Path(scripts_dir)
        self._custom_framework_cdns: Dict[str, Dict[str, List[str]]] = {}

    def update_directories(self, styles_dir: Optional[str] = None, scripts_dir: Optional[str] = None):
        """
        Update asset directories.

        Args:
            styles_dir: New styles directory path
            scripts_dir: New scripts directory path
        """
        if styles_dir:
            self.styles_dir = Path(styles_dir)
            # Clear cache when directory changes
            self.load_css.cache_clear()

        if scripts_dir:
            self.scripts_dir = Path(scripts_dir)
            # Clear cache when directory changes
            self.load_js.cache_clear()

    @lru_cache(maxsize=64)
    def load_css(self, css_name: str, wrap_in_style_tag: bool = True) -> str:
        """
        Load and cache CSS file content.

        Args:
            css_name: Name of CSS file (without .css extension)
            wrap_in_style_tag: If True, wrap content in <style> tags

        Returns:
            CSS content (optionally wrapped in <style> tags)

        Raises:
            AssetNotFoundError: If CSS file not found
        """
        css_path = self.styles_dir / f"{css_name}.css"

        if not css_path.exists():
            # Provide helpful error message
            available = []
            if self.styles_dir.exists():
                available = [f.stem for f in self.styles_dir.glob("*.css")]

            error_msg = f"CSS file '{css_name}.css' not found in {self.styles_dir}"
            if available:
                error_msg += f"\n\nAvailable CSS files: {', '.join(available)}"
            else:
                error_msg += f"\n\nNo CSS files found. Styles directory exists: {self.styles_dir.exists()}"

            error_msg += f"\n\nTip: Create {css_path} or pass an empty list to skip CSS loading"

            raise AssetNotFoundError(error_msg)

        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
        except IOError as e:
            raise AssetNotFoundError(f"Failed to read CSS file '{css_name}.css': {e}")

        if wrap_in_style_tag:
            return f"<style>\n{css_content}\n</style>"
        return css_content

    @lru_cache(maxsize=64)
    def load_js(self, js_name: str, wrap_in_script_tag: bool = True) -> str:
        """
        Load and cache JavaScript file content.

        Args:
            js_name: Name of JS file (without .js extension)
            wrap_in_script_tag: If True, wrap content in <script> tags

        Returns:
            JavaScript content (optionally wrapped in <script> tags)

        Raises:
            AssetNotFoundError: If JS file not found
        """
        js_path = self.scripts_dir / f"{js_name}.js"

        if not js_path.exists():
            # Provide helpful error message
            available = []
            if self.scripts_dir.exists():
                available = [f.stem for f in self.scripts_dir.glob("*.js")]

            error_msg = f"JavaScript file '{js_name}.js' not found in {self.scripts_dir}"
            if available:
                error_msg += f"\n\nAvailable JS files: {', '.join(available)}"
            else:
                error_msg += f"\n\nNo JS files found. Scripts directory exists: {self.scripts_dir.exists()}"

            error_msg += f"\n\nTip: Create {js_path} or pass an empty list to skip JS loading"

            raise AssetNotFoundError(error_msg)

        try:
            with open(js_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
        except IOError as e:
            raise AssetNotFoundError(f"Failed to read JavaScript file '{js_name}.js': {e}")

        if wrap_in_script_tag:
            return f"<script>\n{js_content}\n</script>"
        return js_content

    def load_multiple_css(self, css_files: List[str]) -> str:
        """
        Load multiple CSS files and concatenate.

        Args:
            css_files: List of CSS file names (without .css extension)

        Returns:
            Concatenated CSS content wrapped in <style> tags
        """
        if not css_files:
            return ""

        css_parts = []
        for css_file in css_files:
            try:
                css_parts.append(self.load_css(css_file, wrap_in_style_tag=True))
            except AssetNotFoundError:
                # Continue loading other files even if one fails
                # The error will be caught by render_component
                raise

        return "\n".join(css_parts)

    def load_multiple_js(self, js_files: List[str]) -> str:
        """
        Load multiple JavaScript files and concatenate.

        Args:
            js_files: List of JS file names (without .js extension)

        Returns:
            Concatenated JavaScript content wrapped in <script> tags
        """
        if not js_files:
            return ""

        js_parts = []
        for js_file in js_files:
            try:
                js_parts.append(self.load_js(js_file, wrap_in_script_tag=True))
            except AssetNotFoundError:
                # Continue loading other files even if one fails
                raise

        return "\n".join(js_parts)

    def add_framework_cdn(self, framework: str, css_urls: Optional[List[str]] = None,
                          js_urls: Optional[List[str]] = None):
        """
        Register a custom framework CDN configuration.

        Args:
            framework: Framework name
            css_urls: List of CSS CDN URLs
            js_urls: List of JavaScript CDN URLs
        """
        self._custom_framework_cdns[framework.lower()] = {
            'css': css_urls or [],
            'js': js_urls or []
        }

    def get_framework_includes(self, frameworks: List[str]) -> str:
        """
        Generate CDN include tags for external frameworks.

        Args:
            frameworks: List of framework names or custom CDN URLs

        Returns:
            HTML string with <link> and <script> tags for frameworks
        """
        if not frameworks:
            return ""

        includes = []

        for framework in frameworks:
            framework_lower = framework.lower()

            # Check built-in frameworks first
            if framework_lower in self.FRAMEWORK_CDNS:
                config = self.FRAMEWORK_CDNS[framework_lower]
            # Then check custom frameworks
            elif framework_lower in self._custom_framework_cdns:
                config = self._custom_framework_cdns[framework_lower]
            # If it's a URL, treat as custom CSS/JS
            elif framework.startswith(('http://', 'https://')):
                # Determine if it's CSS or JS by extension
                if framework.endswith('.css'):
                    includes.append(f'<link rel="stylesheet" href="{framework}">')
                elif framework.endswith('.js'):
                    includes.append(f'<script src="{framework}"></script>')
                else:
                    # Default to script tag
                    includes.append(f'<script src="{framework}"></script>')
                continue
            else:
                # Unknown framework, skip
                continue

            # Add CSS links
            for css_url in config.get('css', []):
                includes.append(f'<link rel="stylesheet" href="{css_url}">')

            # Add JS scripts
            for js_url in config.get('js', []):
                includes.append(f'<script src="{js_url}"></script>')

        return "\n".join(includes)

    @staticmethod
    def compute_hash(content: str) -> str:
        """
        Compute MD5 hash of content for cache busting.

        Args:
            content: Content to hash

        Returns:
            First 8 characters of MD5 hash
        """
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def clear_cache(self):
        """Clear all cached assets."""
        self.load_css.cache_clear()
        self.load_js.cache_clear()
