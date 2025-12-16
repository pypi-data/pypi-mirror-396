"""
Props validation system for streamlit-html-components.

Provides JSON Schema-based validation for component props with:
- Runtime type checking
- Custom validation rules
- Schema definitions per component
- Helpful error messages
"""

from typing import Dict, Any, Optional, List, Callable, Union
from pathlib import Path
import json
from dataclasses import dataclass
from enum import Enum

from .exceptions import InvalidPropsError


class ValidationType(Enum):
    """Types of validation that can be performed."""
    REQUIRED = "required"
    TYPE = "type"
    PATTERN = "pattern"
    RANGE = "range"
    ENUM = "enum"
    CUSTOM = "custom"


@dataclass
class ValidationRule:
    """A single validation rule for a prop."""
    prop_name: str
    validation_type: ValidationType
    rule: Optional[Any] = None
    error_message: Optional[str] = None

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against this rule.

        Args:
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if self.validation_type == ValidationType.REQUIRED:
                is_valid = value is not None
                error = self.error_message or "This field is required"

            elif self.validation_type == ValidationType.TYPE:
                is_valid = isinstance(value, self.rule)
                error = self.error_message or f"Expected type {self.rule.__name__}"

            elif self.validation_type == ValidationType.PATTERN:
                import re
                is_valid = bool(re.match(self.rule, str(value)))
                error = self.error_message or f"Must match pattern: {self.rule}"

            elif self.validation_type == ValidationType.RANGE:
                min_val, max_val = self.rule
                is_valid = min_val <= value <= max_val
                error = self.error_message or f"Must be between {min_val} and {max_val}"

            elif self.validation_type == ValidationType.ENUM:
                is_valid = value in self.rule
                error = self.error_message or f"Must be one of: {', '.join(map(str, self.rule))}"

            elif self.validation_type == ValidationType.CUSTOM:
                is_valid = self.rule(value)
                error = self.error_message or "Custom validation failed"

            else:
                return False, "Unknown validation type"

            return (is_valid, None) if is_valid else (False, error)

        except Exception as e:
            return False, f"Validation error: {str(e)}"


