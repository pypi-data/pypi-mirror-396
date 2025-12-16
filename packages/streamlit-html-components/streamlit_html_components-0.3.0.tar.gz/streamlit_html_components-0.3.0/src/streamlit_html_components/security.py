"""
Security utilities for streamlit-html-components.

This module provides security features including:
- Content Security Policy (CSP) header generation
- XSS prevention utilities
- Input sanitization
- Security audit helpers
"""

from typing import Optional, Dict, List
from dataclasses import dataclass, field


@dataclass
class CSPPolicy:
    """
    Content Security Policy configuration.

    CSP helps prevent XSS attacks by controlling which resources
    can be loaded and executed by the browser.

    Example:
        >>> policy = CSPPolicy(
        ...     default_src=["'self'"],
        ...     script_src=["'self'", "'unsafe-inline'"],
        ...     style_src=["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"]
        ... )
        >>> header = policy.to_header()
    """

    # Core directives
    default_src: List[str] = field(default_factory=lambda: ["'self'"])
    script_src: List[str] = field(default_factory=lambda: ["'self'"])
    style_src: List[str] = field(default_factory=lambda: ["'self'"])
    img_src: List[str] = field(default_factory=lambda: ["'self'", "data:", "https:"])
    font_src: List[str] = field(default_factory=lambda: ["'self'", "data:", "https:"])
    connect_src: List[str] = field(default_factory=lambda: ["'self'"])

    # Additional directives
    object_src: List[str] = field(default_factory=lambda: ["'none'"])
    base_uri: List[str] = field(default_factory=lambda: ["'self'"])
    frame_ancestors: List[str] = field(default_factory=lambda: ["'self'"])
    form_action: List[str] = field(default_factory=lambda: ["'self'"])

    # Upgrade insecure requests
    upgrade_insecure_requests: bool = False

    def to_header(self) -> str:
        """
        Generate CSP header value.

        Returns:
            CSP header string

        Example:
            >>> policy = CSPPolicy()
            >>> header = policy.to_header()
            >>> print(header)
            default-src 'self'; script-src 'self'; ...
        """
        directives = []

        # Add all directives that are set
        if self.default_src:
            directives.append(f"default-src {' '.join(self.default_src)}")
        if self.script_src:
            directives.append(f"script-src {' '.join(self.script_src)}")
        if self.style_src:
            directives.append(f"style-src {' '.join(self.style_src)}")
        if self.img_src:
            directives.append(f"img-src {' '.join(self.img_src)}")
        if self.font_src:
            directives.append(f"font-src {' '.join(self.font_src)}")
        if self.connect_src:
            directives.append(f"connect-src {' '.join(self.connect_src)}")
        if self.object_src:
            directives.append(f"object-src {' '.join(self.object_src)}")
        if self.base_uri:
            directives.append(f"base-uri {' '.join(self.base_uri)}")
        if self.frame_ancestors:
            directives.append(f"frame-ancestors {' '.join(self.frame_ancestors)}")
        if self.form_action:
            directives.append(f"form-action {' '.join(self.form_action)}")

        if self.upgrade_insecure_requests:
            directives.append("upgrade-insecure-requests")

        return "; ".join(directives)

    def to_meta_tag(self) -> str:
        """
        Generate CSP meta tag for HTML.

        Returns:
            HTML meta tag string

        Example:
            >>> policy = CSPPolicy()
            >>> meta = policy.to_meta_tag()
            >>> print(meta)
            <meta http-equiv="Content-Security-Policy" content="...">
        """
        return f'<meta http-equiv="Content-Security-Policy" content="{self.to_header()}">'


def create_default_csp(allow_inline_scripts: bool = True, allow_inline_styles: bool = True) -> CSPPolicy:
    """
    Create a default CSP policy suitable for Streamlit components.

    Args:
        allow_inline_scripts: Allow inline scripts (needed for component bridge)
        allow_inline_styles: Allow inline styles (needed for component styling)

    Returns:
        CSPPolicy instance

    Example:
        >>> policy = create_default_csp(allow_inline_scripts=True)
        >>> header = policy.to_header()
    """
    script_src = ["'self'"]
    if allow_inline_scripts:
        script_src.append("'unsafe-inline'")

    style_src = ["'self'"]
    if allow_inline_styles:
        style_src.append("'unsafe-inline'")

    # Add common CDN origins
    style_src.extend([
        "https://cdn.jsdelivr.net",
        "https://unpkg.com",
        "https://cdnjs.cloudflare.com"
    ])

    script_src.extend([
        "https://cdn.jsdelivr.net",
        "https://unpkg.com",
        "https://cdnjs.cloudflare.com"
    ])

    return CSPPolicy(
        default_src=["'self'"],
        script_src=script_src,
        style_src=style_src,
        img_src=["'self'", "data:", "https:"],
        font_src=["'self'", "data:", "https:"],
        connect_src=["'self'"],
        object_src=["'none'"],
        base_uri=["'self'"],
        frame_ancestors=["'self'"],
        form_action=["'self'"]
    )


