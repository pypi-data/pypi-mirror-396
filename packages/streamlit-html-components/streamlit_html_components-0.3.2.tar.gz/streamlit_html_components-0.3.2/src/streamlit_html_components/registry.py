"""
Component registry for validation and management.

This module provides early validation of components at registration time
rather than at render time, leading to better error messages and faster
failure feedback.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, field_validator
import re

from .exceptions import ComponentNotFoundError, TemplateSyntaxError, AssetNotFoundError
from .config_v2 import ComponentConfig
from .diagnostics import FuzzyMatcher, PathSuggester


class ComponentSchema(BaseModel):
    """
    Schema definition for a component.

    Example:
        >>> schema = ComponentSchema(
        ...     name='button',
        ...     template='button.html',
        ...     styles=['button.css'],
        ...     scripts=['button.js']
        ... )
    """

    name: str
    template: str  # Template filename
    styles: Optional[List[str]] = None
    scripts: Optional[List[str]] = None
    props_schema: Optional[Dict[str, Any]] = None  # JSON Schema for props validation

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate component name is alphanumeric with dashes/underscores."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(
                f"Component name '{v}' is invalid.\n"
                f"Must contain only letters, numbers, hyphens, and underscores."
            )
        return v


class ComponentRegistry:
    """
    Registry for managing and validating components.

    The registry validates components at registration time, providing
    early feedback about missing files, syntax errors, etc.

    Example:
        >>> from pathlib import Path
        >>> registry = ComponentRegistry(Path('components'))
        >>> registry.auto_discover()  # Scan and register all components
        >>> 'button' in registry.components  # doctest: +SKIP
        True
    """

    def __init__(self, config: ComponentConfig):
        """
        Initialize registry with component configuration.

        Args:
            config: Component configuration with directory paths
        """
        self.config = config
        self.components: Dict[str, ComponentSchema] = {}

    def register(self, component: ComponentSchema, validate: bool = True) -> None:
        """
        Register a component with optional validation.

        Args:
            component: Component schema to register
            validate: Whether to validate files exist and templates are valid

        Raises:
            ComponentNotFoundError: If template file not found
            TemplateSyntaxError: If template has syntax errors

        Example:
            >>> config = ComponentConfig(
            ...     templates_dir=Path('templates'),
            ...     styles_dir=Path('styles'),
            ...     scripts_dir=Path('scripts')
            ... )  # doctest: +SKIP
            >>> registry = ComponentRegistry(config)  # doctest: +SKIP
            >>> schema = ComponentSchema(name='button', template='button.html')  # doctest: +SKIP
            >>> registry.register(schema)  # doctest: +SKIP
        """
        if validate:
            self._validate_component(component)

        self.components[component.name] = component

    def _validate_component(self, component: ComponentSchema) -> None:
        """
        Validate that component files exist and are valid.

        Args:
            component: Component schema to validate

        Raises:
            ComponentNotFoundError: If required files not found
            TemplateSyntaxError: If template syntax is invalid
        """
        # Validate template exists
        template_path = self.config.templates_dir / component.template
        if not template_path.exists():
            # Find similar template files using fuzzy matching
            available = list(self.config.templates_dir.glob('*.html'))
            available_names = [f.name for f in available]

            # Get suggestions for similar file names
            suggestions_obj = PathSuggester.suggest_similar_files(
                Path(component.template),
                self.config.templates_dir,
                '*.html'
            )
            suggestions = [s.suggestion for s in suggestions_obj]

            raise AssetNotFoundError(
                asset_path=component.template,
                asset_type='template',
                suggestions=suggestions,
                search_directory=str(self.config.templates_dir),
                context={
                    'component_name': component.name,
                    'available_templates': available_names if available_names else ['(none)']
                }
            )

        # Validate Jinja2 template syntax
        try:
            self._validate_template_syntax(template_path)
        except Exception as e:
            raise TemplateSyntaxError(
                template_path=str(template_path),
                error_message=str(e),
                context={'component_name': component.name}
            )

        # Validate style files exist (if specified)
        if component.styles:
            for style_file in component.styles:
                style_path = self.config.styles_dir / style_file
                if not style_path.exists():
                    # Get suggestions for similar files
                    suggestions_obj = PathSuggester.suggest_similar_files(
                        Path(style_file),
                        self.config.styles_dir,
                        '*.css'
                    )
                    suggestions = [s.suggestion for s in suggestions_obj]

                    available = list(self.config.styles_dir.glob('*.css'))
                    available_names = [f.name for f in available]

                    raise AssetNotFoundError(
                        asset_path=style_file,
                        asset_type='style',
                        suggestions=suggestions,
                        search_directory=str(self.config.styles_dir),
                        context={
                            'component_name': component.name,
                            'available_styles': available_names if available_names else ['(none)']
                        }
                    )

        # Validate script files exist (if specified)
        if component.scripts:
            for script_file in component.scripts:
                script_path = self.config.scripts_dir / script_file
                if not script_path.exists():
                    # Get suggestions for similar files
                    suggestions_obj = PathSuggester.suggest_similar_files(
                        Path(script_file),
                        self.config.scripts_dir,
                        '*.js'
                    )
                    suggestions = [s.suggestion for s in suggestions_obj]

                    available = list(self.config.scripts_dir.glob('*.js'))
                    available_names = [f.name for f in available]

                    raise AssetNotFoundError(
                        asset_path=script_file,
                        asset_type='script',
                        suggestions=suggestions,
                        search_directory=str(self.config.scripts_dir),
                        context={
                            'component_name': component.name,
                            'available_scripts': available_names if available_names else ['(none)']
                        }
                    )

    def _validate_template_syntax(self, template_path: Path) -> None:
        """
        Validate Jinja2 template syntax.

        Args:
            template_path: Path to template file

        Raises:
            TemplateSyntaxError: If template has syntax errors
        """
        from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError as Jinja2SyntaxError

        try:
            env = Environment(loader=FileSystemLoader(self.config.templates_dir))
            env.get_template(template_path.name)
        except Jinja2SyntaxError as e:
            raise TemplateSyntaxError(str(e))

    def auto_discover(self, validate: bool = True) -> None:
        """
        Automatically discover and register all components in templates directory.

        Scans the templates directory for .html files and registers them as components.

        Args:
            validate: Whether to validate discovered components

        Example:
            >>> config = ComponentConfig(
            ...     templates_dir=Path('templates'),
            ...     styles_dir=Path('styles'),
            ...     scripts_dir=Path('scripts')
            ... )  # doctest: +SKIP
            >>> registry = ComponentRegistry(config)  # doctest: +SKIP
            >>> registry.auto_discover()  # doctest: +SKIP
            >>> len(registry.components) > 0  # doctest: +SKIP
            True
        """
        templates_dir = self.config.templates_dir

        for template_file in templates_dir.glob('*.html'):
            component_name = template_file.stem

            # Skip if already registered
            if component_name in self.components:
                continue

            # Auto-discover matching CSS and JS files
            css_file = self.config.styles_dir / f"{component_name}.css"
            js_file = self.config.scripts_dir / f"{component_name}.js"

            styles = [css_file.name] if css_file.exists() else None
            scripts = [js_file.name] if js_file.exists() else None

            # Register component
            schema = ComponentSchema(
                name=component_name,
                template=template_file.name,
                styles=styles,
                scripts=scripts
            )

            self.register(schema, validate=validate)

    def get(self, component_name: str) -> Optional[ComponentSchema]:
        """
        Get component schema by name.

        Args:
            component_name: Name of component to retrieve

        Returns:
            ComponentSchema if found, None otherwise

        Example:
            >>> registry = ComponentRegistry(config)  # doctest: +SKIP
            >>> schema = registry.get('button')  # doctest: +SKIP
        """
        return self.components.get(component_name)

    def list_components(self) -> List[str]:
        """
        List all registered component names.

        Returns:
            Sorted list of component names

        Example:
            >>> registry = ComponentRegistry(config)  # doctest: +SKIP
            >>> registry.auto_discover()  # doctest: +SKIP
            >>> components = registry.list_components()  # doctest: +SKIP
        """
        return sorted(self.components.keys())

    def __contains__(self, component_name: str) -> bool:
        """Check if component is registered."""
        return component_name in self.components

    def __len__(self) -> int:
        """Return number of registered components."""
        return len(self.components)
