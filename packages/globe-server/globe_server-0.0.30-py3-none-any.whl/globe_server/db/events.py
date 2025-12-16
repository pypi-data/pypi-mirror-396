"""
SQLAlchemy event listeners and event emission.

This module sets up event listeners for SQLAlchemy models and provides
functions to emit events when model data changes.
"""

import asyncio
import logging
from typing import Dict, Any, Set, Type, Optional
import inspect

from sqlalchemy import event
from sqlalchemy.orm import Session, object_mapper
from sqlalchemy.orm.attributes import get_history

from globe_server.db.orm import (
    Base, Settings, Media, PlaylistItem, ErrorLog
)
from globe_server.utils.eventbus import event_bus

logger = logging.getLogger(__name__)

# Track which models should emit events and to which topics
MODEL_TOPICS = {
    Settings: "settings",
    Media: "media",
    PlaylistItem: "playlist_item",
}

# Keep track of objects changed in a session
changed_objects = set()


def model_to_dict(model: Base) -> Dict[str, Any]:
    """Convert a SQLAlchemy model to a dictionary."""
    result = {}
    for column in object_mapper(model).columns:
        result[column.key] = getattr(model, column.key)
    return result


@event.listens_for(Session, "after_flush")
def after_flush(session: Session, flush_context):
    """Track objects that were changed during a flush."""
    global changed_objects
    
    # Add new and modified objects to the tracking set
    changed_objects.update(session.new)
    changed_objects.update(session.dirty)
    
    # Don't handle deleted objects here as they're tricky with the ORM


@event.listens_for(Session, "after_commit")
def after_commit(session):
    """Emit events after a successful commit."""
    global changed_objects
    
    # Import here to avoid circular imports
    from globe_server.db.broadcast_queue import queue_broadcast
    
    # Process each changed object
    for obj in changed_objects:
        # Check if we're tracking this model type
        if type(obj) in MODEL_TOPICS:
            topic = MODEL_TOPICS[type(obj)]
            data = model_to_dict(obj)
            
            # Queue the broadcast (thread-safe)
            queue_broadcast(topic, data)
            logger.debug(f"Queued broadcast for {topic}")
    
    # Clear the tracking set after commit
    changed_objects.clear()


@event.listens_for(Session, "after_rollback")
def after_rollback(session):
    """Clear tracked objects after a rollback."""
    global changed_objects
    changed_objects.clear()


async def _emit_event(topic: str, data: Dict[str, Any]):
    """Helper function to emit events."""
    try:
        await event_bus.emit(topic, data)
        logger.debug(f"Emitted event for topic {topic}")
    except Exception as e:
        logger.error(f"Error emitting event for topic {topic}: {e}")


# Special case for deletion events
@event.listens_for(Session, "after_flush")
def handle_after_flush_for_deleted(session, flush_context):
    """Handle deletion events."""
    # Import here to avoid circular imports
    from globe_server.db.broadcast_queue import queue_broadcast
    
    # Check for deleted objects
    for obj in session.deleted:
        if type(obj) in MODEL_TOPICS:
            topic = MODEL_TOPICS[type(obj)]
            data = {"id": getattr(obj, "id"), "_action": "deleted"}
            
            # Queue the deletion broadcast (thread-safe)
            queue_broadcast(topic, data)
            logger.debug(f"Queued deletion broadcast for {topic}")


# Initialize the event system
def init_events():
    """Initialize the event system (placeholder for additional setup)."""
    logger.info("Initialized database event listeners")