def create_strict_csp() -> CSPPolicy:
    """
    Create a strict CSP policy with no inline scripts or styles.

    This is the most secure option but may not work with all components.

    Returns:
        CSPPolicy instance

    Example:
        >>> policy = create_strict_csp()
        >>> header = policy.to_header()
    """
    return CSPPolicy(
        default_src=["'self'"],
        script_src=["'self'"],
        style_src=["'self'"],
        img_src=["'self'", "data:"],
        font_src=["'self'", "data:"],
        connect_src=["'self'"],
        object_src=["'none'"],
        base_uri=["'self'"],
        frame_ancestors=["'none'"],
        form_action=["'self'"],
        upgrade_insecure_requests=True
    )


class SecurityAuditor:
    """
    Audit component HTML for security issues.

    Example:
        >>> auditor = SecurityAuditor()
        >>> issues = auditor.audit_html('<script>alert("XSS")</script>')
        >>> if issues:
        ...     print(f"Found {len(issues)} security issues")
    """

    @staticmethod
    def audit_html(html: str) -> List[Dict[str, str]]:
        """
        Audit HTML content for potential security issues.

        Args:
            html: HTML content to audit

        Returns:
            List of issues found (each issue is a dict with 'type' and 'description')

        Example:
            >>> auditor = SecurityAuditor()
            >>> issues = auditor.audit_html('<script>eval(userInput)</script>')
            >>> for issue in issues:
            ...     print(f"{issue['type']}: {issue['description']}")
        """
        issues = []

        # Check for dangerous patterns (all lowercase for case-insensitive matching)
        dangerous_patterns = [
            ('eval(', 'Use of eval() can lead to code injection'),
            ('innerhtml', 'Direct innerHTML assignment can lead to XSS'),
            ('document.write', 'document.write can be exploited for XSS'),
            ('javascript:', 'javascript: URLs can execute arbitrary code'),
            ('onerror=', 'Inline event handlers can be XSS vectors'),
            ('onclick=', 'Inline event handlers can be XSS vectors'),
        ]

        html_lower = html.lower()
        for pattern, description in dangerous_patterns:
            if pattern in html_lower:
                issues.append({
                    'type': 'potential_xss',
                    'pattern': pattern,
                    'description': description,
                    'severity': 'high'
                })

        # Check for external scripts from untrusted domains
        import re
        script_tags = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html, re.IGNORECASE)
        trusted_domains = [
            'cdn.jsdelivr.net',
            'unpkg.com',
            'cdnjs.cloudflare.com',
            'code.jquery.com'
        ]

        for src in script_tags:
            if not any(domain in src for domain in trusted_domains):
                if src.startswith('http://') or src.startswith('https://'):
                    issues.append({
                        'type': 'untrusted_script',
                        'pattern': src,
                        'description': f'Script from potentially untrusted domain: {src}',
                        'severity': 'medium'
                    })

        return issues

    @staticmethod
    def sanitize_user_input(value: str, allow_html: bool = False) -> str:
        """
        Sanitize user input to prevent XSS.

        Args:
            value: Input value to sanitize
            allow_html: If True, allow safe HTML tags

        Returns:
            Sanitized string

        Example:
            >>> auditor = SecurityAuditor()
            >>> safe = auditor.sanitize_user_input('<script>alert("XSS")</script>')
            >>> print(safe)
            &lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;
        """
        if not isinstance(value, str):
            return str(value)

        if not allow_html:
            # Escape all HTML
            return (value
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;')
                .replace('/', '&#x2F;'))

        # If allow_html, use a whitelist of safe tags
        # For now, just escape dangerous tags
        safe_value = value
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'link']

        for tag in dangerous_tags:
            # Case-insensitive replacement
            import re
            safe_value = re.sub(
                f'<{tag}[^>]*>.*?</{tag}>',
                '',
                safe_value,
                flags=re.IGNORECASE | re.DOTALL
            )
            # Also remove self-closing versions
            safe_value = re.sub(
                f'<{tag}[^>]*/>',
                '',
                safe_value,
                flags=re.IGNORECASE
            )

        return safe_value


def inject_csp_meta(html: str, policy: Optional[CSPPolicy] = None) -> str:
    """
    Inject CSP meta tag into HTML head.

    Args:
        html: HTML content
        policy: CSP policy (creates default if None)

    Returns:
        HTML with CSP meta tag injected

    Example:
        >>> html = '<html><head></head><body>Content</body></html>'
        >>> secured_html = inject_csp_meta(html)
        >>> 'Content-Security-Policy' in secured_html
        True
    """
    if policy is None:
        policy = create_default_csp()

    meta_tag = policy.to_meta_tag()

    # Try to inject into <head>
    if '<head>' in html.lower():
        import re
        html = re.sub(
            r'<head>',
            f'<head>\n    {meta_tag}',
            html,
            count=1,
            flags=re.IGNORECASE
        )
    else:
        # No head tag, prepend to HTML
        html = f'{meta_tag}\n{html}'

    return html


# Export public API
__all__ = [
    'CSPPolicy',
    'create_default_csp',
    'create_strict_csp',
    'SecurityAuditor',
    'inject_csp_meta'
]
