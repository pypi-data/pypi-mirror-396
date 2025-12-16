# app/api/media.py
from fastapi import APIRouter, Depends, HTTPException, Header, status, UploadFile, File, Form, Query
from typing import List
from sqlalchemy.orm import Session
from globe_server.db.orm import Media
from globe_server.db.database import create, update, delete, get_by_id, get_all
from globe_server.db.schemas import MediaCreate, MediaRead, MediaUpdate, PlanetOptions
from globe_server.utils import files
from globe_server import config
import os
import logging
import json

router = APIRouter(prefix="/media", tags=["media"])

@router.get("/files")
def list_media_files(type: str = Query(..., regex="^(video|image)$")):
    """List available media files on the server for a given type."""
    try:
        file_list = files.list_media_files(type)
        return {"files": file_list}
    except Exception as e:
        logging.error(f"Error listing media files: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    media_type: str = Form(...),
):
    try:
        if media_type == "image":
            upload_directory = os.path.join(config.GLOBE_MEDIA_DIRECTORY, "Images")
        elif media_type == "video":
            upload_directory = os.path.join(config.GLOBE_MEDIA_DIRECTORY, "Videos")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid media type: {media_type}. Allowed types: image, video"
            )

        file_path = await files.save_uploaded_file(file, upload_directory)
        return {"filepath": file_path}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[MediaRead])
def get_all_media():
    try:
        media_items = get_all(Media)
        return media_items
    except Exception as e:
        logging.error(f"Error getting all media: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@router.post("/", response_model=MediaRead)
def create_media(media: MediaCreate):
    try:
        # Only validate filepath for image and video types
        if media.type in ("image", "video"):
            if not media.filepath or not os.path.exists(media.filepath):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Filepath is required and must exist for image and video types",
                )

        # Serialize planet_options to JSON string if it exists
        planet_options_json = None
        if media.planet_options:
            if isinstance(media.planet_options, dict):
                planet_options_json = json.dumps(media.planet_options)
            else:
                planet_options_json = media.planet_options.model_dump_json(exclude_none=True)

        # Create new media item
        db_media = Media(
            type=media.type,
            name=media.name,
            filepath=media.filepath,
            display_duration=media.display_duration,
            planet_options=planet_options_json
        )
        
        # Use CRUD function that handles broadcasting
        db_media = create(db_media)
        
        return db_media
    except Exception as e:
        logging.error(f"Error creating media: {e}")
        #db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@router.get("/{media_id}", response_model=MediaRead)
def get_media(media_id: int):
    try:
        media = get_by_id(Media, media_id)
        if media is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media item not found"
            )
        return media
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting media: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@router.put("/{media_id}", response_model=MediaRead)
def update_media(media_id: int, media_update: MediaUpdate):
    try:
        # Get the existing media item
        db_media = get_by_id(Media, media_id)
        if db_media is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media item not found"
            )

        # Update the fields that are provided
        update_data = media_update.model_dump(exclude_unset=True)
        
        # Handle planet_options separately if it exists
        if 'planet_options' in update_data and update_data['planet_options'] is not None:
            if isinstance(update_data['planet_options'], dict):
                db_media.planet_options = json.dumps(update_data['planet_options'])
            else:
                db_media.planet_options = update_data['planet_options'].model_dump_json(exclude_none=True)
            del update_data['planet_options']

        # Update all other fields
        for key, value in update_data.items():
            if value is not None:  # Only update non-None values
                setattr(db_media, key, value)

        # Use CRUD function that handles broadcasting
        db_media = update(db_media)
        
        return db_media
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating media: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@router.delete("/{media_id}")
def delete_media(media_id: int):
    try:
        # Get the media item
        db_media = get_by_id(Media, media_id)
        if db_media is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media item not found"
            )
        
        # Store filepath and type before deletion
        filepath = db_media.filepath
        media_type = db_media.type
        
        # Delete the media item from the database using CRUD function
        delete(db_media)
        
        # Delete the file from the file system if it's an image or video
        if media_type in ("image", "video") and filepath:
            try:
                files.delete_file(filepath)
            except Exception as e:
                # Log the error but don't raise an exception, as the media item has already been deleted
                logging.warning(f"Error deleting file: {e}")
        
        return {"message": "Media item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting media: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )