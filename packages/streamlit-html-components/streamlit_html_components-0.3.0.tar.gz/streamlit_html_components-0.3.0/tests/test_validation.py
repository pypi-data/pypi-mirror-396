"""
Tests for props validation system.

Tests for:
- ValidationRule behavior
- PropsSchema creation and validation
- PropsValidator registration and validation
- JSON Schema parsing
- Error message formatting
"""

import pytest
import sys
from pathlib import Path
import tempfile
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from streamlit_html_components.validation import (
    ValidationType,
    ValidationRule,
    PropsSchema,
    PropsValidator
)
from streamlit_html_components.exceptions import InvalidPropsError


class TestValidationRule:
    """Test ValidationRule class."""

    def test_required_validation_pass(self):
        """Test required validation with value present."""
        rule = ValidationRule('name', ValidationType.REQUIRED)
        is_valid, error = rule.validate('John')
        assert is_valid
        assert error is None

    def test_required_validation_fail(self):
        """Test required validation with None value."""
        rule = ValidationRule('name', ValidationType.REQUIRED)
        is_valid, error = rule.validate(None)
        assert not is_valid
        assert 'required' in error.lower()

    def test_type_validation_pass(self):
        """Test type validation with correct type."""
        rule = ValidationRule('age', ValidationType.TYPE, int)
        is_valid, error = rule.validate(25)
        assert is_valid
        assert error is None

    def test_type_validation_fail(self):
        """Test type validation with wrong type."""
        rule = ValidationRule('age', ValidationType.TYPE, int)
        is_valid, error = rule.validate("25")
        assert not is_valid
        assert 'int' in error

    def test_pattern_validation_pass(self):
        """Test pattern validation with matching string."""
        rule = ValidationRule('email', ValidationType.PATTERN, r'^[\w\.-]+@[\w\.-]+\.\w+$')
        is_valid, error = rule.validate('test@example.com')
        assert is_valid
        assert error is None

    def test_pattern_validation_fail(self):
        """Test pattern validation with non-matching string."""
        rule = ValidationRule('email', ValidationType.PATTERN, r'^[\w\.-]+@[\w\.-]+\.\w+$')
        is_valid, error = rule.validate('invalid-email')
        assert not is_valid
        assert 'pattern' in error.lower()

    def test_range_validation_pass(self):
        """Test range validation within bounds."""
        rule = ValidationRule('score', ValidationType.RANGE, (0, 100))
        is_valid, error = rule.validate(50)
        assert is_valid
        assert error is None

    def test_range_validation_fail(self):
        """Test range validation outside bounds."""
        rule = ValidationRule('score', ValidationType.RANGE, (0, 100))
        is_valid, error = rule.validate(150)
        assert not is_valid
        assert '0' in error and '100' in error

    def test_enum_validation_pass(self):
        """Test enum validation with valid choice."""
        rule = ValidationRule('status', ValidationType.ENUM, ['active', 'inactive', 'pending'])
        is_valid, error = rule.validate('active')
        assert is_valid
        assert error is None

    def test_enum_validation_fail(self):
        """Test enum validation with invalid choice."""
        rule = ValidationRule('status', ValidationType.ENUM, ['active', 'inactive', 'pending'])
        is_valid, error = rule.validate('archived')
        assert not is_valid
        assert 'active' in error or 'inactive' in error

    def test_custom_validation_pass(self):
        """Test custom validation with passing function."""
        def is_even(x):
            return x % 2 == 0

        rule = ValidationRule('number', ValidationType.CUSTOM, is_even)
        is_valid, error = rule.validate(4)
        assert is_valid
        assert error is None

    def test_custom_validation_fail(self):
        """Test custom validation with failing function."""
        def is_even(x):
            return x % 2 == 0

        rule = ValidationRule('number', ValidationType.CUSTOM, is_even)
        is_valid, error = rule.validate(3)
        assert not is_valid
        assert error is not None

    def test_custom_error_message(self):
        """Test custom error message."""
        rule = ValidationRule(
            'age',
            ValidationType.RANGE,
            (18, 65),
            error_message="Age must be between 18 and 65"
        )
        is_valid, error = rule.validate(70)
        assert not is_valid
        assert error == "Age must be between 18 and 65"