class PropsSchema:
    """
    Schema definition for component props.

    Supports JSON Schema-like validation rules.

    Example:
        >>> schema = PropsSchema()
        >>> schema.add_rule('name', ValidationType.REQUIRED)
        >>> schema.add_rule('age', ValidationType.TYPE, int)
        >>> schema.add_rule('email', ValidationType.PATTERN, r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$')
        >>> result = schema.validate({'name': 'John', 'age': 30, 'email': 'john@example.com'})
    """

    def __init__(self, schema_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize props schema.

        Args:
            schema_dict: Optional dictionary defining the schema
        """
        self.rules: List[ValidationRule] = []
        self._schema_dict = schema_dict or {}

        if schema_dict:
            self._parse_schema_dict(schema_dict)

    def _parse_schema_dict(self, schema: Dict[str, Any]):
        """
        Parse a JSON Schema-like dictionary into validation rules.

        Args:
            schema: Schema dictionary
        """
        # Parse required fields
        if 'required' in schema:
            for prop_name in schema['required']:
                self.add_rule(prop_name, ValidationType.REQUIRED)

        # Parse properties with type definitions
        if 'properties' in schema:
            for prop_name, prop_def in schema['properties'].items():
                # Type validation
                if 'type' in prop_def:
                    type_map = {
                        'string': str,
                        'number': (int, float),
                        'integer': int,
                        'boolean': bool,
                        'array': list,
                        'object': dict
                    }
                    prop_type = type_map.get(prop_def['type'])
                    if prop_type:
                        self.add_rule(prop_name, ValidationType.TYPE, prop_type)

                # Pattern validation (for strings)
                if 'pattern' in prop_def:
                    self.add_rule(
                        prop_name,
                        ValidationType.PATTERN,
                        prop_def['pattern'],
                        error_message=prop_def.get('patternErrorMessage')
                    )

                # Range validation (for numbers)
                if 'minimum' in prop_def and 'maximum' in prop_def:
                    self.add_rule(
                        prop_name,
                        ValidationType.RANGE,
                        (prop_def['minimum'], prop_def['maximum'])
                    )

                # Enum validation
                if 'enum' in prop_def:
                    self.add_rule(prop_name, ValidationType.ENUM, prop_def['enum'])

    def add_rule(
        self,
        prop_name: str,
        validation_type: ValidationType,
        rule: Any = None,
        error_message: Optional[str] = None
    ):
        """
        Add a validation rule.

        Args:
            prop_name: Name of the prop to validate
            validation_type: Type of validation
            rule: Rule definition (type, pattern, range, etc.)
            error_message: Optional custom error message
        """
        self.rules.append(ValidationRule(
            prop_name=prop_name,
            validation_type=validation_type,
            rule=rule,
            error_message=error_message
        ))

    def validate(self, props: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
        """
        Validate props against all rules.

        Args:
            props: Props dictionary to validate

        Returns:
            Tuple of (is_valid, errors_dict)
            errors_dict maps prop names to error messages
        """
        errors = {}

        # Group rules by prop name
        rules_by_prop: Dict[str, List[ValidationRule]] = {}
        for rule in self.rules:
            if rule.prop_name not in rules_by_prop:
                rules_by_prop[rule.prop_name] = []
            rules_by_prop[rule.prop_name].append(rule)

        # Validate each prop
        for prop_name, prop_rules in rules_by_prop.items():
            value = props.get(prop_name)

            for rule in prop_rules:
                is_valid, error = rule.validate(value)
                if not is_valid:
                    errors[prop_name] = error
                    break  # Stop at first error for this prop

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert schema to JSON Schema dictionary.

        Returns:
            JSON Schema dictionary
        """
        return self._schema_dict.copy()

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'PropsSchema':
        """
        Load schema from JSON file.

        Args:
            file_path: Path to JSON schema file

        Returns:
            PropsSchema instance

        Example:
            >>> schema = PropsSchema.from_file('schemas/button.json')
        """
        with open(file_path, 'r') as f:
            schema_dict = json.load(f)
        return cls(schema_dict)


class PropsValidator:
    """
    Component props validator with schema support.

    Example:
        >>> validator = PropsValidator()
        >>> schema = PropsSchema()
        >>> schema.add_rule('title', ValidationType.REQUIRED)
        >>> schema.add_rule('count', ValidationType.TYPE, int)
        >>>
        >>> validator.register_schema('card', schema)
        >>> validator.validate('card', {'title': 'Hello', 'count': 5})
    """

    def __init__(self):
        """Initialize props validator."""
        self._schemas: Dict[str, PropsSchema] = {}

    def register_schema(self, component_name: str, schema: PropsSchema):
        """
        Register a validation schema for a component.

        Args:
            component_name: Name of the component
            schema: Props schema to use for validation
        """
        self._schemas[component_name] = schema

    def register_schema_from_dict(self, component_name: str, schema_dict: Dict[str, Any]):
        """
        Register a schema from a dictionary.

        Args:
            component_name: Name of the component
            schema_dict: JSON Schema dictionary
        """
        self._schemas[component_name] = PropsSchema(schema_dict)

    def register_schema_from_file(self, component_name: str, file_path: Union[str, Path]):
        """
        Register a schema from a JSON file.

        Args:
            component_name: Name of the component
            file_path: Path to JSON schema file
        """
        self._schemas[component_name] = PropsSchema.from_file(file_path)

    def has_schema(self, component_name: str) -> bool:
        """
        Check if a component has a registered schema.

        Args:
            component_name: Name of the component

        Returns:
            True if schema exists
        """
        return component_name in self._schemas

    def get_schema(self, component_name: str) -> Optional[PropsSchema]:
        """
        Get the schema for a component.

        Args:
            component_name: Name of the component

        Returns:
            PropsSchema or None
        """
        return self._schemas.get(component_name)

    def validate(
        self,
        component_name: str,
        props: Optional[Dict[str, Any]] = None,
        raise_on_error: bool = True
    ) -> tuple[bool, Dict[str, str]]:
        """
        Validate props for a component.

        Args:
            component_name: Name of the component
            props: Props dictionary to validate
            raise_on_error: Whether to raise InvalidPropsError on failure

        Returns:
            Tuple of (is_valid, errors_dict)

        Raises:
            InvalidPropsError: If validation fails and raise_on_error=True
        """
        props = props or {}

        # If no schema registered, skip validation
        if component_name not in self._schemas:
            return (True, {})

        schema = self._schemas[component_name]
        is_valid, errors = schema.validate(props)

        if not is_valid and raise_on_error:
            raise InvalidPropsError(
                f"Props validation failed for component '{component_name}'",
                invalid_props=errors,
                context={'component': component_name}
            )

        return (is_valid, errors)

    def validate_prop(
        self,
        component_name: str,
        prop_name: str,
        value: Any
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a single prop value.

        Args:
            component_name: Name of the component
            prop_name: Name of the prop
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if component_name not in self._schemas:
            return (True, None)

        schema = self._schemas[component_name]

        # Find rules for this prop
        for rule in schema.rules:
            if rule.prop_name == prop_name:
                is_valid, error = rule.validate(value)
                if not is_valid:
                    return (False, error)

        return (True, None)

    def list_schemas(self) -> List[str]:
        """
        List all registered component schemas.

        Returns:
            List of component names with schemas
        """
        return list(self._schemas.keys())


# Export public API
__all__ = [
    'ValidationType',
    'ValidationRule',
    'PropsSchema',
    'PropsValidator'
]
