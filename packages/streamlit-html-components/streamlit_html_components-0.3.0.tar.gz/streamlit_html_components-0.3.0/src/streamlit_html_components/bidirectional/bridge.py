"""Bidirectional communication bridge between JavaScript and Python."""

from typing import Callable, Optional, Any, Dict, List
from datetime import datetime
from dataclasses import dataclass, field
import json


@dataclass
class Event:
    """Represents a communication event."""
    component_name: str
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'component': self.component_name,
            'event': self.event_type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


class BidirectionalBridge:
    """
    Manages bidirectional communication between JavaScript and Python.

    Features:
    - JavaScript → Python communication via postMessage
    - Python → JavaScript data passing via component props
    - Event callback registration
    """

    def __init__(self):
        """Initialize the bidirectional bridge."""
        self._callbacks: Dict[str, Callable] = {}
        self._state: Dict[str, Dict[str, Any]] = {}  # Component states
        self._event_history: List[Event] = []  # Event replay capability
        self._max_history_size: int = 1000  # Limit event history size
        self._state_subscribers: Dict[str, List[Callable]] = {}  # State change listeners

    def wrap_with_bridge(
        self,
        html_content: str,
        component_name: str,
        allowed_origins: Optional[list[str]] = None
    ) -> str:
        """
        Inject communication bridge script into HTML content with origin validation.

        The bridge enables:
        - window.sendToStreamlit(eventType, data) for JS → Python
        - window.onStreamlitData(args) for Python → JS

        Args:
            html_content: Original HTML content
            component_name: Name of the component (for event routing)
            allowed_origins: List of allowed origins (default: window.location.origin)

        Returns:
            HTML content with injected bridge script

        Security:
            - Uses origin validation instead of wildcard (*)
            - Validates incoming messages by origin
            - Uses window.location.origin as default trusted origin
        """
        # Determine target origin for postMessage
        # If no specific origins provided, use window.location.origin (same-origin)
        if allowed_origins and allowed_origins != ['*']:
            # Use first allowed origin or window.location.origin
            target_origin = allowed_origins[0] if allowed_origins[0] != '*' else "window.location.origin"
            # For validation list
            origins_check = ', '.join(f'"{origin}"' for origin in allowed_origins if origin != '*')
            if not origins_check:
                origins_check = 'window.location.origin'
        else:
            # Default to same-origin
            target_origin = "window.location.origin"
            origins_check = "window.location.origin"

        bridge_script = f"""
<script>
// Streamlit HTML Components - Bidirectional Communication Bridge (Secure)
(function() {{
    const COMPONENT_NAME = '{component_name}';
    const ALLOWED_ORIGINS = [{origins_check}];
    const TARGET_ORIGIN = {target_origin};

    // Check if origin is allowed
    function isOriginAllowed(origin) {{
        if (Array.isArray(ALLOWED_ORIGINS)) {{
            return ALLOWED_ORIGINS.includes(origin);
        }}
        return origin === ALLOWED_ORIGINS;
    }}

    // Send data from JavaScript to Python (with origin validation)
    window.sendToStreamlit = function(eventType, data) {{
        if (typeof eventType !== 'string') {{
            console.error('[Bridge] sendToStreamlit: eventType must be a string');
            return;
        }}

        if (!window.parent || window.parent === window) {{
            console.error('[Bridge] Cannot send message: no parent frame');
            return;
        }}

        const message = {{
            type: 'streamlit:setComponentValue',
            value: {{
                event: eventType,
                data: data || {{}},
                component: COMPONENT_NAME,
                timestamp: Date.now()
            }}
        }};

        console.log('[Bridge] Sending to Streamlit:', message);
        // Use validated origin instead of wildcard
        window.parent.postMessage(message, TARGET_ORIGIN);
    }};

    // Receive data from Python (via Streamlit component API) with origin validation
    window.addEventListener('message', function(event) {{
        // Validate origin
        if (!isOriginAllowed(event.origin)) {{
            console.warn('[Bridge] Ignoring message from untrusted origin:', event.origin);
            return;
        }}

        if (event.data.type === 'streamlit:render') {{
            const args = event.data.args;

            if (window.onStreamlitData && typeof window.onStreamlitData === 'function') {{
                console.log('[Bridge] Received from Streamlit:', args);
                window.onStreamlitData(args);
            }}
        }}
    }});

    // Notify Streamlit that component is ready (with origin validation)
    if (window.parent && window.parent !== window) {{
        window.parent.postMessage({{
            type: 'streamlit:componentReady',
            apiVersion: 1
        }}, TARGET_ORIGIN);
    }}

    console.log('[Bridge] Initialized for:', COMPONENT_NAME, 'Allowed origins:', ALLOWED_ORIGINS);
}})();
</script>
"""

        # Insert bridge script before closing body tag, or at the end if no body tag
        if "</body>" in html_content.lower():
            # Find the last occurrence of </body> (case insensitive)
            import re
            html_content = re.sub(
                r'</body>',
                f'{bridge_script}</body>',
                html_content,
                count=1,
                flags=re.IGNORECASE
            )
        else:
            # No body tag, append at the end
            html_content += bridge_script

        return html_content

    def register_callback(
        self,
        component_name: str,
        event_type: str,
        callback: Callable[[Dict[str, Any]], None]
    ):
        """
        Register a Python callback for JavaScript events.

        Args:
            component_name: Name of the component
            event_type: Type of event (e.g., 'click', 'submit', 'change')
            callback: Python function to call when event is triggered

        Example:
            >>> def on_button_click(data):
            ...     print(f"Button clicked with data: {data}")
            >>>
            >>> bridge.register_callback('my_button', 'click', on_button_click)
        """
        key = f"{component_name}:{event_type}"
        self._callbacks[key] = callback

    def handle_event(self, component_name: str, event_data: Dict[str, Any], record: bool = True):
        """
        Process an event received from JavaScript.

        Args:
            component_name: Name of the component that sent the event
            event_data: Event data including 'event' type and 'data' payload
            record: Whether to record this event for replay
        """
        event_type = event_data.get('event')
        if not event_type:
            return

        # Record event if requested
        if record:
            self.record_event(component_name, event_type, event_data.get('data', {}))

        key = f"{component_name}:{event_type}"
        callback = self._callbacks.get(key)

        if callback:
            try:
                callback(event_data.get('data', {}))
            except Exception as e:
                # Log error but don't break Streamlit app
                print(f"Error in component callback: {e}")

    def unregister_callback(self, component_name: str, event_type: str):
        """
        Unregister a callback.

        Args:
            component_name: Name of the component
            event_type: Type of event
        """
        key = f"{component_name}:{event_type}"
        if key in self._callbacks:
            del self._callbacks[key]

    def clear_callbacks(self, component_name: Optional[str] = None):
        """
        Clear callbacks for a component or all callbacks.

        Args:
            component_name: If provided, only clear callbacks for this component.
                          If None, clear all callbacks.
        """
        if component_name is None:
            self._callbacks.clear()
        else:
            keys_to_remove = [
                key for key in self._callbacks.keys()
                if key.startswith(f"{component_name}:")
            ]
            for key in keys_to_remove:
                del self._callbacks[key]

    # ===== State Management =====

    def set_state(self, component_name: str, state: Dict[str, Any], notify: bool = True):
        """
        Set the state for a component.

        Args:
            component_name: Name of the component
            state: State dictionary
            notify: Whether to notify state subscribers
        """
        self._state[component_name] = state.copy()

        if notify:
            self._notify_state_change(component_name, state)

    def get_state(self, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state for a component.

        Args:
            component_name: Name of the component

        Returns:
            State dictionary or None if not found
        """
        return self._state.get(component_name)

    def update_state(
        self,
        component_name: str,
        updates: Dict[str, Any],
        merge: bool = True,
        notify: bool = True
    ):
        """
        Update component state with new values.

        Args:
            component_name: Name of the component
            updates: Dictionary of state updates
            merge: If True, merge with existing state; if False, replace
            notify: Whether to notify state subscribers
        """
        if component_name not in self._state:
            self._state[component_name] = {}

        if merge:
            self._state[component_name].update(updates)
        else:
            self._state[component_name] = updates.copy()

        if notify:
            self._notify_state_change(component_name, self._state[component_name])

    def subscribe_to_state(
        self,
        component_name: str,
        callback: Callable[[Dict[str, Any]], None]
    ):
        """
        Subscribe to state changes for a component.

        Args:
            component_name: Name of the component
            callback: Function to call when state changes
        """
        if component_name not in self._state_subscribers:
            self._state_subscribers[component_name] = []
        self._state_subscribers[component_name].append(callback)

    def unsubscribe_from_state(
        self,
        component_name: str,
        callback: Callable[[Dict[str, Any]], None]
    ):
        """
        Unsubscribe from state changes.

        Args:
            component_name: Name of the component
            callback: Callback to remove
        """
        if component_name in self._state_subscribers:
            try:
                self._state_subscribers[component_name].remove(callback)
            except ValueError:
                pass

    def _notify_state_change(self, component_name: str, state: Dict[str, Any]):
        """Notify all subscribers of a state change."""
        if component_name in self._state_subscribers:
            for callback in self._state_subscribers[component_name]:
                try:
                    callback(state)
                except Exception as e:
                    print(f"Error in state subscriber callback: {e}")

    def get_state_update_script(self, component_name: str) -> str:
        """
        Generate JavaScript code to push state updates to the component.

        Args:
            component_name: Name of the component

        Returns:
            JavaScript code string
        """
        state = self.get_state(component_name)
        if state is None:
            return ""

        state_json = json.dumps(state)
        return f"""
<script>
(function() {{
    if (window.onStreamlitData && typeof window.onStreamlitData === 'function') {{
        window.onStreamlitData({state_json});
    }}
}})();
</script>
"""

    # ===== Event Recording & Replay =====

    def record_event(
        self,
        component_name: str,
        event_type: str,
        data: Dict[str, Any]
    ):
        """
        Record an event for replay capability.

        Args:
            component_name: Name of the component
            event_type: Type of event
            data: Event data
        """
        event = Event(
            component_name=component_name,
            event_type=event_type,
            data=data
        )

        self._event_history.append(event)

        # Limit history size
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size:]

    def get_event_history(
        self,
        component_name: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Event]:
        """
        Get recorded events, optionally filtered.

        Args:
            component_name: Filter by component name
            event_type: Filter by event type
            limit: Maximum number of events to return (most recent)

        Returns:
            List of events
        """
        events = self._event_history

        if component_name:
            events = [e for e in events if e.component_name == component_name]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if limit:
            events = events[-limit:]

        return events

    def replay_events(
        self,
        component_name: Optional[str] = None,
        event_type: Optional[str] = None
    ):
        """
        Replay recorded events by triggering their callbacks.

        Args:
            component_name: Replay only events from this component
            event_type: Replay only events of this type
        """
        events = self.get_event_history(component_name, event_type)

        for event in events:
            event_data = {
                'event': event.event_type,
                'data': event.data,
                'component': event.component_name,
                'timestamp': event.timestamp.isoformat()
            }
            self.handle_event(event.component_name, event_data)

    def clear_event_history(
        self,
        component_name: Optional[str] = None,
        event_type: Optional[str] = None
    ):
        """
        Clear event history.

        Args:
            component_name: Clear only events from this component
            event_type: Clear only events of this type
        """
        if component_name is None and event_type is None:
            self._event_history.clear()
        else:
            self._event_history = [
                e for e in self._event_history
                if (component_name and e.component_name != component_name)
                or (event_type and e.event_type != event_type)
            ]

    def export_events(
        self,
        component_name: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> str:
        """
        Export events as JSON string.

        Args:
            component_name: Export only events from this component
            event_type: Export only events of this type

        Returns:
            JSON string of events
        """
        events = self.get_event_history(component_name, event_type)
        events_dict = [e.to_dict() for e in events]
        return json.dumps(events_dict, indent=2)


# Global bridge instance
_bridge = BidirectionalBridge()


def get_bridge() -> BidirectionalBridge:
    """
    Get the global bidirectional bridge instance.

    Returns:
        Global BidirectionalBridge instance
    """
    return _bridge
