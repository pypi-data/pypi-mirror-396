"""Event emitter base class for playback components."""

from typing import Dict, List, Any, Callable, Optional



class EventEmitter:
    """Basic event emitter implementation."""
    
    def __init__(self):
        self._events = {}
        
    def on(self, event: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register an event handler.
        
        Args:
            event: Event name to listen for
            callback: Function to call when event is emitted
        """
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(callback)
        
    def off(self, event: str, callback: Callable = None) -> None:
        """Unregister an event handler.
        
        Args:
            event: Event name to unregister from
            callback: Specific callback to remove, or None to remove all
        """
        if event not in self._events:
            return
            
        if callback is None:
            self._events[event] = []
        else:
            self._events[event] = [cb for cb in self._events[event] if cb != callback]
            
    def emit(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event to all registered handlers.
        
        Args:
            event: Event name to emit
            data: Data to pass to event handlers
        """
        if data is None:
            data = {}
            
        if event in self._events:
            for callback in self._events[event]:
                callback(data)
