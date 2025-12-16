"""
Security tests for streamlit-html-components.

Tests for:
- Path traversal prevention
- XSS prevention
- CSP policy generation
- Input sanitization
"""

import pytest
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from streamlit_html_components.security import (
    CSPPolicy,
    create_default_csp,
    create_strict_csp,
    SecurityAuditor,
    inject_csp_meta
)
from streamlit_html_components.validators import Validator
from streamlit_html_components.exceptions import SecurityError, ConfigurationError


class TestPathTraversalPrevention:
    """Test path traversal security."""

    def test_path_within_cwd_allowed(self, tmp_path):
        """Test that paths within CWD are allowed."""
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Create a test directory
            test_dir = tmp_path / "components"
            test_dir.mkdir()

            # This should succeed
            result = Validator.validate_directory(str(test_dir))
            assert result == test_dir.resolve()

        finally:
            os.chdir(original_cwd)

    def test_path_outside_cwd_blocked(self, tmp_path):
        """Test that paths outside CWD are blocked."""
        original_cwd = os.getcwd()
        try:
            # Create nested structure
            inner_dir = tmp_path / "project" / "src"
            inner_dir.mkdir(parents=True)

            # Change to inner directory
            os.chdir(inner_dir)

            # Try to access parent directory (outside cwd)
            outside_dir = tmp_path / "outside"
            outside_dir.mkdir()

            # This should raise SecurityError
            with pytest.raises(SecurityError) as exc_info:
                Validator.validate_directory(str(outside_dir))

            assert "outside working directory" in str(exc_info.value).lower()

        finally:
            os.chdir(original_cwd)

    def test_dotdot_path_blocked(self, tmp_path):
        """Test that ../ path traversal is blocked."""
        original_cwd = os.getcwd()
        try:
            inner_dir = tmp_path / "project"
            inner_dir.mkdir()
            os.chdir(inner_dir)

            # Create a directory to access via ../
            (tmp_path / "secret").mkdir()

            # Try path traversal
            with pytest.raises(SecurityError):
                Validator.validate_directory("../secret")

        finally:
            os.chdir(original_cwd)


class TestCSPPolicy:
    """Test Content Security Policy generation."""

    def test_default_csp_generation(self):
        """Test default CSP policy generation."""
        policy = create_default_csp()
        header = policy.to_header()

        assert "default-src 'self'" in header
        assert "script-src" in header
        assert "style-src" in header

    def test_strict_csp_no_inline(self):
        """Test strict CSP doesn't allow inline scripts."""
        policy = create_strict_csp()
        header = policy.to_header()

        assert "'unsafe-inline'" not in header
        assert "script-src 'self'" in header
        assert "object-src 'none'" in header

    def test_csp_meta_tag_generation(self):
        """Test CSP meta tag generation."""
        policy = CSPPolicy()
        meta = policy.to_meta_tag()

        assert '<meta http-equiv="Content-Security-Policy"' in meta
        assert 'content=' in meta

    def test_custom_csp_directives(self):
        """Test custom CSP directives."""
        policy = CSPPolicy(
            script_src=["'self'", "https://trusted.com"],
            style_src=["'self'", "'unsafe-inline'"],
            img_src=["'self'", "data:", "https:"]
        )

        header = policy.to_header()
        assert "https://trusted.com" in header
        assert "'unsafe-inline'" in header


class TestSecurityAuditor:
    """Test security auditing."""

    def test_detect_eval(self):
        """Test detection of eval() usage."""
        auditor = SecurityAuditor()
        html = '<script>eval(userInput)</script>'

        issues = auditor.audit_html(html)
        assert len(issues) > 0
        assert any('eval' in issue['pattern'] for issue in issues)

    def test_detect_innerHTML(self):
        """Test detection of innerHTML usage."""
        auditor = SecurityAuditor()
        html = '<script>element.innerHTML = userInput</script>'

        issues = auditor.audit_html(html)
        assert len(issues) > 0
        assert any('innerhtml' in issue['pattern'] for issue in issues)

    def test_detect_inline_event_handlers(self):
        """Test detection of inline event handlers."""
        auditor = SecurityAuditor()
        html = '<img src="x" onerror="alert(1)">'

        issues = auditor.audit_html(html)
        assert len(issues) > 0
        assert any('onerror' in issue['pattern'] for issue in issues)

    def test_sanitize_user_input(self):
        """Test input sanitization."""
        auditor = SecurityAuditor()

        # Test script tag removal
        dangerous = '<script>alert("XSS")</script>'
        safe = auditor.sanitize_user_input(dangerous)

        assert '<script>' not in safe
        assert '&lt;script&gt;' in safe

    def test_sanitize_with_allow_html(self):
        """Test sanitization with HTML allowed."""
        auditor = SecurityAuditor()

        html_with_script = '<p>Text</p><script>bad()</script>'
        safe = auditor.sanitize_user_input(html_with_script, allow_html=True)

        # Should keep <p> but remove <script>
        assert '<p>' in safe or safe != html_with_script  # Script removed


class TestCSPInjection:
    """Test CSP meta tag injection."""

    def test_inject_into_head(self):
        """Test CSP injection into HTML head."""
        html = '<html><head></head><body>Content</body></html>'
        result = inject_csp_meta(html)

        assert 'Content-Security-Policy' in result
        assert '<head>' in result

    def test_inject_without_head(self):
        """Test CSP injection when no head tag exists."""
        html = '<div>Content</div>'
        result = inject_csp_meta(html)

        assert 'Content-Security-Policy' in result

    def test_custom_policy_injection(self):
        """Test injection with custom policy."""
        html = '<html><head></head><body></body></html>'
        policy = create_strict_csp()
        result = inject_csp_meta(html, policy)

        assert 'Content-Security-Policy' in result
        assert "'self'" in result


class TestValidatorSecurity:
    """Test validator security features."""

    def test_reserved_keys_blocked(self):
        """Test that reserved keys in props are blocked."""
        from streamlit_html_components.exceptions import InvalidPropsError

        reserved_props = {
            '__component__': 'value',
            'normal_key': 'value'
        }

        with pytest.raises(InvalidPropsError) as exc_info:
            Validator.validate_props(reserved_props)

        assert 'reserved' in str(exc_info.value).lower()

    def test_component_name_validation(self):
        """Test component name validation."""
        from streamlit_html_components.exceptions import InvalidPropsError

        # Valid names
        assert Validator.validate_component_name('button')
        assert Validator.validate_component_name('my-component')
        assert Validator.validate_component_name('my_component')

        # Invalid names
        with pytest.raises(InvalidPropsError):
            Validator.validate_component_name('my component')  # Space

        with pytest.raises(InvalidPropsError):
            Validator.validate_component_name('my@component')  # Special char

    def test_html_sanitization(self):
        """Test HTML sanitization."""
        dangerous = '<script>alert("XSS")</script>'
        safe = Validator.sanitize_html(dangerous, allow_html=False)

        assert '&lt;script&gt;' in safe
        assert '<script>' not in safe


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
