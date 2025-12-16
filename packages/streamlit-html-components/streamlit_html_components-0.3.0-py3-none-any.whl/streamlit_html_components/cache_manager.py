"""Cache manager for component rendering performance optimization."""

from typing import Optional, Dict, Any
from pathlib import Path
from collections import OrderedDict
import time

from .serialization import generate_cache_key, serialize_props


class LRUCache:
    """
    Simple LRU (Least Recently Used) cache with size limit.

    When the cache exceeds max_size_bytes, the least recently used items
    are evicted first.
    """

    def __init__(self, max_size_bytes: int = 100 * 1024 * 1024):
        """
        Initialize LRU cache.

        Args:
            max_size_bytes: Maximum cache size in bytes (default: 100MB)
        """
        self.max_size_bytes = max_size_bytes
        self.cache: OrderedDict[str, str] = OrderedDict()
        self.current_size_bytes = 0

    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache, updating its position as most recently used.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        if key not in self.cache:
            return None

        # Move to end (mark as recently used)
        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key: str, value: str) -> None:
        """
        Set value in cache, evicting LRU items if needed.

        Args:
            key: Cache key
            value: Value to cache
        """
        value_size = len(value.encode('utf-8'))

        # If value is larger than max cache size, don't cache it
        if value_size > self.max_size_bytes:
            return

        # Remove if already exists (to update size tracking)
        if key in self.cache:
            old_value_size = len(self.cache[key].encode('utf-8'))
            self.current_size_bytes -= old_value_size
            del self.cache[key]

        # Evict LRU items until there's space
        while self.current_size_bytes + value_size > self.max_size_bytes and self.cache:
            # Remove least recently used (first item)
            lru_key, lru_value = self.cache.popitem(last=False)
            self.current_size_bytes -= len(lru_value.encode('utf-8'))

        # Add new item
        self.cache[key] = value
        self.current_size_bytes += value_size

    def remove(self, key: str) -> None:
        """
        Remove item from cache.

        Args:
            key: Cache key
        """
        if key in self.cache:
            value_size = len(self.cache[key].encode('utf-8'))
            self.current_size_bytes -= value_size
            del self.cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.current_size_bytes = 0

    def __len__(self) -> int:
        """Return number of cached items."""
        return len(self.cache)

    def __contains__(self, key: str) -> bool:
        """Check if key is in cache."""
        return key in self.cache