class TestPropsSchema:
    """Test PropsSchema class."""

    def test_empty_schema(self):
        """Test empty schema allows anything."""
        schema = PropsSchema()
        is_valid, errors = schema.validate({'anything': 'goes'})
        assert is_valid
        assert len(errors) == 0

    def test_required_field(self):
        """Test required field validation."""
        schema = PropsSchema()
        schema.add_rule('name', ValidationType.REQUIRED)

        # Should pass with value
        is_valid, errors = schema.validate({'name': 'John'})
        assert is_valid
        assert len(errors) == 0

        # Should fail without value
        is_valid, errors = schema.validate({})
        assert not is_valid
        assert 'name' in errors

    def test_multiple_rules(self):
        """Test multiple validation rules."""
        schema = PropsSchema()
        schema.add_rule('name', ValidationType.REQUIRED)
        schema.add_rule('name', ValidationType.TYPE, str)
        schema.add_rule('age', ValidationType.TYPE, int)
        schema.add_rule('age', ValidationType.RANGE, (0, 120))

        # Should pass with valid props
        is_valid, errors = schema.validate({'name': 'John', 'age': 30})
        assert is_valid
        assert len(errors) == 0

        # Should fail with invalid types
        is_valid, errors = schema.validate({'name': 123, 'age': '30'})
        assert not is_valid
        assert 'name' in errors or 'age' in errors

    def test_from_dict_json_schema(self):
        """Test creating schema from JSON Schema dictionary."""
        schema_dict = {
            'required': ['title', 'count'],
            'properties': {
                'title': {
                    'type': 'string',
                    'pattern': r'^[A-Z]'
                },
                'count': {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 100
                },
                'active': {
                    'type': 'boolean'
                },
                'tags': {
                    'type': 'array'
                }
            }
        }

        schema = PropsSchema(schema_dict)

        # Valid props
        is_valid, errors = schema.validate({
            'title': 'Test',
            'count': 50,
            'active': True,
            'tags': ['tag1', 'tag2']
        })
        assert is_valid
        assert len(errors) == 0

        # Missing required
        is_valid, errors = schema.validate({'count': 50})
        assert not is_valid
        assert 'title' in errors

        # Invalid type
        is_valid, errors = schema.validate({'title': 'Test', 'count': 'invalid'})
        assert not is_valid
        assert 'count' in errors

    def test_enum_in_schema_dict(self):
        """Test enum validation from schema dictionary."""
        schema_dict = {
            'properties': {
                'status': {
                    'enum': ['draft', 'published', 'archived']
                }
            }
        }

        schema = PropsSchema(schema_dict)

        # Valid enum value
        is_valid, errors = schema.validate({'status': 'draft'})
        assert is_valid

        # Invalid enum value
        is_valid, errors = schema.validate({'status': 'deleted'})
        assert not is_valid
        assert 'status' in errors

    def test_to_dict(self):
        """Test converting schema back to dictionary."""
        schema_dict = {
            'required': ['name'],
            'properties': {
                'name': {'type': 'string'}
            }
        }

        schema = PropsSchema(schema_dict)
        result_dict = schema.to_dict()

        assert result_dict == schema_dict

    def test_from_file(self):
        """Test loading schema from JSON file."""
        schema_dict = {
            'required': ['name', 'email'],
            'properties': {
                'name': {'type': 'string'},
                'email': {
                    'type': 'string',
                    'pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'
                }
            }
        }

        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_dict, f)
            temp_file = f.name

        try:
            schema = PropsSchema.from_file(temp_file)

            # Test validation
            is_valid, errors = schema.validate({
                'name': 'John',
                'email': 'john@example.com'
            })
            assert is_valid
            assert len(errors) == 0

        finally:
            Path(temp_file).unlink()


