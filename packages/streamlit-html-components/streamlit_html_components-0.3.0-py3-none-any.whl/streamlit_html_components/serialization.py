"""
Deterministic serialization utilities for cache key generation.

Ensures that props are serialized consistently for caching, even with
complex data types like datetime, Path, etc.
"""

import json
import hashlib
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict
from decimal import Decimal


def serialize_value(obj: Any) -> Any:
    """
    Convert complex objects to JSON-serializable format.

    This function ensures deterministic serialization for cache keys.

    Args:
        obj: Object to serialize

    Returns:
        JSON-serializable representation

    Example:
        >>> serialize_value(datetime(2025, 12, 11, 10, 30))
        '2025-12-11T10:30:00'
        >>> serialize_value(Path('/tmp/test'))
        '/tmp/test'
    """
    # datetime objects -> ISO format string
    if isinstance(obj, datetime):
        return obj.isoformat()

    # date objects -> ISO format string
    if isinstance(obj, date):
        return obj.isoformat()

    # Path objects -> string
    if isinstance(obj, Path):
        return str(obj)

    # Decimal -> string (preserves precision)
    if isinstance(obj, Decimal):
        return str(obj)

    # Sets -> sorted list (deterministic order)
    if isinstance(obj, set):
        return sorted(list(obj), key=str)

    # Bytes -> base64 string
    if isinstance(obj, bytes):
        import base64
        return base64.b64encode(obj).decode('utf-8')

    # Default: convert to string
    return str(obj)


def serialize_props(props: Dict[str, Any]) -> str:
    """
    Serialize props dictionary to deterministic JSON string.

    Args:
        props: Props dictionary to serialize

    Returns:
        JSON string with sorted keys and deterministic formatting

    Example:
        >>> props = {'name': 'test', 'count': 5, 'date': datetime(2025, 12, 11)}
        >>> json_str = serialize_props(props)
        >>> 'date' in json_str and 'name' in json_str
        True
    """
    return json.dumps(
        props,
        sort_keys=True,  # Deterministic key order
        default=serialize_value,  # Handle complex types
        separators=(',', ':')  # Compact format, no extra whitespace
    )


def hash_props(props: Dict[str, Any]) -> str:
    """
    Generate SHA256 hash of props dictionary.

    Args:
        props: Props dictionary to hash

    Returns:
        Hexadecimal hash string

    Example:
        >>> props = {'text': 'Hello'}
        >>> hash_str = hash_props(props)
        >>> len(hash_str)
        64
    """
    json_str = serialize_props(props)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


def hash_file_content(file_path: Path) -> str:
    """
    Generate SHA256 hash of file contents.

    Args:
        file_path: Path to file

    Returns:
        Hexadecimal hash string

    Raises:
        FileNotFoundError: If file doesn't exist

    Example:
        >>> from pathlib import Path
        >>> hash_str = hash_file_content(Path('/tmp/test.txt'))  # doctest: +SKIP
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read file in binary mode and hash
    hasher = hashlib.sha256()

    with open(file_path, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)

    return hasher.hexdigest()


def hash_multiple_files(file_paths: list[Path]) -> str:
    """
    Generate combined hash of multiple files.

    Args:
        file_paths: List of file paths

    Returns:
        Hexadecimal hash string representing combined hash

    Example:
        >>> paths = [Path('file1.txt'), Path('file2.txt')]
        >>> hash_str = hash_multiple_files(paths)  # doctest: +SKIP
    """
    hasher = hashlib.sha256()

    for file_path in sorted(file_paths, key=str):  # Sort for deterministic order
        if file_path.exists():
            file_hash = hash_file_content(file_path)
            hasher.update(file_hash.encode('utf-8'))
        else:
            # File doesn't exist - include empty hash
            hasher.update(b'')

    return hasher.hexdigest()


def generate_cache_key(
    component_name: str,
    props: Dict[str, Any],
    template_path: Path,
    css_paths: list[Path],
    js_paths: list[Path]
) -> str:
    """
    Generate complete cache key for a component render.

    This creates a unique cache key based on:
    - Component name
    - Props values (hashed)
    - Template file content (hashed)
    - CSS file contents (hashed)
    - JS file contents (hashed)

    Args:
        component_name: Name of the component
        props: Props dictionary
        template_path: Path to template file
        css_paths: List of CSS file paths
        js_paths: List of JS file paths

    Returns:
        Cache key string in format: "component:template_hash:css_hash:js_hash:props_hash"

    Example:
        >>> from pathlib import Path
        >>> key = generate_cache_key(
        ...     'button',
        ...     {'text': 'Click me'},
        ...     Path('button.html'),
        ...     [Path('button.css')],
        ...     [Path('button.js')]
        ... )  # doctest: +SKIP
    """
    # Hash props
    props_hash = hash_props(props) if props else '0' * 64

    # Hash template
    template_hash = hash_file_content(template_path) if template_path.exists() else '0' * 64

    # Hash CSS files
    css_hash = hash_multiple_files(css_paths) if css_paths else '0' * 64

    # Hash JS files
    js_hash = hash_multiple_files(js_paths) if js_paths else '0' * 64

    # Combine into cache key
    cache_key = f"{component_name}:{template_hash}:{css_hash}:{js_hash}:{props_hash}"

    return cache_key