class CacheManager:
    """
    Manages caching of rendered components for performance optimization.

    Features:
    - Content-based cache keys (component + props + file hashes)
    - LRU eviction with size limits
    - TTL (time-to-live) support
    - Selective invalidation
    - Component indexing for efficient invalidation
    - Cache statistics
    """

    def __init__(self, max_size_mb: int = 100):
        """
        Initialize the cache manager.

        Args:
            max_size_mb: Maximum cache size in megabytes (default: 100MB)
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        self._render_cache = LRUCache(max_size_bytes)
        self._timestamps: Dict[str, float] = {}
        self._component_index: Dict[str, set] = {}  # Track keys per component

    @staticmethod
    def cache_key(
        component_name: str,
        props: Dict[str, Any],
        template_path: Optional[Path] = None,
        css_paths: Optional[list[Path]] = None,
        js_paths: Optional[list[Path]] = None
    ) -> str:
        """
        Generate a unique cache key for component state.

        The cache key is based on:
        - Component name
        - Props (serialized deterministically)
        - Template content hash
        - Style content hash
        - Script content hash

        Args:
            component_name: Name of the component
            props: Component props dictionary
            template_path: Path to template file
            css_paths: List of CSS file paths
            js_paths: List of JS file paths

        Returns:
            Cache key string

        Note:
            Uses the new serialization module for deterministic cache key generation
        """
        # Use new serialization utilities for proper cache key generation
        if template_path and css_paths is not None and js_paths is not None:
            return generate_cache_key(
                component_name,
                props or {},
                template_path,
                css_paths,
                js_paths
            )
        else:
            # Fallback for backward compatibility
            # Just hash the props deterministically
            from .serialization import hash_props
            props_hash = hash_props(props or {})
            return f"{component_name}:{props_hash}"

    def get_cached(self, cache_key: str, ttl: Optional[int] = None) -> Optional[str]:
        """
        Retrieve cached component render if valid.

        Args:
            cache_key: Cache key to look up
            ttl: Time-to-live in seconds (None = no expiration)

        Returns:
            Cached HTML string if valid, None otherwise
        """
        cached_value = self._render_cache.get(cache_key)
        if cached_value is None:
            return None

        # Check TTL if specified
        if ttl is not None:
            timestamp = self._timestamps.get(cache_key, 0)
            age = time.time() - timestamp

            if age > ttl:
                # Cache expired, remove it
                self._remove_entry(cache_key)
                return None

        return cached_value

    def set_cached(self, cache_key: str, rendered_html: str, component_name: Optional[str] = None):
        """
        Store rendered component in cache.

        Args:
            cache_key: Cache key
            rendered_html: Rendered HTML content to cache
            component_name: Component name for indexing (optional)
        """
        self._render_cache.set(cache_key, rendered_html)
        self._timestamps[cache_key] = time.time()

        # Track in component index for selective invalidation
        if component_name:
            if component_name not in self._component_index:
                self._component_index[component_name] = set()
            self._component_index[component_name].add(cache_key)

    def _remove_entry(self, cache_key: str):
        """Remove a single cache entry."""
        self._render_cache.remove(cache_key)
        if cache_key in self._timestamps:
            del self._timestamps[cache_key]

        # Remove from component index
        for component_keys in self._component_index.values():
            component_keys.discard(cache_key)

    def invalidate(self, component_name: Optional[str] = None):
        """
        Invalidate cache entries.

        Args:
            component_name: If provided, only invalidate entries for this component.
                          If None, clear all cache.

        Example:
            >>> cache_manager.invalidate('button')  # Clear button cache only
            >>> cache_manager.invalidate()  # Clear all cache
        """
        if component_name is None:
            # Clear all cache
            self._render_cache.clear()
            self._timestamps.clear()
            self._component_index.clear()
        else:
            # Remove entries for specific component using index
            if component_name in self._component_index:
                keys_to_remove = list(self._component_index[component_name])
                for key in keys_to_remove:
                    self._remove_entry(key)
                # Clear the component index entry
                del self._component_index[component_name]

    def cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics including size, entries, and LRU info
        """
        oldest_timestamp = min(self._timestamps.values()) if self._timestamps else None
        newest_timestamp = max(self._timestamps.values()) if self._timestamps else None

        current_time = time.time()

        return {
            'total_entries': len(self._render_cache),
            'total_size_bytes': self._render_cache.current_size_bytes,
            'total_size_kb': round(self._render_cache.current_size_bytes / 1024, 2),
            'total_size_mb': round(self._render_cache.current_size_bytes / (1024 * 1024), 2),
            'max_size_mb': round(self._render_cache.max_size_bytes / (1024 * 1024), 2),
            'usage_percent': round((self._render_cache.current_size_bytes / self._render_cache.max_size_bytes) * 100, 2),
            'oldest_entry_age_seconds': round(current_time - oldest_timestamp, 2) if oldest_timestamp else None,
            'newest_entry_age_seconds': round(current_time - newest_timestamp, 2) if newest_timestamp else None,
            'components_cached': len(self._component_index),
        }

    def clear(self):
        """Clear all cache entries (alias for invalidate())."""
        self.invalidate()


# Global cache instance
_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """
    Get the global cache manager instance.

    Returns:
        Global CacheManager instance
    """
    return _cache_manager


def invalidate_cache(component_name: Optional[str] = None):
    """
    Invalidate component cache.

    Args:
        component_name: If provided, only invalidate this component.
                       If None, clear all cache.
    """
    _cache_manager.invalidate(component_name)


def cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.

    Returns:
        Dictionary with cache statistics
    """
    return _cache_manager.cache_stats()
