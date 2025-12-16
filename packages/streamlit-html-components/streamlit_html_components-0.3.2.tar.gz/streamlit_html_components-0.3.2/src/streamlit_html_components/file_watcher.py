"""
File watcher for hot reload functionality.

Monitors component files (templates, styles, scripts) for changes and
triggers cache invalidation for automatic reloading during development.

Supports both watchdog (if available) and polling fallback.
"""

from typing import Callable, Set, Dict, Optional, List
from pathlib import Path
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime

from .diagnostics import DebugMode


@dataclass
class FileChangeEvent:
    """Event representing a file change."""
    path: Path
    event_type: str  # 'created', 'modified', 'deleted', 'moved'
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"{self.event_type.upper()}: {self.path} at {self.timestamp.strftime('%H:%M:%S')}"


class FileWatcher:
    """
    Watch files for changes and trigger callbacks.

    Supports two modes:
    1. watchdog mode (if watchdog library is installed)
    2. polling mode (fallback, checks files periodically)

    Example:
        >>> from pathlib import Path
        >>> def on_change(event):
        ...     print(f"File changed: {event.path}")
        >>>
        >>> watcher = FileWatcher()
        >>> watcher.watch(Path('templates'), '*.html', on_change)
        >>> watcher.start()
        >>> # Files will be monitored in background
        >>> watcher.stop()
    """

    def __init__(self, poll_interval: float = 1.0, use_watchdog: bool = True):
        """
        Initialize file watcher.

        Args:
            poll_interval: Seconds between polling checks (used in polling mode)
            use_watchdog: Try to use watchdog library if available
        """
        self.poll_interval = poll_interval
        self._use_watchdog = use_watchdog
        self._watchdog_available = False
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._watches: List[Dict] = []
        self._file_mtimes: Dict[Path, float] = {}
        self._observer = None

        # Try to import watchdog
        if use_watchdog:
            try:
                from watchdog.observers import Observer
                from watchdog.events import FileSystemEventHandler
                self._watchdog_available = True
                DebugMode.log_info("FileWatcher: Using watchdog for file monitoring")
            except ImportError:
                DebugMode.log_info("FileWatcher: watchdog not available, using polling")

    def watch(
        self,
        directory: Path,
        pattern: str,
        callback: Callable[[FileChangeEvent], None],
        recursive: bool = False
    ):
        """
        Add a directory to watch.

        Args:
            directory: Directory to watch
            pattern: Glob pattern for files to watch (e.g., '*.html', '*.css')
            callback: Function to call when files change
            recursive: Watch subdirectories recursively
        """
        if not directory.exists():
            DebugMode.log_debug(f"FileWatcher: Directory does not exist: {directory}")
            return

        self._watches.append({
            'directory': directory,
            'pattern': pattern,
            'callback': callback,
            'recursive': recursive
        })

        # Initialize mtimes for existing files
        if not self._watchdog_available:
            self._update_mtimes(directory, pattern, recursive)

        DebugMode.log_debug(f"FileWatcher: Watching {directory}/{pattern}")

    def _update_mtimes(self, directory: Path, pattern: str, recursive: bool):
        """Update modification times for files in directory."""
        glob_func = directory.rglob if recursive else directory.glob
        for file_path in glob_func(pattern):
            if file_path.is_file():
                try:
                    self._file_mtimes[file_path] = file_path.stat().st_mtime
                except OSError:
                    pass

    def start(self):
        """Start watching files."""
        if self._running:
            DebugMode.log_debug("FileWatcher: Already running")
            return

        self._running = True

        if self._watchdog_available:
            self._start_watchdog()
        else:
            self._start_polling()

        DebugMode.log_info("FileWatcher: Started")

    def _start_watchdog(self):
        """Start watchdog-based file monitoring."""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler, FileSystemEvent

            class ComponentFileHandler(FileSystemEventHandler):
                def __init__(self, watcher: 'FileWatcher'):
                    self.watcher = watcher

                def on_any_event(self, event: FileSystemEvent):
                    # Ignore directory events
                    if event.is_directory:
                        return

                    # Map watchdog event types
                    event_type_map = {
                        'created': 'created',
                        'modified': 'modified',
                        'deleted': 'deleted',
                        'moved': 'moved'
                    }

                    event_type = event_type_map.get(event.event_type, 'modified')
                    file_path = Path(event.src_path)

                    # Check if file matches any watched patterns
                    for watch in self.watcher._watches:
                        if self._matches_watch(file_path, watch):
                            change_event = FileChangeEvent(
                                path=file_path,
                                event_type=event_type
                            )
                            DebugMode.log_debug(f"FileWatcher: {change_event}")
                            watch['callback'](change_event)

                def _matches_watch(self, file_path: Path, watch: Dict) -> bool:
                    """Check if file matches watch pattern."""
                    directory = watch['directory']
                    pattern = watch['pattern']

                    # Check if file is in watched directory
                    try:
                        file_path.relative_to(directory)
                    except ValueError:
                        return False

                    # Check if file matches pattern
                    import fnmatch
                    return fnmatch.fnmatch(file_path.name, pattern)

            self._observer = Observer()
            handler = ComponentFileHandler(self)

            # Schedule watches
            for watch in self._watches:
                self._observer.schedule(
                    handler,
                    str(watch['directory']),
                    recursive=watch['recursive']
                )

            self._observer.start()

        except Exception as e:
            DebugMode.log_debug(f"FileWatcher: Watchdog failed, falling back to polling: {e}")
            self._watchdog_available = False
            self._start_polling()

    def _start_polling(self):
        """Start polling-based file monitoring."""
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def _poll_loop(self):
        """Poll files for changes."""
        while self._running:
            for watch in self._watches:
                directory = watch['directory']
                pattern = watch['pattern']
                callback = watch['callback']
                recursive = watch['recursive']

                glob_func = directory.rglob if recursive else directory.glob

                try:
                    for file_path in glob_func(pattern):
                        if not file_path.is_file():
                            continue

                        try:
                            current_mtime = file_path.stat().st_mtime
                            previous_mtime = self._file_mtimes.get(file_path)

                            if previous_mtime is None:
                                # New file
                                event = FileChangeEvent(file_path, 'created')
                                DebugMode.log_debug(f"FileWatcher: {event}")
                                callback(event)
                                self._file_mtimes[file_path] = current_mtime

                            elif current_mtime > previous_mtime:
                                # Modified file
                                event = FileChangeEvent(file_path, 'modified')
                                DebugMode.log_debug(f"FileWatcher: {event}")
                                callback(event)
                                self._file_mtimes[file_path] = current_mtime

                        except OSError:
                            # File might have been deleted
                            if file_path in self._file_mtimes:
                                event = FileChangeEvent(file_path, 'deleted')
                                DebugMode.log_debug(f"FileWatcher: {event}")
                                callback(event)
                                del self._file_mtimes[file_path]

                except Exception as e:
                    DebugMode.log_debug(f"FileWatcher: Error polling {directory}: {e}")

            time.sleep(self.poll_interval)

    def stop(self):
        """Stop watching files."""
        if not self._running:
            return

        self._running = False

        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

        DebugMode.log_info("FileWatcher: Stopped")

    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._running

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


# Export public API
__all__ = [
    'FileWatcher',
    'FileChangeEvent'
]
