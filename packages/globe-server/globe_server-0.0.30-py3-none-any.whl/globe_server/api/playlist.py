# app/api/playlist.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from globe_server.db.orm import Media, PlaylistItem
from globe_server.db.database import create, update, delete, get_by_id, get_all, get_max_position, get_all_ordered_by_position, update_playlist_position
from globe_server.db.schemas import PlaylistItemCreate, PlaylistItemUpdate, PlaylistItemRead
import os
import logging

# Create router for REST endpoints
router = APIRouter(prefix="/playlist", tags=["playlist"])

# Helper functions for consistent data handling using SQLAlchemy ORM

def _get_playlist_item_with_media(playlist_id: int) -> Optional[PlaylistItem]:
    """Fetch a single playlist item with its media data using ORM"""
    return get_by_id(PlaylistItem, playlist_id)

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def get_playlist_items() -> List[PlaylistItem]:
    """
    Get all playlist items ordered by position.
    """
    return get_all_ordered_by_position()

# =====================================================================
# API ENDPOINTS
# =====================================================================

@router.get("/", response_model=List[PlaylistItemRead])
async def get_all_playlist_items():
    """
    Get all playlist items with complete media details.
    
    This endpoint is for direct REST API access to playlist data.
    Real-time updates are now handled by the status WebSocket.
    """
    return get_playlist_items()

@router.post("/", response_model=PlaylistItemRead)
async def create_playlist_item(playlist_item: PlaylistItemCreate):
    logging.info(f"=== CREATE PLAYLIST ITEM CALLED ===")
    logging.info(f"Received playlist_item: {playlist_item}")
    
    try:
        # Check if the media_id exists
        logging.info(f"Checking if media_id {playlist_item.media_id} exists...")
        media = get_by_id(Media, playlist_item.media_id)
        if media is None:
            logging.error(f"Media ID {playlist_item.media_id} not found")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid media_id"
            )
        logging.info(f"Media found: {media.name}")

        # Get the next available position
        logging.info("Getting next position...")
        next_position = get_max_position() + 1
        logging.info(f"Next position: {next_position}")

        # Create new playlist item
        logging.info("Creating PlaylistItem object...")
        new_item = PlaylistItem(
            media_id=playlist_item.media_id,
            position=next_position,
            status="unplayed",
            elapsed_time=0
        )
        
        # Use CRUD function that handles broadcasting
        logging.info("Calling create() to save to database...")
        new_item = create(new_item)
        logging.info(f"Successfully created playlist item with ID: {new_item.id}")
        
        return new_item
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating playlist item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@router.get("/{playlist_id}", response_model=PlaylistItemRead)
async def get_playlist_item(playlist_id: int):
    """
    NOTE: This endpoint is not currently used by the frontend.
    The frontend primarily receives playlist data via WebSockets.
    
    This endpoint is kept for API completeness, external tools,
    and as a fallback mechanism.
    """
    playlist_item = _get_playlist_item_with_media(playlist_id)
    if playlist_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Playlist item not found"
        )
        
    return playlist_item

@router.put("/{playlist_id}", response_model=PlaylistItemRead)
async def update_playlist_item(playlist_id: int, playlist_item_update: PlaylistItemUpdate):
    try:
        # Check if the item exists
        db_item = get_by_id(PlaylistItem, playlist_id)
        if db_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Playlist item not found"
            )
            
        # Check if media_id exists if it's being updated
        if playlist_item_update.media_id is not None:
            media = get_by_id(Media, playlist_item_update.media_id)
            if media is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid media_id"
                )

        # Update the playlist item attributes
        update_data = playlist_item_update.model_dump(exclude_unset=True)
        
        # If position is being updated, use database function to handle shifts
        if 'position' in update_data:
            new_position = update_data['position']
            logging.info(f"Updating item {playlist_id} position to {new_position}")
            
            # Database function handles shifting other items and updating this one
            update_playlist_position(playlist_id, new_position)
            
            # Get the updated item to return
            db_item = get_by_id(PlaylistItem, playlist_id)
        else:
            # No position change, just update other attributes
            for key, value in update_data.items():
                setattr(db_item, key, value)
            db_item = update(db_item)
        
        # Broadcasting is now handled by the CRUD functions
        return db_item
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating playlist item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@router.delete("/{playlist_id}")
async def delete_playlist_item(playlist_id: int):
    try:
        # Check if the item exists
        db_item = get_by_id(PlaylistItem, playlist_id)
        if db_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Playlist item not found"
            )
            
        # Delete the item using CRUD function
        delete(db_item)

        # Reset positions for remaining items
        all_items = get_all_ordered_by_position()
        for i, item in enumerate(all_items, 1):
            if item.position != i:
                item.position = i
                update(item)
        
        # Broadcasting is now handled by the CRUD functions
        return {"message": "Playlist item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting playlist item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )