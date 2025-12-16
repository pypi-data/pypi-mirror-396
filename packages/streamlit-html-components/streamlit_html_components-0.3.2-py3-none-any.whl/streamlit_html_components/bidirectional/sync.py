"""
Real-time state synchronization for bidirectional communication.

Provides state management with:
- Automatic state diffing
- Conflict resolution
- Optimistic updates
- State versioning
"""

from typing import Dict, Any, Optional, Callable, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import copy


class ConflictResolution(Enum):
    """Strategies for resolving state conflicts."""
    CLIENT_WINS = "client_wins"  # Client (JavaScript) state takes precedence
    SERVER_WINS = "server_wins"  # Server (Python) state takes precedence
    LATEST_WINS = "latest_wins"  # Most recent update wins
    MERGE = "merge"  # Attempt to merge non-conflicting changes
    CUSTOM = "custom"  # Use custom conflict resolver


@dataclass
class StateSnapshot:
    """Represents a snapshot of component state at a point in time."""
    state: Dict[str, Any]
    version: int
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "python"  # "python" or "javascript"

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            'state': self.state,
            'version': self.version,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }


class StateDiff:
    """Computes differences between two state objects."""

    @staticmethod
    def diff(old_state: Dict[str, Any], new_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute differences between old and new state.

        Args:
            old_state: Previous state
            new_state: New state

        Returns:
            Dictionary of changes with keys: 'added', 'modified', 'removed'
        """
        changes = {
            'added': {},
            'modified': {},
            'removed': {}
        }

        old_keys = set(old_state.keys())
        new_keys = set(new_state.keys())

        # Find added keys
        for key in new_keys - old_keys:
            changes['added'][key] = new_state[key]

        # Find removed keys
        for key in old_keys - new_keys:
            changes['removed'][key] = old_state[key]

        # Find modified keys
        for key in old_keys & new_keys:
            if old_state[key] != new_state[key]:
                changes['modified'][key] = {
                    'old': old_state[key],
                    'new': new_state[key]
                }

        return changes

    @staticmethod
    def has_changes(diff: Dict[str, Any]) -> bool:
        """Check if diff contains any changes."""
        return bool(diff['added'] or diff['modified'] or diff['removed'])

    @staticmethod
    def apply_diff(state: Dict[str, Any], diff: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a diff to a state.

        Args:
            state: Current state
            diff: Diff to apply

        Returns:
            New state with diff applied
        """
        new_state = copy.deepcopy(state)

        # Apply additions and modifications
        for key, value in diff.get('added', {}).items():
            new_state[key] = value

        for key, changes in diff.get('modified', {}).items():
            new_state[key] = changes['new']

        # Apply removals
        for key in diff.get('removed', {}).keys():
            if key in new_state:
                del new_state[key]

        return new_state


class StateManager:
    """
    Manages real-time state synchronization between Python and JavaScript.

    Features:
    - State versioning
    - Automatic diffing
    - Conflict resolution
    - Optimistic updates
    - State history
    """

    def __init__(
        self,
        conflict_resolution: ConflictResolution = ConflictResolution.LATEST_WINS,
        max_history: int = 100
    ):
        """
        Initialize state manager.

        Args:
            conflict_resolution: Strategy for resolving conflicts
            max_history: Maximum number of state snapshots to keep
        """
        self.conflict_resolution = conflict_resolution
        self.max_history = max_history

        self._states: Dict[str, StateSnapshot] = {}
        self._history: Dict[str, list[StateSnapshot]] = {}
        self._change_listeners: Dict[str, list[Callable]] = {}
        self._conflict_resolver: Optional[Callable] = None

    def get_state(self, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Get current state for a component.

        Args:
            component_name: Name of the component

        Returns:
            State dictionary or None
        """
        snapshot = self._states.get(component_name)
        return snapshot.state if snapshot else None

    def set_state(
        self,
        component_name: str,
        state: Dict[str, Any],
        source: str = "python",
        notify: bool = True
    ) -> StateSnapshot:
        """
        Set state for a component.

        Args:
            component_name: Name of the component
            state: New state
            source: Source of the state ("python" or "javascript")
            notify: Whether to notify change listeners

        Returns:
            New state snapshot
        """
        # Get current version
        current = self._states.get(component_name)
        version = (current.version + 1) if current else 1

        # Create snapshot
        snapshot = StateSnapshot(
            state=copy.deepcopy(state),
            version=version,
            source=source
        )

        # Store snapshot
        self._states[component_name] = snapshot

        # Add to history
        self._add_to_history(component_name, snapshot)

        # Notify listeners
        if notify:
            self._notify_listeners(component_name, snapshot)

        return snapshot

    def update_state(
        self,
        component_name: str,
        updates: Dict[str, Any],
        source: str = "python",
        merge: bool = True,
        notify: bool = True
    ) -> StateSnapshot:
        """
        Update component state with partial changes.

        Args:
            component_name: Name of the component
            updates: Partial state updates
            source: Source of the update
            merge: Whether to merge with existing state
            notify: Whether to notify listeners

        Returns:
            New state snapshot
        """
        current_state = self.get_state(component_name) or {}

        if merge:
            new_state = {**current_state, **updates}
        else:
            new_state = updates

        return self.set_state(component_name, new_state, source, notify)

    def sync_from_client(
        self,
        component_name: str,
        client_state: Dict[str, Any],
        client_version: Optional[int] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Synchronize state from client (JavaScript).

        Handles conflict resolution if server state has changed.

        Args:
            component_name: Name of the component
            client_state: State from client
            client_version: Client's state version (for conflict detection)

        Returns:
            Tuple of (success, conflicts_or_none)
        """
        current = self._states.get(component_name)

        # No server state yet, accept client state
        if current is None:
            self.set_state(component_name, client_state, source="javascript")
            return True, None

        # Check for conflicts
        if client_version is not None and client_version < current.version:
            # Client is behind, resolve conflict
            return self._resolve_conflict(
                component_name,
                client_state,
                current.state
            )

        # No conflict, apply client state
        self.set_state(component_name, client_state, source="javascript")
        return True, None

    def _resolve_conflict(
        self,
        component_name: str,
        client_state: Dict[str, Any],
        server_state: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Resolve a state conflict.

        Args:
            component_name: Name of the component
            client_state: State from client
            server_state: State from server

        Returns:
            Tuple of (success, resolved_state_or_conflicts)
        """
        if self.conflict_resolution == ConflictResolution.CLIENT_WINS:
            self.set_state(component_name, client_state, source="javascript")
            return True, None

        elif self.conflict_resolution == ConflictResolution.SERVER_WINS:
            # Server wins, return server state as the resolution
            return False, server_state

        elif self.conflict_resolution == ConflictResolution.LATEST_WINS:
            # Client update is latest, let it win
            self.set_state(component_name, client_state, source="javascript")
            return True, None

        elif self.conflict_resolution == ConflictResolution.MERGE:
            # Attempt to merge non-conflicting changes
            merged = self._merge_states(client_state, server_state)
            self.set_state(component_name, merged, source="merged")
            return True, None

        elif self.conflict_resolution == ConflictResolution.CUSTOM:
            if self._conflict_resolver:
                resolved = self._conflict_resolver(client_state, server_state)
                self.set_state(component_name, resolved, source="custom")
                return True, None
            else:
                # No custom resolver, fallback to server wins
                return False, server_state

        return False, server_state

    def _merge_states(
        self,
        client_state: Dict[str, Any],
        server_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge client and server states.

        Simple merge: server values take precedence for conflicting keys.

        Args:
            client_state: State from client
            server_state: State from server

        Returns:
            Merged state
        """
        merged = copy.deepcopy(client_state)
        merged.update(server_state)  # Server wins for conflicts
        return merged

    def get_diff(
        self,
        component_name: str,
        since_version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get state changes since a version.

        Args:
            component_name: Name of the component
            since_version: Version to diff from (None = no previous state)

        Returns:
            Diff dictionary or None
        """
        current = self._states.get(component_name)
        if not current:
            return None

        if since_version is None:
            # Return all current state as "added"
            return {
                'added': current.state,
                'modified': {},
                'removed': {}
            }

        # Find the snapshot at since_version
        history = self._history.get(component_name, [])
        old_snapshot = None
        for snapshot in history:
            if snapshot.version == since_version:
                old_snapshot = snapshot
                break

        if not old_snapshot:
            # Version not found, return current state
            return {
                'added': current.state,
                'modified': {},
                'removed': {}
            }

        # Compute diff
        return StateDiff.diff(old_snapshot.state, current.state)

    def get_history(
        self,
        component_name: str,
        limit: Optional[int] = None
    ) -> list[StateSnapshot]:
        """
        Get state history for a component.

        Args:
            component_name: Name of the component
            limit: Maximum number of snapshots (most recent)

        Returns:
            List of state snapshots
        """
        history = self._history.get(component_name, [])
        if limit:
            return history[-limit:]
        return history

    def rollback(
        self,
        component_name: str,
        to_version: Optional[int] = None,
        steps: int = 1
    ) -> Optional[StateSnapshot]:
        """
        Rollback state to a previous version.

        Args:
            component_name: Name of the component
            to_version: Specific version to rollback to
            steps: Number of versions to go back (if to_version not specified)

        Returns:
            Restored state snapshot or None
        """
        history = self._history.get(component_name, [])
        if not history:
            return None

        if to_version is not None:
            # Find specific version
            for snapshot in reversed(history):
                if snapshot.version == to_version:
                    self._states[component_name] = copy.deepcopy(snapshot)
                    return snapshot
        else:
            # Go back N steps
            if len(history) > steps:
                target = history[-(steps + 1)]
                self._states[component_name] = copy.deepcopy(target)
                return target

        return None

    def subscribe(
        self,
        component_name: str,
        callback: Callable[[StateSnapshot], None]
    ):
        """
        Subscribe to state changes.

        Args:
            component_name: Name of the component
            callback: Function to call on state changes
        """
        if component_name not in self._change_listeners:
            self._change_listeners[component_name] = []
        self._change_listeners[component_name].append(callback)

    def unsubscribe(
        self,
        component_name: str,
        callback: Callable[[StateSnapshot], None]
    ):
        """
        Unsubscribe from state changes.

        Args:
            component_name: Name of the component
            callback: Callback to remove
        """
        if component_name in self._change_listeners:
            try:
                self._change_listeners[component_name].remove(callback)
            except ValueError:
                pass

    def set_conflict_resolver(
        self,
        resolver: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
    ):
        """
        Set custom conflict resolver function.

        The resolver should take (client_state, server_state) and return resolved_state.

        Args:
            resolver: Conflict resolution function
        """
        self.conflict_resolution = ConflictResolution.CUSTOM
        self._conflict_resolver = resolver

    def export_state(self, component_name: str) -> Optional[str]:
        """
        Export component state as JSON.

        Args:
            component_name: Name of the component

        Returns:
            JSON string or None
        """
        snapshot = self._states.get(component_name)
        if snapshot:
            return json.dumps(snapshot.to_dict(), indent=2)
        return None

    def import_state(self, component_name: str, json_str: str):
        """
        Import component state from JSON.

        Args:
            component_name: Name of the component
            json_str: JSON string
        """
        data = json.loads(json_str)
        snapshot = StateSnapshot(
            state=data['state'],
            version=data['version'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            source=data.get('source', 'python')
        )
        self._states[component_name] = snapshot
        self._add_to_history(component_name, snapshot)

    def clear(self, component_name: Optional[str] = None):
        """
        Clear state and history.

        Args:
            component_name: Component to clear (None = clear all)
        """
        if component_name is None:
            self._states.clear()
            self._history.clear()
            self._change_listeners.clear()
        else:
            if component_name in self._states:
                del self._states[component_name]
            if component_name in self._history:
                del self._history[component_name]
            if component_name in self._change_listeners:
                del self._change_listeners[component_name]

    def _add_to_history(self, component_name: str, snapshot: StateSnapshot):
        """Add snapshot to history."""
        if component_name not in self._history:
            self._history[component_name] = []

        self._history[component_name].append(copy.deepcopy(snapshot))

        # Limit history size
        if len(self._history[component_name]) > self.max_history:
            self._history[component_name] = self._history[component_name][-self.max_history:]

    def _notify_listeners(self, component_name: str, snapshot: StateSnapshot):
        """Notify all change listeners."""
        if component_name in self._change_listeners:
            for callback in self._change_listeners[component_name]:
                try:
                    callback(snapshot)
                except Exception as e:
                    print(f"Error in state change listener: {e}")


# Export public API
__all__ = [
    'StateManager',
    'StateDiff',
    'StateSnapshot',
    'ConflictResolution'
]
