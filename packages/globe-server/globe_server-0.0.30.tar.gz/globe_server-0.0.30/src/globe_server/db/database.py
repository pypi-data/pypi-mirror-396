"""
Database connection and utilities.

This module provides functions to connect to the database and perform common operations,
using SQLAlchemy ORM for direct model manipulation.
"""

import logging
from typing import Optional, Type, List, Dict, Any, TypeVar

from sqlalchemy.orm import Session as SQLAlchemySession

from globe_server.db.orm import (
    Session, Base,
    Media, PlaylistItem, Settings, ErrorLog
)

logger = logging.getLogger(__name__)

# Type variable for ORM models
T = TypeVar('T', bound=Base)


def disconnect() -> None:
    """Close all SQLAlchemy sessions."""
    Session.remove()

# Generic CRUD operations
def get_by_id(model_class: Type[T], id: int) -> Optional[T]:
    """Get a model instance by ID."""
    session = get_db()
    try:
        return session.query(model_class).filter(model_class.id == id).first()
    finally:
        Session.remove()

def create(model_instance: T) -> T:
    """Create a new model instance (broadcast handled by SQLAlchemy events)."""
    session = get_db()
    try:
        session.add(model_instance)
        session.commit()
        session.refresh(model_instance)
        return model_instance
    finally:
        Session.remove()

def update(model_instance: T) -> T:
    """Update an existing model instance (broadcast handled by SQLAlchemy events)."""
    session = get_db()
    try:
        session.add(model_instance)
        session.commit()
        session.refresh(model_instance)
        return model_instance
    finally:
        Session.remove()

def delete(model_instance: T) -> None:
    """Delete a model instance (broadcast handled by SQLAlchemy events)."""
    session = get_db()
    try:
        session.delete(model_instance)
        session.commit()
    finally:
        Session.remove()

def bulk_update(items: List[T]) -> None:
    """
    Update multiple items in a single transaction.
    
    This is much more efficient than calling update() for each item individually,
    as it uses a single database transaction instead of N transactions.
    
    Args:
        items: List of ORM model instances to update
        
    Example:
        # Reset all playlist items
        items = get_all(PlaylistItem)
        for item in items:
            item.status = 'unplayed'
            item.elapsed_time = 0
        bulk_update(items)
    """
    if not items:
        return
        
    session = get_db()
    try:
        for item in items:
            session.add(item)
        session.commit()
        # Refresh all items to get updated values
        for item in items:
            session.refresh(item)
    finally:
        Session.remove()

def update_playlist_position(item_id: int, new_position: int) -> None:
    """
    Update a playlist item's position, shifting other items to make space.
    
    Args:
        item_id: ID of the playlist item to move
        new_position: Desired new position (1-indexed)
        
    Example:
        # Move item 7 to position 1
        # Before: [A(1), B(2), C(3), D(4)] where C has id=7
        # After:  [C(1), A(2), B(3), D(4)]
        update_playlist_position(7, 1)
    """
    # Get the item being moved
    item = get_by_id(PlaylistItem, item_id)
    if not item:
        raise ValueError(f"Playlist item {item_id} not found")
    
    old_position = item.position
    
    if old_position == new_position:
        return  # No move needed
    
    # Get all items
    all_items = get_all_ordered_by_position()
    
    # Shift items to make space
    for other_item in all_items:
        if other_item.id == item_id:
            # This is the item being moved - update to new position
            other_item.position = new_position
        elif old_position < new_position:
            # Moving down: shift items up between old and new positions
            if old_position < other_item.position <= new_position:
                other_item.position -= 1
        else:
            # Moving up: shift items down between new and old positions
            if new_position <= other_item.position < old_position:
                other_item.position += 1
    
    # Update all affected items in one transaction
    bulk_update(all_items)

def get_all(model_class: Type[T]) -> List[T]:
    """Get all instances of a model."""
    session = get_db()
    try:
        return session.query(model_class).all()
    finally:
        Session.remove()

# Error logging function (keeping this as it has specific logic)
def log_error(endpoint: str, message: str, stacktrace: Optional[str] = None) -> Optional[ErrorLog]:
    """Log an error to the database."""
    session = get_db()
    try:
        error = ErrorLog(endpoint=endpoint, message=message, stacktrace=stacktrace)
        session.add(error)
        session.commit()
        return error
    except Exception as e:
        logger.error(f"Error inserting into errors table: {e}")
        session.rollback()
        return None
    finally:
        Session.remove()

# Helper function to get singleton records
def get_singleton(model_class: Type[T]) -> Optional[T]:
    """Get the singleton instance of a model (assumes only one record exists)."""
    session = get_db()
    try:
        return session.query(model_class).first()
    finally:
        Session.remove()

# Playlist-specific helper functions
def get_max_position() -> int:
    """Get the maximum position value from playlist items."""
    session = get_db()
    try:
        max_item = session.query(PlaylistItem).order_by(PlaylistItem.position.desc()).first()
        return max_item.position if max_item else 0
    finally:
        Session.remove()

def get_all_ordered_by_position() -> List[PlaylistItem]:
    """Get all playlist items ordered by position."""
    session = get_db()
    try:
        return session.query(PlaylistItem).order_by(PlaylistItem.position).all()
    finally:
        Session.remove()

def get_first_by_status(status: str) -> Optional[PlaylistItem]:
    """Get the first playlist item with a specific status, ordered by position."""
    session = get_db()
    try:
        return session.query(PlaylistItem).filter(PlaylistItem.status == status).order_by(PlaylistItem.position).first()
    finally:
        Session.remove()

def get_db():
    """
    Get a database session.
    
    Note: This returns a scoped session. The caller is responsible for
    committing/rolling back. The session will be automatically cleaned up
    by the scoped_session registry.
    
    For FastAPI dependency injection, use Depends(get_db) which handles
    the session lifecycle automatically.
    """
    return Session()