"""
Thread-safe broadcast queue for WebSocket events.

This module provides a queue-based system to safely broadcast database changes
from worker threads to WebSocket clients in the main event loop.
"""

import asyncio
import logging
from queue import Queue
from typing import Dict, Any, Optional
from globe_server.utils.eventbus import event_bus

logger = logging.getLogger(__name__)

# Thread-safe queue for broadcast messages
_broadcast_queue: Queue = Queue()
_worker_task: Optional[asyncio.Task] = None


def queue_broadcast(topic: str, data: Dict[str, Any]) -> None:
    """
    Add a broadcast message to the queue.
    
    This is thread-safe and can be called from any context (sync or async, any thread).
    
    Args:
        topic: The WebSocket topic/channel to broadcast to
        data: The data to broadcast
    """
    _broadcast_queue.put({"topic": topic, "data": data})
    logger.debug(f"Queued broadcast for topic '{topic}'")


async def broadcast_message(topic: str, data: Dict[str, Any]) -> None:
    """
    Directly broadcast a message from async context.
    
    Use this when you're already in an async context and want to broadcast immediately
    without going through the queue.
    
    Args:
        topic: The WebSocket topic/channel to broadcast to
        data: The data to broadcast
    """
    await event_bus.emit(topic, data)
    logger.debug(f"Broadcasted message to topic '{topic}'")


async def _broadcast_worker() -> None:
    """
    Background worker that processes the broadcast queue.
    
    This runs in the main event loop and safely broadcasts messages
    that were queued from worker threads.
    """
    logger.info("Broadcast worker started")
    
    while True:
        try:
            # Check if there are messages to broadcast
            if not _broadcast_queue.empty():
                message = _broadcast_queue.get_nowait()
                topic = message["topic"]
                data = message["data"]
                
                try:
                    # Emit the event - event_bus will handle WebSocket broadcasting
                    await event_bus.emit(topic, data)
                    logger.debug(f"Broadcasted {topic} event")
                    
                except Exception as e:
                    logger.error(f"Error broadcasting {topic}: {e}")
                
                _broadcast_queue.task_done()
            
            # Small delay to prevent CPU hogging
            await asyncio.sleep(0.05)  # 50ms
            
        except Exception as e:
            logger.error(f"Error in broadcast worker: {e}")
            await asyncio.sleep(0.1)


async def start_broadcast_worker() -> None:
    """Start the broadcast worker task."""
    global _worker_task
    
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_broadcast_worker())
        logger.info("Broadcast worker task created")
    else:
        logger.warning("Broadcast worker already running")


async def stop_broadcast_worker() -> None:
    """Stop the broadcast worker task."""
    global _worker_task
    
    if _worker_task and not _worker_task.done():
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
        logger.info("Broadcast worker stopped")
