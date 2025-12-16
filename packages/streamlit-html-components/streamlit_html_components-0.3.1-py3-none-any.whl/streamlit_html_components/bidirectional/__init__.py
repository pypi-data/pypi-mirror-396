"""Bidirectional communication between JavaScript and Python."""

from .bridge import BidirectionalBridge, get_bridge, Event
from .sync import StateManager, StateDiff, StateSnapshot, ConflictResolution

__all__ = [
    'BidirectionalBridge',
    'get_bridge',
    'Event',
    'StateManager',
    'StateDiff',
    'StateSnapshot',
    'ConflictResolution'
]
