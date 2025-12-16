"""
Event bus system for broadcasting changes to WebSocket clients.

This module provides a simple event bus that allows status updates,
database changes, and other events to be broadcast to connected 
WebSocket clients in real-time.
"""

import logging
import asyncio
from typing import Dict, Any, List, Callable, Awaitable, Union

logger = logging.getLogger(__name__)

# Type alias for event callbacks
EventCallback = Callable[[Dict[str, Any]], Union[None, Awaitable[None]]]


class EventBus:
    """
    Event bus for broadcasting status updates and database changes.
    
    This class allows components to subscribe to events (status updates,
    database changes, etc.) and receive notifications in real-time.
    """
    
    def __init__(self):
        self.listeners: Dict[str, List[EventCallback]] = {}
    
    def subscribe(self, topic: str, callback: EventCallback) -> None:
        """
        Subscribe to events for a specific topic.
        
        Args:
            topic: The topic/channel to listen to (e.g., "server", "network", "playlist")
            callback: The callback function to invoke when an event occurs
        """
        if topic not in self.listeners:
            self.listeners[topic] = []
        self.listeners[topic].append(callback)
        logger.debug(f"Added listener for topic '{topic}', total listeners: {len(self.listeners[topic])}")
    
    def unsubscribe(self, topic: str, callback: EventCallback) -> None:
        """
        Unsubscribe from events for a specific topic.
        
        Args:
            topic: The topic/channel to unsubscribe from
            callback: The callback function to remove
        """
        if topic in self.listeners and callback in self.listeners[topic]:
            self.listeners[topic].remove(callback)
            logger.debug(f"Removed listener for topic '{topic}', remaining: {len(self.listeners[topic])}")
    
    async def emit(self, topic: str, data: Dict[str, Any]) -> None:
        """
        Emit an event for a specific topic with data.
        
        Args:
            topic: The topic/channel to broadcast to
            data: The data to send to listeners
        """
        if topic in self.listeners and self.listeners[topic]:
            logger.debug(f"Emitting event for topic '{topic}' to {len(self.listeners[topic])} listeners")
            for callback in self.listeners[topic]:
                try:
                    # Handle both async and sync callbacks
                    result = callback(data)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as e:
                    logger.error(f"Error in event listener for topic '{topic}': {e}")

# Create a singleton instance
event_bus = EventBus()