class TestPropsValidator:
    """Test PropsValidator class."""

    def test_register_schema(self):
        """Test registering a schema."""
        validator = PropsValidator()
        schema = PropsSchema()
        schema.add_rule('title', ValidationType.REQUIRED)

        validator.register_schema('card', schema)

        assert validator.has_schema('card')
        assert validator.get_schema('card') is schema

    def test_register_from_dict(self):
        """Test registering schema from dictionary."""
        validator = PropsValidator()
        schema_dict = {
            'required': ['title'],
            'properties': {
                'title': {'type': 'string'}
            }
        }

        validator.register_schema_from_dict('card', schema_dict)

        assert validator.has_schema('card')

    def test_validate_with_schema(self):
        """Test validation with registered schema."""
        validator = PropsValidator()
        schema = PropsSchema()
        schema.add_rule('title', ValidationType.REQUIRED)
        schema.add_rule('title', ValidationType.TYPE, str)

        validator.register_schema('card', schema)

        # Valid props
        is_valid, errors = validator.validate('card', {'title': 'Test'}, raise_on_error=False)
        assert is_valid
        assert len(errors) == 0

        # Invalid props
        is_valid, errors = validator.validate('card', {}, raise_on_error=False)
        assert not is_valid
        assert 'title' in errors

    def test_validate_raises_on_error(self):
        """Test validation raises exception when raise_on_error=True."""
        validator = PropsValidator()
        schema = PropsSchema()
        schema.add_rule('title', ValidationType.REQUIRED)

        validator.register_schema('card', schema)

        # Should raise InvalidPropsError
        with pytest.raises(InvalidPropsError) as exc_info:
            validator.validate('card', {}, raise_on_error=True)

        assert 'card' in str(exc_info.value)
        assert 'title' in str(exc_info.value)

    def test_validate_without_schema(self):
        """Test validation passes when no schema registered."""
        validator = PropsValidator()

        # Should pass without schema
        is_valid, errors = validator.validate('unknown', {'any': 'props'})
        assert is_valid
        assert len(errors) == 0

    def test_validate_single_prop(self):
        """Test validating a single prop value."""
        validator = PropsValidator()
        schema = PropsSchema()
        schema.add_rule('age', ValidationType.TYPE, int)
        schema.add_rule('age', ValidationType.RANGE, (0, 120))

        validator.register_schema('user', schema)

        # Valid value
        is_valid, error = validator.validate_prop('user', 'age', 30)
        assert is_valid
        assert error is None

        # Invalid value
        is_valid, error = validator.validate_prop('user', 'age', 'invalid')
        assert not is_valid
        assert error is not None

    def test_list_schemas(self):
        """Test listing all registered schemas."""
        validator = PropsValidator()

        schema1 = PropsSchema()
        schema2 = PropsSchema()

        validator.register_schema('card', schema1)
        validator.register_schema('button', schema2)

        schemas = validator.list_schemas()

        assert len(schemas) == 2
        assert 'card' in schemas
        assert 'button' in schemas


class TestIntegrationWithExceptions:
    """Test integration with enhanced exceptions."""

    def test_invalid_props_error_format(self):
        """Test that InvalidPropsError formats validation errors nicely."""
        validator = PropsValidator()
        schema = PropsSchema()
        schema.add_rule('name', ValidationType.REQUIRED)
        schema.add_rule('email', ValidationType.PATTERN, r'^[\w\.-]+@[\w\.-]+\.\w+$')

        validator.register_schema('user', schema)

        try:
            validator.validate('user', {'email': 'invalid'}, raise_on_error=True)
            assert False, "Should have raised InvalidPropsError"
        except InvalidPropsError as e:
            error_str = str(e)
            # Should mention the component
            assert 'user' in error_str
            # Should mention validation errors
            assert 'name' in error_str or 'email' in error_str


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
